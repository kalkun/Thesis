################################################################################
#                                                                              #
#                    These are the UTILS - use responsibly!                    #
#                                                                              #
################################################################################
import os
import sys
import numpy as np
from imageio import imread
from keras.utils import Sequence
from skimage.transform import resize

class ResizeSequence(Sequence):
    """ Accepts a pandas dataframe object, and yields
        tuples of resized, normalized images in size of
        `batch_size`.
        `ys` is a list of column names to extract from dataframe and use as
        target values.
    """

    def __init__(self, dataframe, batch_size=128, targets=['label'], image_dir="../images/"):
        self.dataframe  = dataframe
        self.batch_size = batch_size
        self.ys         = targets
        self.image_dir  = image_dir

        assert os.path.isdir(image_dir), (
                "Directory not found %s.\nCurrent dir is %s" %
                (image_dir, os.getcwd()))


    def __len__(self):
        return int(np.ceil(len(self.dataframe) / self.batch_size))

    def __getitem__(self, index):
        start = index * self.batch_size
        end   = (index +1) * self.batch_size
        batch = self.dataframe.iloc[start:end]

        # if the end batch extends the length of the dataframe
        # make sure to take the remainder from the beginning
        if end >= len(self.dataframe):
            remainder = self.dataframe.iloc[0:end +1]
            batch     = batch.append(remainder)

        # Extract images names,
        # load and resize images for every
        # image in the current batch:
        imgs = np.array([
            resize(
                imread(
                    os.path.join(self.image_dir, name)
                ),
                (224, 224, 3),
                mode="constant" # It's the default, but it'll give a warning if not set :/
            )
            for name in batch.name.values
        ])

        # Extract values from target columns:
        targets = np.array([
            batch[y].values
            for y in self.ys
        ]).transpose()

        return imgs, targets
