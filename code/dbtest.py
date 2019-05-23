from pymongo import MongoClient

if __name__ == "__main__":
    db = MongoClient('mongodb://149.28.85.111:27017')
    print(db)
    testDB = db['testDB']
    print(str(testDB.list_collection_names()))
    testCollection = testDB['testCollection']
    # ll = testCollection.insert_one({"name": "Side", "town": "Gotham"}).inserted_id
    # print(ll)
    print(str(testDB.list_collection_names()))
    pp = testCollection.find_one({"name": "Side"})
    print(pp)
