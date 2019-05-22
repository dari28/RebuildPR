"""module containing background tasks"""
import os

from background_task import background
import sys
import json
from bson import ObjectId
from background_task.models_completed import CompletedTask

# from lib import markup_manage
# from lib import tools
# from lib import learning_model as model
# from lib.dictionary import defix_name_field
# from nlp.config import SEND_POST_URL
# from lib.json_encoder import JSONEncoderHttp
from wiki_parser import get_us_state_list, get_country_names_list, get_pr_city_list
#from lib.learning_model import get_tags
from news import get_sources, get_everything
import hashlib
# coding=utf-8
import urllib3
import re
import requests
from bs4 import BeautifulSoup, NavigableString
import pycountry
import geoposition as geo
from lib import mongo_connection as mongo
from tags import get_tags

@background(schedule=1)
def update_country_list():
    mongodb = mongo.MongoConnection()
    try:
        print("Background task get_country_names_list started")
        mongodb.update_country_list()
        print("Background task get_country_names_list finished")
    except:
        pass


@background(schedule=1)
def get_pr_city_list():
    pr_city_list = []
    try:

        url = requests.get('https://suburbanstats.org/population/puerto-rico/list-of-counties-and-cities-in-puerto-rico').text
        soup = BeautifulSoup(url, 'lxml')
        pr_city = soup.findAll('a', title=re.compile('Population Demographics and Statistics'))
        for city in pr_city:
            ct = dict()
            ct['country'] = '5cdc1484cde53353db41d8cd'
            ct['state'] = '5cdcf40dcde5330f034fccc4'
            ct['name'] = city.get_text()
            ct['location'] = None
            try:
                ct['location'] = geo.get_geoposition({'text': ct['name']})
            except:
                pass
            pr_city_list.append(ct)
    except:
        pass
    return pr_city_list


@background(schedule=1)
def get_us_state_list():
    US_states_list = []
    try:
        url = requests.get('https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations').text
        soup = BeautifulSoup(url, 'lxml')
        table = soup.find('table', "wikitable sortable").findAll('tr')
        for row in table[12:]:
            st = dict()
            state = row.find('td').get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
            state = re.sub(r'[[a-z,0-9].]', '', state)
            description = []
            for desc in row.findAll('td')[2:]:
                d = desc.get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
                if d is not '':
                    description.append(d)
            description = remove(description)
            #!!!ATTENTION!!! USA change to ID
            st['country_id'] = '5cdc1484cde53353db41d8cd'
            st['name'] = state
            st['description'] = description
            st['location'] = None
            try:
                st['location'] = geo.get_geoposition({'text': st['name']})
            except:
                pass
            US_states_list.append(st)
    except:
        pass
    return US_states_list


@background(schedule=1)
def train_on_list(train_text, name, language):
    mongodb = mongo.MongoConnection()
    if mongodb.default_entity.find_one({'name': name}):
        return None

    inserted_id = mongodb.default_entity.insert_one(
        {
            'name': name,
            'model':
                {
                    'train_text': train_text,
                    'train_postags': []
                },
            'available': True,
            'training': "finished",
            'language': language,
            'type': 'list',
            'deleted': False
        },
        # upsert=True
    ).inserted_id
    print(inserted_id)
    return inserted_id


@background(schedule=1)
def train_on_default_list(params):
    language = 'en' if 'language' not in params else params['language']
    mongodb = mongo.MongoConnection()
    # Add country
    countries = list(mongodb.country.find())
    common_names = [x['common_name'] for x in countries]
    common_names = list(set(common_names))
    official_names = [x['official_name'] for x in countries]
    official_names = list(set(official_names))
    train_on_list(list=common_names, name='country_common_names', language=language)
    train_on_list(list=official_names, name='country_official_names', language=language)
    # Add state
    states = list(mongodb.state.find())
    names = [x['name'] for x in states]
    names = list(set(names))
    descriptions = [item for sublist in states for item in sublist['description']]
    descriptions = list(set(descriptions))
    train_on_list(list=names, name='state_names', language=language)
    train_on_list(list=descriptions, name='state_descriptions', language=language)
    # Add pr_city
    pr_cities = list(mongodb.pr_city.find())
    pr_city_names = [x['name'] for x in pr_cities]
    pr_city_names = list(set(pr_city_names))
    train_on_list(list=pr_city_names, name='pr_city_names', language=language)


@background(schedule=1)
def train_article(params):
    mongodb = mongo.MongoConnection()
    language = 'en' if 'language' not in params else params['language']

    if 'article_id' not in params:
        raise EnvironmentError('Request must contain \'article_id\' field')
    article_id = params['article_id']
    if not isinstance(article_id, ObjectId):
        article_id = ObjectId(article_id)

    if mongodb.entity.find_one({'trained': True, 'article_id': article_id}):
        return None

    article = mongodb.source.find_one({'deleted': False, '_id': article_id})
    if not article:
        return None

    if 'content' in article and article['content']:
        tags = get_tags(article['content'], language)
    else:
        tags = get_tags(article['description'], language)

    inserted_id = mongodb.entity.insert_one(
        {
            'article_id': str(article_id),
            'available': True,
            'trained': True,
            #name
            'language': language,
            'type': 'default_stanford',
            'tags': tags,
            'deleted': False
        },
        # upsert=True
    ).inserted_id
    return inserted_id


@background(schedule=1)
def train_untrained_articles():
    mongodb = mongo.MongoConnection()
    import logging
    logger = logging.getLogger()
    logger.info('train_untrained_article START\n **************************')
    print('train_untrained_article START')
    articles = list(mongodb.source.find({'deleted': False}))
    article_ids = [x['_id'] for x in articles]
    trained_articles = list(mongodb.entity.find({'trained': True}))
    trained_article_ids = [ObjectId(x['article_id']) for x in trained_articles]
    untrained_ids = list(set(article_ids)-set(trained_article_ids))
    logger.info('list of untrained article:\n {}'.format(untrained_ids))
    for id in untrained_ids:
        train_article({'article_id': id})
        logger.info('article {} trained'.format(id))
    logger.info('train_untrained_article FINISHED\n **************************')
    print('train_untrained_article FINISHED')
    return untrained_ids


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list
