import json
import datetime
from elasticsearch import Elasticsearch, helpers

def load_tweets(filename):

	raw_data = open(filename, "r").read()
	my_json = json.loads(raw_data)

	def convert_date(date_str):
		d = datetime.datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
		return d

	es_docs = []
	for item in my_json:
		item['created_at'] = convert_date(item['created_at'])
		item['user_created_at'] = convert_date(item['user_created_at'])
		x = {
		"op_type": "create",
		"_index": "tweets-test",
		"_type": "tweet",
		"_source": item}

		es_docs.append(x)


	es = Elasticsearch()
	res = helpers.bulk(es, es_docs)

	load_errors = res[1]

	def push_errors(error_list):
		es_docs = []
		for item in error_list:
			x = {
			"op_type": "create",
			"_index": "tweets-test",
			"_type": "load-errors",
			"error_text": str(item)
			}
			es_docs.append(x)

	if len(load_errors) > 0:
		push_errors(load_errors)

if __name__ == '__main__':
	load_tweets("good-morning-tweets.json")