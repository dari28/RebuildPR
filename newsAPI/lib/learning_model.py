import re

from lib import tools, stanford_module as stanford
from lib.text import Text
from lib.dictionary import defix_name_field
from lib.mongo_connection import MongoConnection
from lib.linguistic_functions import tag, pattern_language, get_base_form_for_word

from bson import ObjectId, errors
from nlp.config import description_tag, STANFORD

# import jnius
import numpy as np
from lib import nlp


def union_res(result1, result2):
    union_dict = dict()
    union_dict2 = dict()
    tuple_tags = list(result1.items()) + list(result2.items())
    # Union the tags
    for (tuple_tag_key,tuple_tag_value) in tuple_tags:
        if tuple_tag_value:
            v = tuple_tag_value
            if isinstance(v, np.int64):
                v = int(v)
            for elem in tuple_tag_value:
                word = elem['word']
                start = elem['start_match']
                ln = elem['length_match']
                n_word = word
                for l in word:
                    if l.isalnum():
                        break
                    else:
                        n_word = n_word.replace(l, '', 1)
                        ln -= 1
                        start += 1
                word = n_word
                for l in word[::-1]:
                    if l.isalnum():
                        break
                    else:
                        n_word = n_word[::-1].replace(l, '', 1)[::-1]
                        ln -= 1
                elem['word'] = n_word
                elem['start_match'] = start
                elem['length_match'] = ln
            if tuple_tag_key in union_dict2:
                for elem in tuple_tag_value:
                    if (elem not in union_dict2[tuple_tag_key]) & (elem['length_match'] > 0):
                        union_dict2[tuple_tag_key].append(elem)
            else:
                trigger = True
                for elem in tuple_tag_value:
                    if elem['length_match'] == 0:
                        trigger = False
                if trigger:
                    union_dict2[tuple_tag_key] = list(v)

    for tag in union_dict2:
        v = union_dict2[tag]
        filter_dict = dict()
        for x in v:
            start_match = x['start_match']
            length_match = x['length_match']
            word = x['word']
            if not start_match in filter_dict:
                filter_dict[start_match] = (length_match, word)
            else:
                if length_match > filter_dict[start_match][0]:
                    filter_dict[start_match] = (length_match, word)
        # list(filter(lambda v: v['start_match'] == 57 and v['length_match'] == max([int(x['length_match']) for x in v]), v))
        # print(filter_dict)

        vv = []
        for sv in filter_dict:
            vv.append({'start_match': sv, 'length_match': filter_dict[sv][0], 'word': filter_dict[sv][1].lower()})

        # print(vv)
        union_dict2[tag] = vv

    return union_dict2


def union_res_with_article_id(result1, result2):
    union_dict = dict()
    union_dict2 = dict()
    tuple_tags = list(result1.items()) + list(result2.items())
    valuta_signs = ['€','$','฿', '₵','₡', '₫', '৳', 'ƒ', '₣', '₲', '₴', '₭', '₽', '₱', '₨', '₪', '₩', '¥', '៛']
    # Union the tags
    # TO_DO: Refactor the ode below
    for (tuple_tag_key,tuple_tag_value) in tuple_tags:
        if tuple_tag_value:
            v = tuple_tag_value
            if isinstance(v, np.int64):
                v = int(v)
            for elem in tuple_tag_value:
                word = elem['word']
                start = elem['start_match']
                ln = elem['length_match']
                article_type = elem['article_type']
                n_word = word
                for l in word:
                    if l.isalnum() or l in valuta_signs:
                        break
                    else:
                        n_word = n_word.replace(l, '', 1)
                        ln -= 1
                        start += 1
                word = n_word
                for l in word[::-1]:
                    if l.isalnum() or l in valuta_signs:
                        break
                    else:
                        n_word = n_word[::-1].replace(l, '', 1)[::-1]
                        ln -= 1
                elem['word'] = n_word
                elem['start_match'] = start
                elem['length_match'] = ln
                elem['article_type'] = article_type
            if tuple_tag_key in union_dict2:
                for elem in tuple_tag_value:
                    if (elem not in union_dict2[tuple_tag_key]) & (elem['length_match'] > 0):
                        union_dict2[tuple_tag_key].append(elem)
            else:
                trigger = True
                for elem in tuple_tag_value:
                    if elem['length_match'] == 0:
                        trigger = False
                if trigger:
                    union_dict2[tuple_tag_key] = list(v)

    for tag in union_dict2:
        v = union_dict2[tag]
        filter_dict = dict()
        for x in v:
            start_match = x['start_match']
            length_match = x['length_match']
            word = x['word']
            article_type = x['article_type']
            if not (start_match, article_type) in filter_dict:
                filter_dict[(start_match, article_type)] = (length_match, word)
            else:
                if length_match > filter_dict[(start_match, article_type)][0]:
                    filter_dict[(start_match, article_type)] = (length_match, word)
        # list(filter(lambda v: v['start_match'] == 57 and v['length_match'] == max([int(x['length_match']) for x in v]), v))
        # print(filter_dict)

        vv = []
        for sv in filter_dict:
            vv.append({'start_match': sv[0], 'length_match': filter_dict[sv][0], 'word': filter_dict[sv][1].lower(), 'article_type': sv[1]})

        union_dict2[tag] = vv

    return union_dict2


