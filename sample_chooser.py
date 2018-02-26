
from protestDB import cursor
from protestDB import models
from imagehash import average_hash
import argparse
import os
from PIL import Image
from collections import defaultdict
import random


def main(folder, seed):
	random.seed(seed)
	pc = cursor.ProtestCursor()
	images = pc.query(models.Images).join(models.ProtestNonProtestVotes,models.ProtestNonProtestVotes.imageID ==
	models.Images.imageHASH).filter(models.ProtestNonProtestVotes.is_protest == 1) # gets protest images

	non_clashing_images = {}
	clashes = defaultdict(list)
	counter = 0

	for image in images:
		counter += 1
		#print("processing ", image.name, counter)
		path = os.path.join(folder, image.name) # gets local path
		img = Image.open(path)
		a_hash = average_hash(img)
		
		if (a_hash in non_clashing_images): # this stores all the clashes if needed to visually inspect them
			clashes[a_hash].append(image)
			#first = img.show() #uncoment for visual inspection
			second_path = os.path.join(folder,non_clashing_images[a_hash].name)
			#second = Image.open(second_path).show() #uncoment for visual inspection
			#input("press somenthing")  #uncoment for visual inspection
		non_clashing_images[a_hash] = image

	#print(len(non_clashing_images))
	temp_list = []
	for img in non_clashing_images.values():
		temp_list.append(img.imageHASH)

	random.shuffle(temp_list)


	for im_hash in temp_list[0:1000]:
		print(im_hash)



if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description=""
	)
	parser.add_argument(
		"image_dir",
		type = str,
	)
	parser.add_argument(
		"--seed",
		type = int,
		default = 3000
	)
	args = parser.parse_args()
	main(args.image_dir, args.seed)