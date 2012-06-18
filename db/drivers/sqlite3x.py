import db.drivers
import sqlite3

from collections import namedtuple


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
    conn.row_factory = _namedtuple_factory
    return conn


def register(conn_string, name=None):
    conn = connect(conn_string)

    def driver(*a, **kwargs):
        return conn

    return db.drivers.register(driver, name)