def get_tags(text, language="en", article_type="default"):
    with MongoConnection() as mongodb:
        is_money_regex_model_exist = True

        entities1 = mongodb.get_default_entity({"type": "default_polyglot", "language": language})
        result1 = predict_entity_polyglot(
            entities1,
            text,
            language)

        for tg in [tg for tg in result1]:
            tag_value = result1.pop(tg)
            if tg not in ['negative words', 'positive words']:
                result1[tg.lower()] = tag_value

        entities2 = mongodb.get_default_entity({"type": "default_stanford", "language": language})
        result2 = predict_entity_stanford_default(
            entities2,
            text,
            language)
        # res2 = result2.copy()
        # for tg in res2:
        for tg in [tg for tg in result2]:
            result2[tg.lower()] = result2.pop(tg)

        if 'detects locations' in result1:
            result1['location'] = result1.pop('detects locations')
        if 'detects persons' in result1:
            result1['person'] = result1.pop('detects persons')
        if 'detects organizations' in result1:
            result1['organization'] = result1.pop('detects organizations')

        if 'money' in result1:
            result1.pop('money')
        if 'money' in result2:
            result2.pop('money')

        result = union_res(result1, result2)
        if is_money_regex_model_exist:
            result3 = nlp.parse_currency(text)
            if result3['money']:
                result['money'] = result3['money']

        [y.update({'article_type': article_type}) for tag in result for y in result[tag]]
        # loc_res_names_id = mongodb.default_entity.find({'type': 'list', 'name': 'names'})
        # loc_res_common_names_id = mongodb.default_entity.find({'type': 'list', 'name': 'common_names'})
        #
        # if loc_res_names_id:
        #     loc_res_names = predict_entity(set_entity=loc_res_names_id, data=[text], language=language)
        #     res = [x for entity in loc_res_names for match in entity['entities'] for x in match['matches']]
        #     if res:
        #         result['location_names'] = res
        # if loc_res_common_names_id:
        #     loc_res_common_names = predict_entity(set_entity=loc_res_common_names_id, data=[text], language=language)
        #     res = [x for entity in loc_res_common_names for match in entity['entities'] for x in match['matches']]
        #     if res:
        #         result['location_common_names'] = res
        return result


def add_article_locations(params):
    mongodb = MongoConnection()

    if 'article_id' not in params:
        raise EnvironmentError('Request must contain \'article_id\' field')
    article_id = params['article_id']
    if not isinstance(article_id, ObjectId):
        article_id = ObjectId(article_id)
    mongodb.add_article_locations(entity_id=article_id)


def get_tags_from_article(params):
    with MongoConnection() as mongodb:
        retrain = False if 'retrain' not in params else params['retrain']
        language = 'en' if 'language' not in params else params['language']

        if 'article_id' not in params:
            raise EnvironmentError('Request must contain \'article_id\' field')
        article_id = params['article_id']
        if not isinstance(article_id, ObjectId):
            try:
                article_id = ObjectId(article_id)
            except (errors.InvalidId, TypeError):
                raise EnvironmentError('\'article_id\' field is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string')

        if mongodb.entity.find_one({'trained': True, 'article_id': article_id}):
            if retrain:
                mongodb.entity.delete_one({'trained': True, 'article_id': article_id})
            else:
                return None

        article = mongodb.article.find_one({'_id': article_id})
        if not article:
            return None

        if 'content' in article and article['content']:
            tags_content = get_tags(article['content'], language, 'content')
            ret_tags = tags_content
        else:
            return None

        if 'description' in article and article['description']:
            tags_description = get_tags(article['description'], language, 'description')
            ret_tags = union_res_with_article_id(ret_tags, tags_description)

        if 'title' in article and article['title']:
            tags_title = get_tags(article['title'], language, 'title')
            ret_tags = union_res_with_article_id(ret_tags, tags_title)

        entity_elem = {
            'article_id': article_id,
            'model': 'default_stanford',
            'tags': ret_tags,
            # 'type': 'content',
            'trained': True,
            'deleted': False
        }
        mongodb.entity.insert_one(entity_elem)

        return entity_elem


