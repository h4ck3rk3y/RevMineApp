from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime
from util import get_price_range,make_soup
from tornado import ioloop, httpclient
import functools

amazon_link = "http://www.amazon.in/product-reviews/%s?sortBy=helpful&pageNumber=%d"

client = MongoClient('mongodb://localhost:27017/')
db = client.revmine_2
reviews = db.reviews
done = db.done
recom = db.recom

def get_details(all_products_url):

	soup = make_soup(all_products_url)
	res = soup.findAll('li',{'class':'s-result-item'})
	related_products = []

	for i in res:
		try:
			name = i.find_all('a',{'class':"a-link-normal s-access-detail-page  a-text-normal"})
			cost = i.find_all('span',{'class':'a-size-base a-color-price s-price a-text-bold'})
			stars = i.find_all('span',{'class':"a-icon-alt"})

			image = i.find_all('img')
			product = {}
			product['name'] = name[0]['title']
			if len(name) == 0:
				continue
			product['link'] = name[0]['href']
			if len(cost) == 0:
				continue
			product['price'] = float(cost[-1].text.strip().replace(",",""))
			product['rating'] = float(stars[0].text.split()[0])
			product['value'] = float(product['price'])/float(product['rating'])
			product['image'] = image[0]['src']
			related_products.append(product)
		except:
			import traceback; traceback.print_exc();
			pass
	return related_products

def main(pid, domain):
	if db.reviews.find({'_id':pid, 'domain': domain}).count()==0:
		doit(pid)

def extract_text(pid, i, li):
	http_client = httpclient.AsyncHTTPClient()
	for page in range(1,6):
		url_ = amazon_link % (pid, page)
		li['i'] += 1
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
	# will scrape reviews' text
	li['title'] = soup('span', {'class': 'a-text-ellipsis'})[0].a.text
	p = re.compile('pageNumber=(\d+)')
	page = int(re.findall(p, response.effective_url)[0])

	for j, row in enumerate(soup('span', {'class': 'review-text'})):
		li[str((page-1)*10 + (j + 1))] = {}
		li[str((page-1)*10 + (j + 1))]['text'] = row.text

	for j, row in enumerate(soup('a', {'class': 'a-size-base a-link-normal review-title a-color-base a-text-bold'})):
		li[str((page-1)*10 + (j + 1))]['link'] = row['href']

def alternates(pid, li):
	#Extracting Alternatives!
	url = "http://www.amazon.in/dp/" + pid
	soup = 	make_soup(url)
	spans = soup.findAll('span',{'class': 'a-list-item'})
	for span in spans:
		links = span.find_all('a',{'class':'a-link-normal a-color-tertiary'})
		if len(links)>0:
			next_url = links[0]['href']
			category = links[0].text.strip()

	star_elements = soup.findAll('i',{'class':'a-icon a-icon-star a-star-4'})
	span = star_elements[0].find('span',{'class':'a-icon-alt'})
	stars = span.text.rstrip(' out of 5 stars')

	span = soup.findAll('span',{'class':'a-size-medium a-color-price'})
	if len(span) > 0:
		price = float(span[0].text.strip().replace(",",""))

	price_range = get_price_range(price)
	all_products_url = "http://amazon.in" + next_url + '&low-price=' + str(price_range[0]) + '&high-price=' + str(price_range[1])
	print all_products_url
	details = get_details(all_products_url)
	own_score = float(price)/float(stars)

	ranked = 0


	sorted_products = sorted(details, key = lambda x:x['value'])
	found = 0
	for x in sorted_products:
		ranked = ranked + 1
		if x['name'].strip() == li['title'].strip():
			found = 1
			break

	if found ==0:
			ranked = -1

	li['rank'] = ranked
	li['low-price'] = price_range[0]
	li['high-price'] = price_range[1]
	li['related_products'] = sorted_products[:10]
	li['category'] = category
	li['domain'] ='www.amazon.in'

def doit(pid):
	li = {}
	li['i'] = 0
	extract_text(pid, li)
	li['_id'] = pid
	alternates(pid, li)
	inserted_review = db.reviews.insert_one(li).inserted_id
	assert(inserted_review == pid)