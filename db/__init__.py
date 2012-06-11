import logging

from contextlib import contextmanager

from dbapiext import execute_f

logger = logging.getLogger(__name__)


class DBError(Exception):
    pass


class UnexpectedCardinality(DBError):
    pass


class Database(object):

    def __init__(self, driver_name=None):
        self.driver_name = driver_name

    @contextmanager
    def tx(self, *args, **kwargs):
        conn = kwargs.pop("_conn", None)
        cursor = kwargs.pop("_cursor", None)

        if conn is None:
            import drivers as _drivers
            conn = _drivers.connect(self.driver_name)

        try:
            if cursor is None:
                cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def items(self, sql, *args, **kwargs):
        conn = kwargs.pop("_conn", None)
        cursor = kwargs.pop("_cursor", None)

        with self.tx(conn, cursor) as cursor:
            execute_f(cursor, sql, *args, **kwargs)
            try:
                results = cursor.fetchall()
            except Exception, ex:
                results = None
                # TODO: This is specifically for psycopg2, we need to handle
                # in general.
                if "no results to fetch" not in str(ex):
                    raise
        return results

    do = items

    def item(self, sql, *args, **kwargs):
        results = self.items(sql, *args, **kwargs)
        num_results = len(results)
        if num_results != 1:
            raise UnexpectedCardinality("Expected exactly one item but got %d." %
                                        num_results)
        return results[0]

    def first(self, sql, *args, **kwargs):
        results = self.items(sql, *args, **kwargs)
        if len(results) > 0:
            return results[0]
        return None

    def count(self, from_plus, *args, **kwargs):
        sql = "SELECT COUNT(*) AS n FROM %s" % from_plus
        result = item(sql, *args, **kwargs)
        return result.n


def get(driver_name=None):
    driver_name = drivers.expand_name(driver_name)
    return Database(driver_name)


def put(database, driver_name=None):
    if database.conn:
        disconnect(database.conn, database.driver_name)


defaultdb = Database()

tx = defaultdb.tx
items = defaultdb.items
item = defaultdb.item
do = defaultdb.do
first = defaultdb.first
count = defaultdb.count

import drivers

__all__ = [
    "tx",
    "do",
    "item",
    "items",
    "count",
    "first",
    "drivers",
]
