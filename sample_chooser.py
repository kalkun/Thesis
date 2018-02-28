
from protestDB import cursor
from protestDB import models
from imagehash import dhash
import argparse
import os
from PIL import Image
from collections import defaultdict
import random
import shutil

def hamming(s1, s2):
    """Calculate the Hamming distance between two bit strings"""
    assert len(s1) == len(s2)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def removeSimilarImages(image_list, folder_source):
	#print ("processing hashes")
	original_images = {}
	original_hashes = []
	for idx, image in enumerate(image_list):
		#print("processing image hash ", image.name, " index ", idx, " out of ", len(image_list))
		path = os.path.join(folder_source, image.name)
		hashh = str(dhash(Image.open(path)))
		original_hashes.append(hashh)
		original_images[hashh] = image

	result_hashes = list(original_hashes)
	#print("processing comparisons")
	for idx, hash1 in enumerate(original_hashes):
		#print("processing hash similiarity to ", hash1, " index ", idx, " out of ", len(original_hashes))
		for jdx in range(idx + 1, len(original_hashes)):
			hash2 = original_hashes[jdx]
			dist = hamming(hash1, hash2)
			similarity = (16 - dist) * 100 / 16
			#print(similarity)
			if (similarity > 38):
				try:
					result_hashes.remove(hash2)
				except Exception as e:
					pass
	result = []
	for hashh in result_hashes:
		result.append(original_images[hashh])

	return result


def main(folder_source, folder_dest, seed):
	random.seed(seed)
	pc = cursor.ProtestCursor()
	images = pc.query(models.Images).join(models.ProtestNonProtestVotes,models.ProtestNonProtestVotes.imageID ==
	models.Images.imageHASH).filter(models.ProtestNonProtestVotes.is_protest == 1) # gets protest images

	img_list = []
	for image in images:
		img_list.append(image)

	temp_list = removeSimilarImages(img_list, folder_source)

	random.shuffle(temp_list)
	#print("result size is ", len(temp_list))

	shutil.rmtree(folder_dest)

	if not os.path.exists(folder_dest): # creates folder to store sample
		os.makedirs(folder_dest)

	for img in temp_list[0:1000]:
		path = os.path.join(folder_dest, img.name) #save sample
		img.get_image().save(path)
		print(img.imageHASH)




if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description=""
	)
	parser.add_argument(
		"dir_source",
		type = str,
	)
	parser.add_argument(
		"--dir_dest",
		type = str,
		default = "sample"
	)
	parser.add_argument(
		"--seed",
		type = int,
		default = 3000
	)
	args = parser.parse_args()
	main(args.dir_source, args.dir_dest, args.seed)