def get_tags_from_all_articles():
    mongodb = MongoConnection()

    mongodb.entity.remove()

    article_ids = [x['_id'] for x in mongodb.article.find()]

    for article_id in article_ids:
        get_tags_from_article({'article_id': article_id})

    return article_ids


def get_tags_from_untrained_articles(params):
    retrain = False if 'retrain' not in params else params['retrain']

    with MongoConnection() as mongodb:
        article_ids = [x['_id'] for x in mongodb.article.find()]
        trained_article_ids = [x['article_id'] for x in mongodb.entity.find({'trained': True})]
        untrained_ids = list(set(article_ids)-set(trained_article_ids))

    for article_id in untrained_ids:
        try:
            get_tags_from_article({'article_id': article_id, 'retrain': retrain})
        except Exception as ex:
            print(ex)
            print(article_id)

    return untrained_ids


def add_locations_to_untrained_articles():
    with MongoConnection() as mongodb:

        article_ids = [x['_id'] for x in mongodb.entity.find({'locations': {'$exists': False}})]

        for article_id in article_ids:
            add_article_locations({'article_id': article_id})


def train_on_list(train_text, name, language):
    mongodb = MongoConnection()
    if mongodb.default_entity.find_one({'name': name}):
        return None

    inserted_id = mongodb.default_entity.insert_one(
        {
            'name': name,
            'model':
                {
                    'train_text': train_text,
                    'train_postags': []
                },
            'available': True,
            'training': "finished",
            'language': language,
            'type': 'list',
            'deleted': False
        }
    ).inserted_id
    return inserted_id


def train_on_default_list(params):
    mongodb = MongoConnection()

    language = 'en' if 'language' not in params else params['language']
    # Add country
    locations = list(mongodb.location.find())
    names = [x['name'].lower() for x in locations]
    names = list(set(names))

    common_names = [x.lower() for location in locations if 'tags' in location for x in location['tags']]
    common_names = list(set(common_names))

    train_on_list(train_text=names, name='names', language=language)
    train_on_list(train_text=common_names, name='common_names', language=language)


def predict_entity(set_entity=None, data=None, language='en'):
    """predict the entity model"""
    # Elements of the list "data" MUST BE str type(utf-8 encoding).
    set_entity = [entity['_id'] if isinstance(entity, dict) else entity for entity in set_entity]
    set_entity = [entity if isinstance(entity, ObjectId) else ObjectId(entity) for entity in set_entity]
    mongo = MongoConnection()
    many_entity = list(mongo.default_entity.find({'_id': {'$in': set_entity}}))
    if len(many_entity) != len(set_entity):
        exists_entity = [entity['_id'] for entity in many_entity]
        diff_entity = set(set_entity) - set(exists_entity)
        raise EnvironmentError('Entities with id {0} not found'.format(str(diff_entity)))

    for entity in many_entity:
        if entity['language'] != language:
            raise EnvironmentError(
                'Entity with id {0} does not support the language of the selected data'.format(entity['_id'])
            )
        # if 'training' not in entity or entity['training'] != "finished":
        #     raise EnvironmentError(
        #         'Entity with id {0} should be trained'.format(entity['_id'])
        #     )

    many_entity = [defix_name_field(entity) for entity in many_entity]

    for i in range(len(many_entity)):
        if isinstance(many_entity[i]['_id'], ObjectId):
            many_entity[i]['_id'] = str(many_entity[i]['_id'])
    dict_entity = tools.sort_model(many_entity)

    results = []
    for document in data:
        document = document if isinstance(document, str) else document.encode('utf-8')
        # document = tools.sample_strip(document) #SIDE DELETE
        # document, back_map = tools.sample_remove_tabs(document) #SIDE DELETE
        results_document = {}
        for type_model in dict_entity:
            if type_model not in model_entity_predict:
                raise EnvironmentError('Entity type {0} unsupported'.format(type_model))
            results_document.update(model_entity_predict[type_model](entities=dict_entity[type_model],
                                                                     data=document, language=language))
        results_list = []
        for key in results_document:
            # matches = tools.sample_update_matches(back_map, document, results_document[key])
            results_list.append({'_id': key, 'matches': results_document[key]})
        results.append({'string': document, 'entities': results_list})

    return results


