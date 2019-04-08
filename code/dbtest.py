from pymongo import MongoClient

if __name__ == "__main__":
    # headliners, errors = get_top_headliners()
    #search_news("Port")
    #nc = NewsCollector()
    # a = get_sources("")
    # b = get_sources("Rus")
    # c = get_sources("Android")
    # d = get_sources("My own name lang")
    #a = get_everything(q="Rico")
    #b = get_everything(q=" porte")
    #print(a)
    #print(b)
    #Create MongoConnection
    db = MongoClient('mongodb://149.28.85.111:27017')
    print(db)
    testDB = db['testDB']
    print(str(testDB.list_collection_names()))
    testCollection = testDB['testCollection']
    #ll = testCollection.insert_one({"name": "Side", "town": "Gotham"}).inserted_id
    #print(ll)
    print(str(testDB.list_collection_names()))
    pp = testCollection.find_one({"name": "Side"})
    print(pp)