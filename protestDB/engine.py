from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite

from protestDB.config import *

class Connection:

    # Defined static, to persist engine across instances
    engine = None

    def __init__(self, db_name_and_path=db_name):
        if Connection.engine is None:
            Connection.setupEngine(db_name_and_path)
        self.conn   = self.engine.connect()

    @staticmethod
    def setupEngine(db_name_and_path=db_name):
        if Connection.engine is not None:
            return Connection.engine
        Connection.engine = create_engine('sqlite+pysqlite:///%s' % db_name_and_path, module=sqlite)
        return Connection.engine
