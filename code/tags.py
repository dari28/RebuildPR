from install_stanford import add_standford_default
from lib import learning_model as model
#from install.install_default_model import add_polyglot_default
import numpy as np
from lib.mongo_connection import MongoConnection

def union_res(result1 , result2):
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

def get_tags(text, language):
    mongo = MongoConnection()
    #entities1 = add_polyglot_default()
    entities1 = list(mongo.default_entity.find({"type": "default_polyglot"}))
    result1 = model.predict_entity_polyglot(
        entities1,
        text,
        language)
    #entities2 = add_standford_default()
    entities2 = list(mongo.default_entity.find({"type": "default_stanford"}))
    result2 = model.predict_entity_stanford_default(
        entities2,
        text,
        language)

    return union_res(result1, result2)
