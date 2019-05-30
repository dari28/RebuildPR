import requests
from datetime import datetime, timedelta

API_KEY = 'aa5ed9dc9edb4b49b3fe02edc73eca22'  # '886e070469344e0381be2fc5cdf24830'

TOP_HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'
EVERYTHING_URL = 'https://newsapi.org/v2/everything'
SOURCES_URL = 'https://newsapi.org/v2/sources'

countries = {
    'ae', 'ar', 'at', 'au', 'be', 'bg', 'br', 'ca', 'ch', 'cn', 'co', 'cu', 'cz', 'de', 'eg', 'fr', 'gb', 'gr', 'hk',
    'hu', 'id', 'ie', 'il', 'in', 'it', 'jp', 'kr', 'lt', 'lv', 'ma', 'mx', 'my', 'ng', 'nl', 'no', 'nz', 'ph', 'pl',
    'pt', 'ro', 'rs', 'ru', 'sa', 'se', 'sg', 'si', 'sk', 'th', 'tr', 'tw', 'ua', 'us', 've', 'za'
}

languages = {'ar', 'en', 'cn', 'de', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'sv', 'ud'}

categories = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}

sort_method = {'relevancy', 'popularity', 'publishedAt'}


def add_second(str_datatime):
    a = datetime.strptime(str_datatime, "%Y-%m-%dT%H:%M:%SZ")
    return (a + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def remove_second(str_datatime):
    a = datetime.strptime(str_datatime, "%Y-%m-%dT%H:%M:%SZ")
    return (a - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


class NewsCollection:
    @staticmethod
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
            url = '{}?q={}&apiKey={}'.format(TOP_HEADLINES_URL, q, API_KEY)
            response = requests.get(url)
            json = response.json()
            status = json["status"]
            if status == 'ok':
                headline_list.extend(json["articles"])
            else:
                errors.append(json["message"])
        except Exception as ex:
            raise EnvironmentError("Error occurs in get_top_headliners: {}".format(ex))
        return headline_list, errors

    @staticmethod
    def get_everything(q, language='en', page=1, from_date=None, to_date=None):
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
        try:
            articles = []
            total_results = 0

            from_date_str = '&from={}'.format(add_second(from_date)) if from_date else ''
            to_date_str = '&to={}'.format(remove_second(to_date)) if to_date else ''
            url = '{}?q={}&language={}&pageSize=100&page={}{}{}&apiKey={}'.format(EVERYTHING_URL, q, language, page, from_date_str, to_date_str, API_KEY)
            response = requests.get(url)
            json = response.json()
            status = json["status"]
            if status == 'ok':
                articles = json["articles"]
                total_results = json["totalResults"]
            # else:
            #     error = json["message"]
        except Exception as ex:
            raise EnvironmentError("Error occurs in get_everything: {}".format(ex))
        return articles, total_results, status

    @staticmethod
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
            url = '{}?q={}&apiKey={}'.format(SOURCES_URL, q, API_KEY)
            response = requests.get(url)
            json = response.json()
            status = json["status"]
            if status == 'ok':
                sources.extend(json["sources"])
            else:
                errors.append(json["message"])
        except Exception as ex:
            raise EnvironmentError("Error occurs in get_sources: {}".format(ex))
        return sources, errors
