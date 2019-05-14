import os
import sys
import logging
from lib import mongo_connection as mongo

mongodb = mongo.MongoConnection()
inserted_ids, deleted_ids = mongodb.update_source_list_from_server()
logger = logging.getLogger()
logger.info('SCHEDULAR UPDATE SOURCES:\n **************************')
logger.info('\n {} \n {}'.format(inserted_ids, deleted_ids))

