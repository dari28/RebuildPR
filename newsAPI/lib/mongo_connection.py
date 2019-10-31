""""Connection class to mongoDB"""

import pymongo
from bson import ObjectId, errors
from news import NewsCollection
from nlp.config import MONGO, MONGO_TABLES  # , TYPE_WITHOUT_FILE, SEND_POST_URL, ADMIN_USER, DEFAULT_USER
import hashlib
import json
import re
import requests
from bs4 import BeautifulSoup
import geoposition as geo
from lib import tools
import time
from geopy.geocoders import Nominatim
import operator
import logging
from urlextract import URLExtract
from newsAPI.settings import LOCAL


def remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


def find_loc_by_name(name):
    with MongoConnection() as mongodb:
        if mongodb.location.count({'tags': {'$in': [name]}}) > 0:
            print('location already in db')
            return mongodb.location.find_one({'tags': {'$in': [name]}})['_id']
        print('search...')
        main_url = 'https://nominatim.openstreetmap.org/'
        search = 'search.php?q=' + name + '&polygon_geojson=1&viewbox='
        url = None
        for i in range(3):
            try:
                url = requests.get(main_url + search).text
            except Exception as e:
                print(e)
                print('sleep_5')
                time.sleep(5)
                if i == 2:
                    return None
            else:
                print('url: OK')
                break
        if not url:
            print('url: Fail!')
            return None
        soup = BeautifulSoup(url, 'lxml')
        if soup.find('div', id='content') is not None:
            content = soup.find('div', id='content')
            print('content: OK')
        else:
            print('content: Fail!')
            return None
        if content.find('div', id='searchresults') is not None:
            search_results = content.find('div', id='searchresults')
            print('search results: OK')
        else:
            print('search results: Fail!')
            return None
        loc_type = None
        loc_url = None
        if search_results.find_all('div') is not None:
            results = search_results.find_all('div')
            print('results: OK')
        else:
            print('results: Fail!')
            return None
        for res in results:
            if res['class'] == ["noresults"]:
                print('location is not found')
                return None
            if res is None:
                return None
            if res.find('a')['href'] is not None:
                location_url = res.find('a')['href']
            else:
                location_url = None
            if res.find('span', {'class': 'type'}) is not None:
                if res.find('span', {'class': 'type'}).get_text().replace('(', '').replace(')', '') is not None:
                    location_type = res.find('span', {'class': 'type'}).get_text().replace('(', '').replace(')', '')
                else:
                    location_type = None
            else:
                location_type = None
            if location_type in ['Country', 'State', 'County', 'City']:
                loc_url = location_url
                print('loc type: OK')
                break
        if loc_url:
            loc_id = loc_url.split('place_id=')[1]
            return find_loc_by_id(loc_id, name)
        else:
            print('no such location')
            return None


def find_loc_by_id(loc_id, tag=None):
    with MongoConnection() as mongodb:
        if mongodb.location.count({'place_id': loc_id}) > 0:
            if tag:
                loc_id = mongodb.location.update_one({'place_id': loc_id}, {'$addToSet': {'tags': tag}}).upserted_id
                return loc_id
            else:
                return None
        main_url = 'https://nominatim.openstreetmap.org/'
        loc_url = 'details.php?place_id=' + loc_id
        parents_list = []
        loc_link = None
        max_attempts = 3
        cur_attemps = 0
        while cur_attemps < max_attempts and not loc_link:
            try:
                loc_link = requests.get(main_url + loc_url).text
            except Exception as e:
                print(e)
                print('sleep_5')
                time.sleep(5)
            cur_attemps += 1

        if not loc_link:
            return None
        loc_info = BeautifulSoup(loc_link, 'lxml')
        loc_details = loc_info.find('table', {'id': 'locationdetails'})
        if not loc_details:
            return None
        details_trs = loc_details.find_all('tr')
        if not details_trs:
            return None

        loc_name = None
        centre_point = None
        loc_type = None
        for tr in details_trs:
            if tr.find('td').get_text() == 'Name':
                nm = tr.find_all('td')[1].find_all('div', {'class': 'line'})
                for n in nm:
                    full_text = n.get_text()
                    l_name = n.find('span').get_text()
                    name_type = full_text.replace(l_name, '')
                    if name_type == ' (int_name)' or name_type == ' (name)':
                        loc_name = l_name
                        break
            if tr.find('td').get_text() == 'Centre Point':
                centre_point = tr.find_all('td')[1].get_text().replace('(', '').replace(')', '')
            if tr.find('td').get_text() == 'Rank':
                loc_type = tr.find_all('td')[1].get_text()

        address_table = loc_info.find('table', {'id': 'address'})
        if not address_table:
            return None
        body = address_table.find('tbody')
        if not body:
            return None
        trs = body.find_all('tr')
        if not trs:
            return None
        for tr in trs:
            links = tr.find_all('a')
            for link in links:
                text = link.get_text()
                if text == 'details >':
                    parent_link = link['href']
                    parent_id = parent_link.split('place_id=')[1]
                    if parent_id != loc_id:
                        parents_list.append(parent_id)
                        # DONT ADD TAGS TO CHILD
                        find_loc_by_id(parent_id)
            if tr['class'] == ["notused"]:
                break
        if not loc_name and not loc_id and not centre_point:
            request_dict = {
                'place_id': loc_id,
                'name': loc_name,
                'location': {
                    'latitude': centre_point.split(',')[0],
                    'longitude': centre_point.split(',')[1]
                },
                'parents': parents_list,
                'type': loc_type,
                'level': len(parents_list)
            }
            if tag:
                request_dict['tags'] = [tag]

            loc_id = mongodb.location.insert_one(request_dict).inserted_id
            return loc_id
        else:
            return None


def remove_codes(address):
    if 'postcode' in address:
        address.pop('postcode', None)
    if 'country_code' in address:
        address.pop('country_code', None)
    return address


