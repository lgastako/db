# FROM http://peter-hoffmann.com/2010/python-sqlite-namedtuple-factory.html
# We can do better.

from collections import namedtuple

def namedtuple_factory(cursor, row):
    """
    Usage:
    con.row_factory = namedtuple_factory
    """
    fields = [col[0] for col in cursor.description]
    Row = namedtuple("Row", fields)
    return Row(*row)

### End stuff from url


def yield_cursor(conn):
    # Can we avoid doing this every time?  
    conn.row_factory = namedtuple_factory
    cursor = conn.cursor()
    yield cursor
