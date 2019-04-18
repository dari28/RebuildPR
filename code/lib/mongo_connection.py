""""Connection class to mongoDB"""

import os
import shutil
import pymongo
from bson import ObjectId, errors

from nlp.config import MONGO#, TYPE_WITHOUT_FILE, SEND_POST_URL, ADMIN_USER, DEFAULT_USER
#from lib.dictionary import fix_name_field
from lib import tools


class MongoConnection(object):
    """Connection class to mongoDB"""

    def __init__(self, config=None, language=None):
        # override the global CONFIG if the config override dict is supplied
        config = dict(MONGO, **config) if config else MONGO
        mongo = pymongo.MongoClient(config['mongo_host'], connect=True)
        self.mongo_db = mongo[config['database']]

    def get_articles(self):
        """Adding a user to the database"""
        return self.articles.find({})