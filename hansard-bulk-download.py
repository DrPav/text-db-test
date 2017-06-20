import json
import os
import hansardAPI as h
from pymongo import MongoClient
# API docs
# http://explore.data.parliament.uk/

def get_all_hansard_data(min_date, max_date):
    """ Loops through all the hansard urls and saves each to file in a folder
    called bulk-data. The folder is created if it does not exist """

    if not os.path.exists('bulk-data'):
        os.makedirs('bulk-data')
    for url in h.hansard_urls:
        filename = url.replace('http://lda.data.parliament.uk/', 'bulk-data/')
        with open(filename, 'w') as f:
            results = h.get_hansard_data(url, min_date, max_date)
            json.dump(results, f)

def push_all_datafiles_to_mongo(mongo_db):
    """ Load all the json files created and push each to their own 
    mongo db collection. Requires a active mongo db object """
    
    for url in h.hansard_urls:
        filename = url.replace('http://lda.data.parliament.uk/', 'bulk-data/')
        collection_name = url.replace('http://lda.data.parliament.uk/', 
                                      'hansard.').replace('.json', '')
        with open(filename, 'r') as f:
            data = json.loads(f.read())
        if len(data) >= 1:
            data = h.convert_all_values(data)
            result = mongo_db[collection_name].insert_many(data)
            print('inserted ' + str(len(result.inserted_ids)))


if __name__ == '__main__':
    get_all_hansard_data('2017-01-01', '2017-05-31')
    
    db = MongoClient().test # db is named test
    push_all_datafiles_to_mongo(db)
    



# Still need to edd error and timeout handling
# Proper logging instead of print to screen



