from bs4 import BeautifulSoup
import requests

def get_price_range(price):
	
	if price >= 0 and price < 1000:
		return (price-100,price+100)
	if price >= 1000 and price < 5000:
		return (price-750,price+750)
	if price >= 5000 and price < 10000:
		return (price-1250,price+1250)
	if price >= 10000 and price < 20000:
		return (price-2000,price+2000)
	if price >= 20000 and price < 40000:
		return (price-5000,price+5000)
	if price >= 40000 and price < 60000:
		return (price-6000,price+6000)
	if price >= 60000:
		return (0.9*price,1.15*price)

def make_soup(url):
	r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})	
	return BeautifulSoup(r.text.encode('utf-8'))
			
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
			product['stars'] = float(stars[0].text.rstrip(" out of 5 stars"))
			product['score'] = float(product['price'])/float(product['stars'])			
			product['image'] = image[0]['src']			
			related_products.append(product)
		except:
			pass
	return related_products
	
def get_amazon_ranks(pid):
	
	url = "http://www.amazon.in/dp/" + pid 
	soup = 	make_soup(url)
	
	spans = soup.findAll('span',{'class': 'a-list-item'})
	for span in spans:
		links = span.find_all('a',{'class':'a-link-normal a-color-tertiary'})
		if len(links)>0:
			next_url = links[0]['href']
	
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

	my_dict = {'name':'Itself', 'price':price, 'stars':stars, 'link':url, 'score':own_score, 'image':'Dummy Image Url'}	
	details.append(my_dict)

	sorted_products = sorted(details, key = lambda x:x['score'])
	position = sorted_products.index(my_dict)
	sorted_products.remove(my_dict)
	final = {}
	final['position'] = position
	final['low-price'] = price_range[0]
	final['high-price'] = price_range[1]
	final['items'] = sorted_products
	return final

def get_flipkart_ranks(pid, name):
	
	url = "http://www.flipkart.com/" + name + "/p/" + pid
	soup = make_soup(url) 	

	breadcrumb = soup.findAll('div',{'class':'breadcrumb-wrap line'})
	taxonomies = breadcrumb[0].find_all('a',{'class':'fk-inline-block'})
	all_products_url = taxonomies[-2]['href']

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
			this_product['score'] = float(this_product['price'])/float(this_product['stars'])
			all_products.append(this_product)
		except:
			pass

	my_dict = {'name':'Itself', 'price':my_price, 'stars':my_stars, 'link':url, 'score':my_score, 'image':'Dummy Image Url'}	
	all_products.append(my_dict)

	sorted_products = sorted(all_products, key = lambda x:x['score'])
	position = sorted_products.index(my_dict)
	sorted_products.remove(my_dict)
	final = {}
	final['position'] = position
	final['low-price'] = low_price
	final['high-price'] = high_price
	final['items'] = sorted_products
	return final


#print get_amazon_ranks('B011RG8SOU')
#print get_flipkart_ranks('itmecyfvrvxrs3xy','dell-21-5-inch-ips-led-s2216h-monitor')
