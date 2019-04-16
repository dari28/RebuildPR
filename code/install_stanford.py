#
#
# import os
#
# from lib.mongo_connection import MongoConnection
# from lib.linguistic_functions import get_supported_languages
# from nlp.config import DEFAULT_USER, SERVER
# from add_exemple import update_decsription
# from install_default_stoplists import upload_stoplists
# from install_stt_models import install_stt
# from install_tts_models import install_tts
#
from lib import stanford_module as stanford

def predict_entity_stanford_default(entities, data, language=None):
    """"""
    #"data" MUST BE str type(utf-8 encoding).
    entity_dict = entities  #tools.sort_model(entities, 'model')

    data = data if isinstance(data, str) else data.encode('utf8')
    #data_predict, back_map = tools.adaptiv_remove_tab(data)
    data_predict = data

    annotation = stanford.Annotation(data_predict)
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
            dict_tag[entity['model_settings']['tag']] = entity['_id']

        for tag in dict_tag:
            result[dict_tag[tag]] = []

        for match in matches:
            result[dict_tag[match['tag']]].append(match['match'])

    # stanford.SystemJava.gc()
    # for key in result:
    #     result[key] = tools.sample_update_matches(back_map, data, result[key])
    return result


def predict_entity_stanford(entities, data, language=None):
    """"""
    #"data" MUST BE str type(utf-8 encoding).
    result = {}
    data = data if isinstance(data, str) else data.encode('utf8')

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

        annotation = stanford.annotation(data_predict, language, settings)
        #document = annotation.get(stanford.getClassAnnotation('TokensAnnotation'))
        #classifier = stanford.CRFClassifier.getClassifier(entity['model'].encode('utf-8'))
        classifier = stanford.CRFClassifier.getClassifier("crf_chinese_7class")
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
                        'word': word
                    }
                    matches.append(match)
        #matches = tools.sample_update_matches(back_map, data, matches)
        result[entity['_id']] = matches

    return result

def add_standford_default():
    """"""
    #mongodb = MongoConnection()

    stanford_models = [
        {
            'model': 'crf_english_3class',
            'tags': ['ORGANIZATION', 'LOCATION', 'PERSON'],
            'language': 'en',
            'name': 'Detects'
        },
        {
            'model': 'crf_english_4class',
            'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'MISC'],
            'language': 'en',
            'name': 'Detects'
        },
        {
            'model': 'crf_english_7class',
            'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'DATE', 'MONEY', 'PERCENT', 'TIME'],
            'language': 'en',
            'name': 'Detects'
        },
        {
            'model': 'crf_chinese_7class',
            'tags': ['ORGANIZATION', 'LOCATION', 'PERSON', 'FACILITY', 'DEMONYM', 'MISC', 'GPE'],
            'language': 'zh',
            'name': ''
        },
        {
            'model': 'crf_german_7class',
            'tags': ['I-MISC', 'B-LOC', 'I-PER', 'I-LOC', 'B-MISC', 'I-ORG', 'B-ORG', 'B-PER'],
            'language': 'de',
            'name': 'Erkennt'
        },
        {
            'model': 'crf_spanish_4class',
            'tags': ['OTROS', 'PERS', 'ORG', 'LUG'],
            'language': 'es',
            'name': 'Detecta'
        },
        {
            'model': 'crf_france_3class',
            'tags': ['I-ORG', 'I-PERS', 'I-LIEU'],
            'language': 'fr',
            'name': '\x44\xC3\xA9\x74\x65\x72\x6D\x69\x6E\x65\x20\x6C\x65\x73'
        }
    ]

    count_tag = {}
    step_tag = {}
    for model in stanford_models:
        #if model['language'] in SERVER['language']:
        if True:
            if model['language'] not in count_tag:
                count_tag[model['language']] = {}
                step_tag[model['language']] = {}
            for tag in model['tags']:
                if tag not in count_tag[model['language']]:
                    count_tag[model['language']][tag] = 0
                    step_tag[model['language']][tag] = 0
                count_tag[model['language']][tag] += 1


    for model in stanford_models:
        #if model['language'] in SERVER['language']:
        if True:
            for tag in model['tags']:
                entity = {
                    #'user': DEFAULT_USER[model['language']],
                    'name': '{0} {1}'.format(model['name'], tag.lower()),
                    'language': model['language'],
                    'model': model['model'],
                    'model_settings': {'tag': tag},
                    'type': 'default_stanford',
                    'training': 'finished',
                    'available': True,
                    'description': description_tag[tag]
                }

                step_tag[model['language']][tag] += 1
                if count_tag[model['language']][tag] > 1:
                    entity['name'] += ' (model {0})'.format(step_tag[model['language']][tag])
                    entity['description'] += \
                        ' (different models were trained on different data, so their results can vary)'

                # find_entity = entity.copy()
                # del find_entity['description']
                # check_exist = mongodb.entity.find_one(find_entity)
                # if check_exist is None:
                #     if '_id' in entity:
                #         del entity['_id']
                #     try:
                #         model_id = mongodb.entity.insert(entity)
                #     except Exception:
                #         print entity
                #         raise
                    # mongodb.users.update_one(
                    #     {'_id':  DEFAULT_USER[model['language']]},
                    #     {'$addToSet': {'entity': model_id}},
                    #     upsert=True
                    # )
