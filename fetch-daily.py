import scrapenews
import hansardAPI
import os
from pymongo import MongoClient
import logging
import datetime



def connect_to_mongo():
    """ Check for mongo connection details in the environment variables,
    if not found then connect to local host
    Use database called textdb"""
    if 'MONGO_URI' in os.environ:
        logging.debug("Connecting to Mongo DB " + os.environ['MONGO_URI'])
        db = MongoClient(os.environ['MONGO_URI']).textdb
    else:
        db = MongoClient().textdb
        logging.debug('Connecting to local mongo db')
    return(db)

def push_to_mongo(db, data, collection_name = 'raw_data'):
    """ Send data to mongo if not empty """
    if len(data) > 0:
        result = db[collection_name].insert_many(data)
        print('inserted ' + str(len(result.inserted_ids)))
    else:
        print('No articles to insert')

def fetch_news(mongodb):
    """ Collect yesterdays relevant bbc and guardian news articles and
    push to mongo """
    bbc_articles = scrapenews.scrape_bbc_yesterday_multiple_keywords()
    push_to_mongo(mongodb, bbc_articles)
    guardian_articles = scrapenews.scrape_guardian_yesterday()
    push_to_mongo(mongodb, guardian_articles)

def fetch_hansard(mongodb):
    """ Script to run daily to fetch yesterdays hansard data.
    Takes data on hansard api with yesterdays date and then send to mongodb """

    yesterday = str(datetime.date.today() - datetime.timedelta(days = 1))
    for url in hansardAPI.hansard_urls:
        data = hansardAPI.get_hansard_data(url, yesterday, yesterday)
        data = hansardAPI.convert_all_values(data)
        push_to_mongo(mongodb, data)

if __name__ == '__main__':
    logging.basicConfig(filename='info.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s')
    logging.info('Starting daily')
    db = connect_to_mongo()
    fetch_news(db)
    fetch_hansard(db)
