from news_const import HISTORY_SOURCES_DIR, HISTORY_NEWS_DIR, DAYS_TO_UPDATE_SOURCES, API_KEY, TOP_HEADLINES_URL, EVERYTHING_URL, SOURCES_URL, MONGO_URL
import requests
import json
from datetime import datetime, timedelta
import hashlib
from pymongo import MongoClient
#from polyglot.text import Text, Word
from install_polyglot import install
from install_stanford import predict_entity_stanford_default, predict_entity_stanford, add_standford_default
from lib import tools, text
class NewsException(Exception):
    pass



# TO_DO: save results to file in "data" directory
def write_sources_to_history(data):
    write_to_history(data, HISTORY_SOURCES_DIR)


def write_news_to_history(data):
    write_to_history(data, HISTORY_NEWS_DIR)


def write_to_history(data, filename):
    try:
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    except IOError as err:
        print("Can't write to file {}. \nError: {}".format(filename, err))
        pass


def read_history_sources():
    return read_history(HISTORY_SOURCES_DIR)


def read_history_news():
    return read_history(HISTORY_NEWS_DIR)


def read_history(filename):
    try:
        with open(filename, 'r') as outfile:
            data = json.load(outfile)
    except IOError as err:
        print("Can't read the file {}. \nError: {}".format(filename, err))
        data = []
        pass
    return data


class NewsCollector:
    """
    Class for collecting news from news sources
    Structure of elements:
    date(str)
    sources(list)
    ----category(str)
    ----country(str)
    ----description(str)
    ----id(str)
    ----language(str)
    ----name(str)
    ----url(str)
    """
    def __init__(self):
        #self.history_sources = read_history_sources()
        self.db = MongoClient(MONGO_URL).news_collector
        #if ("news" in self.db.list_collection_names()):
        self.db_history_news = self.read_history_news_from_db()
        self.db_history_sources = self.read_history_sources_from_db()
        if not self.db_history_sources:
            self.db_history_sources = dict()
            self.db_history_sources['sources'] = {}
            self.db_history_sources['date'] = "0000-00-00"

        if not self.db_history_news:
            self.db_history_news = list()

        #self.history_news = read_history_news()
        #self.history_sources = read_history_sources()
        #self.history_news = read_history_news()

        #if not self.history_sources:
        #    self.history_sources = dict()
        #    self.history_sources['sources'] = []
        #    self.history_sources['date'] = "0000-00-00"

        #if not self.history_news:
            #self.history_news = list()
            #self.history_news =

    def filter_sources(self, country=None, language=None):
        """
        Return sources from history_date filtered by arguments
        :param countries: Can be list, str, None
        :param languages: Can be list, str, None
        :return: sources(list)
        """
        sources = self.db_history_sources['sources']
        if not country and not language:
            return sources
        countries = list(country) if isinstance(country, str) else country
        languages = list(language) if isinstance(language, str) else language
        sources = [x for x in sources
                   if (not countries or x['country'] in countries) and (not languages or x['language'] in languages)]
        return sources

    def get_available_sources(self, language=None, country=None):
        """
        Return available_sources from history_data or request(when data is not actual).
        """
        #If date older than a week we update history_data
        now_week_ago = (datetime.today() - timedelta(days=DAYS_TO_UPDATE_SOURCES)).strftime("%Y-%m-%d")#.strftime("%Y-%m-%d %H:%M:%S")

        #if now_week_ago >= self.history_sources['date']:
        if now_week_ago >= self.db_history_sources['date']:
            #self.history_sources['sources'] = get_sources("")
            #self.history_sources['date'] = datetime.today().strftime("%Y-%m-%d")
            self.db_history_sources['sources'], _ = get_sources("")
            self.db_history_sources['date'] = datetime.today().strftime("%Y-%m-%d")
            #write_sources_to_history(self.history_sources)
            self.write_history_sources_from_db(self.db_history_sources)
        else:
            #self.history_sources = self.read_history_sources_from_db()
            self.db_history_sources = self.read_history_sources_from_db()
        #filter by language and country
        return self.filter_sources(country=country, language=language)
        #shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}

    # def get_available_news(self, q):
    #     self.db_history_news['sources'], _ = get_everything(q)
    #     self.db_history_news['date'] = datetime.today().strftime("%Y-%m-%d")

    def get_articles(self, q):
        #TO_DO: make link with sources
        articles, errors = get_everything(q)
        if errors:
            print(errors)
            return
        now = datetime.today().strftime("%Y-%m-%d")
        #Found the article and get md5 hash
        #TO_DO: Add this as key
        hasher = hashlib.md5()
        hasher.update(json.dumps(articles).encode('utf-8'))
        hash_hex = hasher.hexdigest()
        isFound = False
        for new in self.db_history_news:
            if hash_hex == new['hash']:
                isFound = True

        if not isFound:
            articles_dict = dict()
            articles_dict['articles'] = articles
            articles_dict['date'] = now
            articles_dict['q'] = q
            articles_dict['hash'] = hash_hex
            self.db_history_news.append(articles_dict)
            self.write_history_news_from_db(articles_dict)          #insert_one
            #self.write_history_news_from_db(self.db_history_news)  #insert_many

        return self.db_history_news

    # def get_articles(self, q):
    #     articles, errors = get_everything(q)
    #     if errors:
    #         print(errors)
    #         return
    #     now = datetime.today().strftime("%Y-%m-%d")
    #     #Found the article and get md5 hash
    #     #TO_DO: Add this as key
    #     hasher = hashlib.md5()
    #     hasher.update(articles)
    #     result = hasher.hexdigest()
    #     isFound = False
    #     for new in self.history_news:
    #         if result == hasher.hexdigest(new['articles']):
    #             new['articles'] = articles
    #             isFound = True
    #     if not isFound:
    #         self.history_news['articles'] = articles
    #         self.history_news['date'] = now
    #         self.history_news['q'] = q
    #     #if
    #     articles_dict = dict()
    #     articles_dict['articles'] = articles
    #     articles_dict['date'] = now
    #     articles_dict['q'] = q
    #     return articles

    #def get filtered_article()
    def read_history_news_from_db(self):
        cursor = self.db['articles'].find()
        ret_list = list()
        for c in cursor:
            ret_list.append(c)
        return ret_list

    def read_history_sources_from_db(self):
        return self.db['sources'].find_one()
        # ret_list = list()
        # for c in cursor:
        #     ret_list.append(c)
        # return ret_list

    def write_history_news_from_db(self, data):
        #self.db['articles'].update_many({}, {"$set":data}, upsert=True)
        # for d in data:
        #     self.db['articles'].insert_one(d)
        self.db['articles'].insert_one(data)

    def write_history_sources_from_db(self, data):
        self.db['sources'].insert_one(data)


