import os
#
from lib.mongo_connection import MongoConnection
# from lib.linguistic_functions import get_supported_languages
# from nlp.config import DEFAULT_USER, SERVER
# from add_exemple import update_decsription
# from install_default_stoplists import upload_stoplists
# from install_stt_models import install_stt
# from install_tts_models import install_tts
#
from lib import stanford_module as stanford
from nlp.config import description_tag, STANFORD, stanford_models
from lib import tools
import jnius


def add_standford_default():
    """"""
    mongo = MongoConnection()

    entities = []
    count_tag = {}
    step_tag = {}
    for model in stanford_models:
        #if model['language'] in SERVER['language']:
        if True:
            if model['language'] not in count_tag:
                count_tag[model['language']] = {}
                step_tag[model['language']] = {}
            for tag in model['tags']:
                if tag not in count_tag[model['language']]:
                    count_tag[model['language']][tag] = 0
                    step_tag[model['language']][tag] = 0
                count_tag[model['language']][tag] += 1


    for model in stanford_models:
        #if model['language'] in SERVER['language']:
        if True:
            for tag in model['tags']:
                entity = {
                    #'user': DEFAULT_USER[model['language']],
                    'name': '{0} {1}'.format(model['name'], tag.lower()),
                    'language': model['language'],
                    'model': model['model'],
                    'model_settings': {'tag': tag},
                    'type': 'default_stanford',
                    'training': 'finished',
                    'available': True,
                    'description': description_tag[tag]
                }

                step_tag[model['language']][tag] += 1
                if count_tag[model['language']][tag] > 1:
                    entity['name'] += ' (model {0})'.format(step_tag[model['language']][tag])
                    entity['description'] += \
                        ' (different models were trained on different data, so their results can vary)'

                entities.append(entity)
                find_entity = entity.copy()
                del find_entity['description']
                check_exist = mongo.default_entity.find_one(find_entity)
                if check_exist is None:
                    if '_id' in entity:
                        del entity['_id']
                    try:
                        model_id = mongo.default_entity.insert(entity)
                    except Exception as ex:
                        print(entity)
                        print(ex)
                        raise
                    # mongodb.users.update_one(
                    #     {'_id':  DEFAULT_USER[model['language']]},
                    #     {'$addToSet': {'entity': model_id}},
                    #     upsert=True
                    # )
    return entities
# if __name__ == '__main__':
#     try:
#         f = open('install_default_log', 'a')
#     except:
#         f = open('install_default_log', 'w')
#     import datetime
#     f.write('started at {}\n'.format(datetime.datetime.now()))
#     f.close()
#     ####################################
#     translate_desription = True
#     ###################################
#     add_polyglot_default()
#     add_standford_default()
#
