import os
import sys
import django
_PATH = os.path.abspath(os.path.dirname(__file__))

if _PATH not in sys.path:
    sys.path.append(_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsAPI.settings")
django.setup()

import logging
from lib import mongo_connection as mongo
mongodb = mongo.MongoConnection()
print("SCHEDULAR download_articles_by_phrases STARTED")
logger = logging.getLogger()
mongodb.download_articles_by_phrases()
print("SCHEDULAR download_articles_by_phrases FINISHED")