def get_top_headliners(q):
    """
    Original TOP_HEADLINES_URL request required any of the following parameters: sources, q, language, country, category.
    So need to go through the one of this list. List "category" is the shortest
    :return:
    status(str)                 contain ['ok','error']
    message(str)                if status.error
    code(str)                   if status.error
    totalResults(int)           if status.ok
    articles(list)              if status.ok
    ----author(str)
    ----content(str)
    ----description(str)
    ----publishedAt(str)
    ----source(dict)
    --------id(str)
    --------name(str)
    ----title(str)
    ----url(str)
    ----urlToImage(str)
    """
    headline_list = []
    errors = []
    try:
        #url = ('{}?category={}&apiKey={}').format(const.TOP_HEADLINES_URL, category, new_const.API_KEY)
        url = ('{}?q={}&apiKey={}').format(TOP_HEADLINES_URL, q, API_KEY)
        response = requests.get(url)
        json = response.json()
        status = json["status"]
        if status == 'ok':
            headline_list.extend(json["articles"])
        else:
            errors.append(json["message"])
    except Exception as ex:
        print("Error occurs in get_top_headliners: {}".format(ex))
        raise NewsException
    return headline_list, errors


def get_everything(q):
    """
        Original EVERYTHING_URL request required any of the following parameters: sources, q, language, country, category.
        We you field "q"(search words)
        :return:
        status(str)                 contain ['ok','error']
        message(str)                if status.error
        code(str)                   if status.error
        totalResults(int)           if status.ok
        articles(list)              if status.ok
        ----author(str)
        ----content(str)
        ----description(str)
        ----publishedAt(str)
        ----source(dict)
        --------id(str)
        --------name(str)
        ----title(str)
        ----url(str)
        ----urlToImage(str)
    """
    everything_list = []
    errors = []
    try:
        url = ('{}?q={}&apiKey={}').format(EVERYTHING_URL, q, API_KEY)
        response = requests.get(url)
        json = response.json()
        status = json["status"]
        if status == 'ok':
            everything_list.extend(json["articles"])
        else:
            errors.append(json["message"])
    except Exception as ex:
        print("Error occurs in get_everything: {}".format(ex))
        raise NewsException
    return everything_list, errors


