""""Connection class to mongoDB"""

import os
import shutil
import pymongo
from bson import ObjectId, errors
from news import get_sources, get_everything
from nlp.config import MONGO#, TYPE_WITHOUT_FILE, SEND_POST_URL, ADMIN_USER, DEFAULT_USER
#from lib.dictionary import fix_name_field
from lib import tools
import hashlib
import json

class MongoConnection(object):
    """Connection class to mongoDB"""

    def __init__(self, config=None, language=None):
        # override the global CONFIG if the config override dict is supplied
        config = dict(MONGO, **config) if config else MONGO
        mongo = pymongo.MongoClient(config['mongo_host'], connect=True)
        self.mongo_db = mongo[config['database']]
        self.phrase = self.mongo_db[config['phrase_collection']]
        self.source = self.mongo_db[config['source_collection']]
        self.article = self.mongo_db[config['article_collection']]

    def get_country_list(self):
        country_list = []
        for source in self.source.find({'deleted': False}):
            country = source['country']
            country_list.append(country)
        country_list = list(set(country_list))
        dict_country_list = []
        for country in country_list:
            my_dict = tools.country_code()
            dict_country_list.append({'code': country, 'description': my_dict[country]})

        return dict_country_list

    def get_language_list(self):
        language_list = []
        for source in self.source.find({'deleted': False}):
            language_list.append(source['language'])
        language_list = list(set(language_list))
        return language_list

    def get_sources(self, params):
        ''' parameters may be list or str '''
        search_param = dict()
        search_param['deleted'] = False
        search_fields = ['deleted', 'language', 'country', 'name', 'id', 'category']
        if params:
            for field in search_fields:
                if field in params:
                    search_param[field] = params[field]

        sources = list(self.source.find(search_param))
        # ret_list = []
        # for c in sources:
        #     ret_list.append(c)
        return sources

    def update_source_list_from_server(self):
        # TO_DO: Refactor
        new_sources, _ = get_sources("")
        new_sources_hash = new_sources.copy()
        new_hash_list = []
        for ns in new_sources_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            ns['deleted'] = False
            new_hash_list.append(ns['hash'])

        old_sources = list(self.source.find({'deleted': False}))
        old_sources_hashes = [x['hash'] for x in old_sources]
        adding_sources = [new_s for new_s in new_sources_hash if new_s['hash'] not in old_sources_hashes]
        inserted_ids = []
        for source in adding_sources:
            inserted_ids.append(self.source.insert_one(source).inserted_id)

        deleted_ids = [x['_id'] for x in list(self.source.find({"hash": {"$nin": new_hash_list}}))]
        self.delete_source_list_by_ids(deleted_ids)

        return inserted_ids, deleted_ids


    # def update_source_list_from_server(self):
    #     #TO_DO: Refactor
    #     new_sources, _ = get_sources("")
    #
    #     old_sources = []
    #     old_sources_without_ids = []
    #     for source in self.source.find({'deleted': False}):
    #         #del source['_id']
    #         old_sources.append(source)
    #         temp = source.copy()
    #         del temp['_id']
    #         del temp['deleted']
    #         old_sources_without_ids.append(temp)
    #
    #     adding_sources = [value for value in new_sources if value not in old_sources_without_ids]
    #     inserted_ids = []
    #     for source in adding_sources:
    #         source['deleted'] = False
    #         inserted_ids.append(self.source.insert_one(source).inserted_id)
    #
    #    # deleted_ids = [value['_id'] for value in old_sources if value not in new_sources]
    #     deleted_ids = []
    #     for value in old_sources:
    #         _id = value.pop('_id')
    #         value.pop('deleted')
    #         if value not in new_sources:
    #             deleted_ids.append(_id)
    #     self.delete_source_list_by_ids(deleted_ids)
    #
    #     return inserted_ids, deleted_ids

    def delete_source_list_by_ids(self, ids):
        """Delete sources by the database"""
        for id in ids:
            self.source.update_one(
                {'_id': ObjectId(id)},
                {'$set': {'deleted': True}},
                upsert=True
            )
        return ids
# ***************************** ARTILES ******************************** #

    def get_articles(self):
        """Adding a user to the database"""
        return self.article.find({})

    def update_article_list_from_server(self, params):
        if 'q' not in params:
            raise EnvironmentError('Request must contain \'q\' field')
        q = params['q']
        new_articles, _ = get_everything(q)
        new_articles_hash = new_articles.copy()
        new_hash_list = []
        for ns in new_articles_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            ns['deleted'] = False
            new_hash_list.append(ns['hash'])

        old_sources = list(self.article.find({'deleted': False}))
        old_sources_hashes = [x['hash'] for x in old_sources]
        adding_sources = [new_s for new_s in new_articles_hash if new_s['hash'] not in old_sources_hashes]
        inserted_ids = []
        for source in adding_sources:
            inserted_ids.append(self.article.insert_one(source).inserted_id)

        deleted_ids = [x['_id'] for x in list(self.article.find({"hash": {"$nin": new_hash_list}}))]
        self.delete_source_list_by_ids(deleted_ids)

        return inserted_ids, deleted_ids

    def add_phrases(self, phrases):
        """Adding phrase to the database"""
        inserted_id = self.phrase.insert_one(
            {
                'phrases': phrases,
                'deleted': False
            },
            #upsert=True
        ).inserted_id
        return inserted_id

    def delete_permanent_phrases(self, phrases):
        """Permanent delete phrase by the database"""
        if not isinstance(phrases['_id'], ObjectId):
            phrases['_id'] = ObjectId(phrases['_id'])

        self.phrase.delete_one(
            {'_id': phrases['_id']},
            #upsert=True
        )
        return phrases

    def delete_phrases(self, phrases):
        """Delete phrase by the database"""
        self.phrase.update_one(
            {'_id': ObjectId(phrases['_id'])},
            {'$set': {'deleted': True}},
            upsert=True
        )
        return phrases

    def update_phrases(self, phrases):
        """Updating phrase to the database"""
        if not isinstance(phrases['_id'], ObjectId):
            phrases['_id'] = ObjectId(phrases['_id'])

        if 'deleted' not in phrases:
            phrases['deleted'] = False

        self.phrase.update_one({'_id': phrases['_id']},
                               {'$set': {'phrases': phrases['phrases'],'deleted': phrases['deleted']}},
                               upsert=True)
        return phrases['_id']

    def get_phrases(self, params):
        """Getting phrase to the database"""
        deleted = False
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

