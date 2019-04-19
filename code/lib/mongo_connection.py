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
        self.phrase = self.mongo_db[config['phrase_collection']]

    def get_articles(self):
        """Adding a user to the database"""
        return self.articles.find({})

    def add_phrases(self, phrases):
        """Adding phrase to the database"""
        inserted_id = self.phrase.insert_one(
            {
                'phrases': phrases,
                'deleted': '0'
            },
            #upsert=True
        ).inserted_id
        return inserted_id

    def delete_permanent_phrases(self, phrases):
        """Adding phrase to the database"""
        self.phrase.delete_one(
            {'_id': phrases['_id']},
            #upsert=True
        )
        return phrases

    def delete_phrases(self, phrases):
        """Adding phrase to the database"""
        self.phrase.update_one(
            {'_id': ObjectId(phrases['_id'])},
            {'$set': {'deleted': '1'}},
            upsert=True
        )
        return phrases

    def update_phrases(self, phrases):
        """Adding phrase to the database"""
        self.phrase.update_one({'_id': phrases['_id']},
                               {'$set': {'deleted': phrases['deleted'],'phrases': phrases['phrases']}},
                               upsert=True)
        return phrases

    def get_phrases(self, params):
        """Adding phrase to the database"""
        deleted = '0'
        if params and 'deleted' in params:
            deleted = params['deleted']

        phrases = self.phrase.find(
            {
                'deleted': deleted,
            }
            #upsert=True
        )
        ret_list = []
        for c in phrases:
            ret_list.append(c)
        return ret_list