class MongoConnection(object):
    """Connection class to mongoDB"""

    def __init__(self, config=None, language=None):
        # override the global CONFIG if the config override dict is supplied
        config = dict(MONGO, **config) if config else MONGO

        user = config['user']
        password = config['password']
        auth_source = 'admin'

        if LOCAL:
            self.connection = pymongo.MongoClient(host=config['mongo_host'], connect=True)
        else:
            self.connection = pymongo.MongoClient(host=config['mongo_host'], username=user, password=password, authSource=auth_source, connect=True)

        self.mongo_db = self.connection[config['database']]
        for table in MONGO_TABLES:
            setattr(self, table, self.mongo_db[config[table + '_collection']])
        # self.phrase = self.mongo_db[config['phrase_collection']]
        # self.source = self.mongo_db[config['source_collection']]
        # self.article = self.mongo_db[config['article_collection']]
        # self.q_article = self.mongo_db[config['q_article_collection']]
        # self.location = self.mongo_db[config['location_collection']]
        # self.country = self.mongo_db[config['country_collection']]
        # self.state = self.mongo_db[config['state_collection']]
        # self.pr_city = self.mongo_db[config['pr_city_collection']]
        # self.entity = self.mongo_db[config['entity_collection']]
        # self.default_entity = self.mongo_db[config['default_entity_collection']]
        # self.language = self.mongo_db[config['language_collection']]
        # self.category = self.mongo_db[config['category_collection']]
        # self.iso639 = self.mongo_db[config['iso639_collection']]
        # self.iso3166 = self.mongo_db[config['iso3166_collection']]
        # self.geopy_requests = self.mongo_db[config['geopy_requests_collection']]
        # self.units = self.mongo_db[config['units_collection']]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connection.close()

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
        sources = list(self.source.find(search_param).sort('_id', 1).skip(start).limit(length + 1))
        more = True if len(sources) > length else False
        for source in sources:
            source["articles"] = self.article.count({'source.name': source['name']})
        return sources[:length], more

    def load_iso(self):
        with open(tools.get_abs_path('../data/iso639-3.json'), 'r', encoding="utf-8") as f:
            tree = json.load(f)
        self.iso639.insert(tree['639-3'])
        with open(tools.get_abs_path('../data/iso3166-1.json'), 'r', encoding="utf-8") as f:
            tree = json.load(f)
        self.iso3166.insert(tree['3166-1'])

    def check_mongo_connection(self):
        try:
            for table in MONGO_TABLES:
                c_table = getattr(self, table)
                print('{0:20} : {1}'.format(table, c_table.count({})))
            print('Mongo database connected.')
        except Exception as ex:
            raise EnvironmentError("Problem with mongo connection: " + str(ex))
