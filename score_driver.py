#!/usr/bin/env python3
"""
" This script computes the scores from the
" pairwise comparisons.
"
" The input is the Batch csv output from MTurk
" and the output will be of the format:
"   ```
"   #row, image1, image2, win1, win2, tie
"   ```
" Where win1 indicates the total number that image1
" was selected as the most violent in the comparisons
" between the two images - similarly for `win2` but with
" opporsite meaning.
" The tie indicates the total amount of users that answered the
" violence depicted was similar for the two images.
"
" Remember that each image pair is labelled by ten
" different individuals.
"
" **Usage:**
"
" ```
"   ./score_driver --input <batch_output_csv>
" ```
"
"
" **The header row includes the following named columns:**
"
" AcceptTime
" Answer.choice0
" Answer.choice1
" Answer.choice2
" Answer.choice3
" Answer.choice4
" Answer.choice5
" Answer.choice6
" Answer.choice7
" Answer.choice8
" Answer.choice9
" ApprovalTime
" Approve
" AssignmentDurationInSeconds
" AssignmentId
" AssignmentStatus
" AutoApprovalDelayInSeconds
" AutoApprovalTime
" CreationTime
" Description
" Expiration
" HITId
" HITTypeId
" Input.image_0-1
" Input.image_0-2
" Input.image_1-1
" Input.image_1-2
" Input.image_2-1
" Input.image_2-2
" Input.image_3-1
" Input.image_3-2
" Input.image_4-1
" Input.image_4-2
" Input.image_5-1
" Input.image_5-2
" Input.image_6-1
" Input.image_6-2
" Input.image_7-1
" Input.image_7-2
" Input.image_8-1
" Input.image_8-2
" Input.image_9-1
" Input.image_9-2
" Keywords
" Last30DaysApprovalRate
" Last7DaysApprovalRate
" LifetimeApprovalRate
" LifetimeInSeconds
" MaxAssignments
" NumberOfSimilarHITs
" Reject
" RejectionTime
" RequesterAnnotation
" RequesterFeedback
" Reward
" SubmitTime
" Title
" WorkTimeInSeconds
" WorkerId
"""

import csv
import argparse

from protestDB.cursor import ProtestCursor
pc = ProtestCursor()

base = "https://s3.eu-central-1.amazonaws.com/ecb-protest/"
def get_name(url, _base=None):
    return url.replace(_base or base, '')

def get_hash(url):
    return get_name(url).split('.')[0]


def main(input_file, **kwargs):
    """
    The `main` def for the driver file.
    """

    # The keys will be unique per image pair comparison,
    # the values will be a list of 3 entries with the format:
    # [win1, win2, tie]
    pair_dict = {}
    header = {}
    data = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')

        # Parse the header row in to a dict
        # so that each key is a column name, and the value
        # is the row index
        for k, v in enumerate(reader.__next__()):
            header[v] = k


        # The image column names follows the same (weird) structure
        # so we can just generate the names of all of them:
        img_cols = [
            "Input.image_%s-%s" % (j, i) for j in range(10) for i in range(1, 3)
        ]

        for row in reader:
            # Get the values from the image columns,
            # and parse get the image names from the url:
            images = list(map(
                lambda x: get_name(row[header.get(x)]),
                img_cols
            ))

            # get: Answer.choice[0-9]
            # for every image pair
            for pair in range(0, len(img_cols), 2):

                answer = row[header.get("Answer.choice%s" % int(pair/2))]
                vote = [ 1 if i-1 == int(answer) else 0 for i in range(3) ]

                img_a, img_b = images[pair:pair+2]
                pair_key = ";".join(sorted([img_a, img_b]))

                pair_dict[pair_key] = [ x + vote[i] for i, x in enumerate(
                    pair_dict.get(pair_key, [0, 0, 0]))
                ]


        c = 0
        for k, v in pair_dict.items():
            c += 1
            data.append(
                [
                    c,               # Row number
                    k.split(";")[0], # image 1
                    k.split(";")[1], # image 2
                    v[0],            # win1
                    v[2],            # win2
                    v[1],            # tie
                ]
            )
    UCLA_header = ["row", "image1", "image2", "win1", "win2", "tie"]
    if kwargs["output_file"]:
        with open(kwargs['output_file'], "w") as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(UCLA_header)
            writer.writerows(data)


################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description= "A script to clean and compute the scores from the MTurk "
                     "batch output file. The scores will be inserted into the "
                     "`comparisons` table in the `protestDB`.                 "
    )
    parser.add_argument(
        "-i",
        "--input-file",
        metavar = "file",
        type    = str,
        help    = "The MTurk batch file with HIT results"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        metavar = "file",
        type    = str,
        help    =  "The filename to send the output to. In general this is not "
                   "needed as the outcome typically is to insert the           "
                   "equivalent rows into the database, however, if set, a      "
                   "csvfile in the same format as the UCLA file                "
                   "`pairwise_annot.csv` will be written to                    "
    )
    main(
        **vars(parser.parse_args())
    )
