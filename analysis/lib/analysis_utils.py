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
from sklearn import preprocessing as skpreprocess
from keras import backend as K

class ResizeSequence(Sequence):
    """ Accepts a pandas dataframe object, and yields
        tuples of resized, normalized images in size of
        `batch_size`.
        `ys` is a list of column names to extract from dataframe and use as
        target values.
    """

    def __init__(self, dataframe, batch_size=128, targets=['label', ['police', 'sign']], image_dir="../images/"):
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
            remainder = self.dataframe.iloc[: (end - len(self.dataframe))]
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
            ) / 255             # normalizing
            for name in batch.name.values
        ])

        return BUG





def BuildMaskedLoss(loss_function, mask_value):
    """Builds a loss function that masks based on targets

    Args:
        loss_function: The loss function to mask
        mask_value: The value to mask in the targets

    Returns:
        function: a loss function that acts like loss_function with masked inputs
    """

    def MaskedLossFunction(y_true, y_pred):
        mask = K.cast(K.not_equal(y_true, mask_value), K.floatx())
        return loss_function(y_true * mask, y_pred * mask)

    return MaskedLossFunction


def LrUpdateUCLA(epoch, lr):
    """mimics the way that UCLA updates their learning rate

    Args:
        epoch: The current epoch
        lr: TThe current learning rate

    Returns:
        function: The new learning rate
    """
    new_lr = lr * (0.4 ** (epoch // 4))
    return new_lr


def ClipDFColumn(df, column, cutpoint):
    """Clips a df column at a specified cutpoint. The function will return a modified
    copy of the original pandas df.

    Args:
        df: The pandas dataframe
        column: The column name as a string
        cutpoint: a scalar

    Returns:
        a modified copy of the original pandas df
    """
    df_result = df.copy()
    ix_large = df_result[df_result[column] > cutpoint].index
    df_result.loc[ix_large, column] = cutpoint
    return df_result

def MinMax(df, column):
    """ Performs a min max operation into a dataframe column specified using a string
    
    Args:
        df: The pandas dataframe
        column: The column name as a string

    Returns:
        a modified copy of the original pandas df
    
    """
    df_result = df.copy()
    v = np.matrix(df_result[column])
    scaler = skpreprocess.MinMaxScaler()
    df_result[column] = scaler.fit_transform(v.T)
    return df_result