import requests
import json
import os
# API docs
# http://explore.data.parliament.uk/

start_date = '2017-04-01'
datasets = [
        'http://lda.data.parliament.uk/bills.json',
        'http://lda.data.parliament.uk/commonsoralquestions.json',
        'http://lda.data.parliament.uk/edms.json', #edm = early day motions
        'http://lda.data.parliament.uk/paperslaid.json',
        'http://lda.data.parliament.uk/answeredquestions.json',
        'http://lda.data.parliament.uk/publicationlogs.json',
        'http://lda.data.parliament.uk/researchbriefings.json',
        'http://lda.data.parliament.uk/epetitions.json'
        ]

def get_hansard_data(hansard_url, min_date):
    print(hansard_url)
    counter = 0
    print("getting result " + str(counter))

    r = requests.get(hansard_url, params = {'min-date': min_date})
    print(r.url)
    print('status code ' + str(r.status_code))
    if r.status_code // 100 != 2:
        return()
    counter +=1 

    result = r.json()['result']
    results = result['items']

    more_results = 'next' in result
    while more_results == True:
        print("getting result " + str(counter))
        r = requests.get(result['next'])
        if r.status_code // 100 != 2:
            more_results = False
        else:
            counter += 1
            result = r.json()['result']
            results += result['items']
            more_results = 'next' in result
    return(results)

if __name__ == '__main__':
    if not os.path.exists('bulk-data'):
        os.makedirs('bulk-data')
    for url in datasets:
        filename = url.replace('http://lda.data.parliament.uk/', 'bulk-data/')
        with open(filename, 'w') as f:
            results = get_hansard_data(
                    hansard_url = url, min_date = start_date)
            json.dump(results, f)



# Still need to edd error and timeout handling
# Proper logging instead of print to screen



