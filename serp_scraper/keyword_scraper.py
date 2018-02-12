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
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys


class Scraper:

	def __init__(self, keywords, folder, n_images):
		self.keywords = keywords
		self.n_images = n_images
		self.folder = folder
		self.bing_results_per_page = 35
		self.google_base_url = "https://www.google.co.in/search?q="
		self.google_end_url = "&source=lnms&tbm=isch"
		self.bing_base_url = "http://www.bing.com/images/search?q=" 
		self.bing_end_url = "&FORM=HDRSC2"
		self.bing_header ={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
		self.google_header = {"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}
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
		current_image = 1
		while (True):	
			first = current_image * 35 - 34
			count = first + 34
			query_url = self.bing_base_url + query + self.bing_end_url + "&first=" + str(first) + "&count=" + str(count)
			soup = get_soup(query_url,self.bing_header)
			for a in soup.find_all("a",{"class":"iusc"}):
				mad = json.loads(a["mad"])
				url = mad["turl"]
				#print(url)
				print("(image " + str(current_image) + " out of " + str(self.n_images) + ")" + "downloading url: " + url)
				saveImageFromUrl(url, self.folder)
				if(current_image >= self.n_images):
					print('-' * 80)
					print('\n')
					return
				current_image += 1

	def scrapeGoogle(self, keyword):
		print("scraping keyword: " + keyword + " on google")
		print('\n')
		query= keyword.split()
		query='+'.join(query)
		number_of_scrolls = int(self.n_images / 400 + 1)
		query_url = self.google_base_url + query + self.google_end_url
		driver = webdriver.Chrome()
		driver.get(query_url)

		img_count = 1
		element = driver.find_element_by_tag_name("body")
		# Scroll down
		for i in range(30):
		    element.send_keys(Keys.PAGE_DOWN)
		    time.sleep(0.3)  # bot id protection

		driver.find_element_by_id("smb").click()

		for i in range(50):
		    element.send_keys(Keys.PAGE_DOWN)
		    time.sleep(0.3)  # bot id protection

		time.sleep(0.2)

		# imges = driver.find_elements_by_xpath('//div[@class="rg_meta"]') # not working anymore
		imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
		for img in imges:
			url = json.loads(img.get_attribute('innerHTML'))["ou"]
			print("(image " + str(img_count) + " out of " + str(self.n_images) + ")" + "downloading url: " + url)
			saveImageFromUrl(url, self.folder)
			img_count += 1

			if (img_count > self.n_images):
				break
		driver.quit()


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