def predict_entity_polyglot(entities, data, language=None):
    """The predict function for an entity default_poliglot"""
    # "data" MUST BE unicode type(unicode encoding).
    set_tag = [entity['model_settings']['tag'] for entity in entities]
    matches = []

    # data = data if isinstance(data, unicode) else data.decode('utf8')  # Delete SIDE(PY3)
    try:
        data = data.decode('utf8')
    except UnicodeError:
        pass
    except AttributeError:
        pass

    # if 'case_sensitive' in entity['model_settings'] and not entity['model_settings']['case_sensitive']:

    # Side change/ Try to fix problem with more words in output
    # for entity in entities:
    #     if entity['model_settings']['tag'] in ['negative_word', 'positive_word']:
    #         data = data.lower()

    data_predict, back_map = tools.adaptiv_remove_tab(data)

    # Check enities
    polyglot_text = Text(data_predict, hint_language_code=language, split_apostrophe=True)
    tag_entities = set_polyglot_entity.intersection(set_tag)
    if len(tag_entities) > 0:
        parser_iter = tools.ParsePolyglot(polyglot_text.entities, tag_entities, data_predict, polyglot_text)
        for match in parser_iter:
            matches.append(match)

    # Check polarity word
    # polarity_word = set(set_tag).intersection(set(polarity_word_dict.values()))
    # if len(polarity_word) > 0:
    #     parser_iter = tools.ParsePolyglotPolarity(polyglot_text.words, polarity_word, data_predict, polarity_word_dict)
    #     for match in parser_iter:
    #         matches.append(match)

    dict_tag = {}
    for entity in entities:
        # dict_tag[entity['model_settings']['tag']] = entity['_id'] #SIDE
        dict_tag[entity['model_settings']['tag']] = entity['name']
    result = {}
    for tag in dict_tag:
        result[dict_tag[tag]] = []
    for match in matches:
        result[dict_tag[match['tag']]].append(match['match'])

    for key in result:
        result[key] = tools.sample_update_matches(back_map, data, result[key])

    return result


