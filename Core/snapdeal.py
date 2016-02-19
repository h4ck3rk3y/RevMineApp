from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime

snapdeal_link = "http://www.snapdeal.com/product/%s/%s/ratedreviews?page=%d&sortBy=HELPFUL&ratings=1,2,3,4,5#defRevPDP"


client = MongoClient('mongodb://localhost:27017/')

db = client.revmine

def main(pid, product_name, domain):
	if db.reviews.find({'_id':pid, 'domain': domain}).count()==0:
		doit(pid, product_name)

def extract_text(pid, product_name):
	li = {}
	for page in range(1,6):
		url_ = snapdeal_link % (product_name, pid, page)
		try:
			response = requests.get(url_)
			if response.status_code == 200:
				soup = BeautifulSoup(response.text)
			else:
				continue
		except:
			print 'something awful just happened'

		li['title'] = soup('span', {'class': 'section-head customer_review_tab'})[0].text
		# will scrape reviews' text
		for j, row in enumerate(soup('div', {'class': 'user-review'})):
			li[str((page-1)*10 + (j + 1))] = {}
			li[str((page-1)*10 + (j + 1))]['text'] = row.p.text
			li[str((page-1)*10 + (j + 1))]['link'] = url_


	li['domain'] = 'www.snapdeal.com'
	li['_id'] = pid
	return li


def doit(pid, product_name):

	list_of_reviews = extract_text(pid, product_name)
	inserted_review = db.reviews.insert_one(list_of_reviews).inserted_id
	assert(inserted_review == pid)