import datetime as dt
import hansardAPI as h

def fetch_yesterday():
    """ Script to run daily to fetch yesterdays hansard data """
    yesterday = str(dt.date.today() - dt.timedelta(days = 1))

    for url in h.hansard_urls:
        doc_type = url.replace('http://lda.data.parliament.uk/', 'hansard.') \
            .replace('.json', '')
        data = h.get_hansard_data(url, yesterday, yesterday)
        # Push data to db with the collection type of doc_type

if __name__ == "__main__":
    fetch_yesterday()