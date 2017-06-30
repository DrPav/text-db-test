import requests
import datetime
from dateutil.parser import parse
import logging

hansard_urls = [
        'http://lda.data.parliament.uk/bills.json',
        'http://lda.data.parliament.uk/commonsoralquestions.json',
        'http://lda.data.parliament.uk/edms.json', #edm = early day motions
        'http://lda.data.parliament.uk/paperslaid.json',
        'http://lda.data.parliament.uk/answeredquestions.json',
        'http://lda.data.parliament.uk/publicationlogs.json',
        'http://lda.data.parliament.uk/researchbriefings.json',
        'http://lda.data.parliament.uk/epetitions.json'
        ]

def validate_date(date_text):
    """Checks the date format is YYYY-MM-DD"""
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def convert_dict_values(d):
    """ Convert from strings to dates, integers and booleans for a dictionary
    from the hansard api """
    for k, v in d.items():
        if type(v) == dict:
            if '_datatype' in v:
                if v['_datatype'] == 'dateTime':
                    v['_value'] = parse(v['_value'])
                elif v['_datatype'] == 'boolean':
                    v['_value'] = (v['_value'][0] == 't')
                elif v['_datatype'] == 'integer':
                    v['_value'] = int(v['_value'])
            else:
                convert_dict_values(v)
    return(d)

def get_hansard_data(hansard_url, min_date, max_date):
    """Fetches a json containing data from a hansard url since the min date
    to the max date (inlcuding those dates) """
    validate_date(min_date)
    validate_date(max_date)
    logging.info(hansard_url)
    counter = 0
    logging.info("getting first page")

    r = requests.get(hansard_url, params = {'min-date': min_date,
                                            'max-date': max_date},
        timeout = 60)
    logging.info(r.url)

    #https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    if r.status_code // 100 != 2:
        return()
    counter +=1

    """result is a dictionary. The key 'result' has the data, the other keys
    are meta data about the request. 'items'contains a list of all the data
    'next' is the url to get the next 10 results. Examine the json or docs
    to see all fields """
    result = r.json()['result']
    results = result['items']
    num_results = result['totalResults']

    more_results = 'next' in result
    while more_results == True:
        logging.info("getting result " + str(counter) + str(" of ") +
              str(num_results // 10))
        r = requests.get(result['next'], timeout = 60)
        if r.status_code // 100 != 2:
            more_results = False
        else:
            counter += 1
            result = r.json()['result']
            results += result['items']
            num_results = result['totalResults']
            more_results = 'next' in result
    # Fill in type and source
    for i, result in enumerate(results):
        results[i] = {'type': "hansard",
                      'source': hansard_url,
                      'item': result }


    return(results)

def convert_all_values(list_of_dicts):
    """ Convert all datatypes in entire list of dicts read from hansard API"""
    new_list = []
    logging.debug('Converting datatypes')
    for i in list_of_dicts:
        new_list.append(convert_dict_values(i))
    return(new_list)
