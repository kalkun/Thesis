#!/usr/bin/env python3
#
# Usage either through:
#   ```
#       ./amazon_input_driver.py --files <file with filenames>
#   ```
#   or:
#   ```
#      cat file_with_filenames.txt | ./amazon_input_driver.py
#   ```

import sys
import os
import random
import argparse
import csv

from protestDB.cursor import ProtestCursor
pc = ProtestCursor()

def checkValid(pairs, value1, value2, threshold):
	#print(pairs)
	#print(value1, value2, threshold)
    if (len(pairs[value1]) >= threshold or len(pairs[value2]) >= threshold):
        return False
    if (value1 in pairs[value2] or value2 in pairs[value1]):
        return False
    else:
        return True

def main(files, **kwargs):

    n_pairs = kwargs['k_pairs']

    pool = files * n_pairs
    random.shuffle(pool)
    header = []
    for i in range(10):
        for j in range(1, 3):
            header.append("image_%s-%s" % (i, j))
    rows = []
    rows.append(header)

    pairs = {}
    print("_" * 80)
    print("Starting")

    for i in files:
        pairs[i] = []

    for i in files:
        while (len(pairs[i]) < n_pairs):
            j = pool.pop()
            if (j == i):
                pool = [j] + pool
                continue

            if (checkValid(pairs, i, j, n_pairs)):
                pairs[i].append(j)
                pairs[j].append(i)
            else:
                pool = [j] + pool
                continue


    pairwise = []
    for k, v in pairs.items():
        for j in v:
            pairwise.append((k, j))
    random.shuffle(pairwise)
    row = []
    for pair in pairwise:
        row.append(pair[0])
        row.append(pair[1])
        if len(row) == 10:
            rows.append(row)
            row = []

    with open(kwargs['output_csv'], "w") as f:
        csvwriter = csv.writer(f, delimiter=";")
        csvwriter.writerows(rows)


    print("All done!")
    print("_" * 80)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Builds an input csvfile compatible with amazon MTurk"
    )

    parser.add_argument(
        "--files",
        type=str,
        help="A name of a file with image names separated by newline"
    )
    parser.add_argument(
        "--images-dir",
        default="images/",
        type=str,
        help="The path to the directory of the images (default: 'images/'"
    )
    parser.add_argument(
        "--output-csv",
        default="mturk-input.csv",
        type=str,
        help="The name of the output csv file (default: 'mturk-input.csv'"
    )
    parser.add_argument(
        "-k",
        "--k-pairs",
        default=10,
        type=int,
        help="The number of pairs to generate for each observation"
    )

    args = vars(parser.parse_args())

    if args['files'] is None:

        files = []
        for line in sys.stdin:
            fname = pc.getImage(line.strip()).name
            files.append(fname)

        args["files"] = files

    else:

        files = []
        with open(args["files"], "r") as f:
            for line in f:
                fname = pc.getImage(line.strip()).name
                files.append(fname)
        args["files"] = files



    main(**args)
