from lib.text import Text
from lib import tools
from lib.mongo_connection import MongoConnection
from bson import ObjectId
from lib.dictionary import defix_name_field
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
# model_entity_predict = {
#     'list': predict_entity_list,
#     'default_polyglot': predict_entity_polyglot,
#     'default_stanford': predict_entity_stanford_default,
#     'stanford_crf': predict_entity_stanford
# }
#
# model_intent_predict = {
#     'stanford_cdc': predict_intent_stanford
# }

polarity_word_dict = {
    1: 'positive_word',
    -1: 'negative_word'
}

set_polyglot_entity = set(['I-LOC', 'I-PER', 'I-ORG'])


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


# def predict_entity(set_entity=None, data=None, language='en'):
#     """predict the entity model"""
#     # Elements of the list "data" MUST BE str type(utf-8 encoding).
#     set_entity = [entity['_id'] if isinstance(entity, dict) else entity for entity in set_entity]
#     set_entity = [entity if isinstance(entity, ObjectId) else ObjectId(entity) for entity in set_entity]
#     mongo = MongoConnection()
#     many_entity = list(mongo.entity.find({'_id': {'$in': set_entity}}))
#     if len(many_entity) != len(set_entity):
#         exists_entity = [entity['_id'] for entity in many_entity]
#         diff_entity = set(set_entity) - set(exists_entity)
#         raise EnvironmentError('Entities with id {0} not found'.format(str(diff_entity)))
#
#     for entity in many_entity:
#         if entity['language'] != language:
#             raise EnvironmentError(
#                 'Entity with id {0} does not support the language of the selected data'.format(entity['_id'])
#             )
#         # if 'training' not in entity or entity['training'] != "finished":
#         #     raise EnvironmentError(
#         #         'Entity with id {0} should be trained'.format(entity['_id'])
#         #     )
#
#     many_entity = [defix_name_field(entity) for entity in many_entity]
#
#     for i in range(len(many_entity)):
#         if isinstance(many_entity[i]['_id'], ObjectId):
#             many_entity[i]['_id'] = str(many_entity[i]['_id'])
#     dict_entity = tools.sort_model(many_entity)
#
#     results = []
#     for document in data:
#         document = document if isinstance(document, str) else document.encode('utf-8')
#         #document = tools.sample_strip(document) #SIDE DELETE
#         #document, back_map = tools.sample_remove_tabs(document) #SIDE DELETE
#         results_document = {}
#         for type_model in dict_entity:
#             if type_model not in model_entity_predict:
#                 raise EnvironmentError('Entity type {0} unsupported'.format(type_model))
#             results_document.update(model_entity_predict[type_model](entities=dict_entity[type_model],
#                                                                           data=document, language=language))
#         results_list = []
#         for key in results_document:
#             # matches = tools.sample_update_matches(back_map, document, results_document[key])
#             results_list.append({'_id': key, 'matches': results_document[key]})
#         results.append({'string': document, 'entities': results_list})
#
#     return results

