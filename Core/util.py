from bs4 import BeautifulSoup
import requests

def get_price_range(price):
	if price >= 0 and price < 1000:
		return (max(price-100,0),price+100)
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
		return (int(0.9*price),int(1.15*price))

def make_soup(url):
	r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})
	return BeautifulSoup(r.text.encode('utf-8'))

