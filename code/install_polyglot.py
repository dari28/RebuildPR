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
from nlp.config import description_tag, STANFORD, stanford_models
from lib import tools
from lib.linguistic_functions import get_supported_languages

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


if __name__ == '__main__':
    os.path.sep = '/'
    install()

