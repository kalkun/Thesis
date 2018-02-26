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

def main(files, images_dir=None, **kwargs):
    header = []
    for i in range(10):
        for j in range(1, 3):
            header.append("image_%s-%s" % (i, j))
    print(header)
    rows = []
    rows.append(header)

    rows = make_pairs(files, rows)

    with open(kwargs['output_csv'], "w") as f:
        csvwriter = csv.writer(f, delimiter=";")
        csvwriter.writerows(rows)

def make_pairs(files, rows):
    pairs = {}
    def all_paired():
        for k, v in pairs.items():
            if v < 10:
                return False
        return len(pairs.items()) == len(files)

    def increment_pairs(name):
        if name in pairs:
            pairs[name] += 1
        else:
            pairs[name] = 1

    while not all_paired():
        bag = set(files)
        exhausted = []
        for k, v in pairs.items():
            if v == 10:
                exhausted.append(k)

        bag = bag.difference(set(exhausted))

        if len(bag) < 10:
            # if there are less than ten to draw from
            # then we cannot meaningfully create more rows
            print("_" * 80)
            print("Less than 10 images with less than 10 pairs, exiting")
            return rows

        row = []



        # create new row:
        for i in range(10):
            i = random.randint(0, len(bag) -1)
            j = i
            while j == i:
                # just to make sure that we continue
                # drawing random numbers even if i and
                # j ends up being equal - also by chance.
                j = random.randint(0, len(bag) -1)

            img_i = list(bag)[i]
            img_j = list(bag)[j]
            increment_pairs(img_i)
            increment_pairs(img_j)

            row.append(img_i)
            row.append(img_j)

        rows.append(row)

    print("_" * 80)
    print("All paired, exiting")

    return rows


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
