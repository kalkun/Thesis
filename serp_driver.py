	
from serp_scraper import keyword_scraper
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
		'--sr',
		nargs='+',
		metavar = 'search engines',
		default = ['google'],
		help='search engines separated by spaces'
	)

	parser.add_argument(
		'--key_words',
		nargs='+',
		metavar='kwords',
		required = True,
		help='The key words to be scraped, separated by a comma.',
	)

	parser.add_argument(
	    '--n_images',
	    help='The number of images to be scraped per key word per search engine',
	    default='10',
	    type = int,
	)

	args = parser.parse_args()
	#print(args.key_words)
	scraper = keyword_scraper.Scraper(args.key_words, args.download_folder, args.n_images)
	
	for searchEng in args.sr:
		scraper.scrape(searchEng)
	


if __name__ == '__main__':
	main()