def predict_entity_stanford_default(entities, data, language=None):
    """"""
    # "data" MUST BE str type(utf-8 encoding).
    entity_dict = tools.sort_model(entities, 'model')
    # try:
    #     data = data.encode('utf8')
    # except UnicodeError:
    #     pass
    # except AttributeError:
    #     pass
    # data_predict, back_map = tools.adaptiv_remove_tab(data)  # SIDE Error ValueError: chr() arg not in range(0x110000) occurs
    try:
        j_data_predict = stanford.jString(data.encode('utf-8'))
    except ValueError:
        j_data_predict = stanford.jString(data)

    # data_predict = data
    # j_data_predict = stanford.jString(data_predict)

    annotation = stanford.Annotation(j_data_predict)
    stanford.getTokenizerAnnotator(language).annotate(annotation)
    stanford.getWordsToSentencesAnnotator(language).annotate(annotation)
    stanford.getPOSTaggerAnnotator(language).annotate(annotation)

    result = {}
    tags_already_used = []
    for entity_model in entity_dict:
        matches = []
        set_tag = []
        for entity in entity_dict[entity_model]:
            tag = entity['model_settings']['tag']
            if not tag in tags_already_used:
                set_tag.append(tag)
                tags_already_used.append(tag)

        stanford.load_stanford_ner(entity_model, language).annotate(annotation)
        jTokkenens = annotation.get(stanford.getClassAnnotation('TokensAnnotation'))
        previous_end_pos = 0
        for i in range(jTokkenens.size()):
            if i == 0:
                previous_tag = ''
            else:
                jTokken = jTokkenens.get(i-1)
                previous_tag = jTokken.get(stanford.getClassAnnotation('NamedEntityTagAnnotation'))
            jTokken = jTokkenens.get(i)
            tag = jTokken.get(stanford.getClassAnnotation('NamedEntityTagAnnotation'))

            if tag in set_tag:
                word = jTokken.get(stanford.getClassAnnotation('OriginalTextAnnotation'))
                # word2 = jTokken.get(stanford.getClassAnnotation('TextAnnotation'))
                start_pos = jTokken.get(stanford.getClassAnnotation('CharacterOffsetBeginAnnotation'))
                if not (start_pos > previous_end_pos + 1) and tag == previous_tag:
                    match = matches[-1]
                    end_pos = jTokken.get(stanford.getClassAnnotation('CharacterOffsetEndAnnotation'))
                    previous_end_pos = end_pos
                    match['match']['word'] = match['match']['word'] + ' ' + word
                    match['match']['length_match'] = end_pos - match['match']['start_match']
                    matches[-1] = match
                    continue
                end_pos = jTokken.get(stanford.getClassAnnotation('CharacterOffsetEndAnnotation'))
                previous_end_pos = end_pos
                match = {'match': {'start_match': start_pos,
                                   'length_match': end_pos - start_pos,
                                   'word': word},
                         'tag': tag}
                matches.append(match)

        dict_tag = {}

        for entity in entity_dict[entity_model]:
            # dict_tag[entity['model_settings']['tag']] = entity['_id']  # SIDE DELETE
            dict_tag[entity['model_settings']['tag']] = entity['name']  # SIDE ADD

        for tag in dict_tag:
            # result[dict_tag[tag]] = []
            if not tag in result:
                result[tag] = []

        for match in matches:
            # result[dict_tag[match['tag']]].append(match['match'])
            result[match['tag']].append(match['match'])

        for tag in dict_tag:
            # if not result[dict_tag[tag]]:
            #     del result[dict_tag[tag]]
            if not result[tag]:
                del result[tag]

    # stanford.SystemJava.gc()
    # for key in result:
    #     result[key] = tools.sample_update_matches(back_map, data, result[key])
    return result


def predict_entity_stanford(entities, data, language=None, classifier_dict={}):
    """"""
    # "data" MUST BE str type(utf-8 encoding).
    result = {}
    # result = []
    data = data if isinstance(data, str) else data.encode('utf8')
    for cur_tag in list(description_tag.keys()):
        # for entity in stanford_models:
        for entity in entities:
            if 'model_settings' in entity:
                settings = entity['model_settings']
            else:
                settings = {}
            if 'case_sensitive' in settings and not settings['case_sensitive']:
                data_predict = data.lower()
            else:
                data_predict = data
            # if 'row_delimiter_as_dot' in settings and settings['row_delimiter_as_dot']:
            #     data_predict, back_map = tools.adaptiv_remove_tab(data_predict)
            # else:
            #     data_predict, back_map = tools.remove_tab(data_predict)
            # settings = entity['tags']
            data_predict = data
            annotation = stanford.annotation(data_predict, language, settings)
            # document = annotation.get(stanford.getClassAnnotation('TokensAnnotation'))
            model = tools.get_abs_path(STANFORD[entity['model']])
            model = model if isinstance(model, str) else model.encode('utf8')

            if model not in classifier_dict:
                classifier_dict[model] = stanford.CRFClassifier.getClassifier(stanford.jString(model))
            classifier = classifier_dict[model]

            sentences = annotation.get(stanford.getClassAnnotation('SentencesAnnotation'))

            matches = []
            for i in range(sentences.size()):
                jSentence = sentences.get(i)
                document = jSentence.get(stanford.getClassAnnotation('TokensAnnotation'))
                classifier.classify(document)
                previous_end_pos = 0
                for i in range(document.size()):
                    if i == 0:
                        previous_tag = ''
                    else:
                        jTokken = document.get(i - 1)
                        previous_tag = jTokken.get(stanford.getClassAnnotation('NamedEntityTagAnnotation'))
                    jTokken = document.get(i)
                    tag = jTokken.get(stanford.getClassAnnotation('AnswerAnnotation'))
                    # word = jTokken.get(stanford.getClassAnnotation('TextAnnotation'))
                    # if tag in list(description_tag.keys()):#['A', 'LOCATION', ]:
                    # if tag in ['DATE']:
                    # if tag == cur_tag:
                    if tag in ['A']:
                        word = jTokken.get(stanford.getClassAnnotation('OriginalTextAnnotation'))
                        start_pos = jTokken.get(stanford.getClassAnnotation('CharacterOffsetBeginAnnotation'))
                        if start_pos == previous_end_pos + 1 and tag == previous_tag:
                            match = matches[-1]
                            end_pos = jTokken.get(stanford.getClassAnnotation('CharacterOffsetEndAnnotation'))
                            previous_end_pos = end_pos
                            match['match']['word'] = match['match']['word'] + ' ' + word
                            match['match']['length_match'] = len(match['match']['word'])
                            matches[-1] = match
                            continue
                        end_pos = jTokken.get(stanford.getClassAnnotation('CharacterOffsetEndAnnotation'))
                        previous_end_pos = end_pos
                        match = {
                            'start_match': start_pos,
                            'length_match': end_pos - start_pos,
                            'word': word  # ,
                            # 'tag': tag
                        }
                        matches.append(match)
            # matches = tools.sample_update_matches(back_map, data, matches)
            result[entity['description']] = matches
    # if matches:
    #     result.append(matches)

    return result


