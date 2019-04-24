"""module containing background tasks"""
import os

from background_task import background
import sys
import json
from bson import ObjectId
from background_task.models_completed import CompletedTask

# from lib import markup_manage
# from lib import tools
# from lib.mongo_connection import MongoConnection
# from lib import learning_model as model
# from lib.dictionary import defix_name_field
# from nlp.config import SEND_POST_URL
# from lib.json_encoder import JSONEncoderHttp


@background(schedule=1)
def func():
    print("Background task started")


@background(schedule=1)
def update_articles():
    print("Background task started")

