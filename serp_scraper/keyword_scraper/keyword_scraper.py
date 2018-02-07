""" A simple commandline interface for scraping images

    You pass a folder where the images will be saved on, 
    a single keyword and a single search engine. This little guy does the
    rest.
"""
import os
import urllib.request
import imagehash
import serpscrap
from PIL import Image


class Scraper:

	def __init__(self, keyword, searchEngine, n_pages_per_keyword = 1):
		self.keyword = keyword
		self.searchEngine = searchEngine
		self.n_pages_per_keyword = n_pages_per_keyword
		self.config = serpscrap.Config()
		self.scrap = serpscrap.SerpScrap()
		self.results = None

	def scrape(self):
		self.config.set('search_type', 'image')
		self.config.set('num_pages_for_keyword', self.n_pages_per_keyword)
		self.config.set('search_engines', [self.searchEngine])
		self.scrap.init(config=self.config.get(), keywords=[self.keyword])
		self.results = self.scrap.run()

	def downloadImages(self, folder, limit = -1):
		createFolder(folder)
		for result in self.results[:limit]:
			url = result['serp_url']
			print("downloading url: " + url)
			saveImageFromUrl(url, folder)

def saveImageFromUrl(url, folder):

	try:
		imgpath, headers = urllib.request.urlretrieve(url)
		img = Image.open(imgpath)
		imgHash = str(imagehash.average_hash(img))
		filename = imgHash + '.' + img.format
		path = os.path.join(folder, filename)
		img.save(path)
	except Exception as e:
		print(e)
		print("somenthing went wrong scraping the image url")

def createFolder(folder_path):
	if (not os.path.exists(folder_path)):
		os.mkdir(folder_path)

