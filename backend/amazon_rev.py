from bs4 import BeautifulSoup
from urllib2 import urlopen
from pymongo import MongoClient
import re
from datetime import datetime

amazon_link = "http://www.amazon.in/product-reviews/%s/ref=cm_cr_pr_viewopt_srt?ie=UTF8&showViewpoints=1&sortBy=helpful&pageNumber=%d"


client = MongoClient('mongodb://localhost:27017/')

db = client.revmine
reviews = db.reviews
done = db.done
recom = db.recom

def main(pid):
    if db.reviews.find({'_id':pid}).count()==0:
        doit(pid)

def extract_text(li):

    # Page 1 soup!
    url_ = amazon_link % (li["_id"], 1)
    print "Trying " + url_ + " now!"
    while(1):
        try:
            soup = BeautifulSoup(urlopen(url_).read())
            break
        except:
            continue
    li['title'] = soup('span', {'class': 'a-text-ellipsis'})[0].a.text

    # will scrape reviews' text
    for j, row in enumerate(soup('span', {'class': 'review-text'})):
        li[str(j + 1)] = row.text

    return li

def doit(pid):

    # picking an object from the queue
    product_asin = pid
    li = {}
    li["_id"] = product_asin
    li = extract_text(li)

    inserted_review = reviews.insert_one(li).inserted_id
    assert(inserted_review == product_asin)
