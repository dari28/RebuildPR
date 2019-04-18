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
from rest_framework.decorators import api_view
# import tasks
# from lib import check_config
# from lib import import_export
# from lib import learning_model as model
# from lib import mongo_connection as mongo
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