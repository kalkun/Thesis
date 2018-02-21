#!/usr/bin/env python3

import datetime
from os.path import basename, splitext, exists as file_exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from PIL import Image
import imghdr
import imagehash

from protestDB import models
from protestDB.engine import Connection


class ProtestCursor:
    """ This class defines common methods
        to interfacing with the protest database
        through SQLAlchemy
    """
    def __init__(self):
        self.session = sessionmaker(
            bind=Connection.setupEngine()
        )()
        self.engine = Connection.engine

        self.valid_images = ["jpg", "jpeg", "png"]


    def try_commit(self, session=None):
        """ Rollbacks on commit failure,
            then reraise the error
        """
        session = session or self.session
        try:
            session.commit()
        except:
            session.rollback()
            raise


    def instance_exists(self, modelClass, **kwargs):
        """ Returns True if instance exists filtering
            based on the provided keyword arguments
            otherwise False
        """
        q = self.session.query(modelClass).filter_by(**kwargs)
        return q.count() > 0


    def query(self, modelClass):
        """ Just a short hand wrapper for getting a query on the
            session object.
        """
        return self.session.query(modelClass)


    def queryImages(self):
        """ Returns a query object on the `Images` table """
        return self.query(models.Images)


    def queryTags(self):
        """ Returns a query object on the `Tags` table """
        return self.query(models.Tags)

    def queryLabels(self):
        """ Returns a query object on the `Labels` table """
        return self.query(models.Labels)


    def get(self, modelClass, **kwargs):
        """ Returns exactly one instance or None
            Example usage:
            ```
            get(models.Tags, tagName='protest')
            ```
        """
        return self.session.query(modelClass).filter_by(**kwargs).one_or_none()


    def getImage(self, imagehash):
        """ Returns the image identified by `imagehash`
        """
        return self.get(models.Images, imageHASH=imagehash)


    def getImages(self):
        """ Returns a list of all images """
        return self.session.query(models.Images).all()


    def getTag(self, tagName):
        """ Returns tag identified by `tagName` or None
        """
        return self.get(models.Tags, tagName=tagName.lower())


    def getTags(self):
        """ Returns a list of all tags """
        return self.session.query(models.Tags).all()


    def get_or_create(self, modelClass, do_commit=True, **kwargs):
        """ If object exists it will just be returned,
            otherwise it will be created first, then returned.

            See: https://stackoverflow.com/a/6078058
        """
        instance = self.session.query(modelClass).filter_by(
            **kwargs
        ).one_or_none()

        if not instance is None:
            return instance

        instance = modelClass(**kwargs)
        self.session.add(instance)
        if do_commit:
            self.try_commit()

        return instance


    def update_or_create(self, modelClass, do_commit=True, **kwargs):
        """ Update instance if exists, otherwise create it
            Requires all mandatory fields to be provided
            in order to create instance.
        """
        instance = self.get_or_create(modelClass, do_commit=do_commit, **kwargs)
        for key, value in kwargs.items():
            if getattr(instance, key) == value:
                continue
            setattr(instance, key, value)

        if do_commit:
            self.try_commit()
        return instance

    def insertImageLater(self, **kwargs):
        """ Wrapper for `insertImage` that sets the `do_commit` to False
            but only calls the insertImage if the hash of the requested image
            does not already exist, thereby avoiding later conflicts so that
            bulk insertions may be done reliably.

            Returns Image if it is being created, otherwise None
        """
        img_hash = self.__compute_imagehash(kwargs['path_and_name'])
        if self.instance_exists(models.Images, imageHASH=img_hash):
            return None
        else:
            return self.insertImage(do_commit=False, **kwargs)

    def __compute_imagehash(self, path_and_name, as_string=True):
        """ Returns imagehash given an image """
        img_hash = imagehash.dhash(Image.open(path_and_name))
        return str(img_hash) if as_string else img_hash

    def insertImage(
        self,
        path_and_name,
        source,
        origin,
        url=None,
        position=None,
        timestamp=None,
        label=None,
        tags=None,
        do_commit=True,
    ):
        """ Creates new image row in Image table
            Arguments are:
                `path_and_name` The path and name to the image file, can be relative or absolute.
                `source`        The source of the image. E.g. 'google' or 'UCLA'.
                `origin`        Enum of:
                                ```
                                    test | local | online
                                ```
                                where online should only be used
                                        if file is not locally stored and image is to be retrieved
                                        using the `url` argument.
                `url`           Should be set if `origin` is online.
                `position`      The position of an image search that the image appeared in.
                `timestamp`     Optional, will be set to current timestamp otherwise.
                `label`         A label indicating whether the image is violent or not.
                `tags`          An optional list of tags associated with the image.
        """

        if not origin in ['test', 'local', 'online']:
            raise ValueError(
                "origin must be either: 'local', 'online', or 'test'. Found: %s" % origin
            )

        if origin == 'online' and url is None:
            raise ValueError(
                "Argument 'url' must be set when origin is 'online'"
            )

        if not origin == 'test' and not file_exists(path_and_name):
            raise ValueError(
                "File not found for image path: %s" % path_and_name
            )

        if not tags is None and type(tags) != list:
            raise TypeError(
                "'tags' must be of type list, was '%s' for argument: '%s'" % (
                    type(tags),
                    tags
                )
            )

        filename = basename(path_and_name)
        extension = splitext(filename)[1]

        if not origin == 'test' and not imghdr.what(path_and_name) in self.valid_images:
            raise ValueError(
                "'%s' is not a valid image, must be one of '%s'" % (
                    path_and_name,
                    ', '.join(self.valid_images)
                )
            )

        img_hash = path_and_name if origin == 'test' else self.__compute_imagehash(path_and_name)

        img = self.update_or_create(
            models.Images,
            imageHASH   = img_hash,
            name        = filename,
            filetype    = extension,
            source      = source,
            origin      = origin,
            timestamp   = timestamp or datetime.datetime.now(),
            url         = url,
            position    = position,
            do_commit   = do_commit,
        )

        if not label is None:
            self.insertLabel(
                img.imageHASH,
                label,
                do_commit=do_commit,
            )

        if not tags is None:
            for t in tags:
                self.insertTag(
                    t,
                    img.imageHASH,
                    do_commit=do_commit,
        )

        if do_commit:
            self.try_commit()
        return img


    def insertLabel(
        self,
        imageId,
        label,
        timestamp=None,
        do_commit=True,
    ):
        """ Inserts a label for an image in the scale [0, 1]
            where 1 indicates the most violent, and 0 no violence.
        """
        self.get_or_create(
            models.Labels,
            imageID     = imageId,
            label       = label,
            timestamp   = timestamp or datetime.datetime.now(),
            do_commit   = do_commit,
        )



    def insertTag(
        self,
        tagname,
        imagehash,
        do_commit=True,
    ):
        """ Creates a new tag entrance if the tagname is not previously known.
            then creates a link to the image.

            Returns a tuple of the entry in TaggedImages table, linking the image
            and the tagname, as well as the tagname instance.
        """

        tag = self.get_or_create(
            models.Tags,
            tagName     = tagname.lower(),
            do_commit   = do_commit,
        )

        if not self.instance_exists(models.Images, imageHASH=imagehash):
            raise ValueError("No image exists with imageHASH id: '%s'" % imagehash)

        img = self.session.query(models.Images).get(imagehash)
        img.tags.append(tag)

        if do_commit:
            self.try_commit()

        return tag

    def insertComparison(
        self,
        imageID_1,
        imageID_2,
        vote,
        timestamp=None,
        do_commit=True,
    ):
        """ Small handle to insert a comparison vote """
        return self.get_or_create(
            models.Comparisons,
            imageID_1=imageID_1,
            imageID_2=imageID_2,
            timestamp=timestamp or datetime.datetime.now(),
            do_commit=do_commit,
        )

    def insertProtestNonProtestVotes(
        self,
        imageID,
        is_Protest,
        timestamp=None,
        do_commit=True,
    ):
        """ Handle to insert protest vs non protest votes into DB """
        return self.get_or_create(
            models.ProtestNonProtestVotes,
            imageID=imageID,
            is_protest=is_protest,
            timestamp=timestamp or datetime.datetime.now(),
            do_commit=do_commit,
        )


    def remove(
        self,
        obj,
        do_commit=True
    ):
        """ Given a model object, the instance will be deleted """
        self.session.delete(obj)
        if do_commit:
            self.try_commit()


    def removeImage(
        self,
        image,
        do_commit=True,
    ):
        """ Given either a models.Images instance or a
            string defining an imageHASH, the given image
            will be deletede from the database.
        """
        if not type(image) == models.Images:
            image = self.session.query(models.Image).get(image)

        for label in image.labels:
            self.session.delete(label)
        self.session.delete(image)

        if do_commit:
            self.try_commit()


    def clearDB(
        self,
        confirm=False
    ):
        """ Deletes the entire database, you generally wont need this!
        """
        if confirm == False:
            raise ValueError(
                "Should set argument 'confirm' explicitly to invoke this method"
            )
        for table in dir(models):
            tmpTable = getattr(models, table)
            if hasattr(tmpTable, "__tablename__"):
                self.session.query(tmpTable).delete()

        self.try_commit()
