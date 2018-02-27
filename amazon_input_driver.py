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

url = "https://s3.eu-central-1.amazonaws.com/ecb-protest/"

def checkValid(pairs, value1, value2, threshold):
    if (len(pairs[value1]) >= threshold or len(pairs[value2]) >= threshold):
        return False
    if (value1 in pairs[value2] or value2 in pairs[value1]):
        return False

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

    # Initialize pairs
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


    build_url = lambda name: url + name

    pairwise = set()
    for k, v in pairs.items():
        for j in v:
            pair = sorted([k, j])
            pairwise.update([":".join(pair)])

    pairwise = list(pairwise)

    random.shuffle(pairwise)
    row = []
    for pair in pairwise:
        pair = pair.split(":")
        img_a = pair[0]
        img_b = pair[1]
        row.append(build_url(img_a))
        row.append(build_url(img_b))
        if len(row) == 20:
            rows.append(row)
            row = []

    with open(kwargs['output_csv'], "w") as f:
        csvwriter = csv.writer(f, delimiter=",")
        csvwriter.writerows(rows)


    if kwargs['debug']:
        for k, v in pairs.items():
            print("%35s: %-15s" % (k, len(v)))
    print("\nAll done!")
    print("Number of rows: %s" % len(rows))
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Increase verbosity for debugging"
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
