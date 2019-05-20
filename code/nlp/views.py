# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

import datetime
import subprocess
import psutil
import iso639
from bson import ObjectId, errors
from django.http import JsonResponse
from polyglot import load
from polyglot.detect import Detector, Language
from polyglot.downloader import downloader
#from lib.server_tuning import models_dict
import json
from rest_framework.decorators import api_view
from news import NewsCollector, get_tags
# import tasks
# from lib import check_config
# from lib import import_export
# from lib import learning_model as model
from lib import mongo_connection as mongo
# from lib import transliteration
# from lib import synonym
from lib.json_encoder import JSONEncoderHttp
# from lib.tools import get_error, get_abs_path
# from nlp.config import POLIGLOT, DEFAULT_USER, SERVER, ADMIN_USER
# from speech_to_text import speech_to_text_module
# from text_to_speech import text_to_speech_module
from datetime import datetime, timedelta
import geoposition as geo
from nlp import tasks


@api_view(['POST'])
def test_exception_work(request):
    """
    List all snippets, or create a new snippet.
    """
    raise EnvironmentError("My error")


@api_view(['POST'])
def test_work(request):
    """
    List all snippets, or create a new snippet.
    """
    results = {'status': True, 'response': 'IT Works', 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_country_list(request):
    mongodb = mongo.MongoConnection()
    countries = mongodb.get_country_list()
    results = {'status': True, 'response': {'countries': countries}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_language_list(request):
    mongodb = mongo.MongoConnection()
    languages = mongodb.get_language_list()
    results = {'status': True, 'response': {'languages': languages}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

#                            SOURCES                                 #


@api_view(['POST'])
def get_source_list(request):
    try:
        params = request.data
        mongodb = mongo.MongoConnection()
        sources = mongodb.get_sources(params=params)
    except:
        raise EnvironmentError("Error in get_source_list")
    results = {'status': True, 'response': {'sources': sources}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_source_list_from_server(request):
    mongodb = mongo.MongoConnection()
    inserted_ids, deleted_ids = mongodb.update_source_list_from_server()
    results = {'status': True, 'response': {'inserted_ids': inserted_ids, 'deleted_ids': deleted_ids}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)
#                            ARTICLES                                 #


@api_view(['POST'])
def update_article_list_from_server(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    inserted_ids, deleted_ids = mongodb.update_article_list_from_server(params)
    results = {'status': True, 'response': {'inserted_ids': inserted_ids, 'deleted_ids': deleted_ids}, 'error': {}}

    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_article_list(request):
    params = request.data

    case_sensitive = True if 'case_sensitive' not in request.data else params['case_sensitive']

    ans = []

    mongodb = mongo.MongoConnection()
    q_article = mongodb.q_article.find_one({'q': params['q']})
   # if not q_article or 'date' not in q_article or q_article['date'] < (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"):
    #    inserted_ids, deleted_ids = mongodb.update_article_list_from_server(params)
    #articles = mongodb.get_article_list(params=params)
    articles = mongodb.get_q_article_list(params=params)

    results = {'status': True, 'response': {'articles': articles}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

#                            TAGS                                 #


@api_view(['POST'])
def get_tag_list(request):
    data = request.data['text']
    language = 'en'
    if 'language' in request.data:
        language = request.data['language']
    tags = get_tags(data, language)
    results = {'status': True, 'response': {'tags': tags}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

#                            PHRASE                                 #


@api_view(['POST'])
def get_phrase_list(request):
    params = None
    try:
        params = request.data
    except:
        pass
    mongodb = mongo.MongoConnection()
    response = mongodb.get_phrases(params=params)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_phrase_list(request):
    phrases = request.data
    #nc = NewsCollector()
    #sources = nc.update_phrases()
    mongodb = mongo.MongoConnection()
    response = mongodb.update_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_phrase_list(request):
    try:
        phrases = request.data['phrases']
    except Exception as ex:
        return JsonResponse({'status': False, 'response': [], 'error': ex}, encoder=JSONEncoderHttp)
    mongodb = mongo.MongoConnection()
    response = mongodb.add_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_phrase_list(request):
    phrases = request.data
    mongodb = mongo.MongoConnection()
    response = mongodb.delete_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_permanent_phrase_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response = mongodb.delete_permanent_phrases(params=params)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_country_list(request):
    mongodb = mongo.MongoConnection()
    #response = mongodb.update_country_list()
    tasks.update_country_list()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fill_up_geolocation_country_list(request):
    mongodb = mongo.MongoConnection()
    response = mongodb.fill_up_geolocation_country_list()
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_state_list(request):
    mongodb = mongo.MongoConnection()
    response = mongodb.update_state_list()
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fill_up_geolocation_state_list(request):
    mongodb = mongo.MongoConnection()
    response = mongodb.fill_up_geolocation_state_list()
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_pr_city_list(request):
    mongodb = mongo.MongoConnection()
    response = mongodb.update_pr_city_list()
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fill_up_geolocation_pr_city_list(request):
    mongodb = mongo.MongoConnection()
    response = mongodb.fill_up_geolocation_pr_city_list()
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def train_article(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    inserted_id = mongodb.train_article(params=params)
    results = {'status': True, 'response': {'inserted_id': inserted_id}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_article_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response = mongodb.show_article_list(params=params)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def train_untrained_articles(request):
    mongodb = mongo.MongoConnection()
    inserted_ids = mongodb.train_untrained_articles()
    results = {'status': True, 'response': {'inserted_ids': inserted_ids}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_geoposition(request):
    params = request.data
    geoposition = geo.get_geoposition(params)
    results = {'status': True, 'response': {'geoposition': geoposition}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_geoposition_to_DB(request):
    mongodb = mongo.MongoConnection()
    mongodb.add_geoposition_to_DB()
    results = {'status': True, 'response': {'status': 'OK'}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)
