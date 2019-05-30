import os
import sys
import django
_PATH = os.path.abspath(os.path.dirname(__file__))

if _PATH not in sys.path:
    sys.path.append(_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsAPI.settings")
django.setup()

import logging
logger = logging.getLogger()
logger.info('DJANGO START\n **************************')

from lib import mongo_connection as mongo
mongodb = mongo.MongoConnection()
print("SCHEDULAR UPDATE SOURCES STARTED")
inserted_ids, deleted_ids = mongodb.update_source_list_from_server()

logger.info('\n {} \n {}'.format(inserted_ids, deleted_ids))
print("SCHEDULAR UPDATE SOURCES FINISHED")
