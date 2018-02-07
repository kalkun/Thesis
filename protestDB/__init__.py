from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlite3 import dbapi2 as sqlite

from .models import Base
from .engine import Connection

"""
    Create models if they dont exist:
"""
Base.metadata.create_all(Connection.setupEngine()) # Create tabels if they don't exist
