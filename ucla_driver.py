#!/usr/bin/env python3

import os
import csv
import argparse
import configparser
config = configparser.ConfigParser()
config.read("alembic.ini")

from protestDB.cursor import ProtestCursor

def main(**kwargs):
    image_dir = config['alembic']['image_dir']
    ucla_dir  = kwargs['ucla_dir']
    full_path = os.path.join(image_dir, ucla_dir)

    pc = ProtestCursor()

    if not os.path.exists(full_path):
        raise ValueError(
            "Cannot find UCLA image folder '%s' in image directory '%s'" % (
                ucla_dir,
                image_dir,
            )
        )

    if not kwargs['no_test']:
        extract_rows("test", full_path)
    if not kwargs['no_train']:
        extract_rows("train", full_path, pc)

def extract_rows(name, full_path, pc):
    """ name should be either `train` or `test` since
        these are the only two prepended names for UCLA filenames
    """
    filename = "annot_%s.txt" % name
    with open(os.path.join(full_path, filename)) as f:
        csvreader = csv.reader(f, delimiter='\t')
        header = csvreader.__next__()
        for row in csvreader:
            parsed_row = parse_row(row, header)
            print("_" * 80)
            print("Inserting %s" % parsed_row['fname'])
            try:
                pc.insertImage(
                    path_and_name=os.path.join(full_path, "img/%s" % name, parsed_row['fname']),
                    source="UCLA",
                    origin="local",
                    label=parsed_row['violence'],
                    tags=["UCLA-%s" % name] + list(filter(
                        lambda x: not x is None,
                        [ k if v == 1 else None
                          for k, v in parsed_row.items()
                        ]
                    ))
                )
                with open("%sset_ucla.log" % name, "a") as f:
                    f.write("_" * 80 + '\n')
                    f.write("Inserting %s \n" % parsed_row['fname'])
            except Exception as e:
                print(e)
                with open("%sset_ucla.log" % name, "a") as f:
                    f.write("_" * 80)
                    f.write(str(e))
                continue


def parse_row(row, header):
    parsed = {}
    for k, v in enumerate(header):
        try:
            parsed[v] = float(row[k])
        except:
            parsed[v] = row[k] if row[k] != "-" else None
    return parsed



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Include the protest images collected by UCLA into sqlite db"
    )

    parser.add_argument(
        "--ucla-dir",
        default="UCLA-protest",
        type=str,
        help="The name of the UCLA image directory (default: 'UCLA-protest')"
    )
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="If set, will not include the UCLA test set"
    )
    parser.add_argument(
        "--no-train",
        action="store_true",
        help="If set, will not include UCLA train set"
    )

    args = parser.parse_args()
    main(**vars(args))
