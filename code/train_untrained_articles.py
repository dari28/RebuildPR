import os
import sys
import django
_PATH = os.path.abspath(os.path.dirname(__file__))

if _PATH not in sys.path:
    sys.path.append(_PATH)

print(_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsAPI.settings")
django.setup()

from lib import mongo_connection as mongo
mongodb = mongo.MongoConnection()
print('train_untrained_article STARTED')
mongodb.train_untrained_articles()
print('train_untrained_article FINISHED')