def get_sources(q):
    """
        Original EVERYTHING_URL request required any of the following parameters: sources, q, language, country, category.
        We you field "q"(search words)
        :return:
        status(str)                 contain ['ok','error']
        message(str)                if status.error
        code(str)                   if status.error
        sources(list)               if status.ok
        ----category(str)
        ----country(str)
        ----description(str)
        ----id(str)
        ----language(str)
        ----name(str)
        ----url(str)
    """
    sources = []
    errors = []
    try:
        url = ('{}?q={}&apiKey={}').format(SOURCES_URL, q, API_KEY)
        response = requests.get(url)
        json = response.json()
        status = json["status"]
        if status == 'ok':
            sources.extend(json["sources"])
        else:
            errors.append(json["message"])
    except Exception as ex:
        print("Error occurs in get_sources: {}".format(ex))
        raise NewsException
    return sources, errors


def search_news(q, sources, languages, country, category):
    """
    For updating we use the construction with field:
    q(str): search word what we search
    last_search_date: date of the last search
    data: information what we find
    *ADD data fields*

    :param q:
    :param sources:
    :param languages:
    :param country:
    :param category:
    :return:
    """

    result, errors = get_everything(q)
    if errors:
        print(errors)

    print(result)


set_polyglot_entity = set(['I-LOC', 'I-PER', 'I-ORG'])


