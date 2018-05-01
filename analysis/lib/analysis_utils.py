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
from keras import models as Kmodels
from keras import backend as Kbackend
from keras import applications as Kapplications
from keras import layers as Klayers

from .transforms import *

class ResizeSequence(Sequence):
    """ A sequence generator of batches with images resized to 224 x 224 """

    def __init__(self, dataframe, batch_size=128, targets=['label'], image_dir="../../images/", transforms=[normalizeMinMax]):
        """ Accepts a pandas dataframe object, and yields
            tuples of resized, normalized images in size of.

            Beware, that unless transforms are set, images are passed
            as is, except resized. This includes normalizations.

            Args:
                `dataframe`: A pandas DataFrame to generate batches from
                `batch_size`: Size of batches to generate
                `ys`: A list column names to treat as targets
                `image_dir`: The path to the image directory
                `transforms`: A list of transformations to use. A transform
                              function accepts exactly one positional parameter,
                              the `img`, and returns a PIL image object.

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
                img = skimage_resize(img, shape)

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



def getKSplits(df, n_splits, seed = None):

    """ Splits a dataframe into n_splits number of splits randomly.

        Args:
            `df`: The pandas data frame to be split
            `n_splits`: The number of splits
            `seed`: the seed, if None it will be auto generated. Default = None

        Returns:
            A list of the splits as pandas data frames
    """

    result = []

    # None random seed is same as not setting it
    df_shuffled = df.sample(len(df), random_state = seed)

    fold_size = int(len(df) / n_splits)

    for i in range(n_splits):
        if i == n_splits - 1: # last iteration
            df_fold = df_shuffled[fold_size * (i): len(df)] # gets remainder
        else:
            df_fold = df_shuffled[fold_size * (i):fold_size * (i + 1) ] # python starts indexing at 0
        result.append(df_fold)

    return result


def getKSplitsStratified(df, n_splits, classColumn, seed = None):
    """ Splits a dataframe into n_splits number of splits randomly and assures that
    the each split maintains the original class balance.

    Args:
        `df`: The pandas data frame to be split
        `n_splits`: The number of splits
        'classColumn': The name of the column in the data frame corresponding to the class that needs to
            have its balance maintained. This column should have a binary value of 0 or 1 or
            True or False
        `seed`: the seed, if None it will be auto generated. Default = None

    Returns:
        A list of the splits as pandas data frames
    """
    df_class1 = df[df[classColumn] == True]
    df_class2 = df[df[classColumn] == False]

    k_folds_class1 = getKSplits(df_class1, n_splits, seed)
    k_folds_class2 = getKSplits(df_class2, n_splits, seed)

    # combine
    k_folds_combined = []
    for i in range(n_splits):
        combined_fold = k_folds_class1[i].append(k_folds_class2[i])
        combined_fold_shuffled = combined_fold.sample(len(combined_fold), random_state = seed)
        k_folds_combined.append(combined_fold_shuffled)

    return k_folds_combined


def getKSplitsTwoClassesStratified(df, n_splits, classColumn1, classColumn2, seed = None):

    """ This function currently executes the same job as "getKSplitsStratified" but in two classes
    TODO: Make it general for n classes

    """

    df_class1 = df[(df[classColumn1] == False) & (df[classColumn2] == False)]
    df_class2 = df[(df[classColumn1] == True) & (df[classColumn2] == True)]
    df_class3 = df[(df[classColumn1] == True) & (df[classColumn2] == False)]
    df_class4 = df[(df[classColumn1] == False) & (df[classColumn2] == True)]

    k_folds_class1 = getKSplits(df_class1, n_splits, seed)
    k_folds_class2 = getKSplits(df_class2, n_splits, seed)
    k_folds_class3 = getKSplits(df_class3, n_splits, seed)
    k_folds_class4 = getKSplits(df_class4, n_splits, seed)

    # combine
    k_folds_combined = []
    for i in range(n_splits):
        combined_fold = k_folds_class1[i].append(k_folds_class2[i]).append(k_folds_class3[i]).append(k_folds_class4[i])
        combined_fold_shuffled = combined_fold.sample(len(combined_fold), random_state = seed)
        k_folds_combined.append(combined_fold_shuffled)

    return k_folds_combined



def initializeUCLAModel():

    img_input = Klayers.Input(shape=(224,224,3), name='img_input')

    resnet_model = Kapplications.ResNet50(include_top=False, weights = 'imagenet') (img_input)

    flatten = Klayers.Flatten()(resnet_model)

    protest_out = Klayers.Dense(1, activation='sigmoid', name='protest_out')(flatten)
    violence_out = Klayers.Dense(1, activation='sigmoid', name='violence_out')(flatten)
    visual_out = Klayers.Dense(10, activation='sigmoid', name='visual_out')(flatten)

    return Kmodels.Model(inputs= img_input, outputs=[protest_out, violence_out, visual_out])


def initializeUCLAModelWithoutVisual():

    img_input = Klayers.Input(shape=(224,224,3), name='img_input')

    resnet_model = Kapplications.ResNet50(include_top=False, weights = 'imagenet') (img_input)

    flatten = Klayers.Flatten()(resnet_model)

    protest_out = Klayers.Dense(1, activation='sigmoid', name='protest_out')(flatten)
    violence_out = Klayers.Dense(1, activation='sigmoid', name='violence_out')(flatten)

    return Kmodels.Model(inputs= img_input, outputs=[protest_out, violence_out])




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
