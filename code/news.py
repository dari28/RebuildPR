from news_const import API_KEY, TOP_HEADLINES_URL, EVERYTHING_URL, SOURCES_URL
import requests


def counted(f):
    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return f(*args, **kwargs)
    wrapped.calls = 0
    return wrapped


class NewsCollection:
    @staticmethod
    def get_calls():
        return NewsCollection.get_sources.calls + NewsCollection.get_everything.calls

    @staticmethod
    @counted
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
    @counted
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
            url = '{}?q={}&apiKey={}'.format(EVERYTHING_URL, q, API_KEY)
            response = requests.get(url)
            json = response.json()
            status = json["status"]
            if status == 'ok':
                everything_list.extend(json["articles"])
            else:
                errors.append(json["message"])
        except Exception as ex:
            raise EnvironmentError("Error occurs in get_everything: {}".format(ex))
        return everything_list, errors

    @staticmethod
    @counted
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
