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

    return PIL.Image.fromarray(img_array)

def _get_np_array(image):
    if isinstance(image, np.ndarray):
        return image

    return np.array(image)

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
    scale = random.randint(8, 100) / 100
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
    return image.rotate(rotate, resample=PIL.Image.BILINEAR)

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


def randomResizedCrop(image, square=224):
    """ Does a random crop of .8 to 1.0 of the original image
        then random aspect ratio between 3/4 and 4/3,
        thereafter resize the image to a square of size:
        `square x square`
    """
    image = _get_PIL_object(image)

    image = randomCrop(image)
    image = randomResize(image)
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


def normalize(image, use_imagenet=True):
    """ Normalize the images

        Args:
            `image`: The image to normalize
            `use_imagenet`: A boolean indicating
                            whether to use the
                            mean and std from
                            imagenet
        Returns:
            The normalized image as a PIL image object
    """
    image = _get_np_array(image) / 255

    mean=[0.485, 0.456, 0.406]
    std=[0.229, 0.224, 0.225]

    return (image - mean) / std
