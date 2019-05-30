""""Connection class to mongoDB"""

import pymongo
import pycountry
from bson import ObjectId
from news import NewsCollection
from nlp.config import MONGO  # , TYPE_WITHOUT_FILE, SEND_POST_URL, ADMIN_USER, DEFAULT_USER
import hashlib
import json
import re
import requests
from bs4 import BeautifulSoup
import geoposition as geo
from collections import Counter
import datetime
from lib import tools


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


class MongoConnection(object):
    """Connection class to mongoDB"""

    def __init__(self, config=None, language=None):
        # override the global CONFIG if the config override dict is supplied
        config = dict(MONGO, **config) if config else MONGO
        mongo = pymongo.MongoClient(config['mongo_host'], connect=True)
        self.mongo_db = mongo[config['database']]
        self.news_api_call = self.mongo_db[config['news_api_call_collection']]
        self.phrase = self.mongo_db[config['phrase_collection']]
        self.source = self.mongo_db[config['source_collection']]
        self.article = self.mongo_db[config['article_collection']]
        self.q_article = self.mongo_db[config['q_article_collection']]
        self.location = self.mongo_db[config['location_collection']]
        self.country = self.mongo_db[config['country_collection']]
        self.state = self.mongo_db[config['state_collection']]
        self.pr_city = self.mongo_db[config['pr_city_collection']]
        self.entity = self.mongo_db[config['entity_collection']]
        self.default_entity = self.mongo_db[config['default_entity_collection']]
        self.language = self.mongo_db[config['language_collection']]
        self.category = self.mongo_db[config['category_collection']]
        self.iso639 = self.mongo_db[config['iso639_collection']]
        self.iso3166 = self.mongo_db[config['iso3166_collection']]

    def get_article_language_list(self):
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

        search_fields = ['deleted', 'name', 'id']
        search_fields_list = ['language', 'country', 'category']
        # Convert str to list
        for field in params:
            if field in search_fields_list:
                if params[field] and not isinstance(params[field], list):
                    params[field] = [params[field]]
        # Fill up search_fields
        if params:
            for field in search_fields:
                if field in params:
                    search_param[field] = params[field]
            for field in search_fields_list:
                if field in params:
                    search_param[field] = {'$in': params[field]}
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        sources = list(self.source.find(search_param).skip(start).limit(length + 1))
        more = True if len(sources) > length else False
        return sources[:length], more

    def add_news_api_call(self, call):
        call['start_time'] = datetime.datetime.utcnow()
        return self.news_api_call.insert_one(call).inserted_id

    def load_iso(self):
        with open(tools.get_abs_path('../data/iso639-3.json'), 'r') as f:
            tree = json.load(f)
        self.iso639.insert(tree['639-3'])
        with open(tools.get_abs_path('../data/iso3166-1.json'), 'r') as f:
            tree = json.load(f)
        self.iso3166.insert(tree['3166-1'])

