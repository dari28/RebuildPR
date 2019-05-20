from lib.text import Text
from lib import tools


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
