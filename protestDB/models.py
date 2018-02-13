from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
# THEN WHEN CREATING:
# Base.metadata.create_all(engine)

TaggedImages = Table("TaggedImages",
    Base.metadata,
    Column("imageID", String(100), ForeignKey("Images.imageHASH")),
    Column("tagID", Integer, ForeignKey('Tags.tagID'))
)

class Images(Base):

    __tablename__ = "Images"

    imageHASH   = Column(String(100), primary_key=True)
    name        = Column(String(100), nullable=False)
    source      = Column(String(100), nullable=False)
    filetype    = Column(String(100), nullable=False)
    timestamp   = Column(DateTime, nullable=False)
    url         = Column(String(100), nullable=True)
    origin      = Column(String(100), nullable=False)
    position    = Column(Integer, nullable=True)

    # relationship fields:
    labels      = relationship("Labels")
    tags        = relationship("Tags",
                    secondary=TaggedImages,
                    back_populates="images",
                )

    def __repr__(self):
        return "<Image imageHASH='%s', name='%s'>" % (self.imageHASH, self.name)



class Tags(Base):

    __tablename__   = "Tags"

    tagID   = Column(Integer, primary_key=True)
    tagName = Column(String(100), nullable=False)

    # relationship fields:
    images  = relationship("Images",
                secondary=TaggedImages,
                back_populates="tags",
            )

    def __repr__(self):
        return "<Tags id='%s', tagName='%s'" % (
                self.tagID, self.tagName)


class Comparisons(Base):
    """
    A model class for comparison based votes
    """

    __tablename__ = "Votes"

    comparisonID = Column(Integer, primary_key=True)
    imageID_1    = Column(String(100), ForeignKey('Images.imageHASH'))
    imageID_2    = Column(String(100), ForeignKey('Images.imageHASH'))
    vote         = Column(Integer, nullable=False)
    timestamp    = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Votes id='%s', imageID_1='%s', imageID_2='%s', vote='%s'>" % (
                self.voteID, self.imageID_1, self.imageID_2, vote)


class ProtestNonProtestVotes(Base):
    """
    A model class for labels on whether image is from a protest or not.
    """

    __tablename__ = "ProtestNonProtestVotes"

    protestVoteID = Column(Integer, primary_key=True)
    imageID       = Column(String(100), ForeignKey('Images.imageHASH'))
    is_protest    = Column(Boolean, nullable=False)
    timestamp     = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<ProtestNonProtestVotes id='%s', imageID='%s', is_protest='%s', timestamp='%s'>" % (
                self.protestVoteID, self.imageID, self.is_protest, self.timestamp)


class Labels(Base):
    """
    A class for labeling image as violent or not - where the label itself
    is a floating point between 0 and 1
    """

    __tablename__ = "Labels"

    labelID     = Column(Integer, primary_key=True)
    imageID     = Column(String(100), ForeignKey('Images.imageHASH'))
    timestamp   = Column(DateTime, nullable=False)
    label       = Column(Float, nullable=False)

    def __repr__(self):
        return "<Labels labelID='%s', imageID='%s', label='%s'>" % (
                self.labelID, self.imageID, self.label)
