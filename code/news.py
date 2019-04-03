from newsapi import NewsApiClient
from newsapi import const
import news_const
import requests
import json
from datetime import datetime, timedelta


class NewsException(Exception):
    pass


# TO_DO: save results to file in "data" directory
def write_sources_to_history(data):
    write_to_history(data, news_const.HISTORY_SOURCES_DIR)


def write_news_to_history(data):
    write_to_history(data, news_const.HISTORY_NEWS_DIR)


def write_to_history(data, filename):
    try:
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    except IOError as err:
        print("Can't write to file {}. \nError: {}".format(filename, err))
        pass


def read_history_sources():
    return read_history(news_const.HISTORY_SOURCES_DIR)


def read_history_news():
    return read_history(news_const.HISTORY_NEWS_DIR)


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
        self.history_sources = read_history_sources()
        self.history_news = read_history_news()
        if not self.history_sources:
            self.history_sources = dict()
            self.history_sources['sources'] = []
            self.history_sources['date'] = "0000-00-00"

    def filter_sources(self, country=None, language=None):
        """
        Return sources from history_date filtered by arguments
        :param countries: Can be list, str, None
        :param languages: Can be list, str, None
        :return: sources(list)
        """
        sources = self.history_sources['sources']
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
        now_week_ago = (datetime.today() - timedelta(days=news_const.DAYS_TO_UPDATE_SOURCES)).strftime("%Y-%m-%d")#.strftime("%Y-%m-%d %H:%M:%S")

        if now_week_ago >= self.history_sources['date']:
            self.history_sources['sources'] = get_sources("")
            self.history_sources['date'] = datetime.today().strftime("%Y-%m-%d")
            write_to_history(self.history_sources)
        #filter by language and country
        return self.filter_sources(country=country, language=language)
        #shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}

    def get_articles(self):
        #TO_DO: Add
        raise EnvironmentError


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
        #url = ('{}?category={}&apiKey={}').format(const.TOP_HEADLINES_URL, category, API_KEY)
        url = ('{}?q={}&apiKey={}').format(const.TOP_HEADLINES_URL, q, API_KEY)
        response = requests.get(url)
        json = response.json()
        status = json["status"]
        if status == 'ok':
            headline_list.extend(json["articles"])
        else:
            errors.extend(json["message"])
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
        url = ('{}?q={}&apiKey={}').format(const.EVERYTHING_URL, q, API_KEY)
        response = requests.get(url)
        json = response.json()
        status = json["status"]
        if status == 'ok':
            everything_list.extend(json["articles"])
        else:
            errors.extend(json["message"])
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
        url = ('{}?q={}&apiKey={}').format(const.SOURCES_URL, q, API_KEY)
        response = requests.get(url)
        json = response.json()
        status = json["status"]
        if status == 'ok':
            sources.extend(json["sources"])
        else:
            errors.extend(json["message"])
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
    get_sources(q)
    result, errors = get_everything(q)
    if errors:
        print(errors)

    print(result)

if __name__ == "__main__":
    # headliners, errors = get_top_headliners()
    #search_news("Port")
    nc = NewsCollector()
    print(nc.get_available_sources(language=None))
    # headliners_without_empties = [x for x in headliners if x]


