#
#
import os
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
from nlp.config import description_tag, STANFORD, stanford_models
from lib import tools
import jnius


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

def add_standford_default():
    """"""
    #mongodb = MongoConnection()

    entities = []
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

                entities.append(entity)
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
    return entities
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
#
