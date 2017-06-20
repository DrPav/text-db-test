import datetime as dt
import hansardAPI as h
from pymongo import MongoClient

def fetch_yesterday(mongo_db):
    """ Script to run daily to fetch yesterdays hansard data.
    Takes data on hansard api with yesterdays date and then send to mongodb"""

    yesterday = str(dt.date.today() - dt.timedelta(days = 1))
    for url in h.hansard_urls:
        collection_name = url.replace('http://lda.data.parliament.uk/', 
                                      'hansard.').replace('.json', '')
        data = h.get_hansard_data(url, yesterday, yesterday)
        if len(data) >= 1:
            data = h.convert_all_values(data)
            result = mongo_db[collection_name].insert_many(data)
            print('inserted ' + str(len(result.inserted_ids)))




if __name__ == "__main__":
    db = MongoClient().test # db is named test
    fetch_yesterday(db)
