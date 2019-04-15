#
#
# import os
#
# from lib.mongo_connection import MongoConnection
# from lib.linguistic_functions import get_supported_languages
# from nlp.config import DEFAULT_USER, SERVER
# from add_exemple import update_decsription
# from install_default_stoplists import upload_stoplists
# from install_stt_models import install_stt
# from install_tts_models import install_tts
#
# def add_standford_default():
#     """"""
#     mongodb = MongoConnection()
#
#     stanford_models = [
#         {
#             'model': 'crf_english_3class',
#             'tags': ['ORGANIZATION', 'LOCATION', 'PERSON'],
#             'language': 'en',
#             'name': 'Detects'
#         },
#         {
#             'model': 'crf_english_4class',
#             'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'MISC'],
#             'language': 'en',
#             'name': 'Detects'
#         },
#         {
#             'model': 'crf_english_7class',
#             'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'DATE', 'MONEY', 'PERCENT', 'TIME'],
#             'language': 'en',
#             'name': 'Detects'
#         },
#         {
#             'model': 'crf_chinese_7class',
#             'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'FACILITY', 'DEMONYM', 'MISC', 'GPE'],
#             'language': 'zh',
#             'name': ''
#         },
#         {
#             'model': 'crf_german_7class',
#             'tags': ['I-MISC', 'B-LOC', 'I-PER', 'I-LOC', 'B-MISC', 'I-ORG', 'B-ORG', 'B-PER'],
#             'language': 'de',
#             'name': 'Erkennt'
#         },
#         {
#             'model': 'crf_spanish_4class',
#             'tags': ['OTROS', 'PERS', 'ORG', 'LUG'],
#             'language': 'es',
#             'name': 'Detecta'
#         },
#         {
#             'model': 'crf_france_3class',
#             'tags': ['I-ORG', 'I-PERS', 'I-LIEU'],
#             'language': 'fr',
#             'name': '\x44\xC3\xA9\x74\x65\x72\x6D\x69\x6E\x65\x20\x6C\x65\x73'
#         }
#     ]
#
#     count_tag = {}
#     step_tag = {}
#     for model in stanford_models:
#         if model['language'] in SERVER['language']:
#             if model['language'] not in count_tag:
#                 count_tag[model['language']] = {}
#                 step_tag[model['language']] = {}
#             for tag in model['tags']:
#                 if tag not in count_tag[model['language']]:
#                     count_tag[model['language']][tag] = 0
#                     step_tag[model['language']][tag] = 0
#                 count_tag[model['language']][tag] += 1
#
#
#     for model in stanford_models:
#         if model['language'] in SERVER['language']:
#             for tag in model['tags']:
#                 entity = {
#                     'user': DEFAULT_USER[model['language']],
#                     'name': '{0} {1}'.format(model['name'], tag.lower()),
#                     'language': model['language'],
#                     'model': model['model'],
#                     'model_settings': {'tag': tag},
#                     'type': 'default_stanford',
#                     'training': 'finished',
#                     'available': True,
#                     'description': description_tag[tag]
#                 }
#
#                 step_tag[model['language']][tag] += 1
#                 if count_tag[model['language']][tag] > 1:
#                     entity['name'] += ' (model {0})'.format(step_tag[model['language']][tag])
#                     entity['description'] += \
#                         ' (different models were trained on different data, so their results can vary)'
#
#                 find_entity = entity.copy()
#                 del find_entity['description']
#                 check_exist = mongodb.entity.find_one(find_entity)
#                 if check_exist is None:
#                     if '_id' in entity:
#                         del entity['_id']
#                     try:
#                         model_id = mongodb.entity.insert(entity)
#                     except Exception:
#                         print entity
#                         raise
#                     mongodb.users.update_one(
#                         {'_id':  DEFAULT_USER[model['language']]},
#                         {'$addToSet': {'entity': model_id}},
#                         upsert=True
#                     )
#
# def add_polyglot_default():
#     """Defining default polyglot models"""
#     polyglot_model = [
#         {
#             'model_settings': {
#                 'tag': 'I-LOC',
#                 'polyglot_model': 'ner2',
#                 'case_sensitive': True
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected locations',
#             'name': 'Detects locations'
#         },
#         {
#             'model_settings': {
#                 'tag': 'I-PER',
#                 'polyglot_model': 'ner2',
#                 'case_sensitive': True
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected personality',
#             'name': 'Detects persons'
#         },
#         {
#             'model_settings': {
#                 'tag': 'I-ORG',
#                 'polyglot_model': 'ner2',
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected organizations',
#             'name': 'Detects organizations'
#         },
#         {
#             'model_settings': {
#                 'tag': 'negative_word',
#                 'polyglot_model': 'sentiment2',
#                 'case_sensitive': False
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected negative words',
#             'name': 'negative words'
#         },
#         {
#             'model_settings': {
#                 'tag': 'positive_word',
#                 'polyglot_model': 'sentiment2',
#                 'case_sensitive': False
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected positive words',
#             'name': 'positive words'
#         },
#         # {'model_settings': {'tag': 'polarity_sentence', 'polyglot_model': 'sentiment2'},
#         #  'status': 'train', 'available': True, 'type': 'default_polyglot',
#         #  'name': 'Polyglot default detected polarity of sentence'},
#         # {'model_settings': {'tag': 'polarity_text', 'polyglot_model': 'sentiment2'},
#         #  'status': 'train', 'available': True, 'type': 'default_polyglot',
#         #  'name': 'Polyglot default detected polarity of document'},
#     ]
#
#     mongo = MongoConnection()
#     for language in SERVER['language']:
#         # Adding Entities
#         for model in polyglot_model:
#             #full_name = Language.from_code(language).name
#             #if full_name in tools.list_decode(
#             #        downloader.supported_languages(model['model_settings']['polyglot_model'])
#             #):
#             if language in get_supported_languages(model['model_settings']['polyglot_model']):
#                 model['language'] = language
#                 model['training'] = 'finished'
#                 model['available'] = True
#                 model['user'] = DEFAULT_USER[language]
#                 find_entity = model.copy()
#                 del find_entity['description']
#                 find_model = mongo.entity.find_one(find_entity)
#                 if find_model is None:
#                     if '_id' in model:
#                         del model['_id']
#                     try:
#                         model_id = mongo.entity.insert(model)
#                     except Exception:
#                         print model
#                         raise
#                     mongo.users.update_one(
#                         {'_id': DEFAULT_USER[language]},
#                         {'$addToSet': {'entity': model_id}},
#                         upsert=True
#                     )
#
#
# description_tag = {
#     'ORGANIZATION': 'Trained model of CRF, defining organizations',
#     'LOCATION': 'Trained model of CRF, defining places',
#     'PERSON': 'Trained model of CRF, defining personality',
#     'DATE': 'Trained model of CRF, defining the dates',
#     'MONEY': 'Trained model of CRF, defining finances',
#     'PERCENT': 'Trained model of CRF, defining personality',
#     'TIME': 'Trained model of CRF, defining dates',
#     'MISC': 'Trained model of CRF, defining misc data',
#     'FACILITY': 'Trained model of CRF, defining objects',
#     'DEMONYM': 'Trained model of CRF, defining ethnicity',
#     'GPE': 'Trained model of CRF, defining geographical and political entity, a location which has a government, like U.S.A. or New York',
#     'I-MISC': 'Trained model of CRF, defining misc data (inside entity)',
#     'B-LOC': 'Trained model of CRF, defining places (begin entity)',
#     'I-PER': 'Trained model of CRF, defining personality (inside entity)',
#     'B-PER': 'Trained model of CRF, defining personality (begin entity)',
#     'I-LOC': 'Trained model of CRF, defining places(inside entity)',
#     'B-MISC': 'Trained model of CRF, defining misc data (begin entity)',
#     'I-ORG': 'Trained model of CRF, defining organizations (inside entity)',
#     'B-ORG': 'Trained model of CRF, defining organizations (begin entity)',
#     'OTROS': 'Trained model of CRF, defining misc data',
#     'PERS': 'Trained model of CRF, defining personality',
#     'ORG': 'Trained model of CRF, defining organizations',
#     'LUG': 'Trained model of CRF, defining places',
#     'I-PERS': 'Trained model of CRF, defining personality',
#     'I-LIEU': 'Trained model of CRF, defining places'
# }
#
#
# if __name__ == '__main__':
#     try:
#         f = open('install_default_log', 'a')
#     except:
#         f = open('install_default_log', 'w')
#     import datetime
#     f.write('started at {}\n'.format(datetime.datetime.now()))
#     f.close()
#     ####################################
#     os.path.sep = '/'
#     # host_main = 'http://174.129.126.138/'
#     host_main = 'http://127.0.0.1:8000/'
#
#     # Proxy from https://hidemy.name/ru/proxy-list/
#     proxy = {
#         "http": "http//62.32.75.82:8080"
#     }
#     translate_desription = True
#     ###################################
#     add_polyglot_default()
#     add_standford_default()
#     try:
#         upload_stoplists(host_main)
#     except:
#         print("Failed load stoplist")
#     update_decsription(host_main, proxy, translate_desription)
#     try:
#         install_stt(proxy)
#     except:
#         print "Failed load Sphinx"
#     try:
#         install_tts(proxy)
#     except:
#         print "Failed load MARYTTS"
#
