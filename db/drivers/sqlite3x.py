import db.drivers
import sqlite3

from collections import namedtuple


class Sqlite3Driver(object):

    def __init__(self, conn_string):
        self.conn_string = conn_string


def _namedtuple_factory(cursor, row):
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)


def connect(*args, **kwargs):
    """Wraps sqlite3.connect forcing the options required for a
       db style connection to work.  As of this writing that consists
       of installing a NamedTupleCursor factory but may grow more involved
       over time as things change.
    """

    conn = sqlite3.connect(*args, **kwargs)
    conn.row_factory = self._namedtuple_factory
    return conn


def register(conn_string, name=None):
    driver = Sqlite3Driver(conn_string)
    return db.drivers.register(driver, name)
