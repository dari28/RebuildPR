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
    :param request:

    :return:
    :required:
    """
    raise EnvironmentError("My error")

# noinspection PyUnusedLocal


@api_view(['POST'])
def test_work(request):
    """
    List all snippets, or create a new snippet.
    :param request:
    :return:
    :required:
    """



    return JsonResponse({'test_ans': 'IT Works'}, encoder=JSONEncoderHttp)


# ***************************** TASKS ******************************** #

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_source_list_from_server(request):
    """
    :param request:
    :return:
    :required:
    """   
    # if not Task.objects.filter(task_name=tasks.update_source_list_from_server.name).exists():
    tasks.update_source_list_from_server()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_tags_from_article(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    entity = model.get_tags_from_article(params=params)
    return JsonResponse({'entity': entity}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_tags_from_untrained_articles(request):
    """
    :param request:
    :return:
    :required:
    """   
    # if not Task.objects.filter(task_name=tasks.get_tags_from_untrained_articles.name).exists():
    tasks.get_tags_from_untrained_articles(repeat=Task.NEVER)
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_tags_from_all_articles(request):
    """
    :param request:
    :return:
    :required:
    """   
    model.get_tags_from_all_articles()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def train_on_default_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    tasks.train_on_default_list(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)

# *******************************FIX*********************************** #
@api_view(['POST'])
def fix_sources_and_add_official_field(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_sources_and_add_official_field()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_article_source_with_null_id(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_article_source_with_null_id()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_article_content(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_article_content()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_one_article_by_id(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_one_article_by_id(params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_original_fields(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.fix_original_fields(params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fix_entity_location(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.entity.update({}, {"$unset": {"locations": 1}}, multi=True)
    model.add_locations_to_untrained_articles()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def dev_find_article_ids_with_tag_length_more_than_length(request):
    """
    :param request:
    :return:
    :required:
    """   
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
    """
    :param request:
    :return:
    :required:
    """   
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
    """
    :param request:{"text":'some    text'}
    :return:
    :required: {"text":1}
    """   
    params = request.data
    text = params['text']
    with mongo.MongoConnection() as mongodb:
        ans = mongodb.delete_trash_from_article_content(text)
    return JsonResponse({'before': text, 'after': ans}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def dev_update_sources_by_one_article(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.dev_update_sources_by_one_article(params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_dubles_articles_and_entities(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.remove_dubles_articles_and_entities()
    return JsonResponse({}, encoder=JSONEncoderHttp)
# ***************************** SOURCES ******************************** #


@api_view(['POST'])
def get_source_list(request):
    """
    :param request: {
    "language": ["es", "en"],
    "country": ["us","ca", "gb"],
    "deleted": false,
    "category": ["general","technology"],
    "start": 0,
    "length": 3
}
    :return:
    :required:{'language': 0, 'country': 0, 'deleted': 0, 'name': 0, 'id': 0, 'category': 0, 'start': 0, 'length': 0}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        sources, more = mongodb.get_sources(params=params)
    return JsonResponse({'sources': sources, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_bad_source(request):
    """
    remove_all_bad_source
    Description: remove from source collection all objects with bad: True.

    :param request: {"source_name":'some_name',"source_id": "5d14b4f2c4092420e6da913a"}
    :return:
    :required:{"source_name":1,'_id': 0, 'True': 0, 'start': 0, 'length': 0}
    """
    params = request.data
    if 'source_name' not in params:
        raise EnvironmentError('source_name must be in params')
    with mongo.MongoConnection() as mongodb:
        mongodb.add_bad_source(params['source_name'])
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_bad_source(request):
    """
    :param request:{"source_id":'test_id',"start": 0,"length": 2}
    :return:
    :required:{'start': 0, 'length': 0}
    """
    params = request.data
    if 'source_id' not in params:
        raise EnvironmentError('source_id must be in params')
    with mongo.MongoConnection() as mongodb:
        mongodb.remove_bad_source(params['source_id'])
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def remove_all_bad_source(request):
    """
    :param request:{"length": 2}
    :return:
    :required:{ 'start': 0, 'length': 0}
    """
    with mongo.MongoConnection() as mongodb:
        mongodb.remove_all_bad_source()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# ***************************** ARTILES ******************************** #


@api_view(['POST'])
def get_article_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles, more = mongodb.get_q_article_list(params=params)
    return JsonResponse({'articles': articles, 'more': more}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def get_article_list_by_tag(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles, more, total = mongodb.get_article_list_by_tag(params=params)
    return JsonResponse({'articles': articles, 'more': more, 'total': total}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_article_by_id(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        article = mongodb.get_article_by_id(params=params)
    return JsonResponse({'article': article}, encoder=JSONEncoderHttp)


# ***************************** ENTITY ******************************** #


@api_view(['POST'])
def get_tag_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    data = request.data['text']
    language = 'en'
    if 'language' in request.data:
        language = request.data['language']
    tags = model.get_tags(data, language)

    return JsonResponse({'tags': tags}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def predict_entity(request):
    """
    :param request:
    :return:
    :required:
    """   
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
def parse_currency(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data

    if not params or 'text' not in params:
        raise Exception("Field \'text\' must be")

    ans = nlp.parse_currency(params['text'])
    return JsonResponse({'predict': ans}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_location_info_by_id(request):
    """
    :param request:{"_id": "5cfe253fcfc738d1eafae9ae"}
    :return:
    :required:{'str': 1}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        location = mongodb.get_location_info_by_id(params)
    return JsonResponse({'location': location}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_default_entity(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        entities = mongodb.get_default_entity(params=params)
    return JsonResponse({'entities': entities}, encoder=JSONEncoderHttp)

# ***************************** PHRASES ******************************** #


@api_view(['POST'])
def get_phrase_list(request):
    """
    :param request: {
    "start": 0,
    "length": 2,
    "deleted": false
     }
    :return:
    :required:{'start': 0, 'length': 0, 'deleted': 0}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        phrases, more = mongodb.get_phrases(params=params)
    return JsonResponse({'phrases': phrases, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def update_phrase_list(request):
    """
    :param request:
{
    "ids": ["5cee9954920bbd21ed227595", "5cee9954920bbd21ed227597"],
    "deleted": false
}
    :return:
    :required:{ 'deleted': 0, 'ids': 1}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.update_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_phrase_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.add_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_phrase_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.delete_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def delete_permanent_phrase_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        mongodb.delete_permanent_phrases(params=params)
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def download_articles_by_phrases(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.download_articles_by_phrases()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def fill_up_db_from_zero(request):
    """
    :param request:
    :return:
    :required:
    """   
    model.fill_up_db_from_zero()
    return JsonResponse({}, encoder=JSONEncoderHttp)


# ***************************** GEOLOCATION ******************************** #

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_country_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.update_country_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_state_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.update_state_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_pr_city_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.update_pr_city_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def add_locations_to_untrained_articles(request):
    """
    :param request:
    :return:
    :required:
    """   
    model.add_locations_to_untrained_articles()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_article_list(request):
    """
    :param request: {
    "tags":{
        "person": "trump"
    },
    "language": "en",
    "start": 0,
    "length": 1
}

    :return:
    :required:{'start': 0, 'length': 0, 'status': 0}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        response, more = mongodb.show_article_list(params=params)
    return JsonResponse({'article': response, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_geoposition(request):
    """
    :param request:{"text": "Puerto Rico" }
    :return:
    :required:{'text': 1}
    """
    params = request.data
    geoposition = geo.get_geoposition(params)
    return JsonResponse({'geoposition': geoposition}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def fill_up_geolocation(request):
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.fill_up_geolocation(mongodb.location, 'name')
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def tag_stat(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        tags, more = mongodb.tag_stat(params=params)
    return JsonResponse({'tags': tags, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_language_list(request):
    """
    :param request:
    :return:
    :required:
    """
    language = [{'code': k, 'name': v} for k, v in languages_dict.items()]
    return JsonResponse({'language': language}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_source_list(request):
    """
    :param request:
{
	"length": 2
}     :return:
    :required:{'start': 0, 'length': 0}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        sources, more = mongodb.show_source_list(params)
    return JsonResponse({'sources': sources, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def show_tagged_article_list(request):
    """
    :param request:
    {
	"status": "tagged",
	"start" : 0,
	"length": 1,
    "language": "en"
    }
    :return:
    :required:{ 'status': 0, 'start': 0, 'length': 0}
    """
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles, trained, untrained, more = mongodb.show_tagged_article_list(params=params)
    return JsonResponse({'trained count': trained, 'untrained count': untrained, 'trained articles': articles, 'more': more}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def predict_entity(request):
    """
    :param request:
    :return:
    :required:
    """   
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
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.update_language_list()
    return JsonResponse({}, encoder=JSONEncoderHttp)

# **************************** CATEGORY ***************************

# noinspection PyUnusedLocal


@api_view(['POST'])
def update_category(request):
    """
    :param request:
    :return:
    :required:
    """   
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
    """
    :param request:
    :return:
    :required:
    """   
    with mongo.MongoConnection() as mongodb:
        mongodb.load_iso()
    return JsonResponse({}, encoder=JSONEncoderHttp)


@api_view(['POST'])
def aggregate_articles_by_locations(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        articles = mongodb.aggregate_articles_by_locations(params=params)
    return JsonResponse(articles, encoder=JSONEncoderHttp)


@api_view(['POST'])
def tag_stat_by_articles_list(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        tags = mongodb.tag_stat_by_articles_list(params=params)
    return JsonResponse(tags, encoder=JSONEncoderHttp)


@api_view(['POST'])
def get_locations_by_level(request):
    """
    :param request:
    :return:
    :required:
    """   
    params = request.data
    with mongo.MongoConnection() as mongodb:
        locations, more = mongodb.get_locations_by_level(params=params)
    return JsonResponse({'locations': locations, 'more': more}, encoder=JSONEncoderHttp)