def predict_entity_list(entities, data, language='en'):
    """The predict function for an entity list"""
    # "data" MUST BE unicode type(unicode encoding).
    matches = {}
    try:
        data = data.decode('utf8')
    except UnicodeError:
        pass
    except AttributeError:
        pass
    data = tools.escape(data)
    for entity in entities:
        match = []
        if 'model_settings' in entity:
            settings = entity['model_settings']
        else:
            settings = {}
        # if 'case_sensitive' in settings and not settings['case_sensitive']:
        #     data_predict = data.lower()
        # else:
        #     data_predict = data
        data_predict = data.lower()
        if 'match_level' in settings:
            match_level = settings['match_level']
        else:
            match_level = -1
        if 'normal_form' in settings:
            normal_form = settings['normal_form']
        else:
            normal_form = False

        if 'train_postags' in settings:
            train_postags = settings['train_postags']
        else:
            train_postags = False
        train_postags = train_postags or normal_form

        train_dict = entity['model']
        train_list = train_dict['train_text']

        if 'train_postags' in train_dict:
            train_tags = train_dict['train_postags']
        else:
            train_tags = None

        if 'row_delimiter_as_dot' in settings and settings['row_delimiter_as_dot']:
            data_predict, back_map = tools.adaptiv_remove_tab(data_predict)
        else:
            data_predict, back_map = tools.remove_tab(data_predict)

        match_level = 0  # Add SIDE(normal_form)
        # normal_form = True  # Add SIDE(normal_form)
        # train_postags = True  # Add SIDE(normal_form)
        side_normal = True  # Add SIDE(normal_form)

        data_text = Text(data_predict, hint_language_code=language)
        if train_postags:
            if language in pattern_language:
                tagged_list = tag(data_predict, language)
                word_list = [tagged[0] for tagged in tagged_list]
            else:
                tagged_list = data_text.pos_tags
                word_list = data_text.words
        else:
            tagged_list = None
            word_list = data_text.words
        i = 0

        for entry in train_list:
            entry = entry.lower()  # Add SIDE(case_sensitive)
            if match_level == 0 and not normal_form:
                match_entry = [[m.start(), m.end() - 1] for m in re.finditer(tools.escape(entry), data_predict)]

                extend_matchto_word = \
                    tools.ParseMatchesUnits(iter(match_entry), data_predict, word_list, tagged_list)

                for match_word in extend_matchto_word:
                    word, start_match, end_match, _, _, word_tag = match_word
                    if side_normal or word == entry:
                        if train_postags and train_tags[i] != word_tag:
                            continue
                        match.append({
                            'start_match': start_match,
                            'length_match': end_match - start_match,
                            'word': word
                        })
                i = i + 1
            elif match_level == 0 and normal_form:

                normal_data = NormalForm(data_predict, word_list, tagged_list, language)

                match_entry = [[m.start(), m.end() - 1] for m in re.finditer(tools.escape(entry), normal_data.normal_text)]

                extend_matchto_word = tools.ParseMatchesUnits(
                    iter(match_entry), normal_data.normal_text, normal_data.normal_words, tagged_list)

                pos_match = []

                for match_word in extend_matchto_word:
                    word, _, _, _, _, word_tag = match_word
                    if word == entry and train_tags[i] == word_tag:
                        pos_match.append(match_word[3:5])

                negative_matchto_word = tools.ParseMatchesUnitsBack(
                    iter(pos_match), data_predict, word_list
                )  # (self, matches, text, units, units_tag=None)
                for match_word in negative_matchto_word:
                    entry, start_match, end_match, _, _, _ = match_word
                    match.append({'start_match': start_match,
                                  'length_match': end_match - start_match,
                                  'word': entry})

                i = i + 1

            elif match_level == 1:
                match_entry = [[m.start(), m.end()] for m in re.finditer(tools.escape(entry), data_predict)]
                morphemes = []
                for word in data_text.tokens:
                    morphemes.extend(word.morphemes)
                # extend_match_morpheme = tools.ParseMatchesUnits(
                #     match_entry, data_text.string, morphemes)
                extend_match_morpheme = tools.ParseMatchesMorphemes(
                    match_entry, data_text, entity['language'])
                for match_morpheme in extend_match_morpheme:
                    if entry == match_morpheme[0]:
                        match.append({'start_match': match_morpheme[1],
                                      'length_match': match_morpheme[2]-match_morpheme[1],
                                      'word': match_morpheme[0]})
            else:
                match += [{'start_match': m.start(), 'length_match': m.end() - m.start(), 'word': entry}
                          for m in re.finditer(tools.escape(entry), data_predict)]

        match = tools.sample_update_matches(back_map, data, match)

        match = sorted(match, key=lambda x: x['start_match'])

        matches.update({entity['_id']: match})

    return matches


