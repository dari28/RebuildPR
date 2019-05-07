"""install polyglot module"""

import os
import sys
import traceback

# current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if current_folder not in sys.path:
#     sys.path.append(current_folder)

from polyglot import load
from polyglot.downloader import Downloader

from lib import tools
#from lib.mongo_connection import MongoConnection
#from lib.linguistic_functions import get_supported_languages
from nlp.config import POLIGLOT #, STANFORD, DEFAULT_USER, SERVER, STANDFORD_PACKAGE

def install():
    # nltk.download('wordnet')
    """install polyglot"""
    try:
        os.path.sep = '/'
        polyglot_path = POLIGLOT['path_polyglot_data']
        polyglot_path = tools.get_abs_path(polyglot_path)

        if not os.path.exists(polyglot_path):
            os.makedirs(polyglot_path)

        load.polyglot_path = polyglot_path

        downloader = Downloader(download_dir=polyglot_path)

        for language in ['es', 'fr', 'de', 'ru', 'en']:
            if not downloader.is_installed('embeddings2.' + language):
                downloader.download('embeddings2.' + language)
                print('embeddings2.' + language + 'loaded')
            if not downloader.is_installed('ner2.' + language):
                downloader.download('ner2.' + language)
                print('ner2.' + language + 'loaded')
            if not downloader.is_installed('sentiment2.' + language):
                downloader.download('sentiment2.' + language)
                print('sentiment2.' + language + 'loaded')
            if not downloader.is_installed('morph2.' + language):
                downloader.download('morph2.' + language)
                print('morph2.' + language + 'loaded')
            # if not downloader.is_installed('pos2.' + language):
            #     downloader.download('pos2.' + language)
            print(language)
            # if not downloader.is_installed('transliteration2.' + language):
            #     downloader.download('transliteration2.' + language)
        # downloader.download('embeddings2.es')
        # downloader.download('pos2.es')
        # downloader.download('ner2.es')
    except:
        ex_type, ex, tb = sys.exc_info()
        tools.message_box(str(ex) + 'TracebackError' + ''.join(traceback.format_exc()),
                          str(ex_type), 0)
        raise EnvironmentError(str(ex) + 'TracebackError' + ''.join(traceback.format_exc()))


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
#
#

if __name__ == '__main__':
    os.path.sep = '/'
    install()