# ***************************** GEOLOCATION ******************************** #

    def update_country_list(self):
        country_list = []
        url = requests.get('https://en.wikipedia.org/wiki/List_of_sovereign_states').text
        soup = BeautifulSoup(url, 'lxml')
        my_table = soup.find('table')
        countries = my_table.findAll('td', style="vertical-align:top;")
        for country in countries:
            cntr = dict()
            zzz = country.find('span', style="display:none")
            name = country.get_text().replace(zzz.get_text(), '') if zzz else country.get_text()
            name = name.replace('→', '–').replace('\n', '')
            name = re.sub(r'[[a-z,0-9].]', '', name)
            name = name.replace('[', '')
            common_name = name.split('–')[0].strip()
            official_name = name.split('–')[1].strip() if len(name.split('–')) > 1 else common_name.strip()
            country_code = list(self.iso3166.find({'$or': [{'name': official_name}, {'name': common_name},
                                                         {'official_name': official_name}, {'official_name': common_name}]}))
            cntr['name'] = official_name
            cntr['type'] = 'country'
            cntr['common name'] = common_name
            if len(country_code) > 0:
                cntr['code'] = country_code[0]['alpha_2'] if country_code[0]['alpha_2'] else country_code[0]['alpha_3']
            else:
                cntr['code'] = 'unknown code'
            cntr['location'] = None
            try:
                cntr['location'] = geo.get_geoposition({'text': cntr['name']})
            except Exception:
                pass
            cntr['parent'] = None
            country_list.append(cntr)
        self.location.insert(country_list)

    def update_state_list(self):
        us_states_list = []
        url = requests.get('https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations').text
        soup = BeautifulSoup(url, 'lxml')
        table = soup.find('table', "wikitable sortable").findAll('tr')
        for row in table[12:]:
            st = dict()
            state = row.find('td').get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
            state = re.sub(r'[[a-z,0-9].]', '', state)
            description = []
            for desc in row.findAll('td')[2:]:
                d = desc.get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
                if d is not ('' or r'\d'):
                    description.append(d)
            description = remove(description)
            country = self.location.find_one({'name': "United States of America"})
            st['parent'] = country['_id'] if country else None
            st['type'] = 'state'
            st['name'] = state
            st['description'] = description
            st['location'] = None
            try:
                st['location'] = geo.get_geoposition({'text': st['name']})
            except Exception:
                pass
            us_states_list.append(st)
        self.location.insert(us_states_list)

    def update_pr_city_list(self):
        pr_city_list = []
        url = requests.get('https://suburbanstats.org/population/puerto-rico/list-of-counties-and-cities-in-puerto-rico').text
        soup = BeautifulSoup(url, 'lxml')
        pr_city = soup.findAll('a', title=re.compile('Population Demographics and Statistics'))
        for city in pr_city:
            ct = dict()
            state = self.location.find_one({'name': "Puerto Rico"})
            ct['parent'] = state['_id'] if state else None
            ct['name'] = city.get_text()
            ct['type'] = 'city'
            try:
                ct['location'] = geo.get_geoposition({'text': ct['name']})
            except Exception:
                pass
            pr_city_list.append(ct)
        self.location.insert(pr_city_list)

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
        """
        Description: update source list from news collector (for scheduler)
        It makes request to server and updates sources in db.
        It adds new sources and deletes(change ‘deleted’ filed) not available sources. The ‘response’ field contains that ids.
        Input: None
        :return: inserted_ids and deleted_ids of sources
        """
        new_sources, _ = NewsCollection.get_sources("")
        new_sources_hash = new_sources.copy()
        new_hash_list = []
        last_call_list = list(self.news_api_call.find({'type': 0, 'end_time': {'$exists': True}}).sort('start_time', -1).limit(1))
        try:
            last_call = last_call_list.pop()
        except Exception as ex:
            print("First call of update_source")
            last_call = None
        if last_call and last_call['start_time'] + datetime.timedelta(hours=1) > datetime.datetime.utcnow():
            return [], []

        news_api_call_id = self.add_news_api_call({'type': 0})

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
            source['articles'] = self.article.count({'source.id': source['id']})
            inserted_ids.append(self.source.update_one(source, {'$set': source}, upsert=True).upserted_id)

        deleted_ids = [x['_id'] for x in self.source.find({"hash": {"$nin": new_hash_list}})]
        self.delete_source_list_by_ids(deleted_ids)

        self.news_api_call.update_one({'_id': news_api_call_id}, {'$set': {'end_time': datetime.datetime.utcnow()}})

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
#     def update_article_list_one_q(self, q):
#         # TO_DO: Change 1 hour to 24 hour
#         last_call_list = list(self.news_api_call.find({'q': q, 'type': 1, 'end_time': {'$exists': True}}).sort('start_time', -1).limit(1))
#         try:
#             last_call = last_call_list.pop()
#         except Exception as ex:
#             print('First call of {}'.format(q))
#             last_call = None
#         if last_call:
#             print(last_call['start_time'] + datetime.timedelta(hours=1))
#         print(datetime.datetime.utcnow())
#         if last_call and last_call['start_time'] + datetime.timedelta(hours=1) > datetime.datetime.utcnow():
#             return [], []
#
#         news_api_call_id = self.add_news_api_call({'q': q, 'type': 1})
#
#         new_articles, _ = NewsCollection.get_everything(q)
#         new_articles_hash = new_articles.copy()
#         new_hash_list = []
#         for ns in new_articles_hash:
#             hasher = hashlib.md5()
#             hasher.update(json.dumps(ns).encode('utf-8'))
#             ns['hash'] = hasher.hexdigest()
#             ns['deleted'] = False
#             new_hash_list.append(ns['hash'])
#
#         old_articles = self.article.find({'deleted': False})
#         old_sources_hashes = [x['hash'] for x in old_articles]
#         adding_articles = [new_s for new_s in new_articles_hash if new_s['hash'] not in old_sources_hashes]
#
#         inserted_ids = []
#         for article in adding_articles:
#             source = self.source.find_one({'deleted': False, 'id': article['source']['id'], 'name': article['source']['name']})
#             if source:
#                 article['source']['language'] = source['language']
#                 article['source']['category'] = source['category']
#                 article['source']['country'] = source['country']
#             inserted_ids.append(self.article.insert_one(article).inserted_id)
#
#         q_article = [x for articles in self.q_article.find({'q': q}) for x in articles['articles']]
#         current_article_ids = q_article
#         deleted_ids = [x['_id'] for x in self.article.find({"hash": {"$nin": new_hash_list}, '_id': {'$in': current_article_ids}, 'deleted': False})]
#         self.delete_article_list_by_ids(deleted_ids)
#
#         existing_article_ids = [x['_id'] for x in self.article.find({"hash": {"$in": new_hash_list}, 'deleted': False})]
#         self.q_article.update_one({'q': q},
#                                   {'$set': {'articles': existing_article_ids},
#                                    "$currentDate": {"lastModified": True}},
#                                   upsert=True)
#
#         self.news_api_call.update_one({'_id': news_api_call_id}, {'$set': {'end_time': datetime.datetime.utcnow()}})
#
#         return inserted_ids, deleted_ids

    def update_article_list_one_q(self, q, language, new_articles):
        new_articles_hash = new_articles.copy()
        new_hash_list = []
        for ns in new_articles_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            new_hash_list.append(ns['hash'])

        old_articles = self.article.find()
        old_sources_hashes = [x['hash'] for x in old_articles]
        adding_articles = [new_s for new_s in new_articles_hash if new_s['hash'] not in old_sources_hashes]

        inserted_ids = []
        for article in adding_articles:
            # !!! Attention
            # source = self.source.find_one({'deleted': False, 'id': article['source']['id'], 'name': article['source']['name']})
            source = self.source.find_one({
                'deleted': False,
                '$or': [
                    {'id': article['source']['id']},
                    {'name': article['source']['name']}
                ]
            })
            if source:
                article['source']['language'] = source['language']
                article['source']['category'] = source['category']
                article['source']['country'] = source['country']
            inserted_ids.append(self.article.insert_one(article).inserted_id)

        current_article_ids = [x for articles in self.q_article.find({'q': q, 'language': language}) for x in articles['articles']]

        # deleted_ids = [x['_id'] for x in self.article.find({'hash': {'$nin': new_hash_list}, '_id': {'$in': current_article_ids}, 'deleted': False})]
        # self.delete_article_list_by_ids(deleted_ids)

        new_article_ids = [x['_id'] for x in self.article.find({'hash': {'$in': new_hash_list}})]
        article_ids = list(set(current_article_ids+new_article_ids))
        self.q_article.update_one({'q': q, 'language': language},
                                  {'$set': {'articles': article_ids},
                                   '$currentDate': {'lastModified': True}},
                                  upsert=True)

        # self.news_api_call.update_one({'_id': news_api_call_id}, {'$set': {'end_time': datetime.datetime.utcnow()}})

        # return inserted_ids, deleted_ids

    def update_article_list_from_server(self, params):
        """
        Description: update article list from news collector (for scheduler)
        It makes request to server and updates articles in db.
        It adds new sources and deletes(change ‘deleted’ filed) not available sources. The ‘response’ field contains that ids.
        :param params:
        q - search word (str or list)
        :return: inserted_ids and deleted_ids of article
        """
        if 'q' not in params:
            raise EnvironmentError('Request must contain \'q\' field')
        q = params['q']
        if not isinstance(q, list):
            q = [q]

        for one_q in q:
            self.update_article_list_one_q(one_q)
        return [], []

    def get_q_article_list(self, params):
        if 'q' not in params:
            raise EnvironmentError('Request must contain \'q\' field')

        q = params['q']
        # Convert str to list
        if not isinstance(q, list):
            q = [q]

        case_sensitive = True
        if 'case_sensitive' in params:
            case_sensitive = params['case_sensitive']
        if not case_sensitive:
            q = [x.lower() for x in q]

        deleted = False
        if 'deleted' in params:
            deleted = params['deleted']

        search_param = dict()

        search_fields = ['name', 'id']
        search_fields_list = ['language', 'country', 'category']
        # Convert str to list
        for field in params:
            if field in search_fields_list:
                if params[field] and not isinstance(params[field], list):
                    params[field] = [params[field]]
        # Fill up search_fields
        if params:
            for field in search_fields:
                if field in params:
                    search_param['source.'+field] = params[field]
            for field in search_fields_list:
                if field in params:
                    search_param['source.'+field] = {'$in': params[field]}

        articles = [x for articles in self.q_article.find({'q': {'$in': q}}, {'_id': 0, 'articles': 1}) for x in articles['articles']]
        search_param['_id'] = {'$in': articles}

        search_param['deleted'] = deleted

        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        # full_artilces = list(self.article.find({'_id': {"$in": articles['articles']}}))
        full_articles = list(self.article.find(search_param).skip(start).limit(length + 1))
        more = True if len(full_articles) > length else False
        return full_articles[:length], more

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

    def add_phrases(self, params):
        """Adding phrase to the database"""
        if 'phrases' not in params:
            raise EnvironmentError('Request must contain \'phrases\' field')
        phrases = params['phrases']
        if not isinstance(phrases, list):
            phrases = [phrases]

        language = 'en'
        if 'language' in params:
            language = params['language']

        for phrase in phrases:
            self.phrase.update_one(
                {
                    'phrase': phrase,
                    'language': language,
                    'deleted': False
                },
                {
                    '$set': {
                        'phrase': phrase,
                        'language': language,
                        'deleted': False
                    }
                },
                upsert=True
            )

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

    def delete_phrases(self, params):
        """Delete phrase by the database"""
        if 'ids' not in params:
            raise EnvironmentError('Request must contain \'ids\' field')
        ids = params['ids']
        if isinstance(ids, str):
            ids = list(ids)

        ids = [ObjectId(_id) if not isinstance(_id, ObjectId) else _id for _id in ids]
        self.phrase.update_many(
            {'_id': {'$in': ids}},
            {'$set': {'deleted': True}},
            upsert=True
        )

    def update_phrases(self, params):
        """Updating phrase to the database"""
        if 'ids' not in params:
            raise EnvironmentError('Request must contain \'ids\' field')
        ids = params['ids']
        if isinstance(ids, str):
            ids = list(ids)

        ids = [ObjectId(_id) if not isinstance(_id, ObjectId) else _id for _id in ids]

        update_set = {}

        if 'deleted' in params:
            update_set['deleted'] = params['deleted']

        self.phrase.update_many(
            {'_id': {'$in': ids}},
            {'$set': update_set},
            upsert=True
        )

    def get_phrases(self, params):
        """Getting phrase to the database"""
        deleted = False
        if params and 'deleted' in params:
            deleted = params['deleted']

        return list(self.phrase.find({'deleted': deleted}))

    def download_articles_by_phrases(self):
        new_phrases = list(self.phrase.find({'deleted': False, 'to': {'$exists': False}}))
        old_phrases = list(self.phrase.find({'deleted': False, 'to': {'$exists': True}}))

        for phrase in new_phrases:
            _id = phrase['_id']
            q = phrase['phrase']
            language = phrase['language']
            articles, _, status = NewsCollection.get_everything(q, language)  # Only first page
            self.update_article_list_one_q(q, language, articles)
            if articles:
                published_at_list = sorted([article['publishedAt'] for article in articles])
                date_from = published_at_list[0]
                date_to = published_at_list[-1]
                self.phrase.update_one({'_id': _id}, {'$set': {'to': date_to, 'from': date_from}})

        for phrase in old_phrases:
            _id = phrase['_id']
            q = phrase['phrase']
            language = phrase['language']
            articles, total_count, status = NewsCollection.get_everything(q, language, from_date=phrase['to'])
            for x in range(total_count // 100):
                added, tc, status = NewsCollection.get_everything(q, language, from_date=phrase['to'], page=2+x)
                if tc == 0:
                    print("Добавить в дозагрузку")
                articles = articles + added
            self.update_article_list_one_q(q, language, articles)
            if articles:
                published_at_list = sorted([article['publishedAt'] for article in articles])
                date_to = published_at_list[-1]
                self.phrase.update_one({'_id': _id}, {'$set': {'to': date_to}})

        phrases = self.phrase.find({'deleted': False})
        # Download while we can
        own_status = 'ok'
        for phrase in phrases:
            if own_status == 'ok':
                _id = phrase['_id']
                q = phrase['phrase']
                language = phrase['language']
                articles, total_count, status = NewsCollection.get_everything(q, language, to_date=phrase['from'])
                self.update_article_list_one_q(q, language, articles)
                if articles:
                    published_at_list = sorted([article['publishedAt'] for article in articles])
                    date_from = published_at_list[0]
                    self.phrase.update_one({'_id': _id}, {'$set': {'from': date_from}})

    # ***************************** Train articles ******************************** #

    def get_default_entity(self, params):
        search_params = {}
        if params and 'type' in params:
            search_params['type'] = params['type']


        search_params['language'] = 'en'
        if params and 'language' in params:
            search_params['language'] = params['language']
        return list(self.default_entity.find(search_params))

    def update_language_list(self):
        language_list = list(self.iso639.find({'$or': [{'alpha_2': {'$exists': False}}, {'alpha_2': {'$exists': False}}]}))
        for lang in language_list:
            if hasattr(lang, 'alpha_2'):
                lang['article'] = self.article.count_documents({'source.language': lang.alpha_2})
                lang['source'] = self.source.count_documents({'language': lang.alpha_2})
        self.language.insert(language_list)
        
    def show_article_list(self, params):
        if 'tags' not in params:
            raise EnvironmentError('Request must contain \'tags\' field')
        tags = params['tags']
        query = dict()
        query_list = []
        for tag in tags.keys():
            query_list.append({'tags.{0}.word'.format(tag): tags.get(tag)})
        query['$or'] = query_list
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        list_to_show = list(self.entity.find(query).skip(start).limit(length))
        more = True if len(list_to_show) > start + length else False
        return list_to_show[:length], more

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

    def show_language_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        l_list = list(self.language.find().skip(start).limit(length + 1))
        more = True if len(l_list) > length else False
        return l_list[:length], more

    def get_language(self, params):
        if 'code' not in params:
            raise EnvironmentError('Request must contain \'code\' field')
        language = self.language.find_one({'code': params['code']})
        return language

    def show_country_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        c_list = list(self.country.find().skip(start).limit(length + 1))
        more = True if len(c_list) > length else False
        return c_list[:length], more

    def show_state_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        s_list = list(self.state.find().skip(start).limit(length + 1))
        more = True if len(s_list) > length else False
        return s_list[:length], more

    def show_pr_city_list(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        pr_list = list(self.pr_city.find().skip(start).limit(length + 1))
        more = True if len(pr_list) > length else False
        return pr_list[:length], more

    def show_trained_article_list(self, params):
        search_param = dict()
        status = 'trained' if 'status' not in params else params['status']
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        trained = self.entity.count({'trained': True})
        untrained = self.entity.count({'trained': False})
        search_param['trained'] = True if status == 'trained' else False
        articles = list(self.entity.find(search_param).skip(start).limit(length + 1))
        more = True if len(articles) > length else False
        return articles[:length], trained, untrained, more

    # ***************************** Category ******************************** #

    def update_category(self):
        categories = self.source.distinct("category")

        old_category = self.category.find({'deleted': False})
        adding_category = [new_c for new_c in categories if new_c not in old_category]
        for category in adding_category:
            cat = dict()
            cat['name'] = category
            cat['articles'] = self.article.count({'source.category': category})
            cat['sources'] = self.source.count({'category': category})
            self.category.insert_one(cat)



