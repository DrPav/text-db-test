from lxml import html
import requests
from dateutil.parser import parse
import datetime
from pymongo import MongoClient
import logging

keywords = ['transport', 'road', 'rail', 'dft', 'airport', 'freight',
'car', 'train', 'plane', 'maritime', 'walk', 'cycle' ]

def get_bbc_news(keyword, page_num = 1):
    """ Collect up to n_articles articles headlines with their url and date.
    It uses the bbc search page and filters to news articles. It is not sorted
    in alphabetical order so 50 articles are collected to cover the last few
    days """

    request_url = ('http://www.bbc.co.uk/search?q=' + keyword +
        '&filter=news&page=' + str(page_num)) # 10 articles per page
    logging.debug('Requesting ' + request_url)
    page = requests.get(request_url)
    tree = html.fromstring(page.content)
    headlines = tree.xpath('//ol[@class="search-results results"]/li/article/' +
                           'div/h1[@itemprop="headline"]/a/text()')
    urls = tree.xpath('//ol[@class="search-results results"]/li/article/' +
                      'div/h1[@itemprop="headline"]/a/@href')
    dates = tree.xpath('//ol[@class="search-results results"]/li/' +
                       'article/aside[@class="flags top"]/' +
                       'dl/dd/time[@class="display-date"]/@datetime')
    logging.debug('Number of headlines returned: ' + str(len(headlines)))
    return(headlines, urls, dates)

def convert_scraped_news(headlines, urls, dates):
    """ Convert the three lists into a JSON like list of dictionaries """
    logging.debug('Converting scraped news into dict')
    data = []
    for i in range(len(headlines)):
        d = {'headline': headlines[i],
             'url': urls[i],
             'date': parse(dates[i])
            }
        data.append(d)
    return(data)

def filter_yesterday(news_data):
    """ Returns only news articles published yesterday. Takes data in the
    format produced by convert_scraped_news() """
    logging.debug('Filtering for yesterdays news')
    new_data = []
    yesterday = datetime.date.today() - datetime.timedelta(days = 1)
    for item in news_data:
        if item['date'].date() == yesterday:
            new_data.append(item)
    return(new_data)

def add_type_source(news_data, source):
    logging.debug('Recording the source as: ' + source)
    for i, item in enumerate(news_data):
        news_data[i] = {'type': 'news',
                        'source': source,
                        'item:': item}
    return(news_data)

def scrape_bbc_yesterday_multiple_keywords():
    logging.debug('Getting multiple bbc articles')
    data = []
    for keyword in keywords:
        for page_num in [1,2,3]:
            logging.info('Page ' + str(page_num) +
                         ', Search Term: ' + keyword)
            headlines, urls, dates = get_bbc_news(keyword, page_num)
            d = convert_scraped_news(headlines, urls, dates)
            data.extend(filter_yesterday(d))
    # Drop duplicates
    # https://stackoverflow.com/questions/7090758/python-remove-duplicate-dictionaries-from-a-list
    logging.debug('Removing duplicates')
    data = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in data)]
    data = add_type_source(data, 'bbc')
    return(data)

def scrape_bbc_pages_multiple_keywords(n_pages = 30):
    logging.info('Number of bbc articles pages to fetch: ' + str(n_pages))
    data = []
    for keyword in keywords:
        for page_num in range(n_pages):
            ogging.info('Page ' + str(page_num) +
                         ', Search Term: ' + keyword)
            headlines, urls, dates = get_bbc_news(keyword, page_num + 1)
            d = convert_scraped_news(headlines, urls, dates)
            data.extend(d)
    # Drop duplicates
    # https://stackoverflow.com/questions/7090758/python-remove-duplicate-dictionaries-from-a-list
    logging.debug('Removing duplicates')
    data = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in data)]
    data = add_type_source(data, 'bbc')
    return(data)

def get_guardian_news(guardian_url = 'https://www.theguardian.com/uk/transport'):
    """ Collect the headlines and dates and article url for news on the
    gardian website uk transport section """
    logging.debug('Requesting ' + request_url)
    page = requests.get(guardian_url)
    tree = html.fromstring(page.content)
    headlines = tree.xpath('//div[@class="fc-item__container"]/' +
                           'a[@class = "u-faux-block-link__overlay js-headline-text"]/' +
                           'text()')
    urls = tree.xpath('//div[@class="fc-item__container"]/' +
                           'a[@class = "u-faux-block-link__overlay js-headline-text"]/' +
                           '@href')
    dates = tree.xpath('//div[@class="fc-item__container"]/' +
                       'div[@class="fc-item__content"]/aside/time/@datetime')
    logging.debug('Number of headlines returned: ' + str(len(headlines)))
    return(headlines, urls, dates)

def scrape_guardian_yesterday():
    a,b,c = get_guardian_news()
    guardian_data = convert_scraped_news(a,b,c)
    guardian_data = filter_yesterday(guardian_data)
    guardian_data = add_type_source(guardian_data, 'guardian')
    return(guardian_data)

def scrape_guardian_pages(n_pages = 45):
    """ Scrape through guardian transport pages """
    logging.info('Number of guardian pages to fetch: ' + str(n_pages))
    data = []
    for i in range(n_pages):
        print("Getting guardian transport page" + str(i))
        url = 'https://www.theguardian.com/uk/transport?page=' + str(i + 1)
        headlines, urls, dates = get_guardian_news(url)
        d = convert_scraped_news(headlines, urls, dates, 'guardian')
        data.extend(d)
    # Drop duplicates
    data = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in data)]
    data = add_type_source(data, 'guardian')
    return(data)
