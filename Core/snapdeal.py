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
		price = soup('span', {'class', 'payBlkBig'})[0].text
		category_link = pages_link = soup('a', {'class' : "bCrumbOmniTrack"})[-1]['href']  + "?sort=plrty&q=Price:" + ",".get_price_range(price)

		related_products = []

		try:
			response = requests.get(category_link, headers= {'User-Agent': "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330"})
			new_soup = BeautifulSoup(response.text)

			items = new_soup('div', {'class': 'col-xs-6  product-tuple-listing js-tuple'})
			for x in items:
				temp_soup = BeautifulSoup(x)
				image = temp_soup('img', {'class': 'product-image'})[0]['src']
				name = temp_soup('p', {'class': 'product-title'})[0].text
				price = temp_soup('span',{'class': 'product-price'} )[0].text
				rating = temp_soup('div', {'class': 'filled-stars'})[0]['style'][6:-1]
				rating = float(rating) * 0.05
				related_products.append({'image': image, 'name': name, 'price': price, 'rating': rating, 'value': rating/float(price)})

		li['related_products'] = sorted(related_products,key=lambda k: k['value'], reverse=True)

		li['price'] = price
		li['category'] = soup('a', {'class' : "bCrumbOmniTrack"})[-1].span.text

		rank = 0

		for x in li['related_products']:
			rank = i + 1
			if x['name'] == li['title']:
				break
		li['rank'] = rank

		except:
			print 'something awful happened getting related products'




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