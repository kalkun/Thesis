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
from skimage.transform import resize as skimage_resize
from sklearn import preprocessing as skpreprocess
from keras import backend as K
import matplotlib.pyplot as plt
from sklearn import metrics

from .transforms import *

class ResizeSequence(Sequence):

    def __init__(self, dataframe, batch_size=128, targets=['label'], image_dir="../images/", transforms=[normalize]):
        """ Accepts a pandas dataframe object, and yields
            tuples of resized, normalized images in size of.

            Beware, that unless transforms are set, images are passed
            as is, except resized. This includes normalizations.

            Args:
                `dataframe`: A pandas DataFrame to generate batches from
                `batch_size`: Size of batches to generate
                `ys`: A list column names to treat as targets
                `image_dir`: The path to the image directory
                `transforms`: A list of transformations to use

        """
        self.dataframe  = dataframe
        self.batch_size = batch_size
        self.ys         = targets
        self.image_dir  = image_dir
        self.transforms = transforms

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

        """ Load images, then apply any provided
            transformation functions. If the images
            are not in correct shape, then resizing is
            done to fit the input layer
        """
        imgs = []
        for name in batch.name.values:
            img = imread(os.path.join(self.image_dir, name))
            for transform in self.transforms:
                img = transform(img)

            shape = (224, 224, 3)
            img = np.array(img)
            if not img.shape == shape:
                img = skimage_resize(img, (224, 224, 3))

            imgs.append(img)

        imgs = np.array(imgs)

        ys = [batch[y].values for y in self.ys]

        return imgs, ys

def getExperimentName(notebook, datalength, epochs, init_lr, *args):
    """ Provides a standardized way of naming
        log files and model files so that the hyper parameters
        are part of the naming

        Args:
            `notebook`: Name of the notebook runing the expiriment
            `datalength`: Length of dataset
            `epochs`: Number of epochs
            *args: A list of other defining terms for the experiment

        Returns:
            A string to be used as name for .hdf5 and .log files
    """
    notebook = os.path.basename(notebook).split(".")[0]
    name = "{}_datalen-{}_epochs-{}_init_lr-{}".format(
        notebook, datalength, epochs, init_lr
    )
    return name + "_" + "_".join(args)



def getSplits(df, train_size, val_size, test_size, seed=None):
    """ Builds train, validation and test set

        Args:
            df: DataFrame object to split
            train_size: size of training set
            val_size: size of validation set
            test_size: size of test set
            seed: Optional argument to seed the random function

        Returns:
            tuple: The 3 elements are the train, validation and test
                   set respectively.
    """
    size = len(df)

    # size is considered a percentage if less than 1:
    train_size = int(train_size * size) if train_size < 1 else train_size
    val_size = int(val_size * size) if val_size < 1 else val_size
    test_size = int(test_size * size) if test_size < 1 else test_size

    if not seed is None:
        np.random.seed(seed)

    train_val_idx = np.random.choice(
        a=range(size),
        size=train_size + val_size,
        replace=False
    )
    train_idx = train_val_idx[:train_size]
    val_idx = train_val_idx[train_size:]

    train = df.iloc[train_idx]
    val = df.iloc[val_idx]
    test = df.drop(train.index).drop(val.index) # test is equal to the leftover

    assert len(train) + len(val) + len(test) == len(df)

    return train, val, test


def buildMaskedLoss(loss_function, mask_value):
    """Builds a loss function that masks based on targets

    Args:
        loss_function: The loss function to mask
        mask_value: The value to mask in the targets

    Returns:
        function: a loss function that acts like loss_function with masked inputs
    """

    def maskedLossFunction(y_true, y_pred):
        mask = K.cast(K.not_equal(y_true, mask_value), K.floatx())
        return loss_function(y_true * mask, y_pred * mask)

    return maskedLossFunction


def lrUpdateUCLA(epoch, lr):
    """mimics the way that UCLA updates their learning rate

    Args:
        epoch: The current epoch
        lr: TThe current learning rate

    Returns:
        function: The new learning rate
    """
    new_lr = lr * (0.4 ** (epoch // 4))
    return new_lr


def clipDFColumn(df, column, cutpoint):
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

def minMax(df, column):
    """ Performs a min max operation into a dataframe column specified using a string
        All NaN values are ignored.

    Args:
        df: The pandas dataframe
        column: The column name as a string

    Returns:
        a modified copy of the original pandas df

    """
    df_result = df.copy()
    not_nulls = df[column].isnull() == False

    v = np.matrix(df_result.loc[not_nulls, column]) #.as_matrix()
    scaler = skpreprocess.MinMaxScaler()
    df_result.loc[not_nulls, column] = scaler.fit_transform(v.T)
    return df_result

def plotROC(attr, target, pred, save_as=None):
    """Plot a ROC curve and show the accuracy score and the AUC"""
    fig, ax = plt.subplots()
    auc = metrics.roc_auc_score(target, pred)
    acc = metrics.accuracy_score(target, (pred >= 0.5).astype(int))
    fpr, tpr, _ = metrics.roc_curve(target, pred)
    plt.plot(fpr, tpr, lw = 2, label = attr.title())
    plt.legend(loc = 4, fontsize = 15)
    plt.title(('ROC Curve for {attr} (Accuracy = {acc:.3f}, AUC = {auc:.3f})'
               .format(attr = attr.title(), acc= acc, auc = auc)),
              fontsize = 15)
    plt.xlabel('False Positive Rate', fontsize = 15)
    plt.ylabel('True Positive Rate', fontsize = 15)
    if not save_as is None:
        plt.savefig(save_as)
    else:
        plt.show()
