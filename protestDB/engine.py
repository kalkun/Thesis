from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite
from sqlalchemy.interfaces import PoolListener

import os
import configparser
config = configparser.ConfigParser()
self_path = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(self_path, "alembic.ini"))
db_name=config['alembic']['db_name']


# Takes care of enforcing foreign keys when inserting into the db
class ForeignKeysListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')

class Connection:

    # Defined static, to persist engine across instances
    engine = None

    def __init__(self, db_name_and_path=db_name):
        if Connection.engine is None:
            Connection.setupEngine(db_name_and_path)
        self.conn   = self.engine.connect()

    @staticmethod
    def setupEngine(db_name_and_path=db_name):
        if not Connection.engine is None:
            return Connection.engine
        if db_name_and_path == db_name:
            db_name_and_path = os.path.join(self_path, db_name)
        Connection.engine = create_engine('sqlite+pysqlite:///%s' % db_name_and_path,
         module=sqlite, 
         listeners=[ForeignKeysListener()])
        return Connection.engine
