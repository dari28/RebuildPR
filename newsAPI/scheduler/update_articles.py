import os
import sys
import django
_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if _PATH not in sys.path:
    sys.path.append(_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsAPI.settings")

import logging
logger = logging.getLogger()
logger.info(_PATH)

django.setup()

logger.info('DJANGO START\n **************************')

from lib import mongo_connection as mongo
mongodb = mongo.MongoConnection()
logger.info("SCHEDULAR download_articles_by_phrases STARTED")
mongodb.download_articles_by_phrases()
logger.info("SCHEDULAR download_articles_by_phrases FINISHED")
