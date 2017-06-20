import scrapenews
import dateutil.parser
import datetime

def test_bbc_news_number_of_articles():
    """ Test a headline, url and date is collected for each article and that
    at least one article is returned """
    headlines, urls, dates = scrapenews.get_bbc_news('transport', 2)
    assert len(headlines) == len(urls) == len(dates) and len(headlines) > 0

def test_convert_bbc_news():
    """ Data transformation as expected """
    headlines = ['Headline A', 'Headline B']
    urls = ['www.a.com', 'www.b.com']
    dates = ['2017-06-13T08:38:45Z', '2017-06-19T12:33:02Z']
    data_expected = [
        {'headline': 'Headline A',
        'url': 'www.a.com',
        'date': dateutil.parser.parse('2017-06-13T08:38:45Z')
        },
        {'headline': 'Headline B',
        'url': 'www.b.com',
        'date': dateutil.parser.parse('2017-06-19T12:33:02Z')
        }]
    data_returned = scrapenews.convert_bbc_news(headlines, urls, dates)
    assert data_returned == data_expected

def test_filter_yesterday():
    """ Supply three dates. Only yesterdays should be returned """
    data_input = [
        {'headline': 'Today',
         'date': datetime.datetime.today(),
         'url': 'www.bbc.com'},
        {'headline': 'Yesterday',
         'date': datetime.datetime.today() - datetime.timedelta(days = 1),
         'url': 'www.bbc.com'},
        {'headline': 'Two days ago',
         'date': datetime.datetime.today() - datetime.timedelta(days = 2),
         'url': 'www.bbc.com'}
    ]
    data_output = scrapenews.filter_yesterday(data_input)
    assert len(data_output) == 1 and data_output[0]['headline'] == 'Yesterday'
