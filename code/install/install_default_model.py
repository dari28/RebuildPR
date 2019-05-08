import os

#from lib.mongo_connection import MongoConnection
from lib.linguistic_functions import get_supported_languages
from nlp.config import SERVER


def add_polyglot_default():
    """Defining default polyglot models"""
    entities = []
    polyglot_model = [
        {
            'model_settings': {
                'tag': 'I-LOC',
                'polyglot_model': 'ner2',
                'case_sensitive': True
            },
            'training': 'finished',
            'available': True,
            'type': 'default_polyglot',
            'description': 'Trained model based on a neural network, detected locations',
            'name': 'Detects locations'
        },
        {
            'model_settings': {
                'tag': 'I-PER',
                'polyglot_model': 'ner2',
                'case_sensitive': True
            },
            'training': 'finished',
            'available': True,
            'type': 'default_polyglot',
            'description': 'Trained model based on a neural network, detected personality',
            'name': 'Detects persons'
        },
        {
            'model_settings': {
                'tag': 'I-ORG',
                'polyglot_model': 'ner2',
            },
            'training': 'finished',
            'available': True,
            'type': 'default_polyglot',
            'description': 'Trained model based on a neural network, detected organizations',
            'name': 'Detects organizations'
        },
        {
            'model_settings': {
                'tag': 'negative_word',
                'polyglot_model': 'sentiment2',
                'case_sensitive': False
            },
            'training': 'finished',
            'available': True,
            'type': 'default_polyglot',
            'description': 'Trained model based on a neural network, detected negative words',
            'name': 'negative words'
        },
        {
            'model_settings': {
                'tag': 'positive_word',
                'polyglot_model': 'sentiment2',
                'case_sensitive': False
            },
            'training': 'finished',
            'available': True,
            'type': 'default_polyglot',
            'description': 'Trained model based on a neural network, detected positive words',
            'name': 'positive words'
        },
        # {'model_settings': {'tag': 'polarity_sentence', 'polyglot_model': 'sentiment2'},
        #  'status': 'train', 'available': True, 'type': 'default_polyglot',
        #  'name': 'Polyglot default detected polarity of sentence'},
        # {'model_settings': {'tag': 'polarity_text', 'polyglot_model': 'sentiment2'},
        #  'status': 'train', 'available': True, 'type': 'default_polyglot',
        #  'name': 'Polyglot default detected polarity of document'},
    ]

    #mongo = MongoConnection()
    for language in SERVER['language']:
        # Adding Entities
        for model in polyglot_model:
            #full_name = Language.from_code(language).name
            #if full_name in tools.list_decode(
            #        downloader.supported_languages(model['model_settings']['polyglot_model'])
            #):
            if language in get_supported_languages(model['model_settings']['polyglot_model']):
                model['language'] = language
                model['training'] = 'finished'
                model['available'] = True
                #model['user'] = DEFAULT_USER[language]
                entities.append(model)
                # find_entity = model.copy()
                # del find_entity['description']
                # find_model = mongo.entity.find_one(find_entity)
                # if find_model is None:
                #     if '_id' in model:
                #         del model['_id']
                #     try:
                #         model_id = mongo.entity.insert(model)
                #     except Exception:
                #         print model
                #         raise
                #     mongo.users.update_one(
                #         {'_id': DEFAULT_USER[language]},
                #         {'$addToSet': {'entity': model_id}},
                #         upsert=True
                #     )
    return entities

