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

def make_soup(all_products_url):
	r = requests.get(all_products_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})	
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
	
def get_ranks(pid, domain):
	
	url = "http://" + domain + '/dp/' + pid 
	r = requests.get(url)
	soup = 	BeautifulSoup(r.text)
	
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
	all_products_url = "http://" + domain + next_url + '&low-price=' + str(price_range[0]) + '&high-price=' + str(price_range[1])

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

print get_ranks('B011RG8SOU','www.amazon.in')
