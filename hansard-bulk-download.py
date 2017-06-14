import json
import os
import hansardAPI as h
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


if __name__ == '__main__':
    get_all_hansard_data('2017-04-10', '2017-05-25')
    
    # Convert values for one of them
    with open('bulk-data/commonsoralquestions.json', 'r') as f:
        x = json.loads(f.read())
    output = h.convert_all_values(x)
    # Then push to DB
    



# Still need to edd error and timeout handling
# Proper logging instead of print to screen