#
# def add_polyglot_default():
#     """Defining default polyglot models"""
#     polyglot_model = [
#         {
#             'model_settings': {
#                 'tag': 'I-LOC',
#                 'polyglot_model': 'ner2',
#                 'case_sensitive': True
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected locations',
#             'name': 'Detects locations'
#         },
#         {
#             'model_settings': {
#                 'tag': 'I-PER',
#                 'polyglot_model': 'ner2',
#                 'case_sensitive': True
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected personality',
#             'name': 'Detects persons'
#         },
#         {
#             'model_settings': {
#                 'tag': 'I-ORG',
#                 'polyglot_model': 'ner2',
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected organizations',
#             'name': 'Detects organizations'
#         },
#         {
#             'model_settings': {
#                 'tag': 'negative_word',
#                 'polyglot_model': 'sentiment2',
#                 'case_sensitive': False
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected negative words',
#             'name': 'negative words'
#         },
#         {
#             'model_settings': {
#                 'tag': 'positive_word',
#                 'polyglot_model': 'sentiment2',
#                 'case_sensitive': False
#             },
#             'training': 'finished',
#             'available': True,
#             'type': 'default_polyglot',
#             'description': 'Trained model based on a neural network, detected positive words',
#             'name': 'positive words'
#         },
#         # {'model_settings': {'tag': 'polarity_sentence', 'polyglot_model': 'sentiment2'},
#         #  'status': 'train', 'available': True, 'type': 'default_polyglot',
#         #  'name': 'Polyglot default detected polarity of sentence'},
#         # {'model_settings': {'tag': 'polarity_text', 'polyglot_model': 'sentiment2'},
#         #  'status': 'train', 'available': True, 'type': 'default_polyglot',
#         #  'name': 'Polyglot default detected polarity of document'},
#     ]
#
#     mongo = MongoConnection()
#     for language in SERVER['language']:
#         # Adding Entities
#         for model in polyglot_model:
#             #full_name = Language.from_code(language).name
#             #if full_name in tools.list_decode(
#             #        downloader.supported_languages(model['model_settings']['polyglot_model'])
#             #):
#             if language in get_supported_languages(model['model_settings']['polyglot_model']):
#                 model['language'] = language
#                 model['training'] = 'finished'
#                 model['available'] = True
#                 model['user'] = DEFAULT_USER[language]
#                 find_entity = model.copy()
#                 del find_entity['description']
#                 find_model = mongo.entity.find_one(find_entity)
#                 if find_model is None:
#                     if '_id' in model:
#                         del model['_id']
#                     try:
#                         model_id = mongo.entity.insert(model)
#                     except Exception:
#                         print model
#                         raise
#                     mongo.users.update_one(
#                         {'_id': DEFAULT_USER[language]},
#                         {'$addToSet': {'entity': model_id}},
#                         upsert=True
#                     )
#
#
description_tag = {
    'ORGANIZATION': 'Trained model of CRF, defining organizations',
    'LOCATION': 'Trained model of CRF, defining places',
    'PERSON': 'Trained model of CRF, defining personality',
    'DATE': 'Trained model of CRF, defining the dates',
    'MONEY': 'Trained model of CRF, defining finances',
    'PERCENT': 'Trained model of CRF, defining personality',
    'TIME': 'Trained model of CRF, defining dates',
    'MISC': 'Trained model of CRF, defining misc data',
    'FACILITY': 'Trained model of CRF, defining objects',
    'DEMONYM': 'Trained model of CRF, defining ethnicity',
    'GPE': 'Trained model of CRF, defining geographical and political entity, a location which has a government, like U.S.A. or New York',
    'I-MISC': 'Trained model of CRF, defining misc data (inside entity)',
    'B-LOC': 'Trained model of CRF, defining places (begin entity)',
    'I-PER': 'Trained model of CRF, defining personality (inside entity)',
    'B-PER': 'Trained model of CRF, defining personality (begin entity)',
    'I-LOC': 'Trained model of CRF, defining places(inside entity)',
    'B-MISC': 'Trained model of CRF, defining misc data (begin entity)',
    'I-ORG': 'Trained model of CRF, defining organizations (inside entity)',
    'B-ORG': 'Trained model of CRF, defining organizations (begin entity)',
    'OTROS': 'Trained model of CRF, defining misc data',
    'PERS': 'Trained model of CRF, defining personality',
    'ORG': 'Trained model of CRF, defining organizations',
    'LUG': 'Trained model of CRF, defining places',
    'I-PERS': 'Trained model of CRF, defining personality',
    'I-LIEU': 'Trained model of CRF, defining places'
}
#
#
# if __name__ == '__main__':
#     try:
#         f = open('install_default_log', 'a')
#     except:
#         f = open('install_default_log', 'w')
#     import datetime
#     f.write('started at {}\n'.format(datetime.datetime.now()))
#     f.close()
#     ####################################
#     translate_desription = True
#     ###################################
#     add_polyglot_default()
#     add_standford_default()
#     try:
#         upload_stoplists(host_main)
#     except:
#         print("Failed load stoplist")
#     update_decsription(host_main, proxy, translate_desription)
#     try:
#         install_stt(proxy)
#     except:
#         print "Failed load Sphinx"
#     try:
#         install_tts(proxy)
#     except:
#         print "Failed load MARYTTS"
#
