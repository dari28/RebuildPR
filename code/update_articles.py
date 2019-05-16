import os
import sys
import logging
from lib import mongo_connection as mongo

phrases = ["Puerto Rico", "Puerto Rican"]
mongodb = mongo.MongoConnection()
print("SCHEDULAR UPDATE ARTICLES STARTED")
logger = logging.getLogger()
logger.info('SCHEDULAR ARTICLES SOURCES:\n **************************')
for q in phrases:
    inserted_ids, deleted_ids = mongodb.update_article_list_from_server({'q': q})
    logger.info('{}\n **************************'.format(q))

print("SCHEDULAR UPDATE ARTICLES FINISHED")
