# -*- coding: utf-8 -*-
from bson import ObjectId, errors
from django.http import JsonResponse
from rest_framework.decorators import api_view
from lib import mongo_connection as mongo
from lib.json_encoder import JSONEncoderHttp
import geoposition as geo
from nlp import tasks
from lib import learning_model as model

# ***************************** TEST FUNCTIONS ******************************** #

# noinspection PyUnusedLocal


@api_view(['POST'])
def test_exception_work(request):
    """
    List all snippets, or create a new snippet.
    """
    raise EnvironmentError("My error")

# noinspection PyUnusedLocal


@api_view(['POST'])
def test_work(request):
    """
    List all snippets, or create a new snippet.
    """
    results = {'status': True, 'response': 'IT Works', 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


# ***************************** TASKS ******************************** #

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_source_list_from_server(request):
    tasks.update_source_list_from_server()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_tags_from_article(request):
    params = request.data
    tasks.get_tags_from_article(params=params)
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_tags_from_untrained_articles(request):
    tasks.get_tags_from_untrained_articles()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_tags_from_all_articles(request):
    tasks.get_tags_from_all_articles()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def train_on_default_list(request):
    params = request.data
    tasks.train_on_default_list(params=params)
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# ***************************** SOURCES ******************************** #


@api_view(['POST'])
def get_source_list(request):
    try:
        params = request.data
        mongodb = mongo.MongoConnection()
        sources, more = mongodb.get_sources(params=params)
    except:
        raise EnvironmentError("Error in get_source_list")
    results = {'status': True, 'response': {'sources': sources, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# ***************************** ARTILES ******************************** #


@api_view(['POST'])
def get_article_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    articles, more = mongodb.get_q_article_list(params=params)
    results = {'status': True, 'response': {'articles': articles, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_article_list_by_tag(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    articles, more, total = mongodb.get_article_list_by_tag(params=params)
    results = {'status': True, 'response': {'articles': articles, 'more': more, 'total': total}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_article_language_list(request):
    mongodb = mongo.MongoConnection()
    languages = mongodb.get_article_language_list()
    results = {'status': True, 'response': {'languages': languages}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_article_by_id(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    article = mongodb.get_article_by_id(params=params)
    results = {'status': True, 'response': {'article': article}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_dubles_articles(request):
    # params = request.data
    mongodb = mongo.MongoConnection()
    mongodb.remove_dubles_articles()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# ***************************** ENTITY ******************************** #


@api_view(['POST'])
def get_tag_list(request):
    data = request.data['text']
    language = 'en'
    if 'language' in request.data:
        language = request.data['language']
    tags = model.get_tags(data, language)
    results = {'status': True, 'response': {'tags': tags}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def predict_entity(request):
    data = request.data
    if 'entity' not in data:
        raise EnvironmentError('Entity not defined')
    if 'language' not in data:
        raise EnvironmentError('The input format is not correct! The input data must contain the "language" field.')
    if 'data' not in data:
        raise EnvironmentError('The input format is not correct! The input data must contain the "data" field.')

    entity_id = []
    for entity in data['entity']:
        try:
            entity_id.append(ObjectId(entity))
        except:
            raise errors.InvalidId('Invalid value for "entity" = {0}'.format(entity))

    predict_result = model.predict_entity(data=data['data'], set_entity=entity_id, language=data['language'])
    results = {'status': True, 'response': {'predict': predict_result}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_default_entity(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    entities = mongodb.get_default_entity(params=params)
    results = {'status': True, 'response': {'entities': entities}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# ***************************** PHRASES ******************************** #


@api_view(['POST'])
def get_phrase_list(request):
    try:
        params = request.data
    except Exception as ex:
        return JsonResponse({'status': False, 'response': {}, 'error': ex}, encoder=JSONEncoderHttp)
    mongodb = mongo.MongoConnection()
    phrases = mongodb.get_phrases(params=params)
    results = {'status': True, 'response': {'phrases': phrases}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_phrase_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    mongodb.update_phrases(params=params)
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_phrase_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    mongodb.add_phrases(params=params)
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_phrase_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    mongodb.delete_phrases(params=params)
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_permanent_phrase_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    mongodb.delete_permanent_phrases(params=params)
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def download_articles_by_phrases(request):
    mongodb = mongo.MongoConnection()
    mongodb.download_articles_by_phrases()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def fill_up_db_from_zero(request):
    model.fill_up_db_from_zero()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


# ***************************** GEOLOCATION ******************************** #

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_country_list(request):
    mongodb = mongo.MongoConnection()
    mongodb.update_country_list()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_state_list(request):
    mongodb = mongo.MongoConnection()
    mongodb.update_state_list()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_pr_city_list(request):
    mongodb = mongo.MongoConnection()
    mongodb.update_pr_city_list()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_article_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response, more = mongodb.show_article_list(params=params)
    results = {'status': True, 'response': {'article': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_geoposition(request):
    params = request.data
    geoposition = geo.get_geoposition(params)
    results = {'status': True, 'response': {'geoposition': geoposition}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fill_up_geolocation(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    mongodb.fill_up_geolocation(mongodb.location, 'name')
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def tag_stat(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    tags = mongodb.tag_stat(params=params)
    results = {'status': True, 'response': {'tags': tags}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_language_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response, more = mongodb.show_language_list(params=params)
    results = {'status': True, 'response': {'language': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_unlocated_articles(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response, more = mongodb.get_unlocated_articles(params=params)
    results = {'status': True, 'response': {'articles': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_country_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response, more = mongodb.show_country_list(params=params)
    results = {'status': True, 'response': {'country': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_state_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response, more = mongodb.show_state_list(params=params)
    results = {'status': True, 'response': {'state': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_pr_city_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response, more = mongodb.show_pr_city_list(params=params)
    results = {'status': True, 'response': {'pr_city': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_trained_article_list(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    articles, trained, untrained, more = mongodb.show_trained_article_list(params=params)
    results = {'status': True, 'response': {'trained count': trained, 'untrained count': untrained, 'trained articles': articles, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def predict_entity(request):
    data = request.data
    if 'entity' not in data:
        raise EnvironmentError('Entity not defined')
    if 'language' not in data:
        raise EnvironmentError('The input format is not correct! The input data must contain the "language" field.')
    if 'data' not in data:
        raise EnvironmentError('The input format is not correct! The input data must contain the "data" field.')

    entity_ids = []

    if not isinstance(data['entity'], list):
        data['entity'] = [data['entity']]

    if not isinstance(data['data'], list):
        data['data'] = [data['data']]

    for entity in data['entity']:
        try:
            entity_ids.append(ObjectId(entity))
        except:
            raise errors.InvalidId('Invalid value for "entity" = {0}'.format(entity))

    predict_result = model.predict_entity(data=data['data'], set_entity=entity_ids, language=data['language'])
    results = {'status': True, 'response': {'predict': predict_result}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_language(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    response = mongodb.get_language(params=params)
    results = {'status': True, 'response': response, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_language_list(request):
    mongodb = mongo.MongoConnection()
    mongodb.update_language_list()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# **************************** CATEGORY ***************************

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_category(request):
    mongodb = mongo.MongoConnection()
    mongodb.update_category()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_category(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    # FUNCTION IN PROGRESS
    response, more = mongodb.show_category(params=params)
    results = {'status': True, 'response': {'state': response, 'more': more}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def load_iso(request):
    mongodb = mongo.MongoConnection()
    mongodb.load_iso()
    results = {'status': True, 'response': {}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)


@api_view(['POST'])
def find_articles_by_locations(request):
    params = request.data
    mongodb = mongo.MongoConnection()
    articles = mongodb.find_articles_by_locations(params=params)
    results = {'status': True, 'response': {'count': articles['count'], 'articles': articles['articles_list']}, 'error': {}}
    return JsonResponse(results, encoder=JSONEncoderHttp)

