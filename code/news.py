from news_const import API_KEY, TOP_HEADLINES_URL, EVERYTHING_URL, SOURCES_URL
import requests
from datetime import datetime, timedelta


# def counted(f):
#     def wrapped(*args, **kwargs):
#         wrapped.calls += 1
#         return f(*args, **kwargs)
#     wrapped.calls = 0
#     return wrapped


def add_second(str_datatime):
    a = datetime.strptime(str_datatime, "%Y-%m-%dT%H:%M:%SZ")
    return (a + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def remove_second(str_datatime):
    a = datetime.strptime(str_datatime, "%Y-%m-%dT%H:%M:%SZ")
    return (a - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


class NewsCollection:
    @staticmethod
    def get_calls():
        return NewsCollection.get_sources.calls + NewsCollection.get_everything.calls

    @staticmethod
    # @counted
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
    # @counted
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

            datetime.strptime(from_date, '%b %d %Y %I:%M%p')
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
    # @counted
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
