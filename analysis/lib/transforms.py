""" This module describes a bunch of transformations to of images.
    The functions accepts a PIL Image or a numpy array, and returns
    a PIL Image object where the transformation has been applied.
"""

import random
import PIL
import numpy as np
from PIL import ImageEnhance

def _get_PIL_object(img_array):
    if isinstance(img_array, PIL.Image.Image):
        return img_array

    return PIL.Image.fromarray(img_array.astype('uint8')).convert("RGB") # guarantees RGB


def _get_np_array(image):
    if isinstance(image, np.ndarray):
        return image

    return np.array(image)[:,:,:3] # guarantees RGB

def resize(image, size=256):
    """ Resize image according to `size`
        if size is an integer a square is returend

        Args:
            `image`: The image to resize
            `size`: A tuple or an integer of the output
                    size
    """
    image = _get_PIL_object(image)

    return image.resize(size if type(size) == tuple else (size, size), resample=PIL.Image.BILINEAR)

def centerCrop(image, size=224):
    """ Crops image to `size` around center
        if size is an integer a square is returned

        Args:
            `image`: The image to crop
            `size`: A tuple or an integer of the output
                    size
    """
    cx, cy = image.width //2, image.height //2
    if type(size) == tuple:
        x, y = size
    else:
        x, y = size, size

    return image.crop((cx-x//2, cy-y//2, cx+x//2, cy+y//2))


def randomCrop(image, min_percent=8, max_percent=100):
    """
        Does a random crop of size between `min_percent`
        and `max_percent`, of the original image which
        defaults to: 8% and 100% respectively.

        Args:
            `image`: The image to crop
            `min_percent`: minimum scale of crop
            `max_percent`: maximum scale of crop

        Returns:
            Cropped image as a PIL image object
    """
    image = _get_PIL_object(image)

    """
    Cropping is defined as a 4-tuple of coordinates of the
    4 corners, we're cropping in the range of .08 to 1. so we
    just need to know where to start from:
    """
    w, h = image.size
    scale = random.randint(min_percent, max_percent) / 100
    new_w = w * scale
    new_h = h * scale

    assert int(new_w/new_h) == int(w/h), "Aspect ratio should be the same"

    left = random.randint(0, int(w-new_w))
    upper = random.randint(0, int(h-new_h))

    right, lower = int(left+new_w), int(upper+new_h)

    return image.crop((left, upper, right, lower))


def randomResize(image, aspect_ratio=(3/4, 4/3)):
    """ Returns an image randomly rezised to an
        aspect ratio with in the range defined by
        `aspect_ratio`

        Args:
            `image`: The image to resize
            `aspect_ratio`: A tuple of the min and max
                            aspect ratio

        Returns:
            Resized image as a PIL image object
    """
    image = _get_PIL_object(image)

    w, h = image.size

    ratio = random.randrange(int(aspect_ratio[0] * 100), int(aspect_ratio[1] * 100)) / 100

    if random.random() < .5:
        w = int(w * ratio)
    else:
        h = int(h * ratio)

    return image.resize((w, h), resample=PIL.Image.BILINEAR) # BILINEAR is default by pytorch


def randomRotation(image, degrees=30):
    """ Randomly rotate the image to the range
        of [-degrees, degrees]

        Args:
            `image`: The image to rotate
            `degrees`: An integer or tuple of the min
                       and max rotation. If integer
                       is given, assumes the min is
                       -1 * degrees.
        Returns:
            Randomly rotated image as a PIL image object
    """
    image = _get_PIL_object(image)

    if type(degrees) == int:
        degrees = [-1 * degrees, degrees]
    else:
        degrees = list(degrees)

    rotate = random.randrange(*degrees)
    return image.rotate(rotate, resample=PIL.Image.NEAREST) # as pytorch does it


def randomHorizontalFlip(image, prob=.5):
    """ Randomly flips the image

        Args:
            `image`: The image to flip
            `prob`: A floating point indicating
                    the probability of a flip
                    in percent.

        Returns:
            The flipped (or non flipped) image as a PIL object
    """
    image = _get_PIL_object(image)

    if random.random() < prob:
        return image.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    return image


def randomResizedCrop(
        image,
        square=224,
        aspect_ratio=(3/4, 4/3),
        min_percent=8,
        max_percent=100):
    """ Does a random crop of .08 to 1.0 of the original image
        then random aspect ratio between 3/4 and 4/3,
        thereafter resize the image to a square of size:
        `square x square`

        Args:
            `image` : Required positional argument representing one image
            `square`: The dimensions of the output image provided as one
                      integer, meaning the output image size is
                      width = height = square.
            `aspect_ratio`: The aspect ratio that the image is resized to.
            `min_percent`: The minimum size of the crop given as an integer
                           indicating a percentage of the original image.
            `max_percent`: Maximum size of the crop.

        Returns:
            PIL image object after the transformations has been applied.
    """
    image = _get_PIL_object(image)

    image = randomCrop(image, min_percent=min_percent, max_percent=max_percent)
    image = randomResize(image, aspect_ratio=aspect_ratio)
    return image.resize((square, square))


def colorJitter(image, brightness=.4, contrast=.4, saturation=.4):
    """ Randomly change the brightness, contrast, and saturation
        of an image.
        See: http://pytorch.org/docs/master/torchvision/transforms.html#torchvision.transforms.ColorJitter

        Args:
            `image`: The image to transform
            `brightness`: How much to jitter brightness
            `contrast`: How much to jitter brightness
            `saturation`: How much to jitter saturation

        Returns:
            The transformed image as a PIL image object
    """
    image = _get_PIL_object(image)

    transforms = []

    brightness_factor = random.uniform(max(0, 1 - brightness), 1 + brightness)
    transforms.append(lambda img: ImageEnhance.Brightness(img).enhance(brightness_factor))

    contrast_factor = random.uniform(max(0, 1 - contrast), 1 + contrast)
    transforms.append(lambda img: ImageEnhance.Contrast(img).enhance(contrast_factor))

    saturation_factor = random.uniform(max(0, 1 - saturation), 1 + saturation)
    transforms.append(lambda img: ImageEnhance.Color(img).enhance(saturation_factor))

    random.shuffle(transforms)

    for transform in transforms:
        image = transform(image)

    return image


def normalizeStandardScore(image, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    """ Normalize the images using the Zscore normalization. assumes the PIL image mode to be RGB

        Args:
            `image`: The image to normalized
            `mean`: A list of 3 values containing the mean values for the RGB channels respectively
            to be normalized.
            `std`: A list of 3 values containing the standard deviation values for the RGB channels respectively
            to be normalized.
        Returns:
            The normalized image as a PIL image object
    """

    assert (len(mean) == 3 and len(std) == 3), "mean and std should have three values each"

    image = _get_np_array(image)

    return (image - mean) / std

def normalizeMinMax(image):
    """ Normalize the image between 0 and 1. Assumes the PIL image mode
    to be RGB

        Args:
            `image` The image to be normalized
        Returns:
            The normalized image as a PIL image object
    """


    return _get_np_array(image) / 255.0


def lighting(image):
    """ Fancy PCA or Alexnet style lighting

        From [Alex Krizhevsky, 2012]:
        > "Specifically, we perform PCA on the set of RGB pixel values throughout
        > the ImageNet training set. To each training image we add multiples of
        > the found principial components, with magnitudes proportional to the
        > corresponding eigenvalues times a random variable drawn from a Gaussian
        > with mean zero and standard deviation 0.1."

        Args:
            `image`: The image to be fancy with

        Returns:
            Numpy array of the transformed image matrix
    """

    # Some images are might be RGBA, which would fail

    image = _get_np_array(image)
    shape = image.shape

    alphastd = 0.1
    eigval = np.array([0.2175, 0.0188, 0.0045])
    eigvec = np.array([
        [-0.5675,  0.7192,  0.4009],
        [-0.5808, -0.0045, -0.8140],
        [-0.5836, -0.6948,  0.4203]
    ])

    alpha = np.random.normal(loc=0.0, scale=alphastd, size=(3,1))
    rgb = alpha * (eigval.reshape([3, 1]) * eigvec)


    image = image + rgb.sum(axis=0)



    return image
