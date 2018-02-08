	
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
		'--sr','--list', 
		nargs='+',
		metavar = 'seareng',
		default = ['google'],
		help='search engines separated by spaces')

	parser.add_argument(
	    '--npages',
	    help='The number of page results to be scraped',
	    default='1',
	)
	parser.add_argument(
	    '--limitres',
	    help='Limit the number of results to a given number',
	    default='-1',
	    type = int,
	)
	args = parser.parse_args()
	print(args.sr)
	scraper = keyword_scraper.Scraper(args.key_words, args.download_folder, args.npages, args.limitres)
	
	for searchEng in args.sr:
		scraper.scrape(searchEng)
	


if __name__ == '__main__':
	main()