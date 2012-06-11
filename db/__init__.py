from __future__ import unicode_literals

import logging

from contextlib import contextmanager
from functools import partial

from dbapiext import execute_f

logger = logging.getLogger(__name__)


class UnexpectedCardinality(Exception):
    pass


@contextmanager
def tx(*args, **kwargs):
    conn = kwargs.pop("_conn", None)
    cursor = kwargs.pop("_cursor", None)

    if conn is None:
        import drivers as _drivers
        conn = _drivers.connect()

    try:
        if cursor is None:
            cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def items(sql, *args, **kwargs):
    conn = kwargs.pop("_conn", None)
    cursor = kwargs.pop("_cursor", None)

    with tx(conn, cursor) as cursor:
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


def item(sql, *args, **kwargs):
    results = items(sql, *args, **kwargs)
    num_results = len(results)
    if num_results != 1:
        raise UnexpectedCardinality("Expected exactly one item but got %d." %
                                    num_results)
    return results[0]


def first(sql, *args, **kwargs):
    results = items(sql, *args, **kwargs)
    if len(results) > 0:
        return results[0]
    return None


def count(from_plus, *args, **kwargs):
    sql = "SELECT COUNT(*) AS n FROM %s" % from_plus
    result = item(sql, *args, **kwargs)
    return result.n


class Database(object):

    def __init__(self, driver_name):
        self.driver_name = driver_name

    def tx(self, *args, **kwargs):
        yield tx(*args, **kwargs)

    def do(self, *args, **kwargs):
        if "_conn" in kwargs:
            logger.debug("Using connection from kwargs.")
        else:
            logger.debug("Creating connection using driver: %s",
                         self.driver_name)
            kwargs["_conn"] = drivers.connect(self.driver_name)
        return do(*args, **kwargs)

    def item(self, *args, **kwargs):
        return item(*args, **kwargs)

    def items(self, *args, **kwargs):
        return items(*args, **kwargs)

    def count(self, *args, **kwargs):
        return count(*args, **kwargs)


def get(driver_name=None):
    driver_name = drivers.expand_name(driver_name)
    return Database(driver_name)


def put(database, driver_name=None):
    if database.conn:
        disconnect(database.conn, database.driver_name)


# def make_create(table):
#     def create(dikt):
#         names = []
#         values = []
#         for name, value in dikt.iteritems():
#             names.append(name)
#             values.append(value)
#         sql = "INSERT INTO %s (%s) VALUES (%X) RETURNING *"
#         row = do(sql, table, names, values)
#         return row
#     return create

import drivers
__all__ = [
    "do",
    "item",
    "items",
    "count",
    "drivers",
]
