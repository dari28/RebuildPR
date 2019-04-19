# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import subprocess
import psutil
import iso639
from bson import ObjectId, errors
from django.http import JsonResponse
from polyglot import load
from polyglot.detect import Detector, Language
from polyglot.downloader import downloader
import json
from rest_framework.decorators import api_view
from news import NewsCollector
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


@api_view(['POST'])
def test_work(request):
    """
    List all snippets, or create a new snippet.
    """
    # data = request.data
    # path_data_polyglot = POLIGLOT['path_polyglot_data']
    # downloader.download_dir = path_data_polyglot
    # load.polyglot_path = path_data_polyglot
    # lang_list = []
    # if not isinstance(data, list):
    #     raise EnvironmentError(
    #         'Invalid input format! An example of how it should be: ["Sample1", "Sample2", ...]'.format())

    results = {'status': True, 'response': "IT Works", 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_source_list(request):
    nc = NewsCollector()
    sources = nc.get_available_sources()
    results = {'status': True, 'response': sources, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_article_list(request):
    data = json.loads(request.data['_content'])['q']
    ans = []
    nc = NewsCollector()
    for q in data:
        sources = nc.get_articles(q)
        ans.append({'q': q, 'sources': sources})
    results = {'status': True, 'response': ans, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_tag_list(request):
    data = json.loads(request.data['_content'])['text']
    nc = NewsCollector()
    sources = nc.get_tags(data)
    results = {'status': True, 'response': sources, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_phrase_list(request):
    params = None
    try:
        params = json.loads(request.data['_content'])
    except:
        pass
    #nc = NewsCollector()
    #sources = nc.get_phrases()
    mongodb = mongo.MongoConnection()
    response = mongodb.get_phrases(params=params)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_phrase_list(request):
    phrases = json.loads(request.data['_content'])
    #nc = NewsCollector()
    #sources = nc.update_phrases()
    mongodb = mongo.MongoConnection()
    response = mongodb.update_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_phrase_list(request):
    phrases = json.loads(request.data['_content'])
   # nc = NewsCollector()
   # sources = nc.update_phrases()
    mongodb = mongo.MongoConnection()
    response = mongodb.add_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

@api_view(['POST'])
def delete_phrase_list(request):
    phrases = json.loads(request.data['_content'])
   # nc = NewsCollector()
   # sources = nc.update_phrases()
    mongodb = mongo.MongoConnection()
    response = mongodb.delete_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

@api_view(['POST'])
def delete_permanent_phrase_list(request):
    phrases = json.loads(request.data['_content'])
   # nc = NewsCollector()
   # sources = nc.update_phrases()
    mongodb = mongo.MongoConnection()
    response = mongodb.delete_permanent_phrases(phrases=phrases)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)