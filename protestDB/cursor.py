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
    """
        This class defines common methods
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
        return self.session.query(q.exists())


    def get_or_create(self, modelClass, **kwargs):
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
        self.try_commit()

        return instance


    def update_or_create(self, modelClass, **kwargs):
        """ Update instance if exists, otherwise create it
            Requires all mandatory fields to be provided
            in order to create instance.
        """
        instance = self.get_or_create(modelClass, **kwargs)
        for key, value in kwargs.items():
            if getattr(instance, key) == value:
                continue
            setattr(instance, key, value)

        self.try_commit()
        return instance


    def insertImage(
        self,
        path_and_name,
        source,
        origin,
        url=None,
        position=None,
        timestamp=None,
        label=None,
        tags=None
    ):
        """ Creates new image row in Image table
            Arguments are:
                `path_and_name` The path and name to the image file, can be relative or absolute.
                `source`        The source of the image.
                `origin`        Enum of:
                                ```
                                    test | local | online
                                ```
                                where online should only be used
                                        if file is not locally stored and image is to be retrieved
                                        using the `url` argument.
                `timestamp`     Optional, will be set to current timestamp otherwise.
                `url`           Should be set if `origin` is online.
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

        img_hash = path_and_name if origin == 'test' else imagehash.average_hash(Image.open(path_and_name))

        img = self.update_or_create(
            models.Images,
            imageHASH   = str(img_hash),
            name        = filename,
            filetype    = extension,
            source      = source,
            origin      = origin,
            timestamp   = timestamp or datetime.datetime.now(),
            url         = url,
            position    = position
        )

        if not label is None:
            self.insertLabel(
                img.imageHASH,
                label
            )

        if not tags is None:
            for t in tags:
                self.insertTag(
                    t,
                    img.imageHASH,
                )
        return img



    def insertLabel(
        self,
        imageId,
        label,
        timestamp=None
    ):
        """ Inserts a label for an image in the scale [0, 1]
            where 1 indicates the most violent, and 0 no violence.
        """
        self.get_or_create(
            models.Labels,
            imageID     = imageId,
            label       = label,
            timestamp   = timestamp or datetime.datetime.now()
        )



    def insertTag(
        self,
        tagname,
        imagehash
    ):
        """ Creates a new tag entrance if the tagname is not previously known.
            then creates a link to the image.

            Returns a tuple of the entry in TaggedImages table, linking the image
            and the tagname, as well as the tagname instance.
        """

        tag = self.get_or_create(
            models.Tags,
            tagName=tagname.lower()
        )

        if not self.instance_exists(models.Images, imageHASH=imagehash):
            raise ValueError("No image exists with imageHASH id: '%s'" % imagehash)

        image_tag_rel = self.get_or_create(
            models.TaggedImages,
            imageID = imagehash,
            tagID   = tag.tagID
        )

        self.try_commit()

        return image_tag_rel, tag


    def removeImage(
        self,
        image
    ):
        """ Given either a models.Images instance or a
            string defining an imageHASH, the given image
            will be deletede from the database.
        """
        if type(image) == models.Images:
            self.session.delete(image)
        else:
            img = self.session.query(models.Image).get(image)
            self.session.delete(img)

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
