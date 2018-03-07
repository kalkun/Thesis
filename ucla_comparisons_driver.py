

"""This is script is used to insert scores from UCLA into the db based on the csv file they've sent us """

import argparse
import csv
from protestDB import cursor
from protestDB import models

PATH_TO_FILE = "ucla_files/pairwise_annot.csv"

def main(csv_path, add_to_db):

	pc = cursor.ProtestCursor()


	with open(csv_path, 'r') as f:
		reader = csv.reader(f, delimiter = ',', quotechar = '"')
		header = {}
		header_input = next(reader)
		for k, v in enumerate(header_input):
			header[v] = k
		for row in reader:
			img1_name = row[header["image1"]]
			img2_name = row[header["image2"]]
			win1 = row[header["win1"]]
			win2 = row[header["win2"]]
			tie = row[header["tie"]]

			#print(img1_name)

			try:
				img1_hash = pc.queryImages().filter(models.Images.name == img1_name).one_or_none().imageHASH
			except Exception as e:
				print(img1_name)

			try:
				img2_hash = pc.queryImages().filter(models.Images.name == img1_name).one_or_none().imageHASH
			except Exception as e:
				print(img2_name)

			#print (img1, img2, win1, win2, tie)





if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='Annomaly detection script',
	    description='This is script is used to insert scores from UCLA into the db based on the csv file\
	    sent by them'
	)
	parser.add_argument(
		'--csv_path',
	    metavar='path',
	    help='Path to the csv file',
	    default = PATH_TO_FILE
	)
	parser.add_argument(
		'--db',
	    help='flag, if true it will ad to db',
	    action="store_true"
	)
	args = parser.parse_args()
	main(args.csv_path, args.db)