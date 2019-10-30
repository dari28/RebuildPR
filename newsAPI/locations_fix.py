from lib.mongo_connection import MongoConnection
from bson import ObjectId

mongo = MongoConnection()
entities = mongo.entity.find({'locations': {'$exists': True}})
for entity in entities:
    loc_list = entity['locations']
    new_loc_list = loc_list
    for loc in loc_list:
        parents = mongo.location.find_one({'_id': loc})['parents']
        for parent in parents:
            parent = mongo.location.find_one({'place_id': parent})
            if parent and (parent['_id'] not in new_loc_list):
                new_loc_list.append(parent['_id'])
    mongo.entity.update_one({'_id': entity['_id']}, {'$set': {'locations': new_loc_list}})
