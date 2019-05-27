"""Configuring the server at startup"""

import os
import sys
import traceback

from polyglot import load
from polyglot.downloader import Downloader
from polyglot.detect import Language
from background_task.models import Task

from lib import tools
from lib.mongo_connection import MongoConnection
from lib import stanford_module as stanford
from nlp.config import POLIGLOT, STANFORD, STANDFORD_PACKAGE, SERVER#, DEFAULT_USER, , CONFIGURATION_FILES, REPEAT_FINAL_PROCESSING, ADMIN_USER
#from nlp.tasks import final_processing
from lib.linguistic_functions import get_supported_languages
from lib.stanford_module import jString
from install.install_default_model import add_polyglot_default
from install_stanford import add_standford_default
from lib.text import Text


def load_models():
    models = [
        'crf_english_3class', 'crf_english_4class', 'crf_english_7class', 'crf_chinese_7class', 'crf_german_7class', 'crf_spanish_4class', 'crf_france_3class'
    ]
    classifier_dict = dict()
    for model in models:
        model = tools.get_abs_path(STANFORD[model])
        model = model if isinstance(model, str) else model.encode('utf8')
        if model not in classifier_dict:
            classifier_dict[model] = stanford.CRFClassifier.getClassifier(stanford.jString(model))
    return classifier_dict


def polyglot_default_install():
    """checking and caching polyglot"""
    try:
        os.path.sep = '/'
        polyglot_path = POLIGLOT['path_polyglot_data']
        polyglot_path = tools.get_abs_path(polyglot_path)

        if not os.path.exists(polyglot_path):
            os.makedirs(polyglot_path)

        load.polyglot_path = polyglot_path

        downloader = Downloader(download_dir=polyglot_path)
        for language in SERVER['language']:
            sentiment = False
            entities = False
            morph = False
            pos = False
            full_name = Language.from_code(language).name

            if language in get_supported_languages('embeddings2'):
                #if not downloader.is_installed(unicode('embeddings2.' + language)):
                if not downloader.is_installed('embeddings2.' + language):
                    raise EnvironmentError(
                        'The {0} module for {1}({2}) was not found, to install this package,'
                        ' run "./install/install_polyglot.py"'.format('embeddings2', full_name, language))

            if language in get_supported_languages('ner2'):
                entities = True
                #if not downloader.is_installed(unicode('ner2.' + language)):
                if not downloader.is_installed('ner2.' + language):
                    raise EnvironmentError(
                        'The {0} module for {1} was not found, to install this package,'
                        ' run "./install/install_polyglot.py"'.format('ner2', full_name))

            if language in get_supported_languages('sentiment2'):
                sentiment = True
                #if not downloader.is_installed(unicode('sentiment2.' + language)):
                if not downloader.is_installed('sentiment2.' + language):
                    raise EnvironmentError(
                        'The {0} module for {1} was not found, to install this package,'
                        ' run "./install/install_polyglot.py"'.format('sentiment2', full_name))

            if language in get_supported_languages('morph2'):
                morph = True
                # if not downloader.is_installed(unicode('morph2.' + language)):
                if not downloader.is_installed('morph2.' + language):
                    raise EnvironmentError(
                        'The {0} module for {1} was not found, to install this package,'
                        ' run "./install/install_polyglot.py"'.format('morph2', full_name))
            #TO_DO: Fix problem with pos2
            if language in get_supported_languages('pos2'):
                pos = True
                # if not downloader.is_installed(unicode('pos2.' + language)):
                if not downloader.is_installed('pos2.' + language):
                    raise EnvironmentError(
                        'The {0} module for {1} was not found, to install this package,'
                        ' run "./install/install_polyglot.py"'.format('pos2', full_name))
            # FOR POLYGLOT DOWNLOAD ON START SERVER
            if sentiment or entities or morph:
                text_polyglot = Text('Testing and cashing', hint_language_code=language)
                if sentiment:
                    _ = text_polyglot.words[0].polarity
                    _ = text_polyglot.sentences[0].polarity
                if entities:
                    _ = text_polyglot.entities
                if morph:
                    _ = text_polyglot.morphemes

    except:
        ex_type, ex, tb = sys.exc_info()
        # tools.message_box(str(ex) + 'TracebackError'+''.join(traceback.format_exc()),
        #                  str(ex_type), 0)
        raise EnvironmentError(str(ex) + 'TracebackError'+''.join(traceback.format_exc()))


def standford_default_install():
    """check standford Ner"""
    for language in SERVER['language']:
        if language in STANFORD['languages']:
            for model_name in STANDFORD_PACKAGE[language]:
                if not os.path.exists(tools.get_abs_path(STANFORD[model_name])):
                    text_error = \
                        '{0} file with model for stanford NER was not found.'.format(
                            tools.get_abs_path(STANFORD[model_name])
                        )
                    # tools.message_box(text_error, 'Error', 0)
                    raise EnvironmentError(text_error)
            _ = stanford.getTokenizerAnnotator(language)
            _ = stanford.getWordsToSentencesAnnotator(language)
            _ = stanford.getPOSTaggerAnnotator(language)
            for model_name in STANDFORD_PACKAGE[language]:
                _ = stanford.load_stanford_ner(model_name, language)
#
# def create_folder():
#     """"""
#     for folder in CONFIGURATION_FILES:
#         if not os.path.exists(CONFIGURATION_FILES[folder]):
#             os.makedirs(CONFIGURATION_FILES[folder])


# def add_final_processing():
#     """Preparing the task queue"""
#     try:
#         name_final_processing = final_processing.name
#         for task in Task.objects.all():
#             # Removing the final_processing task (so that this task is in one instance)
#             if task.task_name == name_final_processing:
#                 task.delete()
#             # Unlocking with an task
#             if task.locked_by:
#                 print task.locked_by
#                 task.locked_by = None
#                 task.save()
#         final_processing(repeat=REPEAT_FINAL_PROCESSING)
#     except Exception:
#         pass


# def add_admin_user():
#     mongo = MongoConnection()
#     if not mongo.users.find_one({'_id': ADMIN_USER}):
#         mongo.users.insert_one({'_id': ADMIN_USER})




def execution_at_startup():
    """Function that executes the necessary code at startup"""
    polyglot_default_install()
    standford_default_install()
    add_polyglot_default()
    add_standford_default()
    #create_folder()
    #add_final_processing()
    #add_admin_user()


if __name__ == '__main__':
    # os.path.sep = '/'
    # polyglot_path = POLIGLOT['path_polyglot_data']
    # polyglot_path = tools.get_abs_path(polyglot_path)
    # load.polyglot_path = polyglot_path
    # test = Text('Testing and cashing', hint_language_code='en')
    # sentences = test.sentences
    # pola = sentences[0].polarity
    # print pola
    #polyglot_default_install()
    execution_at_startup()