# ***************************** GEOLOCATION ******************************** #

    def update_country_list(self):
        # country_list = []
        url = requests.get('https://en.wikipedia.org/wiki/List_of_sovereign_states').text
        soup = BeautifulSoup(url, 'lxml')
        my_table = soup.find('table')
        countries = my_table.findAll('td', style="vertical-align:top;")
        for country in countries:
            # cntr = dict()
            c_span = country.find('span', style="display:none")
            name = country.get_text().replace(c_span.get_text(), '') if c_span else country.get_text()
            name = name.replace('→', '–').replace('\n', '')
            name = re.sub(r'[[a-z,0-9].]', '', name)
            name = name.replace('[', '')
            common_name = name.split('–')[0].strip()
            official_name = name.split('–')[1].strip() if len(name.split('–')) > 1 else common_name.strip()
            if common_name:
                find_loc_by_name(common_name)
            else:
                find_loc_by_name(official_name)
        #     country_code = list(self.iso3166.find({'$or': [{'name': official_name}, {'name': common_name},
        #                                                    {'official_name': official_name}, {'official_name': common_name}]}))
        #
        #     cntr['name'] = official_name
        #     cntr['type'] = 'country'
        #     cntr['common name'] = common_name
        #     if len(country_code) > 0:
        #         cntr['code'] = country_code[0]['alpha_2'] if country_code[0]['alpha_2'] else country_code[0]['alpha_3']
        #     else:
        #         cntr['code'] = 'unknown code'
        #     cntr['location'] = None
        #     # try:
        #     #     cntr['location'] = geo.get_geoposition({'text': cntr['name']})
        #     # except Exception:
        #     #     pass
        #     cntr['parent'] = None
        #     country_list.append(cntr)
        # self.location.insert(country_list)

    def update_state_list(self):
        # us_states_list = []
        url = requests.get('https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations').text
        soup = BeautifulSoup(url, 'lxml')
        table = soup.find('table', "wikitable sortable").findAll('tr')
        for row in table[12:]:
            st = dict()
            state = row.find('td').get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
            state = re.sub(r'[[a-z,0-9].]', '', state)
            find_loc_by_name(state)
        #     description = []
        #     for desc in row.findAll('td')[2:]:
        #         d = desc.get_text().replace('\n', '').replace('\r', '').replace(u'\xa0', u'')
        #         if d is not ('' or r'\d'):
        #             description.append(d)
        #     description = remove(description)
        #     country = self.location.find_one({'name': "United States of America"})
        #     if country:
        #         p_list = [country['_id']]
        #         if country['parent']:
        #             p_list.append(country['parent'])
        #     else:
        #         p_list = None
        #     st['parent'] = p_list
        #     st['type'] = 'state'
        #     st['name'] = state
        #     st['description'] = description
        #     st['location'] = None
        #     # try:
        #     #     st['location'] = geo.get_geoposition({'text': st['name']})
        #     # except Exception:
        #     #     pass
        #     us_states_list.append(st)
        # self.location.insert(us_states_list)

    def update_pr_city_list(self):
        # pr_city_list = []
        url = requests.get('https://suburbanstats.org/population/puerto-rico/list-of-counties-and-cities-in-puerto-rico').text
        soup = BeautifulSoup(url, 'lxml')
        pr_city = soup.findAll('a', title=re.compile('Population Demographics and Statistics'))
        for city in pr_city:
            find_loc_by_name(city.get_text())
        #     ct = dict()
        #     state = self.location.find_one({'name': "Puerto Rico"})
        #     if state:
        #         p_list = [state['_id']]
        #         if state['parent']:
        #             p_list.append(state['parent'])
        #     else:
        #         p_list = None
        #     ct['parent'] = p_list
        #     ct['name'] = city.get_text()
        #     ct['type'] = 'city'
        #     ct['location'] = None
        #     # try:
        #     #     ct['location'] = geo.get_geoposition({'text': ct['name']})
        #     # except Exception:
        #     #     pass
        #     pr_city_list.append(ct)
        # self.location.insert(pr_city_list)

    @staticmethod
    def fill_up_geolocation(table, field):
        table_list = table.find({'location':  {'$eq': None}})
        updated_ids = []
        for table_item in table_list:
            _id = table_item['_id']
            updated_ids.append(_id)
            table_item['location'] = None
            try:
                table_item['location'] = geo.get_geoposition({'text': table_item[field]})
            except Exception as ex:
                print(ex)
            table.update_one({'_id': _id}, {'$set': table_item})
        return updated_ids

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

        return inserted_ids, deleted_ids

    def add_bad_source(self, source_name):
        self.source.insert({'bad': True, 'name': source_name})

    def remove_bad_source(self, source_id):
        if not isinstance(source_id, ObjectId):
            source_id = ObjectId(source_id)
        self.source.delete_one({'_id': source_id})

    def remove_all_bad_source(self):
        self.source.delete_many({'bad': True})

    def check_source(self, source_name):
        source = list(self.source.find_one({'name': source_name}))
        if len(source) > 0:
            return source[0]['bad']

    def delete_source_list_by_ids(self, ids):
        """Delete sources by the database"""
        for id in ids:
            self.source.update_one(
                {'_id': ObjectId(id) if not isinstance(id, ObjectId) else id},
                {'$set': {'deleted': True}},
                upsert=True
            )
        return ids

    def add_article_locations(self, entity_id):

        article = self.entity.find_one({'_id': entity_id})
        print('entity_id: ', entity_id)
        if 'location' in article['tags']:
            tags = article['tags']['location']
            art = self.article.find_one({'_id': article['article_id']})
            if 'language' in art['source']:
                lang = art['source']['language']
            else:
                lang = "en"
            locations = []
            for tag in list(tags):
                location = find_loc_by_name(tag['word'])
                loc_list = list(self.location.find_one({'_id': location})['parents'])
                loc_list.append(location)
                for loc in loc_list:
                    if loc not in locations:
                        locations.append(loc)
            self.entity.update_one({'_id': entity_id}, {'$set': {'locations': locations}})

    # def find_articles_by_location(self, params):
    #     if 'location' not in params:
    #         raise EnvironmentError('Request must contain \'location\' field')
    #     location = params['location']
    #     articles = dict()
    #     art_list = list(self.entity.find({'locations': {'$in': [location]}}))
    #     articles_list = []
    #     for l in art_list:
    #         articles_list.append(l['_id'])
    #     articles['articles_list'] = articles_list
    #     articles['count'] = len(articles_list)
    #     return articles

    def aggregate_articles_by_locations(self, params):
        if 'locations' in params:
            locations = params['locations']
            if not isinstance(locations, list):
                locations = [locations]
            locations = [location if isinstance(location, ObjectId) else ObjectId(location) for location in locations]
            location_match = {"$in": locations}
        else:
            location_match = {"$exists": False}

        pipeline = [
            {"$match": {
                "locations": location_match
            }},
            {"$addFields": {
                "tags": {"$objectToArray": "$tags"}
            }},
            {"$unwind": "$tags"},
            {"$unwind": "$tags.v"}
        ]
        if 'keywords' in params:
            kw = params['keywords']
            if not isinstance(kw, list):
                kw = [kw]
            pipeline += [
                {"$match": {
                    "tags.v.word": {
                        "$in": kw
                    }
                }}
            ]
        if 'pers/org' in params:
            porg = params['pers/org']
            if not isinstance(porg, list):
                porg = [porg]
            pipeline += [
                {"$match": {
                    "tags.k": {
                        "$in": ["person", "organization"]
                    }
                }},
                {"$group": {
                    "_id": "$_id",
                    # "article_id": {"$push":{"article_id":"$article_id"}},
                    "tag_words": {
                        "$push": {
                            "tag_cat": "$tags.k",
                            "tag_word": "$tags.v.word",
                        }
                    },
                }},
                {"$match": {"tag_words.tag_word": {"$all": porg}}},
            ]
        # else:
        #     pipeline += [
        #         {"$group": {
        #             "_id": "$_id",
        #             "article_id": {"$push": {"article_id": "$article_id"}},
        #
        #         }},
        #         ]
        pipeline += [
            {"$project": {"_id": 1, 'article_id': '$article_id'}}
            ]
        articles = list(self.entity.aggregate(pipeline=pipeline, allowDiskUse=True))
        entity_ids = [art['_id'] for art in articles]
        article_ids = [art['article_id'] for art in articles]

        article_full = list(self.article.find({'_id': {"$in": article_ids}}, {'title': 1, 'author': 1, 'publishedAt': 1}).sort('_id', 1))

        tags_list = self.tag_stat_by_articles_list({'articles': entity_ids})
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        # count = len(articles)
        count = len(article_full)
        more = True if count > length else False
        out = {'articles_count': count, 'articles_list': article_full[start: start + length], 'more': more, 'tags_list': tags_list}
        return out

    def tag_stat_by_articles_list(self, params):
        if 'articles' not in params or not isinstance(params['articles'], list):
            raise EnvironmentError('Request must contain \'articles\' field and articles must be list type')
        tags = ['location', 'person', 'organization', 'money', 'percent', 'date', 'time']
        articles = params['articles']
        ids = [ObjectId(_id) if not isinstance(_id, ObjectId) else _id for _id in articles]
        pipeline = [
            {"$addFields": {
                "tags": {"$objectToArray": "$tags"}
            }},
            {'$match': {
                '_id': {
                    '$in': ids
                }
            }},
            {"$unwind": "$tags"},
            {"$unwind": "$tags.v"},
            {'$match': {
                'tags.k': {
                    '$in': tags}
            }},
            {"$group": {
                "_id": {
                    # "tag": "$tags.k",
                    "phrase": "$tags.v.word",
                    "count": "$count"
                },
                "count": {"$sum": 1}
            }},
            {'$sort': {'count': -1}},
            {'$project': {'tag': '$_id.phrase', 'count': 1, '_id': 0}},
        ]

        return list(self.entity.aggregate(pipeline, allowDiskUse=True))

    def get_locations_by_level(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        is_only_nonempty = 'only_nonempty' in params and params['only_nonempty']
        entity_locations_unpacked = []
        if is_only_nonempty:
            entity_locations = list(self.entity.aggregate([
                {'$project': {'locations': 1, '_id': 0}},
                {'$unwind': '$locations'},
                {'$group': {'_id': None, 'locations': {'$addToSet': "$locations"}}},

            ]))
            try:
                entity_locations_unpacked = entity_locations[0]['locations']
            except Exception as ex:
                print(ex)
                entity_locations_unpacked = []
        if 'location' not in params:
            pipeline = [
                {'$match': {'level': 0}},
                {'$group': {'_id': '$_id'}},
                {'$project': {'_id': 1}},
                {'$sort': {'_id': 1}}
            ]

            if is_only_nonempty:
                pipeline += [
                    {'$match': {'_id': {'$in': entity_locations_unpacked}}}
                ]

            pipeline += [
                {'$skip': start},
                {'$limit': length + 1}
            ]
            locations = list(self.location.aggregate(pipeline))
        else:
            location = params['location']
            loc_id = ObjectId(location) if not isinstance(location, ObjectId) else location
            loc = self.location.find_one({'_id': loc_id})

            if not loc:
                raise EnvironmentError('No element with such _id')

            place_id = loc['place_id']

            pipeline1 = [
                {'$match': {'parents': {'$in': [place_id]}, 'level': loc['level'] + 1, '_id': {'$in': entity_locations_unpacked}}},
                {'$group': {'_id': '$_id'}},
                {'$project': {'_id': 1}}
            ]

            # pipeline2 = [
            #     {'$match': {'level': loc['level'] + 1}},
            #     {'$unwind': '$parents'},
            #     {'$match': {'parents': place_id}},
            #     {'$group': {'_id': '$_id'}},
            #     {'$project': {'_id': 1}}
            # ]

            pipeline1 += [
                {'$skip': start},
                {'$limit': length + 1}
            ]

            locations = list(self.location.aggregate(pipeline1))
        locations = [x['_id'] for x in locations]
        more = True if len(locations) > length else False
        return locations[:length], more

    # ***************************** ARTICLES ******************************** #
    def delete_trash_from_article_content(self, content):
        content = re.sub(r'\[\+(\d)+ \w+\]$', '', content)  # remove [+657 chars] at the end
        content = re.sub(r'\w+… ?$', '', content)  # remove end characters with ...
        content = re.sub(r'… ?$', '', content)  # remove end ...
        content = re.sub(r'\ufffd', '', content, flags=re.U)  # remove �
        # content = re.sub(r'\x0a', '', content)  # remove /r
        # content = re.sub(r'\x0d', '', content)  # remove /n
        content = re.sub(r'[\u00A0]+', ' ', content, flags=re.U)  # remove spaces
        content = re.sub(r'[\r\n\t\f\v]+', ' ', content)  # change spec symbols to one space
        content = re.sub(r'[\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u200b\u202b\u205f\u2060\u3000]+', ' ', content, flags=re.U)  # remove spaces
        content = re.sub(r'[ ]{2,}', ' ', content)  # change 2+ spaces to one space
        extractor = URLExtract()
        urls = extractor.find_urls(content)
        for url in urls:
            content = content.replace(url, '')
        content = re.sub(r'(?:\w+\.pdf|\w+\.txt|\w+\.doc|\w+\.docx'
                      r'|\w+\.odt|\w+\.rtf|\w+\.tex|\w+\.wks'
                      r'|\w+\.wps|\w+\.wpd|\w+\.exe|\w+\.3g2'
                      r'|\w+\.3gp|\w+\.avi|\w+\.flv|\w+\.h264'
                      r'|\w+\.m4v|\w+\.mkv|\w+\.mov|\w+\.mp4'
                      r'|\w+\.mpg|\w+\.mpeg|\w+\.rm|\w+\.swf'
                      r'|\w+\.vob|\w+\.wmv|\w+\.bak|\w+\.cab'
                      r'|\w+\.cfg|\w+\.cpl|\w+\.cur|\w+\.dll'
                      r'|\w+\.dmp|\w+\.drv|\w+\.icns|\w+\.ico'
                      r'|\w+\.ini|\w+\.lnk|\w+\.msi|\w+\.sys'
                      r'|\w+\.tmp|\w+\.ods|\w+\.xlr|\w+\.xls'
                      r'|\w+\.xlsx|\w+\.c|\w+\.class|\w+\.cpp'
                      r'|\w+\.cs|\w+\.h|\w+\.java|\w+\.sh'
                      r'|\w+\.swift|\w+\.vb|\w+\.key|\w+\.odp'
                      r'|\w+\.pps|\w+\.ppt|\w+\.pptx|\w+\.asp'
                      r'|\w+\.aspx|\w+\.cer|\w+\.cfm|\w+\.cgi'
                      r'|\w+\.pl|\w+\.css|\w+\.htm|\w+\.html'
                      r'|\w+\.js|\w+\.jsp|\w+\.part|\w+\.php'
                      r'|\w+\.py|\w+\.rss|\w+\.xhtml|\w+\.ai'
                      r'|\w+\.bmp|\w+\.gif|\w+\.ico|\w+\.jpeg'
                      r'|\w+\.jpg|\w+\.png|\w+\.ps|\w+\.psd'
                      r'|\w+\.svg|\w+\.tif|\w+\.tiff|\w+\.fnt'
                      r'|\w+\.fon|\w+\.otf|\w+\.ttf|\w+\.apk'
                      r'|\w+\.bat|\w+\.bin|\w+\.cgi|\w+\.pl'
                      r'|\w+\.com|\w+\.gadget|\w+\.jar|\w+\.py'
                      r'|\w+\.wsf|\w+\.csv|\w+\.dat|\w+\.db'
                      r'|\w+\.dbf|\w+\.log|\w+\.mdb|\w+\.sav'
                      r'|\w+\.sql|\w+\.tar|\w+\.xml|\w+\.bin'
                      r'|\w+\.dmg|\w+\.iso|\w+\.toast|\w+\.vcd'
                      r'|\w+\.7z|\w+\.arj|\w+\.deb|\w+\.pkg'
                      r'|\w+\.rar|\w+\.rpm|\w+\.tar.gz|\w+\.z'
                      r'|\w+\.zip|\w+\.aif|\w+\.cds|\w+\.mid'
                      r'|\w+\.midi|\w+\.mp3|\w+\.mpa|\w+\.ogg'
                      r'|\w+\.wav|\w+\.wma|\w+\.wpl)', '', content)
        content = re.sub(r'www\.\S+', '', content)  # remove url1
        content = re.sub(r'https?:\/\/\S+', '', content)  # remove url2
        content = re.sub(r'[→]+', '', content)  # remove strange symbols

        content = re.sub(r'Click here to join', '', content)  # remove links
        content = re.sub(r'Click here', '', content)  # remove links
        content = re.sub(r'</?\w+>', '', content)  # remove html tags

        content = re.sub(r'[\u2010\u2011\u2012\u2013\u2014]', '-', content, flags=re.U)  # change hyphen to normal hyphen
        content = re.sub(r'[-]{2,}', '-', content)  # change 2+ hyphen to one hyphen
        content = re.sub(r' -', ' ', content)  # change hyphen to normal hyphen
        content = re.sub(r'- ', ' ', content)  # change hyphen to normal hyphen
        content = re.sub(r'[ ]{2,}', ' ', content)  # change 2+ spaces to one space
        content = re.sub(r'[\u201c\u201d\u201e\u201f"]', "'", content, flags=re.U)  # change double-quotes to normal double-quotes
        content = re.sub(r"[\u2018\u2019\u201a\u201b']", "'", content, flags=re.U)  # change single-quotes to normal single-quotes
        # content = re.sub(r" '", " ", content)  # remove single-quotes with space before
        # content = re.sub(r"' ", " ", content)  # remove single-quotes with space after
        content = re.sub(r"[/]+", "/", content)  # get only one /
        content = re.sub(r" /", " ", content)  # remove / with space before
        content = re.sub(r"/ ", " ", content)  # remove / with space after
        content = re.sub(r'[ ]{2,}', ' ', content)  # change 2+ spaces to one space
        content = content.strip()
        return content

    def fix_sources_and_add_official_field(self):
        ans = self.source.update_many(
            {
                "language": {"$exists": True},
                "unofficial": {"$exists": False}
            },
            {
                "$set": {"unofficial": False}
            }
        )
        source_names = self.article.distinct("source.name", {"source.language": {"$exists": False}, 'source.id': None})
        for source_name in source_names:
            if not self.source.find_one({"name": source_name}):
                self.source.insert_one({'id': source_name, "name": source_name, "url": source_name, "unofficial": True})

    def fix_article_source_with_null_id(self):
        articles = self.article.find({"source.id": None})
        articles_without_update = []
        for article in articles:
            article_id = article["_id"]
            article_source_name = article["source"]["name"]
            source = self.source.find_one({"name": article_source_name})
            if source and 'unofficial' in source and source['unofficial']:
                self.article.update_one(
                    {"_id": article_id},
                    {"$set": {
                        "source.id": source['id'], "source.name": source['name']
                    }}
                )
            else:
                articles_without_update += article_id

    def fix_one_article_by_id(self, params):
        _id = params['_id']
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        article = self.article.find_one({'_id': _id})
        try:
            if 'content' not in article or not article['content']:
                self.article.delete_one({'_id': article['_id']})

            if 'original_content' in article:
                content = article['original_content']
            else:
                content = article['content']
                article['original_content'] = content

            if 'original_title' in article:
                title = article['original_title']
            else:
                title = article['title']
                article['original_title'] = title

            if 'original_description' in article:
                description = article['original_description']
            else:
                description = article['description']
                article['original_description'] = description

            content = self.delete_trash_from_article_content(content)
            article['content'] = content
            title = self.delete_trash_from_article_content(title)
            article['title'] = self.delete_trash_from_article_content(title)
            description = self.delete_trash_from_article_content(description)
            article['description'] = self.delete_trash_from_article_content(description)

            self.article.update_one(
                {'_id': article['_id']},
                {'$set': {
                    'content': article['content'],
                    'title': article['title'],
                    'description': article['description'],
                    'original_content': article['original_content'],
                    'original_title': article['original_title'],
                    'original_description': article['original_description'],
                }}
            )
        except Exception as ex:
            print(ex)
            print('Error in article {}'.format(article['_id']))
            pass

    def fix_article_content(self):
        # articles_without_content_fix = self.article.find({'original_content': {'$exists': False}})
        all_articles = self.article.find()
        for article in all_articles:
            try:
                if 'content' not in article or not article['content']:
                    self.article.delete_one({'_id': article['_id']})
                    continue
                if 'original_content' in article:
                    content = article['original_content']
                else:
                    content = article['content']
                    article['original_content'] = content

                if 'original_title' in article:
                    title = article['original_title']
                else:
                    title = article['title']
                    article['original_title'] = title

                if 'original_description' in article:
                    description = article['original_description']
                else:
                    description = article['description']
                    article['original_description'] = description

                content = self.delete_trash_from_article_content(content)
                article['content'] = content
                title = self.delete_trash_from_article_content(title)
                article['title'] = self.delete_trash_from_article_content(title)
                description = self.delete_trash_from_article_content(description)
                article['description'] = self.delete_trash_from_article_content(description)

                self.article.update_one(
                    {'_id': article['_id']},
                    {'$set': {
                        'content': article['content'],
                        'title': article['title'],
                        'description': article['description'],
                        'original_content': article['original_content']
                    }}
                )
            except Exception as ex:
                print(ex)
                print('Error in article {}'.format(article['_id']))
                pass

    def dev_find_article_ids_with_tag_length_more_than_length(self, params):
        length = params['length']

        articles_ids = list(self.entity.aggregate([
            {"$addFields": {
                "tags": {"$objectToArray": "$tags"}
            }},
            {"$unwind": "$tags"},
            {"$unwind": "$tags.v"},
            {'$project': {"phrase_length": {'$strLenCP': "$tags.v.word"}, 'article_id': '$article_id'}},
            {'$match': {"phrase_length": {'$gt': length}}},
            {'$project': {'article_id': '$article_id'}}
        ]))

        return articles_ids

    def dev_update_sources_by_one_article(self, params):
        _id = params['_id']
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        source_name = self.article.find_one({'_id': _id, 'source.id': None}, {'source.name': 1})

    def fix_original_fields(self, params):
        list_of_articles = params['article_ids']
        for article_id in list_of_articles:
            if not isinstance(article_id, ObjectId):
                article_id = ObjectId(article_id)
            article = self.article.find_one({'_id': article_id})
            article_hash = article['hash']
            date = article['publishedAt']
            q = article['original_content'].split(' ')[0]
            articles, tc, st = NewsCollection.get_everything(q, 'en', from_date=date, to_date=date)
            new_articles_hash = articles.copy()
            for ns in new_articles_hash:
                hasher = hashlib.md5()
                hasher.update(json.dumps(ns).encode('utf-8'))
                ns_hash = hasher.hexdigest()
                if ns_hash == article_hash:
                    article['original_content'] = ns['content']
                    article['original_title'] = ns['title']
                    article['original_description'] = ns['description']
                    article['content'] = self.delete_trash_from_article_content(ns['content'])
                    article['title'] = self.delete_trash_from_article_content(ns['title'])
                    article['description'] = self.delete_trash_from_article_content(ns['description'])
                    self.article.update_one({'hash': article_hash}, {'$set': article}, upsert=True)

    def update_article_list_one_q(self, q, language, new_articles):
        new_articles_hash = new_articles.copy()
        new_hash_list = []
        for ns in new_articles_hash:
            hasher = hashlib.md5()
            hasher.update(json.dumps(ns).encode('utf-8'))
            ns['hash'] = hasher.hexdigest()
            new_hash_list.append(ns['hash'])
            ns['original_content'] = ns['content']
            ns['original_title'] = ns['title']
            ns['original_description'] = ns['description']
            ns['content'] = self.delete_trash_from_article_content(ns['content'])
            ns['title'] = self.delete_trash_from_article_content(ns['title'])
            ns['description'] = self.delete_trash_from_article_content(ns['description'])

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
            if source and 'unofficial' in source:
                if source['unofficial']:
                    article['source']['id'] = source['id']
                else:
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

    def get_q_article_list(self, params):
        if 'used_filter_phrase' not in params:
            # raise EnvironmentError('Request must contain \'used_filter_phrase\' field')
            q = self.phrase.find({}, {'phrase': 1})
            q = [x['phrase'] for x in q]
        else:
            q = params['used_filter_phrase']
            # Convert str to list
            if not isinstance(q, list):
                q = [q]

        # case_sensitive = True
        # if 'case_sensitive' in params:
        #     case_sensitive = params['case_sensitive']
        # if not case_sensitive:
        #     q = [x.lower() for x in q]

        q = [x.lower() for x in q]

        search_param = dict()

        if 'source_id' in params:
            params['id'] = params.pop('source_id')

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

        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']

        article_pipeline = [
            {'$project': {
                'q': {'$toLower': "$q"},
                'articles': '$articles'
            }},
            {'$match': {
                'q': {'$in': q}
            }},
            {'$unwind': '$articles'},
            {'$project': {
                'article_ids': '$articles',
                '_id': 0
            }},
            {'$lookup': {
                'from': 'article',
                'localField': 'article_ids',
                'foreignField': '_id',
                'as': 'articles'
            }},
            {'$project': {
                'articles': '$articles'
            }},
            {'$unwind': '$articles'},
            {'$project': {
                'articles': '$articles',
                'source': '$articles.source'
            }},
            {'$match': search_param},
            {'$replaceRoot': {'newRoot': '$articles'}},
            {'$sort': {'_id': 1}},
            {'$skip': start},
            {'$limit': length + 1}
        ]

        full_articles = list(self.q_article.aggregate(article_pipeline))
        more = True if len(full_articles) > length else False
        return full_articles[:length], more

    def get_article_list_by_tag(self, params):
        if 'tag_word' not in params:
            raise EnvironmentError('Request must contain \'tag_word\' field')

        tag_word = params['tag_word'].lower()  # Case insensitive

        if 'tag' not in params:
            # raise EnvironmentError('Request must contain \'tag\' field')
            tag_match = {'tags.v.word': tag_word}
        else:
            tag = params['tag'].lower()  # Case insensitive

            if tag not in ['person', 'location', 'organization', 'date', 'time', 'misc', 'negative words', 'positive words']:
                raise EnvironmentError("\'Tag\' field must be in one of the words : "
                                       "(person', 'location', 'organization', 'date', 'time', 'misc', 'negative words', 'positive words')")
            tag_match = {'tags.k': tag, 'tags.v.word': tag_word}

        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        language = "en" if "language" not in params else params["language"]
        pipeline = [
            {"$addFields": {
                "tags": {"$objectToArray": "$tags"}
            }},
            {"$unwind": "$tags"},
            {"$unwind": "$tags.v"},
            {'$match': tag_match},
            {'$group': {
                '_id': "$article_id",
            }},
            {'$project': {'article_id': '$_id', '_id': 0}},
            {'$lookup': {
                'from': "article",
                'localField': "article_id",
                'foreignField': "_id",
                'as': "article"
            }},
            {'$unwind': '$article'},
            {'$match': {
                'article.content': {'$ne': None},
                'article.source.language': language
            }},

            {'$project': {
                '_id': 0, 'article_id': '$article._id', 'author': '$article.author', 'title': '$article.title', 'publishedAt': '$article.publishedAt'}},

            {'$sort': {
                'article_id': 1
            }}
        ]

        count_articles = len(list(self.entity.aggregate(pipeline, allowDiskUse=True)))

        pipeline += [
            {'$skip': start},
            {'$limit': length + 1}
        ]

        full_articles = list(self.entity.aggregate(pipeline, allowDiskUse=True))

        for article in full_articles:
            undefined_fields = ['title', 'author']
            for field in undefined_fields:
                if not article[field]:
                    article[field] = '<undefined>'

        more = True if len(full_articles) > length else False
        return full_articles[:length], more, count_articles

    def get_article_by_id(self, params):
        if '_id' not in params:
            raise EnvironmentError('Request must contain \'_id\' field')

        _id = params['_id']

        if not isinstance(_id, ObjectId):
            try:
                _id = ObjectId(_id)
            except (errors.InvalidId, TypeError):
                raise EnvironmentError('\'_id\' field is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string')

        article = self.article.find_one({'_id': _id, 'content': {'$ne': None}}, {'source': 0, 'urlToImage': 0, 'hash': 0, 'original_content': 0,
                                                                                 'original_title': 0, 'original_description': 0})
        if not article:
            raise EnvironmentError('Article with \'_id\' {} does not exist or has empty content'.format(_id))

        undefined_fields = ['title', 'author']
        for field in undefined_fields:
            if not article[field]:
                article[field] = "<undefined>"
        if article:
            tags = self.entity.find_one({'article_id': _id})
            if tags:
                article['tags'] = tags['tags']
            else:
                article['tags'] = {}
            locations = self.entity.find_one({'article_id': _id})
            if locations and ('locations' in locations):
                article['locations'] = locations['locations']
            else:
                article['locations'] = []
            return article
        else:
            raise EnvironmentError('No article with \'_id\' {}'.format(_id))
        #         return list(self.article.aggregate([
#     {
#            '$lookup': {
#                 'from': 'entity',
#                 'localField': '_id',
#                 'foreignField': 'article_id',
#                 'as': 'tags'
#             }
#         },
#               {'$match':
#                   {
#                       '_id': ObjectId('5cef87325350b82f045db467')
#                   }
#               }
# ]))

    # ***************************** Phrases ******************************** #

    def add_default_phrases(self):
        self.add_phrases(params={
            "phrases": ["Puerto Rico", "Puerto Rican"],
            "language": "en"
        })

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
                # upsert=True
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
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        deleted = False
        if params and 'deleted' in params:
            deleted = params['deleted']

        phrases = list(self.phrase.find({'deleted': deleted}).sort('_id', 1).skip(start).limit(length + 1))
        more = True if len(phrases) > length else False
        return phrases[:length], more

    def download_articles_by_phrases(self):
        new_phrases = list(self.phrase.find({'deleted': False, 'to': {'$exists': False}}))
        old_phrases = list(self.phrase.find({'deleted': False, 'to': {'$exists': True}}))

        for phrase in new_phrases:
            _id = phrase['_id']
            q = phrase['phrase']
            language = phrase['language']
            f_articles, _, status = NewsCollection.get_everything(q, language)  # Only first page
            articles = []
            for article in f_articles:
                source_name = article['source']['name']
                if self.check_source(source_name):
                    pass
                else:
                    articles.append(article)
            self.update_article_list_one_q(q, language, articles)
            if articles:
                published_at_list = sorted([article['publishedAt'] for article in articles])
                date_from = published_at_list[0]
                date_to = published_at_list[-1]
                self.phrase.update_one({'_id': _id}, {'$set': {'to': date_to, 'from': date_from, 'updated_all_old_article': False}})

        for phrase in old_phrases:
            _id = phrase['_id']
            q = phrase['phrase']
            language = phrase['language']
            articles, total_count, status = NewsCollection.get_everything(q, language, from_date=phrase['to'])
            for x in range(total_count // 100):
                added, tc, status = NewsCollection.get_everything(q, language, from_date=phrase['to'], page=2+x)
                articles = articles + added
            self.update_article_list_one_q(q, language, articles)
            if articles:
                published_at_list = sorted([article['publishedAt'] for article in articles])
                date_to = published_at_list[-1]
                self.phrase.update_one({'_id': _id}, {'$set': {'to': date_to}})

        self.download_old_articles_by_phrases_while_we_can()

    def download_old_articles_by_phrases_while_we_can(self):
        we_can_download = True
        attempts_left = 500
        phrase_count_to_download = self.phrase.count({'deleted': False, 'updated_all_old_article': False})
        while we_can_download and attempts_left > 0 and phrase_count_to_download > 0:
            attempts_left -= phrase_count_to_download
            for phrase in self.phrase.find({'deleted': False, 'updated_all_old_article': False}):
                _id = phrase['_id']
                q = phrase['phrase']
                language = phrase['language']
                from_date = phrase['from']
                articles, total_count, status = NewsCollection.get_everything(q, language, to_date=from_date)
                if status != 'ok':
                    we_can_download = False
                if status == 'ok' and total_count == 0:
                    self.phrase.update_one({'_id': _id}, {'$set': {'updated_all_old_article': True}})
                self.update_article_list_one_q(q, language, articles)
                if articles:
                    published_at_list = sorted([article['publishedAt'] for article in articles])
                    self.phrase.update_one({'_id': _id}, {'$set': {'from': published_at_list[0]}})

            phrase_count_to_download = self.phrase.count({'deleted': False, 'updated_all_old_article': False})
    # ***************************** Train articles ******************************** #

    def get_location_info_by_id(self, params):
        if '_id' not in params:
            raise EnvironmentError('Request must contain \'_id\' field')
        _id = params['_id']
        _id = ObjectId(_id) if not isinstance(_id, ObjectId) else _id
        return self.location.find_one({'_id': _id})

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
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        language = "en" if "language" not in params else params["language"]

        query = dict()
        query_list = []
        for tag in tags.keys():
            query_list.append({'tags.{0}.word'.format(tag): tags.get(tag).lower()})
        query['$or'] = query_list

        pipeline = [
            {'$match': query},
            {'$lookup': {
                'from': 'article',
                'localField': 'article_id',
                'foreignField': '_id',
                'as': 'article'
            }},
            {'$match': {'article.source.language': language}},
            {'$project': {'article': 0}},
            {'$sort': {'_id': 1}},
            {'$skip': start},
            {'$limit': length + 1}
        ]
        list_to_show = list(self.entity.aggregate(pipeline))
        more = True if len(list_to_show) > length else False
        return list_to_show[:length], more

    def show_source_list(self, params):
        bad = False if 'bad' not in params else params['bad']
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        list_to_show = list(self.source.find({'bad': True})) if bad else list(self.source.find())
        more = True if len(list_to_show) > length else False
        return list_to_show[:length], more

    def remove_dubles_articles_and_entities(self):
        hashes = []
        articles = list(self.article.find({}, {'_id': 1, 'hash': 1}))
        for article in articles:
            if article['hash'] in hashes:
                self.article.delete_one({'_id': article['_id']})
            else:
                hashes.append(article['hash'])

        entities = list(self.entity.find({}, {'_id': 1, 'article_id': 1, 'model': 1}))
        entity_list = []
        for entity in entities:
            if (entity['article_id'], entity['model']) in entity_list:
                self.entity.delete_one({'_id': entity['_id']})
            else:
                entity_list.append((entity['article_id'], entity['model']))

    def tag_stat(self, params):
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        tag_list = ['location', 'person', 'organization', 'money', 'percent', 'date', 'time']
        tag_list += ['money2', "location_names", "location_common_names"]

        tags = params['tag'] if 'tag' in params else tag_list

        if isinstance(tags, str):
            tags = [tags]
        is_only_one_tag = len(tags) == 1
        tags = [tag.lower() for tag in tags]

        for tag in tags:
            if tag not in tag_list:
                raise EnvironmentError('Value of the field "tag" {} must be in {}'.format(tag, tag_list))

        include_articles_without_sources = False if 'include_articles_without_sources' not in params else params["include_articles_without_sources"]
        language = "en" if "language" not in params else params["language"]
        if include_articles_without_sources:
            language_pipeline = []
        else:
            language_pipeline = [
            {'$lookup': {
                'from': 'article',
                'localField': 'article_id',
                'foreignField': '_id',
                'as': 'article'
            }},
            {'$match': {'article.source.language': language}},
            {'$project': {'article': 0}}
        ]
        # RETURN COUNT OF SELECTED TAGS

        # pipeline = [
        #     {'$lookup': {
        #         'from': 'article',
        #         'localField': 'article_id',
        #         'foreignField': '_id',
        #         'as': 'article'
        #     }},
        #     {'$match': {'article.source.language': language}},
        #     {'$project': {'article': 0}},
        #     {"$addFields": {
        #         "tags": {"$objectToArray": "$tags"}
        #     }},
        #     {"$unwind": "$tags"},
        #     {"$unwind": "$tags.v"},
        #     {"$group": {
        #         "_id": {
        #             "tag": "$tags.k",
        #             "phrase": "$tags.v.word"
        #         },
        #         "count": {"$sum": 1}
        #     }},
        #     {'$sort': {'count': -1, '_id.tag': 1, '_id.phrase': 1}},
        #     {'$match': {'_id.tag': {'$in': tags}}}
        # ]

        # RETURN COUNT OF ARTICLE WHICH CONTAIN SELECTED TAGS
        pipeline = language_pipeline
        pipeline += [
            {"$addFields": {
                "tags": {"$objectToArray": "$tags"}
            }},

            {"$unwind": "$tags"},
            {"$unwind": "$tags.v"},
            {'$match': {'tags.k': {'$in': tags}}},
            {"$group": {
                "_id": {
                    "tag": "$tags.k",
                    "phrase": "$tags.v.word",
                    "article_id": "$article_id"
                }
            }},
            {"$group": {
                "_id": {
                    "tag": "$_id.tag",
                    "phrase": "$_id.phrase"
                },
                "count": {"$sum": 1},
            }},
        ]

        debug_sort = False if 'debug_sort' not in params else params['debug_sort']
        if debug_sort:
            pipeline += [
                {'$project': {"phrase_length": {'$strLenCP': "$_id.phrase"}, "count": "$count"}},
                {'$sort': {'phrase_length': -1, 'count': -1, '_id.tag': 1, '_id.phrase': 1}}
            ]
        else:
            pipeline += [{'$sort': {'count': -1, '_id.tag': 1, '_id.phrase': 1}}]

        pipeline += [{'$skip': start}]
        more = True if len(list(self.entity.aggregate(pipeline, allowDiskUse=True))) > length else False
        pipeline += [{'$limit': length}]

        if is_only_one_tag:
            pipeline += [
                {"$group": {
                    "_id": "$_id.tag",
                    "tag_list": {
                        "$push": {
                            "count": "$count",
                            "phrase": "$_id.phrase"
                        }
                    }
                }},
                {'$project': {'tag': '$_id', 'tag_list': 1, '_id': 0}},
                # {'$replaceRoot': {'newRoot': '$tag_list'}}
            ]
        else:
            if debug_sort:
                pipeline += [
                    {'$project': {
                        'tag': '$_id.tag', "phrase": "$_id.phrase", "phrase_length": "$phrase_length", "count": "$count", "_id": 0
                    }},
                ]
            else:
                pipeline += [
                    {'$project': {
                        'tag': '$_id.tag', "phrase": "$_id.phrase", "count": "$count", "_id": 0
                    }},
                ]
        return list(self.entity.aggregate(pipeline, allowDiskUse=True)), more

    def show_tagged_article_list(self, params):
        search_param = dict()
        status = 'tagged' if 'status' not in params else params['status']
        start = 0 if 'start' not in params else params['start']
        length = 10 if 'length' not in params else params['length']
        language = "en" if "language" not in params else params["language"]

        trained = self.entity.count({'trained': True})
        untrained = self.entity.count({'trained': False})
        search_param['trained'] = True if status == 'tagged' else False

        pipeline = [
            {'$match': search_param},
            {'$lookup': {
                'from': 'article',
                'localField': 'article_id',
                'foreignField': '_id',
                'as': 'article'
            }},
            {'$match': {'article.source.language': language}},
            {'$project': {'article': 0}},
            {'$sort': {'_id': 1}},
            {'$skip': start},
            {'$limit': length + 1}
        ]

        articles = list(self.entity.aggregate(pipeline))
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

    def show_category(self, params):
        raise Exception("Function in progress")