def fill_up_db_from_zero():
    mongodb = MongoConnection()
    # Download sources and fill up db.source
    mongodb.update_source_list_from_server()
    # Add start phrases and fill up db.phrase
    mongodb.add_default_phrases()
    # Download articles from words in db.phrase and fill up db.article and db.q_article
    mongodb.download_articles_by_phrases()
    # Fill up ??? by languages
    print('download_articles_by_phrases done')
    mongodb.load_iso()
    # Fill up db.country from wiki_parser
    mongodb.update_country_list()
    mongodb.update_state_list()
    mongodb.update_pr_city_list()
    print('update_*_list done')
    # Fill up db.default_entity by entity_list from locations
    train_on_default_list({"language": "en"})
    print('train_on_default_list done')
    # Fill up db.entity by tags in articles
    get_tags_from_untrained_articles()
    add_locations_to_untrained_articles()
    print('get_tags_from_untrained_articles done')
    # Add to db.country values geolocations
    mongodb.fill_up_geolocation(mongodb.location, 'name')
    print('fill_up_geolocation done')
    print('all done')


class NormalForm(object):
    _normal_text = None
    _normal_words = None

    def __init__(self, text, words, tags, lang):
        self.origin_text = text
        self.origin_words = words
        self.language = lang
        self.tags = tags

    def to_normal(self):
        text = self.origin_text
        end_pos = 0
        # normal_words = self.origin_words
        normal_words = []
        pref_end = 0
        new_text = ''
        for i in range(len(self.origin_words)):
            word = self.origin_words[i]
            ini_pos = self.origin_text.find(word, end_pos)
            end_pos = ini_pos + len(word)
            normal_form = get_base_form_for_word(word, self.language, self.tags[i][1])
            # normal_form = word
            new_text += text[pref_end:ini_pos] + normal_form
            pref_end = end_pos
            # normal_words.append(unicode(normal_form))
            normal_words.append(str(normal_form))
        new_text += text[pref_end:]
        self._normal_text = new_text
        self._normal_words = normal_words

    @property
    def normal_text(self):
        if not self._normal_text:
            self.to_normal()
        return self._normal_text

    @property
    def normal_words(self):
        if not self._normal_words:
            self.to_normal()
        return self._normal_words

#
# model_entity_train = {
#     'list': train_entity_list,
#     'stanford_crf': train_entity_stanford
# }
#
# model_intent_train = {
#     'stanford_cdc': train_intent_stanford
# }
#
model_entity_predict = {
    'list': predict_entity_list,
    'default_polyglot': predict_entity_polyglot,
    'default_stanford': predict_entity_stanford_default,
    # 'stanford_crf': predict_entity_stanford
}
#
# model_intent_predict = {
#     'stanford_cdc': predict_intent_stanford
# }

polarity_word_dict = {
    1: 'positive_word',
    -1: 'negative_word'
}

set_polyglot_entity = set(['I-LOC', 'I-PER', 'I-ORG'])
