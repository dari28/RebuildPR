# -*- coding: utf-8 -*-
from bson import ObjectId, errors
from django.http import JsonResponse
from rest_framework.decorators import api_view
from lib import mongo_connection as mongo
from lib.json_encoder import JSONEncoderHttp
import geoposition as geo
from nlp import tasks
from lib import learning_model as model, nlp
from background_task.models import Task
from news import languages_dict
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
    return JsonResponse({'test_ans': 'IT Works'}, encoder=JSONEncoderHttp)


# ***************************** SOURCES ******************************** #


@api_view(['POST'])
def get_source_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        sources, more = mongodb.get_sources(params=params)
    return JsonResponse({'sources': sources, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_bad_source(request):
    params = request.data
    if 'source_name' not in params:
        raise EnvironmentError('source_name must be in params')
    with mongo.MongoConnection() as mongodb:
        mongodb.add_bad_source(params['source_name'])
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_bad_source(request):
    params = request.data
    if 'source_id' not in params:
        raise EnvironmentError('source_id must be in params')
    with mongo.MongoConnection() as mongodb:
        mongodb.remove_bad_source(params['source_id'])
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_all_bad_source(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.remove_all_bad_source()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_source_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        sources, more = mongodb.show_source_list(params)
    return JsonResponse({'sources': sources, 'more': more}, encoder=JSONEncoderHttp)


# ***************************** ARTILES ******************************** #


@api_view(['POST'])
def get_article_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles, more = mongodb.get_q_article_list(params=params)
    return JsonResponse({'articles': articles, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_article_by_id(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        article = mongodb.get_article_by_id(params=params)
    return JsonResponse({'article': article}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_article_list_by_tag(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles, more, total = mongodb.get_article_list_by_tag(params=params)
    return JsonResponse({'articles': articles, 'more': more, 'total': total}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_article_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        response, more = mongodb.show_article_list(params=params)
    return JsonResponse({'article': response, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_tagged_article_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles, trained, untrained, more = mongodb.show_tagged_article_list(params=params)
    return JsonResponse({'trained count': trained, 'untrained count': untrained, 'trained articles': articles, 'more': more}, encoder=JSONEncoderHttp)


# ***************************** TAGS ******************************** #


@api_view(['POST'])
def get_tag_list(request):
    data = request.data['text']
    language = 'en'
    if 'language' in request.data:
        language = request.data['language']
    tags = model.get_tags(data, language)

    return JsonResponse({'tags': tags}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def tag_stat(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        tags, more = mongodb.tag_stat(params=params)
    return JsonResponse({'tags': tags, 'more': more}, encoder=JSONEncoderHttp)


# ***************************** PHRASES ******************************** #


@api_view(['POST'])
def get_phrase_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        phrases, more = mongodb.get_phrases(params=params)
    return JsonResponse({'phrases': phrases, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_phrase_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.add_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_phrase_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.delete_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_phrase_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.update_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


# ***************************** ENTITY ******************************** #


@api_view(['POST'])
def get_tags_from_article(request):
    params = request.data
    entity = model.get_tags_from_article(params=params)
    return JsonResponse({'entity': entity}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def parse_currency(request):
    params = request.data

    if not params or 'text' not in params:
        raise Exception("Field \'text\' must be")

    ans = nlp.parse_currency(params['text'])
    return JsonResponse({'predict': ans}, encoder=JSONEncoderHttp)


# ***************************** OTHER ******************************** #


@api_view(['POST'])
def get_geoposition(request):
    params = request.data
    geoposition = geo.get_geoposition(params)
    return JsonResponse({'geoposition': geoposition}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_language_list(request):
    language = [{'code': k, 'name': v} for k, v in languages_dict.items()]
    return JsonResponse({'language': language}, encoder=JSONEncoderHttp)


# ***************************** LOCATIONS ******************************** #


@api_view(['POST'])
def get_locations_by_level(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        locations, more = mongodb.get_locations_by_level(params=params)
    return JsonResponse({'locations': locations, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def aggregate_articles_by_locations(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles = mongodb.aggregate_articles_by_locations(params=params)
    return JsonResponse(articles, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_location_info_by_id(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        location = mongodb.get_location_info_by_id(params)
    return JsonResponse({'location': location}, encoder=JSONEncoderHttp)


# ********************* Fill up db from zero ***************
# noinspection PyUnusedLocal


@api_view(['POST'])
def fill_up_db_from_zero(request):
    model.fill_up_db_from_zero()
    return JsonResponse({}, encoder=JSONEncoderHttp)


# ********************* END OF Fill up db from zero ********

# noinspection PyUnusedLocal


@api_view(['POST'])
# task
def update_source_list_from_server(request):
    # if not Task.objects.filter(task_name=tasks.update_source_list_from_server.name).exists():
    tasks.update_source_list_from_server()
    return JsonResponse({}, encoder=JSONEncoderHttp)


# noinspection PyUnusedLocal


@api_view(['POST'])
# task
def get_tags_from_untrained_articles(request):
    params = request.data
    # if not Task.objects.filter(task_name=tasks.get_tags_from_untrained_articles.name).exists():
    # tasks.get_tags_from_untrained_articles(repeat=Task.NEVER)
    # tasks.get_tags_from_untrained_articles.now()  # (repeat=Task.NEVER)
    model.get_tags_from_untrained_articles(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_tags_from_all_articles(request):
    model.get_tags_from_all_articles()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
# task
def train_on_default_list(request):
    params = request.data
    tasks.train_on_default_list(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)

# *******************************FIX*********************************** #
@api_view(['POST'])
def fix_sources_and_add_official_field(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_sources_and_add_official_field()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_article_source_with_null_id(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_article_source_with_null_id()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_article_content(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_article_content()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_one_article_by_id(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_one_article_by_id(params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_original_fields(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_original_fields(params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_entity_location(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.entity.update({}, {"$unset": {"locations": 1}}, multi=True)
    model.add_locations_to_untrained_articles()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def dev_find_article_ids_with_tag_length_more_than_length(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        article_ids = mongodb.dev_find_article_ids_with_tag_length_more_than_length(params)
    article_ids = [x['article_id'] for x in article_ids]
    dictinct_article_ids = []
    for x in article_ids:
        if x not in dictinct_article_ids:
            dictinct_article_ids.append(x)
    return JsonResponse({'article_ids': dictinct_article_ids, 'total': len(dictinct_article_ids)}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_article_content_and_retrain_entity_bt_article_ids(request):
    params = request.data
    article_ids = params['article_ids']
    with mongo.MongoConnection() as mongodb:
        for article_id in article_ids:
            mongodb.fix_one_article_by_id({"_id": article_id})
            model.get_tags_from_article({
                "retrain": True,
                "article_id": article_id
            })
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_trash_from_article_content(request):
    params = request.data
    text = params['text']
    with mongo.MongoConnection() as mongodb:
        ans = mongodb.delete_trash_from_article_content(text)
    return JsonResponse({'before': text, 'after': ans}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def dev_update_sources_by_one_article(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.dev_update_sources_by_one_article(params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_dubles_articles_and_entities(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.remove_dubles_articles_and_entities()
    return JsonResponse({}, encoder=JSONEncoderHttp)


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

    return JsonResponse({'predict': predict_result}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_default_entity(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        entities = mongodb.get_default_entity(params=params)
    return JsonResponse({'entities': entities}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_permanent_phrase_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.delete_permanent_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def download_articles_by_phrases(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.download_articles_by_phrases()
    return JsonResponse({}, encoder=JSONEncoderHttp)


# ***************************** GEOLOCATION ******************************** #

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_country_list(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.update_country_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_state_list(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.update_state_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_pr_city_list(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.update_pr_city_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_locations_to_untrained_articles(request):
    model.add_locations_to_untrained_articles()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fill_up_geolocation(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.fill_up_geolocation(mongodb.location, 'name')
    return JsonResponse({}, encoder=JSONEncoderHttp)


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

    return JsonResponse({'predict': predict_result}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_language_list(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.update_language_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# **************************** CATEGORY ***************************

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_category(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.update_category()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_category(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        # FUNCTION IN PROGRESS
        response, more = mongodb.show_category(params=params)
    return JsonResponse({'state': response, 'more': more}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def load_iso(request):
    with mongo.MongoConnection() as mongodb:
        mongodb.load_iso()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def tag_stat_by_articles_list(request):
    params = request.data
    with mongo.MongoConnection() as mongodb:
        tags = mongodb.tag_stat_by_articles_list(params=params)
    return JsonResponse(tags, encoder=JSONEncoderHttp)

