""" A simple commandline interface for scraping images

    You pass a folder where the images will be saved on, 
    multiple keywords and multiple search engines. This little guy does the
    rest.
"""
import os
import urllib.request
import imagehash
import serpscrap
from PIL import Image
from bs4 import BeautifulSoup
import json
import pprint


class Scraper:

	def __init__(self, keywords, folder, n_pages_per_keyword = 1, limitRes = -1):
		self.keywords = keywords
		self.limitRes = limitRes
		self.folder = folder
		self.n_pages_per_keyword = n_pages_per_keyword
		self.config = serpscrap.Config()
		self.config.set('search_type', 'image')
		self.config.set('num_pages_for_keyword', self.n_pages_per_keyword)
		self.config.set( 'sleeping_min', 2)
		self.config.set('sleeping_max', 5)
		self.scrap = serpscrap.SerpScrap()
		self.bing_base_url = "http://www.bing.com/images/search?q=" 
		self.bing_end_url = "&FORM=HDRSC2"
		self.bing_header ={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
		createFolder(self.folder) 
	

	def scrape(self, searchEng):
		if (searchEng == 'google'):
			print('\n')
			for keyword in self.keywords:
				self.scrapeGoogle(keyword)
			print('-' * 80)
			print('\n')
		elif(searchEng == 'bing'):
			print('\n')
			for keyword in self.keywords:
				self.scrapeBing(keyword)
			print('-' * 80)
			print('\n')
		else:
			print("no handlers for " + str(searchEng))

	def scrapeBing(self,keyword):
		print("scraping keyword: " + keyword + " on bing")
		print('\n')
		query= keyword.split()
		query='+'.join(query)
		for x in range(1,self.n_pages_per_keyword + 1):
			print("page " + str(x) + " out of " + str(self.n_pages_per_keyword))
			first = x * 35 - 34
			count = first + 34
			query_url = self.bing_base_url + query + self.bing_end_url + "&first=" + str(first) + "&count=" + str(count)
			print(query_url)
			soup = get_soup(query_url,self.bing_header)
			for a in soup.find_all("a",{"class":"iusc"})[:self.limitRes]:
				mad = json.loads(a["mad"])
				url = mad["turl"]
				#print(url)
				print("downloading url: " + url)
				saveImageFromUrl(url, self.folder)
			print('-' * 80)
			print('\n')

	def scrapeGoogle(self, keyword):
		print("scraping keyword: " + keyword + " on google")
		print('\n')
		self.scrap.init(config=self.config.get(), keywords= [keyword])
		self.results = self.scrap.run()
		for result in self.results[:self.limitRes]:
			#pprint.pprint(result)
			url = result['serp_url']
			print("downloading url: " + url)
			print("image " + str(result['serp_rank']) + " out of " + str(result['query_num_results_page'])\
				+ " of page " + str(result['query_page_number']) + " out of " + str(self.n_pages_per_keyword))
			saveImageFromUrl(url, self.folder)
		print('-' * 80)
		print('\n')

def saveImageFromUrl(url, folder):

	try:
		imgpath, headers = urllib.request.urlretrieve(url)
		img = Image.open(imgpath)
		imgHash = str(imagehash.average_hash(img))
		print(imgHash)
		filename = imgHash + '.' + img.format
		path = os.path.join(folder, filename)
		img.save(path)
	except Exception as e:
		print(e)
		print("somenthing went wrong scraping the image url")

def createFolder(folder_path):
	if (not os.path.exists(folder_path)):
		os.mkdir(folder_path)

def get_soup(url,header):
	#return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)),
	# 'html.parser')
	return BeautifulSoup(urllib.request.urlopen(
	    urllib.request.Request(url,headers=header)),
	'html.parser')
