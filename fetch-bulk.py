import scrapenews
import hansardAPI
import os
import datetime
from pymongo import MongoClient
from dateutil.parser import parse
import requests
import time
import logging

def connect_to_mongo():
    """ Check for mongo connection details in the environment variables,
    if not found then connect to local host
    Use database called textdb"""
    if 'MONGO_URI' in os.environ:
        db = MongoClient(os.environ['MONGO_URI']).textdb
    else:
        db = MongoClient().textdb
    return(db)

def push_to_mongo(db, data, collection_name = 'raw_data'):
    """ Send data to mongo if not empty """
    if len(data) > 0:
        result = db[collection_name].insert_many(data)
        logging.debug('inserted ' + str(len(result.inserted_ids)) +
              " to " + collection_name)
    else:
        logging.info('No articles to insert')

def fetch_news(mongo_db):
    bbc_articles = scrapenews.scrape_bbc_pages_multiple_keywords()
    push_to_mongo(mongo_db, bbc_articles)
    guardian_articles = scrapenews.scrape_guardian_pages()
    push_to_mongo(mongo_db, guardian_articles)

def fetch_hansard_chunk(mongo_db, start_date, end_date):
    for url in hansardAPI.hansard_urls:
        try:
            data = hansardAPI.get_hansard_data(url, start_date, end_date)
            data = hansardAPI.convert_all_values(data)
            push_to_mongo(mongo_db, data)
        except requests.exceptions.Timeout:
            # Wait 5 mins and try again
            logging.info('Connection timeout')
            time.sleep(300)
            try:
                data = hansardAPI.get_hansard_data(url, start_date, end_date)
                data = hansardAPI.convert_all_values(data)
                push_to_mongo(mongo_db, data)
            except:
                logging.info('Failed a second time')

def fetch_all_hansard_chunks(mongo_db, start_date):
    start_date = parse(start_date)
    more_chunks = True
    while more_chunks:
        string_start_date = str(start_date.date())
        end_date = start_date + datetime.timedelta(days = 20)
        string_end_date = str(end_date.date())
        logging.info('Fetching hansard for ' + string_start_date +
                     ' to ' + string_end_date)
        logging.info('---------------------------')
        fetch_hansard_chunk(mongo_db, string_start_date, string_end_date)
        more_chunks = end_date < datetime.datetime.today()
        start_date = end_date + datetime.timedelta(days = 1)

if __name__ == '__main__':
    logging.basicConfig(filename='info.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    logging.info('Starting bulk')
    db = connect_to_mongo()
    fetch_news(db)
    fetch_all_hansard_chunks(db, '2017-04-01')
