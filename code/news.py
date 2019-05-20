from news_const import HISTORY_SOURCES_DIR, HISTORY_NEWS_DIR, DAYS_TO_UPDATE_SOURCES, API_KEY, TOP_HEADLINES_URL, EVERYTHING_URL, SOURCES_URL, MONGO_URL
import requests

class NewsException(Exception):
    pass


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
       # print("Error occurs in get_everything: {}".format(ex))
        raise EnvironmentError("Error occurs in get_everything: {}".format(ex))
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
    # models = ['crf_english_3class', 'crf_english_4class', 'crf_english_7class', 'crf_chinese_7class', 'crf_german_7class', 'crf_spanish_4class',
    #           'crf_france_3class']
    # classifier_dict = dict()
    # for model in models:
    #     model = tools.get_abs_path(STANFORD[model])
    #     model = model if isinstance(model, str) else model.encode('utf8')
    #     if model not in classifier_dict:
    #         classifier_dict[model] = stanford.CRFClassifier.getClassifier(stanford.jString(model))
    #     classifier = classifier_dict[model]
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
    result = get_tags(test_article, 'es')
    print(result)
    #########ADD struct for matching########
    result2 = list()
    for elems in result:
        for elem in elems:
            word = elem['word']
            tag = elem['tag']
            if not (word in [x['word'] for x in result2] and tag in [x['tag'] for x in result2]):
                result2.append({'word': word, 'tag': tag, 'matches': []})
            match = {
                'start_match': elem['start_match'],
                'length_match': elem['length_match']
            }
            for x in result2:
                if x['tag'] == tag and x['word'] == word:
                    if match in x['matches']:
                        continue
                    else:
                        x['matches'].append(match)
    print(result2)
    ######ADD filter#########################
    result_filter = list()
    for x in result2:
        if x['tag'] == 'PERSON':
            result_filter.append(x)
    print(nc.db_history_sources)
    print(nc.db_history_news)
    #print(nc.get_available_sources(language=None))
    # headliners_without_empties = [x for x in headliners if x]


