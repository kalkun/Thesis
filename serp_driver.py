	
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
		help='search engines separated by spaces. Default is google'
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
	    help='The number of images to be scraped per key word per search engine. Defaulted to 10 images',
	    default='10',
	    type = int,
	)

	parser.add_argument(
	    '--timeout',
	    help='Timeout in seconds. Defaulted to 10 seconds',
	    default='10',
	    type = float,
	)

	args = parser.parse_args()
	#print(args.key_words)
	scraper = keyword_scraper.Scraper(args.key_words, args.download_folder, args.n_images, args.timeout)
	
	for searchEng in args.sr:
		scraper.scrape(searchEng)
	


if __name__ == '__main__':
	main()