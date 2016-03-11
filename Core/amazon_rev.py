from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime
from util import get_price_range,make_soup

amazon_link = "http://www.amazon.in/product-reviews/%s?sortBy=helpful&pageNumber=%d"


client = MongoClient('mongodb://localhost:27017/')

db = client.revmine_2
reviews = db.reviews
done = db.done
recom = db.recom


def get_details(all_products_url):

	soup = make_soup(all_products_url)
	res = soup.findAll('li',{'class':'s-result-item  celwidget '})

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
			product['price'] = float(cost[0].text.strip().replace(",",""))
			product['rating'] = float(stars[0].text.rstrip(" out of 5 stars"))
			product['value'] = float(product['price'])/float(product['rating'])
			product['image'] = image[0]['src']
			related_products.append(product)
		except:
			pass
	return related_products

def main(pid, domain):
	if db.reviews.find({'_id':pid, 'domain': domain}).count()==0:
		doit(pid)

def extract_text(li):
	count = 0
	for page in range(1,6):
		# Page 1 soup!
		url_ = amazon_link % (li["_id"], page)
		print "Trying " + url_ + " now!"
		try:
			response = requests.get(url_)
			if response.status_code==200:
				soup = BeautifulSoup(response.text)
			else:
				continue
		except:
			print 'continued'
			continue

		li['title'] = soup('span', {'class': 'a-text-ellipsis'})[0].a.text

		# will scrape reviews' text
		for j, row in enumerate(soup('span', {'class': 'review-text'})):
			li[str((page-1)*10 + (j + 1))] = {}
			li[str((page-1)*10 + (j + 1))]['text'] = row.text
			count +=1

		for j, row in enumerate(soup('a', {'class': 'a-size-base a-link-normal review-title a-color-base a-text-bold'})):
			li[str((page-1)*10 + (j + 1))]['link'] = row['href']
	li['count'] = count
	#Extracting Alternatives!
	url = "http://www.amazon.in/dp/" + li['_id']
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
	return li

def doit(pid):

	# picking an object from the queue
	product_asin = pid
	li = {}
	li["_id"] = product_asin
	li = extract_text(li)

	inserted_review = reviews.insert_one(li).inserted_id
	assert(inserted_review == product_asin)
