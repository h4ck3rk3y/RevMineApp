from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import re
from datetime import datetime
from util import make_soup

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
	

	#Extracting Alternatives!
	url = "http://www.flipkart.com/" + product_name + "/p/" + pid
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
		if len(prices) == 2 and my_price < prices[1] and my_price > prices[0]:
			url_split = all_products_url.split('?') 			
			new_all_products_url = 'http://www.flipkart.com' + url_split[0] + "?p%5B%5D=facets.price_range%255B%255D%3DRs.%2B" + str(prices[0]) + "%2B-%2BRs.%2B" + str(prices[1]) + "&" + url_split[1]					
			low_price = prices[0]
			high_price = prices[1]
			break
		if len(prices) == 1 and my_price > prices[0]:
			url_split = all_products_url.split('?') 			
			new_all_products_url = 'http://www.flipkart.com' + url_split[0] + "?p%5B%5D=facets.price_range%255B%255D%3DRs.%2B" + str(prices[0]) + "%2Band%2BAbove&" + url_split[1]	
			low_price = prices[0]
			high_price = 'Infinity!'
			break

	soup = make_soup(new_all_products_url)
	other_products = soup.findAll('div',{'class':'product-unit unit-4 browse-product new-design '})

	all_products = []
	for i in other_products:
		try:
			this_product = {}
			this_product['image'] = i.find('img')['data-src']
			this_product['price'] = float(i.find('span',{'class':'fk-font-17 fk-bold 11'}).text.lstrip('Rs. ').replace(",",""))
			this_product['stars'] = float(i.find('div',{'class':'fk-stars-small'})['title'].rstrip(' star'))
			name_title = i.find('div',{'class':'pu-title fk-font-13'}).find('a')
			this_product['name'] = name_title['title']
			this_product['link'] = 'http://www.flipkart.com' + name_title['href']
			this_product['value'] = float(this_product['price'])/float(this_product['stars'])
			all_products.append(this_product)
		except:
			pass

	my_dict = {'name':'Itself', 'price':my_price, 'stars':my_stars, 'link':url, 'value':my_score, 'image':'Dummy Image Url'}	
	
	exist_flag = 0	
	for i in all_products:	
		if i['link'] == url:
			exist_flag = 1
			break
	if exist_flag == 0:
		all_products.append(my_dict)

	sorted_products = sorted(all_products, key = lambda x:x['value'])
	position = sorted_products.index(my_dict)

	li['domain'] = 'www.flipkart.com'
	li['_id'] = pid
	li['category'] = category
	li['position'] = position
	li['low-price'] = low_price
	li['high-price'] = high_price
	li['related_products'] = sorted_products
	return li

def doit(pid, product_name):

	list_of_reviews = extract_text(pid, product_name)
	inserted_review = db.reviews.insert_one(list_of_reviews).inserted_id
	print 'yahan bhi aagaya'
	assert(inserted_review == pid)
