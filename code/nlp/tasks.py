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
def fill_up_geolocation_country_list(self):
    try:
        print("Background task fill_up_geolocation_country_list started")
        ids = mongo.MongoConnection.fill_up_geolocation(self.country, 'official_name')
        print("Background task fill_up_geolocation_country_list finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def fill_up_geolocation_state_list(self):
    try:
        print("Background task fill_up_geolocation_state_list started")
        ids = mongo.MongoConnection.fill_up_geolocation(self.state, 'name')
        print("Background task fill_up_geolocation_state_list finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def fill_up_geolocation_pr_city_list(self):
    try:
        print("Background task fill_up_geolocation_pr_city_list started")
        ids = mongo.MongoConnection.fill_up_geolocation(self.pr_city, 'name')
        print("Background task fill_up_geolocation_pr_city_list finished. Response: \n{}".format(ids))
    except:
        pass


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
