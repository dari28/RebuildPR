""""Connection class to mongoDB"""

import os
import shutil
import pymongo
import pycountry
from bson import ObjectId, errors
from news import get_sources, get_everything
from nlp.config import MONGO#, TYPE_WITHOUT_FILE, SEND_POST_URL, ADMIN_USER, DEFAULT_USER
import hashlib
import json
from wiki_parser import get_us_state_list, get_country_names_list, get_pr_city_list
import geoposition as geo
from collections import Counter


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
        self.q_article = self.mongo_db[config['q_article_collection']]
        self.country = self.mongo_db[config['country_collection']]
        self.state = self.mongo_db[config['state_collection']]
        self.pr_city = self.mongo_db[config['pr_city_collection']]
        self.entity = self.mongo_db[config['entity_collection']]
        self.default_entity = self.mongo_db[config['default_entity_collection']]

    def get_country_list(self):
        country_list = []
        for source in self.source.find({'deleted': False}):
            country_list.append(source['country'])
        country_list = list(set(country_list))
        dict_country_list = []
        for country in country_list:
            country_name = pycountry.countries.get(alpha_2=country.upper())
            dict_country_list.append({'code': country, 'description': country_name.name if country_name else "Unknown country"})

        return dict_country_list

    def get_language_list(self):
        language_list = []
        for source in self.source.find({'deleted': False}):
            language_list.append(source['language'])
        language_list = list(set(language_list))
        dict_language_list = []
        for lang in language_list:
            language = pycountry.languages.get(alpha_2=lang)
            dict_language_list.append({'code': lang, 'description': language.name if language else "Unknown language"})
        return dict_language_list

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
        return sources

    def update_country_list(self):
        country_list = get_country_names_list()
        self.country.insert(country_list)
        return country_list

    def fill_up_geolocation_country_list(self):
        counties = list(self.country.find({'location': {'$exists': False}}))
        updated_ids = []
        for country in counties:
            _id = country['_id']
            updated_ids.append(_id)
            country['location'] = None
            try:
                country['location'] = geo.get_geoposition({'text': country['official_name']})
            except Exception:
                pass
            self.country.update_one({'_id': _id}, {'$set': country})
        return updated_ids

    def update_state_list(self):
        states_list = get_us_state_list()
        self.state.insert(states_list)
        return states_list

    def fill_up_geolocation_state_list(self):
        states = list(self.state.find({'location': {'$exists': False}}))
        updated_ids = []
        for state in states:
            _id = state['_id']
            updated_ids.append(_id)

            state['location'] = None
            try:
                state['location'] = geo.get_geoposition({'text': state['name']})
            except Exception:
                pass
            self.state.update_one({'_id': _id}, {'$set': state})
        return updated_ids

    def update_pr_city_list(self):
        pr_city_list = get_pr_city_list()
        self.pr_city.insert(pr_city_list)
        return pr_city_list

    def fill_up_geolocation_pr_city_list(self):
        pr_city_list = list(self.pr_city.find({'location': {'$exists': False}}))
        updated_ids = []
        for pr_city in pr_city_list:
            _id = pr_city['_id']
            updated_ids.append(_id)

            pr_city['location'] = None
            try:
                pr_city['location'] = geo.get_geoposition({'text': pr_city['name']})
            except Exception:
                pass
            self.pr_city.update_one({'_id': _id}, {'$set': pr_city})
        return updated_ids

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
        #TO_DO: Make two collection. article_q should keep only ids of articles
        if 'q' not in params:
            raise EnvironmentError('Request must contain \'q\' field')
        q = params['q']
        #TO_DO: Add check for time
        new_articles, _ = get_everything(q)
        new_articles_hash = new_articles.copy()
        new_hash_list = []
        for ns in new_articles_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            ns['deleted'] = False
            new_hash_list.append(ns['hash'])

        old_articles = list(self.article.find({'deleted': False}))
        old_sources_hashes = [x['hash'] for x in old_articles]
        adding_articles = [new_s for new_s in new_articles_hash if new_s['hash'] not in old_sources_hashes]

        inserted_ids = []
        for article in adding_articles:
            source = self.source.find_one({'deleted': False, 'id': article['source']['id'], 'name': article['source']['name']})
            if source:
                article['source']['language'] = source['language']
                article['source']['category'] = source['category']
                article['source']['country'] = source['country']
            inserted_ids.append(self.article.insert_one(article).inserted_id)

        q_article = self.q_article.find_one({'q': q})
        current_article_ids = q_article['articles']
        deleted_ids = [x['_id'] for x in list(self.article.find({"hash": {"$nin": new_hash_list}, '_id': {'$in': current_article_ids}, 'deleted': False}))]
        self.delete_article_list_by_ids(deleted_ids)

        existing_article_ids = [x['_id'] for x in list(self.article.find({"hash": {"$in": new_hash_list}, 'deleted': False}))]
        self.q_article.update_one({'q': q},
                                 {'$set': {'articles': existing_article_ids},
                                  "$currentDate": {"lastModified": True}},
                                 upsert=True)

        return inserted_ids, deleted_ids

    def get_article_list(self, params):
        if 'q' not in params:
            raise EnvironmentError('Request must contain \'q\' field')
        search_param = dict()
        search_param['q'] = params['q']
        search_fields = ['id', 'name', 'language', 'country', 'category']
        if params:
            for field in search_fields:
                if field in params:
                    search_param['source'][field] = params[field]

        return list(self.article.find(search_param))

    def get_q_article_list(self, params):
        if 'q' not in params:
            raise EnvironmentError('Request must contain \'q\' field')

        q = params['q']
        articles = self.q_article.find_one({'q': q})

        search_param = dict()
        search_fields = ['id', 'name', 'language', 'country', 'category']
        search_param['_id'] = {"$in": articles['articles']}
        #search_param['source'] = dict()
        if params:
            for field in search_fields:
                if field in params:
                    search_param['source.'+field] = params[field]

        #full_artilces = list(self.article.find({'_id': {"$in": articles['articles']}}))
        full_artilces = list(self.article.find(search_param))
        articles['articles'] = full_artilces
        return articles

    def delete_article_list_by_ids(self, ids):
        """Delete sources by the database"""
        for id in ids:
            self.article.update_one(
                {'_id': ObjectId(id)},
                {'$set': {'deleted': True}},
                upsert=True
            )
        return ids
    # ***************************** Phrases ******************************** #

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

    def delete_permanent_phrases(self, params):
        """Permanent delete phrase by the database"""
        if 'ids' not in params:
            raise EnvironmentError('Request must contain \'ids\' field')
        ids = params['ids']
        if isinstance(ids, str):
            ids = list(ids)
        for _id in ids:
            if not isinstance(_id, ObjectId):
                _id = ObjectId(_id)

            self.phrase.delete_one(
                {'_id': _id},
                #upsert=True
            )
        return params

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

        return list(self.phrase.find({'deleted': deleted}))

    # ***************************** Train articles ******************************** #

    # def train_article(self, params):
    #     language = 'en' if 'language' not in params else params['language']
    #
    #     if 'article_id' not in params:
    #         raise EnvironmentError('Request must contain \'article_id\' field')
    #     article_id = params['article_id']
    #     if not isinstance(article_id, ObjectId):
    #         article_id = ObjectId(article_id)
    #
    #     if self.entity.find_one({'trained': True, 'article_id': article_id}):
    #         return None
    #
    #     article = self.source.find_one({'deleted': False, '_id': article_id})
    #     if not article:
    #         return None
    #
    #     if 'content' in article and article['content']:
    #         tags = get_tags(article['content'], language)
    #     else:
    #         tags = get_tags(article['description'], language)
    #
    #     inserted_id = self.entity.insert_one(
    #         {
    #             'article_id': str(article_id),
    #             'model': 'default_stanford',
    #             'tags': tags,
    #             'trained': True,
    #             'deleted': False
    #         },
    #         # upsert=True
    #     ).inserted_id
    #     return inserted_id

    # def train_untrained_articles(self):
    #     import logging
    #     logger = logging.getLogger()
    #     logger.info('train_untrained_article START\n **************************')
    #     print('train_untrained_article START')
    #     articles = list(self.source.find({'deleted': False}))
    #     article_ids = [x['_id'] for x in articles]
    #     trained_articles = list(self.entity.find({'trained': True}))
    #     trained_article_ids = [ObjectId(x['article_id']) for x in trained_articles]
    #     untrained_ids = list(set(article_ids)-set(trained_article_ids))
    #     logger.info('list of untrained article:\n {}'.format(untrained_ids))
    #     for id in untrained_ids:
    #         self.train_article({'article_id': id})
    #         logger.info('article {} trained'.format(id))
    #     logger.info('train_untrained_article FINISHED\n **************************')
    #     print('train_untrained_article FINISHED')
    #     return untrained_ids

    def show_article_list(self, params):
        language = 'en'

        if 'tags' not in params:
            raise EnvironmentError('Request must contain \'tags\' field')
        tags = params['tags']
        show = dict()
        # if not isinstance(article_id, ObjectId):
        #     article_id = ObjectId(article_id)

        # article = self.source.find_one({'deleted': False, '_id': article_id})
        # if not article:
        #     return None
        # tags = get_tags(article['description'], language)
        list_to_show = []
        ent = self.entity.find()
        for article in ent:
            a_tags = article['tags']
            n = 0
            for a_t_k, a_t_v in a_tags.items():
                for t in tags:
                    for t_k, t_v in t.items():
                        if (t_k == a_t_k) & (t_v == a_t_v[0]['word']):
                            n += 1
            if n > 0:
                list_to_show.append(article)
        show['Articles'] = list_to_show
        return show

    def tag_stat(self, params):
        tag = params['tag']
        phrase_list = []
        stat = dict()
        stat['tag'] = tag
        ent = self.entity.find()
        for article in ent:
            a_tags = article['tags']
            for a_t_k, a_t_v in a_tags.items():
                if a_t_k == tag:
                    phrase_list.append(a_t_v[0]['word'])
        word_list = Counter(phrase_list).most_common()
        t = []
        for phrase in word_list:
            d = dict()
            d['phrase'] = phrase[0]
            d['count'] = phrase[1]
            t.append(d)
        stat['tag_list'] = t
        return stat
