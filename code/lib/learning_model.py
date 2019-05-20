from lib.text import Text
from lib import tools
from bson import ObjectId
from lib.dictionary import defix_name_field
from lib.mongo_connection import MongoConnection
from lib import stanford_module as stanford
from nlp.config import description_tag, STANFORD, stanford_models
from lib import tools
import jnius

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
        #document = tools.sample_strip(document) #SIDE DELETE
        #document, back_map = tools.sample_remove_tabs(document) #SIDE DELETE
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
    #"data" MUST BE unicode type(unicode encoding).
    set_tag = [entity['model_settings']['tag'] for entity in entities]
    matches = []

    #data = data if isinstance(data, unicode) else data.decode('utf8')

    #if 'case_sensitive' in entity['model_settings'] and not entity['model_settings']['case_sensitive']:
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
        #dict_tag[entity['model_settings']['tag']] = entity['_id'] #SIDE
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
    #"data" MUST BE str type(utf-8 encoding).
    entity_dict = tools.sort_model(entities, 'model')
    try:
        data = data.encode('utf8')
    except:
        pass
    #data_predict, back_map = tools.adaptiv_remove_tab(data) #SIDE DELETE
    data_predict = data #SIDE ADD

    annotation = stanford.Annotation(stanford.jString(data_predict))
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
            #result[dict_tag[tag]] = []
            result[tag] = []

        for match in matches:
            #result[dict_tag[match['tag']]].append(match['match'])
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


def predict_entity_stanford(entities, data, language=None, classifier_dict = {}):
    """"""
    #"data" MUST BE str type(utf-8 encoding).
    result = {}
    #result = []
    data = data if isinstance(data, str) else data.encode('utf8')
    for cur_tag in list(description_tag.keys()):
        for entity in entities:
        #for entity in stanford_models:
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
            #settings = entity['tags']
            data_predict = data
            annotation = stanford.annotation(data_predict, language, settings)
            #document = annotation.get(stanford.getClassAnnotation('TokensAnnotation'))
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
                    #if tag in list(description_tag.keys()):#['A', 'LOCATION', ]:
                    if tag in ['A']:
                    #if tag in ['DATE']:
                    #if tag == cur_tag:
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
                            'word': word#,
                           # 'tag': tag
                        }
                        matches.append(match)
            #matches = tools.sample_update_matches(back_map, data, matches)
            result[entity['description']] = matches
    # if matches:
    #     result.append(matches)

    return result

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
   # 'list': predict_entity_list,
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