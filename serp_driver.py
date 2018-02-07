	
from serp_scraper.keyword_scraper import keyword_scraper
import argparse

def main():

	parser = argparse.ArgumentParser(
		prog='Keyword scraper',
	    description='Commandline line tool for scraping images from search engines',
	)
	parser.add_argument(
		'download_folder',
	    metavar='folder',
	    help='Path to the directory the images will be saved on, if it does not exist it will be created',
	)
	parser.add_argument(
		'key_words',
		metavar='kwords',
		help='The key words to be scraped, separated by a comma.',
	)

	parser.add_argument(
	    'search_engines',
	    metavar='seareng',
	    help='The search engines to be scraped from, separated by a comma.',
	)
	parser.add_argument(
	    '--npages',
	    help='The number of page results to be scraped',
	    default='1',
	)

	parser.add_argument(
	    '--limitres',
	    help='Limit the number of results to a given number',
	    default='-1',
	)
	args = parser.parse_args()
	print(dir(keyword_scraper))
	scraper = keyword_scraper.Scraper(args.key_words, args.search_engines, args.npages)
	scraper.scrape()
	scraper.downloadImages(args.download_folder, int(args.limitres))


if __name__ == '__main__':
	main()