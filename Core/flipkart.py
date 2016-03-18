from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime
from util import make_soup
from tornado import ioloop, httpclient
import functools

flipkart_link = "http://www.flipkart.com/%s/product-reviews/%s?type=top&start=%d"

client = MongoClient('mongodb://localhost:27017/')

db = client.revmine_2


def main(pid, product_name, domain):
	if db.reviews.find({'_id':pid, 'domain': domain}).count()==0:
		doit(pid, product_name)

def extract_text(pid, product_name, li):
	http_client = httpclient.AsyncHTTPClient()
	for page in range(0,5):
		url_ = flipkart_link % (product_name, pid, page*10)
		print url_
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

	p = re.compile('start=(\d+)')
	page = int(re.findall(p, response.effective_url)[0])/10

	li['title'] = soup('img', {'onload':'img_onload(this);'})[0]["alt"]
	for j, row in enumerate(soup('span', {'class': 'review-text'})):
		li[str((page)*10 + (j + 1))] = {}
		li[str((page)*10 + (j + 1))]['text'] = row.text

	for j, row in enumerate(soup('a',text='Permalink')):
		li[str((page)*10 + (j + 1))]['link'] = row['href']


#Extracting Alternatives!
def alternates(product_name, pid, li):
	url = "http://www.flipkart.com/" + product_name + "/p/" + pid.lower()
	print url
	soup = make_soup(url)

	breadcrumb = soup.findAll('div',{'class':'breadcrumb-wrap line'})
	taxonomies = breadcrumb[0].find_all('a',{'class':'fk-inline-block'})
	all_products_url = taxonomies[-2]['href']
	category = taxonomies[-2].text.strip()

	my_price = float(soup.find('span',{'class':'selling-price omniture-field'})['data-evar48'])
	my_stars = float(soup.find('div',{'class':'bigStar'}).text)
	my_score = my_price/my_stars

	soup = make_soup('http://www.flipkart.com/' + all_products_url)
	price_ranges = soup.find('ul',{'id':'price_range'}).find_all('li',{'class':'facet'})
	for p in price_ranges:
		title = p['title']
		prices = [int(s) for s in title.split() if s.isdigit()]
		if len(prices) == 2 and my_price <= prices[1] and my_price > prices[0]:
			url_split = all_products_url.split('?')
			new_all_products_url = 'http://www.flipkart.com' + url_split[0] + "?p%5B%5D=facets.price_range%255B%255D%3DRs.%2B" + str(prices[0]) + "%2B-%2BRs.%2B" + str(prices[1]) + "&" + url_split[1]
			low_price = prices[0]
			high_price = prices[1]
			break
		if len(prices) == 1 and my_price >= prices[0] and 'Above' in title:
			url_split = all_products_url.split('?')
			new_all_products_url = 'http://www.flipkart.com' + url_split[0] + "?p%5B%5D=facets.price_range%255B%255D%3DRs.%2B" + str(prices[0]) + "%2Band%2BAbove&" + url_split[1]
			low_price = prices[0]
			high_price = 200000
			break
		if len(prices) == 1 and my_price <= prices[0] and 'Below' in title:
			url_split = all_products_url.split('?')
			new_all_products_url = 'http://www.flipkart.com' + url_split[0] + "?p%5B%5D=facets.price_range%255B%255D%3DRs.%2B" + str(prices[0]) + "%2Band%2BBelow&" + url_split[1]
			high_price = prices[0]
			low_price = 0
			break


	soup = make_soup(new_all_products_url)
	other_products = soup.findAll('div',{'class':'product-unit'})
	all_products = []
	for i in other_products:
		try:
			this_product = {}
			this_product['image'] = i.find('img')['data-src']
			this_product['price'] = float(i.find('span',{'class':'fk-font-17'}).text.lstrip('Rs. ').replace(",",""))
			this_product['rating'] = round(float(i('div', {'class': 'rating'})[0]['style'][6:-2])*0.05,2)
			name_title = i.find('div',{'class':'pu-title fk-font-13'}).find('a')
			this_product['name'] = name_title['title']
			this_product['link'] = 'http://www.flipkart.com' + name_title['href']
			this_product['value'] = float(this_product['price'])/float(this_product['rating'])
			all_products.append(this_product)
		except:
			import traceback; traceback.print_exc();
			pass



	sorted_products = sorted(all_products, key = lambda x:x['value'])

	ranked = 0
	found = 0
	for x in sorted_products:
		ranked = ranked + 1
		if  li['title'].strip()[:li['title'].strip().find(':')] in x['name'].strip():
			found = 1
			break

	if found ==0:
		ranked = -1

	position = ranked

	li['title'] = li['title'].strip()[:li['title'].strip().find(':')]
	li['domain'] = 'www.flipkart.com'
	li['_id'] = pid
	li['category'] = category
	li['rank'] = position
	li['low-price'] = low_price
	li['high-price'] = high_price
	li['related_products'] = sorted_products[:10]


def doit(pid, product_name):
	li = {}
	li['i'] = 0
	extract_text(pid, product_name, li)
	print 'extraction done?'
	alternates(product_name, pid, li)
	inserted_review = db.reviews.insert_one(li).inserted_id
	assert(inserted_review == pid)
