from lib.mongo_connection import MongoConnection
from bson import ObjectId
from news import NewsCollection
import hashlib
import json

mongodb = MongoConnection()
article_id = "5d1082d6471b9289e20d31b4"
if not isinstance(article_id, ObjectId):
    article_id = ObjectId(article_id)
article = mongodb.article.find_one({'_id': article_id})
article_hash = article['hash']
date = article['publishedAt']
q = article['original_content'].split(' ')[0]
articles, tc, st = NewsCollection.get_everything(q, 'en', from_date=date, to_date=date)
new_articles_hash = articles.copy()
new_hash_list = []
for ns in new_articles_hash:
    hasher = hashlib.md5()
    hasher.update(json.dumps(ns).encode('utf-8'))
    ns_hash = hasher.hexdigest()
    if ns_hash == article_hash:
        article['original_content'] = ns['content']
        article['original_title'] = ns['title']
        article['original_description'] = ns['description']
        article['content'] = mongodb.delete_trash_from_article_content(ns['content'])
        article['title'] = mongodb.delete_trash_from_article_content(ns['title'])
        article['description'] = mongodb.delete_trash_from_article_content(ns['description'])
        mongodb.article.update_one({'hash': article_hash}, {'$set': article}, upsert=True)



pass


