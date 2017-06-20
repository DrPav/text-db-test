from lxml import html
import requests
from dateutil.parser import parse
import datetime
from pymongo import MongoClient


def get_bbc_news(keyword, n_articles):
    """ Collect up to n_articles articles headlines with their url and date.
    It uses the bbc search page and filters to news articles. It is not sorted
    in alphabetical order so 50 articles are collected to cover the last few
    days """

    request_url = ('http://www.bbc.co.uk/search?q=' + keyword +
        '&filter=news#page=' + str(n_articles // 10)) # 10 articles per page
    page = requests.get(request_url)
    tree = html.fromstring(page.content)
    headlines = tree.xpath('//ol[@class="search-results results"]/li/article/' +
                           'div/h1[@itemprop="headline"]/a/text()')
    urls = tree.xpath('//ol[@class="search-results results"]/li/article/' +
                      'div/h1[@itemprop="headline"]/a/@href')
    dates = tree.xpath('//ol[@class="search-results results"]/li/' +
                       'article/aside[@class="flags top"]/' +
                       'dl/dd/time[@class="display-date"]/@datetime')
    return(headlines, urls, dates)

def convert_bbc_news(headlines, urls, dates):
    """ Convert the three lists into a JSON like list of dictionaries """
    data = []
    for i in range(len(headlines)):
        d = {'headline': headlines[i],
             'url': urls[i],
             'date': parse(dates[i])}
        data.append(d)
    return(data)

def filter_yesterday(bbc_data):
    """ Returns only bbc news articles published yesterday """
    new_data = []
    for item in bbc_data:
        yesterday = datetime.date.today() - datetime.timedelta(days = 1)
        if item['date'].date() == yesterday:
            new_data.append(item)
    return(new_data)

def scrape_bbc_yesterday_multiple_keywords():
    keywords = ['transport', 'road', 'rail', 'dft', 'airport', 'freight',
    'car', 'train', 'plane', 'maritime', 'walk', 'cycle' ]
    data = []
    for keyword in keywords:
        print(keyword)
        headlines, urls, dates = get_bbc_news(keyword, 5)
        d = convert_bbc_news(headlines, urls, dates)
        data.extend(filter_yesterday(d))
    # Drop duplicates
    # https://stackoverflow.com/questions/7090758/python-remove-duplicate-dictionaries-from-a-list
    data = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in data)]
    return(data)

def push_to_mongo(data, collection_name):
    db = MongoClient().test # db is named test
    if len(data) > 0:
        result = db[collection_name].insert_many(data)
        print('inserted ' + str(len(result.inserted_ids)))

if __name__ == '__main__':
    bbc_articles = scrape_bbc_yesterday_multiple_keywords()
    push_to_mongo(bbc_articles, 'news.bbc')
