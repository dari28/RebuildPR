""""Connection class to mongoDB"""

import pymongo
import pycountry
from bson import ObjectId
from news import NewsCollection
from nlp.config import MONGO  # , TYPE_WITHOUT_FILE, SEND_POST_URL, ADMIN_USER, DEFAULT_USER
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
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        sources = list(self.source.find(search_param).skip(start).limit(length + 1))
        more = True if len(sources) > length else False
        return sources[:-1], more

    # ***************************** GEOLOCATION ******************************** #

    def update_country_list(self):
        country_list = get_country_names_list()
        self.country.insert(country_list)

    def update_state_list(self):
        states_list = get_us_state_list()
        self.state.insert(states_list)

    def update_pr_city_list(self):
        pr_city_list = get_pr_city_list()
        self.pr_city.insert(pr_city_list)

    @staticmethod
    def fill_up_geolocation(table, field):
        table_list = table.find({'location': {'$exists': False}})
        updated_ids = []
        for table_item in table_list:
            _id = table_item['_id']
            updated_ids.append(_id)
            table_item['location'] = None
            try:
                table_item['location'] = geo.get_geoposition({'text': table_item[field]})
            except Exception:
                pass
            table.update_one({'_id': _id}, {'$set': table_item})
        return updated_ids

    def fill_up_geolocation_country_list(self):
        return MongoConnection.fill_up_geolocation(self.country, 'official_name')

    def fill_up_geolocation_state_list(self):
        return MongoConnection.fill_up_geolocation(self.state, 'name')

    def fill_up_geolocation_pr_city_list(self):
        return MongoConnection.fill_up_geolocation(self.pr_city, 'name')

    def update_source_list_from_server(self):
        # TO_DO: Refactor
        new_sources, _ = NewsCollection.get_sources("")
        new_sources_hash = new_sources.copy()
        new_hash_list = []
        for ns in new_sources_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            ns['deleted'] = False
            new_hash_list.append(ns['hash'])

        old_sources = self.source.find({'deleted': False})
        old_sources_hashes = [x['hash'] for x in old_sources]
        adding_sources = [new_s for new_s in new_sources_hash if new_s['hash'] not in old_sources_hashes]
        inserted_ids = []
        for source in adding_sources:
            inserted_ids.append(self.source.insert_one(source).inserted_id)

        deleted_ids = [x['_id'] for x in self.source.find({"hash": {"$nin": new_hash_list}})]
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
        new_articles, _ = NewsCollection.get_everything(q)
        new_articles_hash = new_articles.copy()
        new_hash_list = []
        for ns in new_articles_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            ns['deleted'] = False
            new_hash_list.append(ns['hash'])

        old_articles = self.article.find({'deleted': False})
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
        deleted_ids = [x['_id'] for x in self.article.find({"hash": {"$nin": new_hash_list}, '_id': {'$in': current_article_ids}, 'deleted': False})]
        self.delete_article_list_by_ids(deleted_ids)

        existing_article_ids = [x['_id'] for x in self.article.find({"hash": {"$in": new_hash_list}, 'deleted': False})]
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
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        #full_artilces = list(self.article.find({'_id': {"$in": articles['articles']}}))
        full_articles = list(self.article.find(search_param).skip(start).limit(length + 1))
        more = True if len(full_articles) > length else False
        return full_articles, more

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

    def get_default_entity(self, params):
        search_params = {}
        if params and 'type' in params:
            search_params['type'] = params['type']

        search_params['language'] = 'en'
        if params and 'language' in params:
            search_params['language'] = params['language']

        return list(self.default_entity.find(search_params))

    def show_article_list(self, params):
        language = 'en'

        if 'tags' not in params:
            raise EnvironmentError('Request must contain \'tags\' field')
        tags = params['tags']
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
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
        more = True if len(list_to_show) > start + length else False
        return list_to_show[start:start + length], more

    def tag_stat(self, params):
        if 'tag' not in params:
            raise EnvironmentError('Request must contain \'tag\' field')
        tag = params['tag']
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
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
        more = True if len(t) > start + length else False
        stat['tag_list'] = t[start:start + length]
        return stat

    def show_country_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        c_list = list(self.country.find().skip(start).limit(length + 1))
        more = True if len(c_list) > length else False
        return c_list[:-1], more

    def show_state_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        s_list = list(self.state.find().skip(start).limit(length + 1))
        more = True if len(s_list) > length else False
        return s_list[:-1], more

    def show_pr_city_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        pr_list = list(self.pr_city.find().skip(start).limit(length + 1))
        more = True if len(pr_list) > length else False
        return pr_list[:-1], more

    def show_trained_article_list(self, params={'status': 'trained'}):
        search_param = dict()
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        trained = self.entity.count({'trained': True})
        untrained = self.entity.count({'trained': False})
        search_param['trained'] = True if params['status'] == 'trained' else False
        articles = list(self.entity.find(search_param).skip(start).limit(length + 1))
        more = True if len(articles) > length else False
        return articles, trained, untrained, more
