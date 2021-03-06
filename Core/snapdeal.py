from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime
from util import get_price_range
snapdeal_link = "http://www.snapdeal.com/product/%s/%s/ratedreviews?page=%d&sortBy=HELPFUL&ratings=1,2,3,4,5#defRevPDP"
from tornado import ioloop, httpclient
import functools


client = MongoClient('mongodb://localhost:27017/')

db = client.revmine_2



def main(pid, product_name, domain):
	if db.reviews.find({'_id':pid, 'domain': domain}).count()==0:
		doit(pid, product_name)


def extract_text(pid, product_name, li):
	http_client = httpclient.AsyncHTTPClient()
	for page in range(1,6):
		url_ = snapdeal_link % (product_name, pid, page)
		print url_
		li['i']+=1
		cb = functools.partial(handler, li)
		http_client.fetch(url_, cb)
	ioloop.IOLoop.instance().start()

def handler(li, response):
	if response.code != 200:
		return
	li['i'] -= 1
	if li['i'] == 0:
		ioloop.IOLoop.instance().stop()
	soup = BeautifulSoup(response.body)

	p = re.compile('page=(\d+)')
	page = int(re.findall(p, response.effective_url)[0])
	li['title'] = soup('span', {'class': 'section-head customer_review_tab'})[0].text
	# will scrape reviews' text
	for j, row in enumerate(soup('div', {'class': 'user-review'})[2:]):
		li[str((page-1)*10 + (j + 1))] = {}
		li[str((page-1)*10 + (j + 1))]['text'] = row.p.text
		li[str((page-1)*10 + (j + 1))]['link'] = response.effective_url



def alternates(product_name, pid, li):
	related_products = []
	try:
		response = requests.get("http://www.snapdeal.com/product/%s/%s/"%(product_name,pid))
		new_soup = BeautifulSoup(response.text)
		price = new_soup('span', {'class', 'payBlkBig'})[0].text
		price = int(price.replace(',', ''))
		category_link = new_soup('a', {'class' : "bCrumbOmniTrack"})[-1]['href']  + "?sort=plrty&q=Price:" + ",".join([str(get_price_range(price)[0]),str(get_price_range(price)[1])])
		li['low-price'] = get_price_range(price)[0]
		li['high-price'] = get_price_range(price)[1]
		li['price'] = price
		li['category'] = new_soup('a', {'class' : "bCrumbOmniTrack"})[-1].span.text
		response = requests.get(category_link, headers= {'User-Agent': "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330"})
		new_soup = BeautifulSoup(response.text)

		stuff = new_soup('div', {'class': 'product-tuple-listing'})
		for x in stuff:
			try:
				temp_soup = BeautifulSoup(str(x))

				if temp_soup('img', {'class': 'product-image'})[0].has_attr('src'):
					image = temp_soup('img', {'class': 'product-image'})[0]['src']
				else:
					image = temp_soup('img', {'class': 'product-image'})[0]['lazysrc']

				for href in temp_soup.findAll('a'):
					if href.has_attr('data-position'):
						link = href['href']
						break

				name = temp_soup('p', {'class': 'product-title'})[0].text
				price = temp_soup('span',{'class': 'product-price'} )[0].text
				price = price.lstrip('Rs. ').replace(',', '')
				rating = temp_soup('div', {'class': 'filled-stars'})[0]['style'][6:-1]
				rating = float(rating) * 0.05
				related_products.append({'image': image, 'name': name, 'price': price, 'rating': round(rating,2), 'value': float(price)/rating, 'link': link})
			except:
				pass
				import traceback; traceback.print_exc();
		li['related_products'] = sorted(related_products,key=lambda k: k['value'])
		ranked = 0
		found = 0
		for x in li['related_products']:
			ranked = ranked + 1
			if x['name'].strip() == li['title'].strip():
				found = 1
				break
		if found ==0:
			ranked = -1
		li['rank'] = ranked
		li['related_products']  = li['related_products'][:10]


	except:
		import traceback; traceback.print_exc();
		print 'something awful happened getting related products'



	li['domain'] = 'www.snapdeal.com'
	li['_id'] = pid


def doit(pid, product_name):
	li = {}
	li['i'] = 0
	extract_text(pid, product_name, li)
	print 'extraction done?'
	alternates(product_name, pid,li)
	inserted_review = db.reviews.insert_one(li).inserted_id
	assert(inserted_review == pid)