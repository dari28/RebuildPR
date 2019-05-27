"""module containing background tasks"""

from background_task import background
# from background_task.models_completed import CompletedTask

from lib import mongo_connection as mongo
from lib import learning_model as model

# ***************************** GEOLOCATION ******************************** #


@background(schedule=1)
def update_country_list():
    mongodb = mongo.MongoConnection()
    try:
        print("Background task update_country_list started")
        mongodb.update_country_list()
        print("Background task update_country_list finished")
    except:
        pass


@background(schedule=1)
def fill_up_geolocation_country_list(self):
    try:
        print("Background task fill_up_geolocation_country_list started")
        ids = mongo.MongoConnection.fill_up_geolocation(self.country, 'official_name')
        print("Background task fill_up_geolocation_country_list finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def fill_up_geolocation_state_list(self):
    try:
        print("Background task fill_up_geolocation_state_list started")
        ids = mongo.MongoConnection.fill_up_geolocation(self.state, 'name')
        print("Background task fill_up_geolocation_state_list finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def fill_up_geolocation_pr_city_list(self):
    try:
        print("Background task fill_up_geolocation_pr_city_list started")
        ids = mongo.MongoConnection.fill_up_geolocation(self.pr_city, 'name')
        print("Background task fill_up_geolocation_pr_city_list finished. Response: \n{}".format(ids))
    except:
        pass

# ***************************** ENTITY ******************************** #


@background(schedule=1)
def train_on_list(train_text, name, language):
    try:
        print("Background task train_article started")
        ids = model.train_on_list(train_text, name, language)
        print("Background task train_article finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def train_on_default_list(params):
    try:
        print("Background task train_article started")
        ids = model.train_on_default_list(params)
        print("Background task train_article finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def train_article(params):
    try:
        print("Background task train_article started")
        ids = model.train_article(params)
        print("Background task train_article finished. Response: \n{}".format(ids))
    except:
        pass


@background(schedule=1)
def train_untrained_articles():
    try:
        print("Background task train_article started")
        ids = model.train_untrained_articles()
        print("Background task train_article finished. Response: \n{}".format(ids))
    except:
        pass

# ***************************** UPDATE ******************************** #


@background(schedule=1)
def update_article_list_from_server(params):
    mongodb = mongo.MongoConnection()
    try:
        print("Background task update_article_list_from_server started")
        inserted_ids, deleted_ids = mongodb.update_article_list_from_server(params)
        print("Background task update_article_list_from_server finished. Response: \n{} \n{}".format(inserted_ids, deleted_ids))
    except Exception as ex:
        print(ex)
        pass


@background(schedule=1)
def update_source_list_from_server():
    mongodb = mongo.MongoConnection()
    try:
        print("Background task update_source_list_from_server started")
        inserted_ids, deleted_ids = mongodb.update_source_list_from_server()
        print("Background task update_source_list_from_server finished. Response: \n{} \n{}".format(inserted_ids, deleted_ids))
    except Exception as ex:
        print(ex)
        pass
