

"""install polyglot module"""

import os
import sys
import traceback

# current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if current_folder not in sys.path:
#     sys.path.append(current_folder)

from polyglot import load
from polyglot.downloader import Downloader
import ctypes

#from lib import tools
#from lib.mongo_connection import MongoConnection
#from lib.linguistic_functions import get_supported_languages
#from nlp.config import POLIGLOT, STANFORD, DEFAULT_USER, SERVER, STANDFORD_PACKAGE


POLIGLOT = dict(
    path_polyglot_data='../polyglot_data',
)

STANFORD = dict(
    # languages=['en', 'zh', 'de', 'es', 'fr', 'ar'],
    # # languages=[],
    # crf_english_3class='./stanford_corenlp/classifiers/english.all.3class.distsim.crf.ser.gz',
    # crf_english_4class='./stanford_corenlp/classifiers/english.conll.4class.distsim.crf.ser.gz',
    # crf_english_7class='./stanford_corenlp/classifiers/english.muc.7class.distsim.crf.ser.gz',
    # crf_chinese_7class='./stanford_corenlp/classifiers/chinese.misc.distsim.crf.ser.gz',
    # crf_german_7class='./stanford_corenlp/classifiers/german.conll.hgc_175m_600.crf.ser.gz',
    # crf_spanish_4class='./stanford_corenlp/classifiers/spanish.ancora.distsim.s512.crf.ser.gz',
    # crf_france_3class='./stanford_corenlp/classifiers/france.3class.crf.ser.gz',
    # # path_stanford_ner='./stanford_corenlp/stanford-corenlp-3.8.0.jar',
    # path_stanford_ner='./stanford_corenlp/stanford_update.jar',
)

STANDFORD_PACKAGE = {
    # 'en': [
    #     'crf_english_3class',
    #     'crf_english_4class',
    #     'crf_english_7class'
    # ],
    'es': ['crf_spanish_4class'],
    # 'zh': ['crf_chinese_7class'],
    # 'de': ['crf_german_7class'],
    # 'fr': ['crf_france_3class'],
    # 'ar': []
}


def get_abs_path(path):
    """"""
    path = path if os.path.isabs(path) else \
        os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(sys.modules['nlp.config'].__file__)),
                path
            )
        )
    return path


def message_box(text='', head='', type_box=0):
    """Universal message box"""
    if sys.platform == "linux" or sys.platform == "linux2":
        # linux
        pass
    elif sys.platform == "darwin":
        # OS X
        pass
    # elif sys.platform == "win32":
    #     # Windows...
    #     ctypes.windll.user32.MessageBoxA(None, text, head, type_box)


def install():
    # nltk.download('wordnet')
    """install polyglot"""
    try:
        os.path.sep = '/'
        polyglot_path = POLIGLOT['path_polyglot_data']
        #polyglot_path = tools.get_abs_path(polyglot_path)
        polyglot_path = get_abs_path(polyglot_path)

        if not os.path.exists(polyglot_path):
            os.makedirs(polyglot_path)

        load.polyglot_path = polyglot_path

        downloader = Downloader(download_dir=polyglot_path)

        # for language in SERVER['language']:
        #     if language in get_supported_languages('embeddings2'):
        #             #if not downloader.is_installed(unicode('embeddings2.' + language)):
        #             if not downloader.is_installed('embeddings2.' + language):
        #                 downloader.download('embeddings2.' + language)
        #     if language in get_supported_languages('ner2'):
        #             #if not downloader.is_installed(unicode('ner2.' + language)):
        #             if not downloader.is_installed('ner2.' + language):
        #                 downloader.download('ner2.' + language)
        #     if language in get_supported_languages('sentiment2'):
        #             #if not downloader.is_installed(unicode('sentiment2.' + language)):
        #             if not downloader.is_installed('sentiment2.' + language):
        #                 downloader.download('sentiment2.' + language)
        #     if language in get_supported_languages('morph2'):
        #             #if not downloader.is_installed(unicode('morph2.' + language)):
        #             if not downloader.is_installed('morph2.' + language):
        #                 downloader.download('morph2.' + language)
        #     if language in get_supported_languages('pos2'):
        #             #if not downloader.is_installed(unicode('pos2.' + language)):
        #             if not downloader.is_installed('pos2.' + language):
        #                 downloader.download('pos2.' + language)
        #     if language in get_supported_languages('transliteration2'):
        #             #if not downloader.is_installed(unicode('transliteration2.' + language)):
        #             if not downloader.is_installed('transliteration2.' + language):
        #                 downloader.download('transliteration2.' + language)
        downloader.download('embeddings2.es')
        downloader.download('pos2.es')
        downloader.download('ner2.es')
    except:
        ex_type, ex, tb = sys.exc_info()
        #tools.message_box(str(ex) + 'TracebackError'+''.join(traceback.format_exc()),
        message_box(str(ex) + 'TracebackError' + ''.join(traceback.format_exc()),
                          str(ex_type), 0)
        raise EnvironmentError(str(ex) + 'TracebackError' + ''.join(traceback.format_exc()))


if __name__ == '__main__':
    os.path.sep = '/'
    install()

