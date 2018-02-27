import unittest
import argparse
import csv
from protestDB import cursor
from protestDB import models
from amazon_input_driver import url
import requests as req

PATH_CSV = "mturk-input.csv"


class TestTurkInput(unittest.TestCase):

	def setUp(self):
		self.pc = cursor.ProtestCursor()
		self.data = {}
		self.rows = []
		self.unique_images = set()
		with open(PATH_CSV, 'r') as f:
			csvreader = csv.reader(f, delimiter = ',')
			next(csvreader)
			for row in csvreader:
				row_dict = {}
				img_as = row[::2] # gets every second image
				img_bs = row[1::2] # gets every second image starting from index 1

				for i in range(len(img_as)):
					assert img_as[i] != img_bs[i], "there was a duplicate" # checks if there are pairs of the same image
					

					# ads the first image to the dictonary
					if (img_as[i] in self.data):
						self.data[img_as[i]].append(img_bs[i])
					else:
						self.data[img_as[i]] = [img_bs[i]]

					# ads the second image to the dictonary
					if (img_bs[i] in self.data):
						self.data[img_bs[i]].append(img_as[i])
					else:
						self.data[img_bs[i]] = [img_as[i]]
					
					# keep a count of how many times each image appears
					if img_as[i] in row_dict:
						row_dict[img_as[i]] += 1
					else:
						row_dict[img_as[i]] = 1

					if img_bs[i] in row_dict:
						row_dict[img_bs[i]] += 1
					else:
						row_dict[img_bs[i]] = 1


					self.unique_images.update([img_bs[i], img_as[i]])

				self.rows.append(row_dict)

	def test_image_has_10_pairs(self):
		for key in self.data:
			self.assertEqual(len(self.data[key]), 10)

	# This test should fail if a single image appears 5 times in one hit 
	def test_frequency_repetition(self):
		
		for dic in self.rows:
			for key in dic:
				self.assertLess(dic[key], 5)

	def test_unique_images(self):
		self.assertEqual(len(self.unique_images), 1000)

	def test_images_source(self):
		for image_name in self.unique_images:
			#print("img_name: ", image_name)
			img_hash = image_name[len(url):]
			#print("img_hash: ",img_hash)
			img = self.pc.queryImages().filter_by(name=img_hash).one()
			# remember, this is line below is based on the assumption that there is a one to one correspondence
			# between protestNonProtestVotes and image
			vote = self.pc.get(models.ProtestNonProtestVotes, imageID = img.imageHASH) 
			#print("img", img)
			# img = self.pc.getImage(img_hash)
			self.assertEqual(img.source, "Luca Rossi - ECB")
			self.assertEqual(vote.is_protest, True)

	#def test_image_available(self):
		""" Test that each image URL is available from Amazon S3
			at the provided URL. """
	#	for image_url in self.unique_images:
	#		self.assertTrue(req.get(image_url).ok, msg="Image should be available at '%s'" % image_url)


if __name__ == '__main__':
	unittest.main()
