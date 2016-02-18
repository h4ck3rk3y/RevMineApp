from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime

amazon_link = "http://www.snapdeal.com/product/%s/%s/ratedreviews?page=%d&sortBy=HELPFUL&ratings=1,2,3,4,5#defRevPDP"


client = MongoClient('mongodb://localhost:27017/')

db = client.revmine


def extract_text(pid, product_name):
	list_of_reviews = []
    for page in range(1,6):
        url_ = amazon_link % (product_name, pid, page)
        try:
        	response = requests.get(url)
        	if response.status == 200:
        		soup = BeautifulSoup(response.text)
        	else:
        		continue
        except:
        	print 'something awful just happened'


        li['title'] = soup('span', {'class': 'section-head customer_review_tab'})[0].a.text
        # will scrape reviews' text
        for j, row in enumerate(soup('div', {'class': 'user-review'})):
            li[str((page-1)*10 + (j + 1))] = {}
            li[str((page-1)*10 + (j + 1))]['text'] = row.p.text

        li['domain'] = 'snapdeal'
    return li

def doit(pid, product_name):

    list_of_reviews = extract_text(pid, product_name)
    inserted_review = reviews.insert_one(list_of_reviews).inserted_id
    assert(inserted_review == pid)