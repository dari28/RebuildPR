import re

from lib import tools, stanford_module as stanford
from lib.text import Text
from lib.dictionary import defix_name_field
from lib.mongo_connection import MongoConnection
from lib.linguistic_functions import tag, pattern_language, get_base_form_for_word

from bson import ObjectId
from nlp.config import description_tag, STANFORD, stanford_models

import jnius
import numpy as np


def union_res(result1, result2):
    union_dict = dict()
    for r1 in result1:
        if result1[r1]:
            v = result1[r1]
            if isinstance(v, np.int64):
                v = int(v)
            if r1 in union_dict:
                union_dict[r1].append(v)
            else:
                union_dict[r1] = list(v)
    for r2 in result2:
        if result2[r2]:
            v = result2[r2]
            if isinstance(v, np.int64):
                v = int(v)
            if r2 in union_dict:
                union_dict[r2].append(v)
            else:
                union_dict[r2] = list(v)

    return union_dict


def get_tags(text, language="en"):
    mongodb = MongoConnection()

    entities1 = mongodb.get_default_entity({"type": "default_polyglot", "language": language})
    result1 = predict_entity_polyglot(
        entities1,
        text,
        language)

    entities2 = mongodb.get_default_entity({"type": "default_stanford", "language": language})
    result2 = predict_entity_stanford_default(
        entities2,
        text,
        language)

    return union_res(result1, result2)


def train_article(params):
    mongodb = MongoConnection()

    language = 'en' if 'language' not in params else params['language']

    if 'article_id' not in params:
        raise EnvironmentError('Request must contain \'article_id\' field')
    article_id = params['article_id']
    if not isinstance(article_id, ObjectId):
        article_id = ObjectId(article_id)

    if mongodb.entity.find_one({'trained': True, 'article_id': article_id}):
        return None

    article = mongodb.article.find_one({'deleted': False, '_id': article_id})
    if not article:
        return None

    if 'content' in article and article['content']:
        tags = get_tags(article['content'], language)
    else:
        tags = get_tags(article['description'], language)

    inserted_id = mongodb.entity.insert_one(
        {
            'article_id': str(article_id),
            'model': 'default_stanford',
            'tags': tags,
            'trained': True,
            'deleted': False
        },
        # upsert=True
    ).inserted_id
    return inserted_id


def train_untrained_articles():
    mongodb = MongoConnection()

    article_ids = [x['_id'] for x in mongodb.source.find({'deleted': False})]
    trained_article_ids = [ObjectId(x['article_id']) for x in mongodb.entity.find({'trained': True})]
    untrained_ids = list(set(article_ids)-set(trained_article_ids))

    for id in untrained_ids:
        # self.train_article({'article_id': id}
        train_article({'article_id': id})

    return untrained_ids


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
        },
        # upsert=True
    ).inserted_id
    return inserted_id


def train_on_default_list(params):
    mongodb = MongoConnection()

    language = 'en' if 'language' not in params else params['language']
    # Add country
    countries = mongodb.country.find()
    common_names = [x['common_name'].lower() for x in countries]
    common_names = list(set(common_names))
    official_names = [x['official_name'].lower() for x in countries]
    official_names = list(set(official_names))
    train_on_list(train_text=common_names, name='country_common_names', language=language)
    train_on_list(train_text=official_names, name='country_official_names', language=language)
    # Add state
    states = mongodb.state.find()
    names = [x['name'].lower() for x in states]
    names = list(set(names))
    descriptions = [item.lower() for sublist in states for item in sublist['description']]
    descriptions = list(set(descriptions))
    train_on_list(train_text=names, name='state_names', language=language)
    train_on_list(train_text=descriptions, name='state_descriptions', language=language)
    # Add pr_city
    pr_cities = mongodb.pr_city.find()
    pr_city_names = [x['name'].lower() for x in pr_cities]
    pr_city_names = list(set(pr_city_names))
    train_on_list(train_text=pr_city_names, name='pr_city_names', language=language)


def predict_entity(set_entity=None, data=None, language='en'):
    """predict the entity model"""
    # Elements of the list "data" MUST BE str type(utf-8 encoding).
    set_entity = [entity['_id'] if isinstance(entity, dict) else entity for entity in set_entity]
    set_entity = [entity if isinstance(entity, ObjectId) else ObjectId(entity) for entity in set_entity]
    mongo = MongoConnection()
    many_entity = list(mongo.entity.find({'_id': {'$in': set_entity}}))
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
    for entity in entities:
        if entity['model_settings']['tag'] in ['negative_word', 'positive_word']:
            data = data.lower()

    data_predict, back_map = tools.adaptiv_remove_tab(data)

    # Check enities
    polyglot_text = Text(data_predict, hint_language_code=language, split_apostrophe=True)
    tag_entities = set_polyglot_entity.intersection(set_tag)
    if len(tag_entities) > 0:
        parser_iter = tools.ParsePolyglot(polyglot_text.entities, tag_entities, data_predict, polyglot_text)
        for match in parser_iter:
            matches.append(match)

    # Check polarity word
    polarity_word = set(set_tag).intersection(set(polarity_word_dict.values()))
    if len(polarity_word) > 0:
        parser_iter = tools.ParsePolyglotPolarity(polyglot_text.words, polarity_word, data_predict, polarity_word_dict)
        for match in parser_iter:
            matches.append(match)

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
    for entity_model in entity_dict:
        matches = []
        set_tag = []
        for entity in entity_dict[entity_model]:
            set_tag.append(entity['model_settings']['tag'])

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
            # dict_tag[entity['model_settings']['tag']] = entity['_id'] #SIDE DELETE
            dict_tag[entity['model_settings']['tag']] = entity['name']  # SIDE ADD

        for tag in dict_tag:
            # result[dict_tag[tag]] = []
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
