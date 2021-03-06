"""module containing background tasks"""

from background_task import background
# from background_task.models_completed import CompletedTask

from lib import mongo_connection as mongo
from lib import learning_model as model
from background_task.models import Task
# ***************************** GEOLOCATION ******************************** #


@background(schedule=1, name='update_country_list')
def update_country_list():
    mongodb = mongo.MongoConnection()
    try:
        print("Background task update_country_list started")
        mongodb.update_country_list()
        print("Background task update_country_list finished")
    except Exception as ex:
        print(ex)
        pass

# ***************************** ENTITY ******************************** #


@background(schedule=1, name='train_on_list')
def train_on_list(train_text, name, language):
    try:
        print("Background task train_on_list started")
        ids = model.train_on_list(train_text, name, language)
        print("Background task train_on_list finished. Response: \n{}".format(ids))
    except Exception as ex:
        print(ex)
        pass


@background(schedule=1, name='train_on_default_list')
def train_on_default_list(params):
    try:
        print("Background task train_on_default_list started")
        ids = model.train_on_default_list(params)
        print("Background task train_on_default_list finished. Response: \n{}".format(ids))
    except Exception as ex:
        print(ex)
        pass


@background(schedule=1, name='get_tags_from_article')
def get_tags_from_article(params):
    try:
        print("Background task get_tags_from_article started")
        id = model.get_tags_from_article(params)
        print("Background task get_tags_from_article finished. Response: \n{}".format(id))
    except Exception as ex:
        print(ex)
        pass


@background(schedule=1, name='get_tags_from_untrained_articles')
def get_tags_from_untrained_articles():
    # if not Task.objects.filter(task_name=get_tags_from_untrained_articles.name).exists():
    # if len(list(Task.objects.filter(task_name=get_tags_from_untrained_articles.name))) == 1:
    try:
        print("Background task get_tags_from_untrained_articles started")
        ids = model.get_tags_from_untrained_articles()
        print("Background task get_tags_from_untrained_articles finished. Response: \n{}".format(ids))
    except Exception as ex:
        print(ex)
        pass


@background(schedule=1, name='get_tags_from_all_articles')
def get_tags_from_all_articles():
    try:
        print("Background task get_tags_from_untrained_articles started")
        ids = model.get_tags_from_all_articles()
        print("Background task get_tags_from_untrained_articles finished. Response: \n{}".format(ids))
    except Exception as ex:
        print(ex)
        pass

# ***************************** UPDATE ******************************** #


@background(schedule=1, name='update_source_list_from_server')
def update_source_list_from_server():
    mongodb = mongo.MongoConnection()
    try:
        print("Background task update_source_list_from_server started")
        inserted_ids, deleted_ids = mongodb.update_source_list_from_server()
        print("Background task update_source_list_from_server finished. Response: \n{} \n{}".format(inserted_ids, deleted_ids))
    except Exception as ex:
        print(ex)
        pass
