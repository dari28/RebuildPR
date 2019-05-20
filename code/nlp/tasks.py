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
from news import get_tags
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


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list
