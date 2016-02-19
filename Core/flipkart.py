from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime

flipkart_link = "http://www.flipkart.com/%s/product-reviews/%s?type=top&start=%d"


client = MongoClient('mongodb://localhost:27017/')

db = client.revmine

def main(pid, product_name, domain):
    if db.reviews.find({'_id':pid, 'domain': domain}).count()==0:
        doit(pid, product_name)

def extract_text(pid, product_name):
    li = {}
    for page in range(0,5):
        url_ = flipkart_link % (product_name, pid, page*10)
        print url_
        try:
            response = requests.get(url_)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text)
            else:
                continue
        except:
            print 'something awful just happened'

        li['title'] = soup('img', {'onload':'img_onload(this);'})[0]["alt"]

        for j, row in enumerate(soup('span', {'class': 'review-text'})):
            li[str((page)*10 + (j + 1))] = {}
            li[str((page)*10 + (j + 1))]['text'] = row.text

        for j, row in enumerate(soup('a',text='Permalink')):
            li[str((page)*10 + (j + 1))]['link'] = row['href']

    li['domain'] = 'www.flipkart.com'
    li['_id'] = pid
    return li

def doit(pid, product_name):

    list_of_reviews = extract_text(pid, product_name)
    inserted_review = db.reviews.insert_one(list_of_reviews).inserted_id
    print 'yahan bhi aagaya'
    assert(inserted_review == pid)