import scrapenews
import hansardAPI
import os
import datetime
from pymongo import MongoClient

def connect_to_mongo():
    """ Check for mongo connection details in the environment variables,
    if not found then connect to local host
    Use database called textdb"""
    if 'MONGO_URI' in os.environ:
        db = MongoClient(os.environ['MONGO_URI']).textdb
    else:
        db = MongoClient().textdb
    return(db)

def push_to_mongo(db, data, collection_name):
    """ Send data to mongo if not empty """
    if len(data) > 0:
        result = db[collection_name].insert_many(data)
        print('inserted ' + str(len(result.inserted_ids)) +
              " to " + collection_name)
    else:
        print('No articles to insert')

def fetch_news(mongo_db):
    bbc_articles = scrapenews.scrape_bbc_pages_multiple_keywords()
    push_to_mongo(mongo_db, bbc_articles, 'news.bbc')
    guardian_articles = scrapenews.scrape_guardian_pages()
    push_to_mongo(mongo_db, guardian_articles, 'news.guardian')

def fetch_hansard(mongo_db, start_date, end_date):
    for url in hansardAPI.hansard_urls:
        collection_name = url.replace('http://lda.data.parliament.uk/',
                                      'hansard.').replace('.json', '')
        data = hansardAPI.get_hansard_data(url, start_date, end_date)
        data = hansardAPI.convert_all_values(data)
        push_to_mongo(mongo_db, data, collection_name)

if __name__ == '__main__':
    db = connect_to_mongo()
    fetch_news(db)
    hansardAPI.fetch_hansard(db, '2017-05-01', '2017-05-31')