if __name__ == "__main__":
    # headliners, errors = get_top_headliners()
    #search_news("Port")
    nc = NewsCollector()
    # a = get_sources("")
    # b = get_sources("Rus")
    # c = get_sources("Android")
    # d = get_sources("My own name lang")
    #a = get_everything(q="Rico")
    #b = get_everything(q=" porte")
    #print(a)
    #print(b)
    #Create MongoConnection

    #nc.read_history_sources_from_db()
    #print(a)
    install() #Already do this
    matches = []
   # nc.get_available_sources()
   # articles = nc.get_articles("puerto rico")

    test_article = "Puerto mocha Rico. Eddie Rosario, the Minnesota Twins left fielder, can’t remember the exact year, but he was a youth baseball player in his native Puerto Rico when he was given the choice of two jerseys: No. 21 or another number. \
    “I’m not Roberto Clemente,” said Rosario, 27, who now wears one of the next-closest options, No. 20. “I can’t wear that.”\
    No. 21 is sacred in baseball, particularly to Puerto Ricans, because it was the longtime number of Clemente, the iconic player who hailed from the island. Even as a youngster in Guayama, Rosario knew of Clemente’s importance, which led him to join the majority of Puerto Rican major leaguers in doing something that Major League Baseball hasn’t: decline the use of No. 21 in an effort to essentially retire it.\
    Of the 235 Puerto Rico-born players who have appeared in the major leagues since Clemente’s death 47 years ago, only 16 have used No. 21 — and none in the past five seasons, according to Baseball Reference.\
    Advertisement\
    “That’s very powerful,” said Luis Clemente, 52, one of Roberto Clemente’s sons.\
    In addition to Roberto Clemente’s accomplishments on the field — a 15-time All-Star, 12-time Gold Glove Award winner, two-time World Series champion with the Pittsburgh Pirates and member of the 3,000-hit club — he was a fierce advocate for Latino players and against Jim Crow segregation. A year after he died in a plane crash on Dec. 31, 1972, while escorting earthquake relief from Puerto Rico to Nicaragua, Clemente became the first player from Latin America inducted into the Baseball Hall of Fame.\
    On Monday and Tuesday, Major League Baseball celebrated Jackie Robinson, who broke the color barrier in baseball on April 15, 1947, by having every player wear his No. 42 jersey, which was retired in 1997 and remains the only one to receive that special honor by all 30 teams. Many Puerto Ricans believe the same M.L.B.-wide retirement should also go to Clemente, who also made his major league debut this week, on April 17, 1955."
    #

    # for article in articles:
    #     for art in article['articles']:
    #         #art_text = text.Text()
    #         if not art['content']:
    #             continue
    #         print(art['content'])
    #         polyglot_text = text.Text(art['content'], hint_language_code='es', split_apostrophe=True)
    #         print("****ARTICLE*****")
    #         print(polyglot_text.entities)
    #         print("**************************")
    #         # tag_entities = set_polyglot_entity#.intersection('I-LOC')
    #         # if len(tag_entities) > 0:
    #         #     parser_iter = tools.ParsePolyglot(polyglot_text.entities, tag_entities, art['content'], polyglot_text)
    #         #     for match in parser_iter:
    #         #         matches.append(match)
    #         for sent in polyglot_text.sentences:
    #             print(sent, "\n")
    #             for entity in sent.entities:
    #                 print(entity.tag, entity)
    #         print("*************END**********")
    #predict_entity_stanford_default({
    entities = add_standford_default()
    result = predict_entity_stanford(
        # {
        # "language":"en",
        # "type":"stanford_crf",
        # "name":"example entity",
        # "model_settings":{},
        # "description":"Example for creating an entity "
        #             },

            # [
            #     {"_id": "5aaa494edf790d0d3cb45044", "available": True, "training": "finished", "user": "303030303030303030306573",
            #      "language": "es", "description": "Trained model of CRF, defining misc data", "model": "crf_spanish_4class", "model_settings": {"tag": "OTROS"},
            #      "type": "default_stanford", "name": "Detecta otros"},
            #     {"_id": "5aaa494edf790d0d3cb45045", "available": True, "training": "finished", "user": "303030303030303030306573",
            #      "language": "es", "description": "Trained model of CRF, defining personality", "model": "crf_spanish_4class",
            #      "model_settings": {"tag": "PERS"}, "type": "default_stanford", "name": "Detecta pers"},
            #     {"_id": "5aaa494edf790d0d3cb45046", "available": True, "training": "finished", "user": "303030303030303030306573",
            #      "language": "es", "description": "Trained model of CRF, defining organizations", "model": "crf_spanish_4class",
            #      "model_settings": {"tag": "ORG"}, "type": "default_stanford", "name": "Detecta org"},
            #     {"_id": "5aaa494edf790d0d3cb45047", "available": True, "training": "finished", "user": "303030303030303030306573",
            #      "language": "es", "description": "Trained model of CRF, defining places", "model": "crf_spanish_4class", "model_settings": {"tag": "LUG"},
            #      "type": "default_stanford", "name": "Detecta lug"},
            #     {"_id": "5aaa494edf790d0d3cb45027", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining organizations (different models were trained on different data, so their results can vary)\nExample:\n\tText: The United Nations (UN) is an intergovernmental organization tasked to promote international cooperation and to create and maintain international order.\n\tFound matches: United Nations, UN",
            #      "model": "crf_english_3class", "model_settings": {"tag": "ORGANIZATION"}, "type": "default_stanford", "name": "Detects organization (model 1)"},
            #     {"_id": "5aaa494edf790d0d3cb45028", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining places (different models were trained on different data, so their results can vary)\nExample:\n\tText: Australia' s insolation greatly exceeds the average values in Europe, Russia, and most of North America.\n\tFound matches: Australia, Europe, Russia, North America",
            #      "model": "crf_english_3class", "model_settings": {"tag": "LOCATION"}, "type": "default_stanford", "name": "Detects location (model 1)"},
            #     {"_id": "5aaa494edf790d0d3cb45029", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining personality (different models were trained on different data, so their results can vary)\nExample:\n\tText: In 1905, Albert Einstein published a special theory of relativity.\n\tFound matches: Albert Einstein",
            #      "model": "crf_english_3class", "model_settings": {"tag": "PERSON"}, "type": "default_stanford", "name": "Detects person (model 1)"},
            #     {"_id": "5aaa494edf790d0d3cb4502a", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining organizations (different models were trained on different data, so their results can vary)\nExample:\n\tText: The United Nations (UN) is an intergovernmental organization tasked to promote international cooperation and to create and maintain international order.\n\tFound matches: United Nations, UN",
            #      "model": "crf_english_4class", "model_settings": {"tag": "ORGANIZATION"}, "type": "default_stanford", "name": "Detects organization (model 2)"},
            #     {"_id": "5aaa494edf790d0d3cb4502b", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining places (different models were trained on different data, so their results can vary)\nExample:\n\tText: Australia' s insolation greatly exceeds the average values in Europe, Russia, and most of North America.\n\tFound matches: Australia, Europe, Russia, North America",
            #      "model": "crf_english_4class", "model_settings": {"tag": "LOCATION"}, "type": "default_stanford", "name": "Detects location (model 2)"},
            #     {"_id": "5aaa494edf790d0d3cb4502c", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining personality (different models were trained on different data, so their results can vary)\nExample:\n\tText: In 1905, Albert Einstein published a special theory of relativity.\n\tFound matches: Albert Einstein",
            #      "model": "crf_english_4class", "model_settings": {"tag": "PERSON"}, "type": "default_stanford", "name": "Detects person (model 2)"},
            #     {"_id": "5aaa494edf790d0d3cb4502d", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining misc data\nExample:\n\tText: President Xi Jinping of China, on his first state visit to the United States, showed off his familiarity with American history and pop culture on Tuesday night.\n\tFound matches: American",
            #      "model": "crf_english_4class", "model_settings": {"tag": "MISC"}, "type": "default_stanford", "name": "Detects misc"},
            #     {"_id": "5aaa494edf790d0d3cb4502e", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining organizations (different models were trained on different data, so their results can vary)\nExample:\n\tText: The United Nations (UN) is an intergovernmental organization tasked to promote international cooperation and to create and maintain international order.\n\tFound matches: United Nations",
            #      "model": "crf_english_7class", "model_settings": {"tag": "ORGANIZATION"}, "type": "default_stanford", "name": "Detects organization (model 3)"},
            #     {"_id": "5aaa494edf790d0d3cb4502f", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining places (different models were trained on different data, so their results can vary)\nExample:\n\tText: Australia' s insolation greatly exceeds the average values in Europe, Russia, and most of North America.\n\tFound matches: Australia, Europe, Russia, North America",
            #      "model": "crf_english_7class", "model_settings": {"tag": "LOCATION"}, "type": "default_stanford", "name": "Detects location (model 3)"},
            #     {"_id": "5aaa494edf790d0d3cb45030", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining personality (different models were trained on different data, so their results can vary)\nExample:\n\tText: In 1905, Albert Einstein published a special theory of relativity.\n\tFound matches: Albert Einstein",
            #      "model": "crf_english_7class", "model_settings": {"tag": "PERSON"}, "type": "default_stanford", "name": "Detects person (model 3)"},
            #     {"_id": "5aaa494edf790d0d3cb45031", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining the dates\nExample:\n\tText: President Xi Jinping of China, on his first state visit to the United States, showed off his familiarity with American history and pop culture on Tuesday night.\n\tFound matches: Tuesday",
            #      "model": "crf_english_7class", "model_settings": {"tag": "DATE"}, "type": "default_stanford", "name": "Detects date"},
            #     {"_id": "5aaa494edf790d0d3cb45032", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining finances\nExample:\n\tText: Venezuela president offers pregnant women $3.83 a month.\n\tFound matches: $3.83",
            #      "model": "crf_english_7class", "model_settings": {"tag": "MONEY"}, "type": "default_stanford", "name": "Detects money"},
            #     {"_id": "5aaa494edf790d0d3cb45033", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining percent\nExample:\n\tText: The budget of our city has grown by 20 percent.\n\tFound matches: 20 percent",
            #      "model": "crf_english_7class", "model_settings": {"tag": "PERCENT"}, "type": "default_stanford", "name": "Detects percent"},
            #     {"_id": "5aaa494edf790d0d3cb45034", "available": True, "training": "finished", "user": "30303030303030303030656e",
            #      "language": "en",
            #      "description": "Trained model of CRF, defining time\nExample:\n\tText: President Xi Jinping of China, on his first state visit to the United States, showed off his familiarity with American history and pop culture on Tuesday night.\n\tFound matches: night",
            #      "model": "crf_english_7class", "model_settings": {"tag": "TIME"}, "type": "default_stanford", "name": "Detects time"}
            #
            # ],
        entities,
        test_article, 'es')
    print(result)
    print(nc.db_history_sources)
    print(nc.db_history_news)
    #print(nc.get_available_sources(language=None))
    # headliners_without_empties = [x for x in headliners if x]


