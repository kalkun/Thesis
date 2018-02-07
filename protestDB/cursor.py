import datetime
from os.path import basename, exists as file_exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from PIL import Image
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
            bind=Connection.engine if Connection.engine is not None else Connection.setupEngine()
        )()


    def insertImage(
        self,
        path_and_name,
        source,
        imgtype,
        timestamp=None,
        url=None,
        label=None # TODO: providing label results in an insertion into the label tabel
    ):
        """ Creates new image row in Image table
            Arguments are:
                `path_and_name` The path and name to the image file, can be relative or absolute.
                `source`        The source of the image.
                `imgtype`       Enum of:
                                ```
                                    test | local | online
                                ```
                                where online should only be used
                                        if file is not locally stored and image is to be retrieved
                                        using the `url` argument.
                `timestamp`     Optional, will be set to current timestamp otherwise.
                `url`           Should be set if `imgtype` is online.
        """

        if not imgtype in ['test', 'local', 'online']:
            raise ValueError("imgtype must be either: 'local', 'online', or 'test'. Found: %s" % imgtype)

        if imgtype == 'online' and url is None:
            raise ValueError("Argument 'url' must be set when imgtype is 'online'")

        if not file_exists(path_and_name) and not imgtype == 'test':
            raise ValueError("File not found for image path: %s" % path_and_name)

        img_hash = path_and_name if imgtype == 'test' else imagehash.average_hash(Image.open(path_and_name))
        self.session.add(
            models.Images(
                imageHASH   = str(img_hash),
                name        = basename(path_and_name),
                source      = source,
                imgtype     = imgtype,
                timestamp   = timestamp or datetime.datetime.now(),
                url         = url
            )
        )
        try:
            self.session.commit()
        except exc.IntegrityError as e:
            self.session.rollback()
            raise ValueError(
                "Image already exists with hash %s for image named: %s" % (
                    img_hash,
                    basename(path_and_name)
                )
            )
