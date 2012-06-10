from __future__ import unicode_literals

import logging

from contextlib import contextmanager
from functools import partial

import psycopg2
from psycopg2.extras import NamedTupleCursor

from dbapiext import execute_f

logger = logging.getLogger(__name__)

DEFAULT_DRIVER_NAME = "DEFAULT"

# A mapping from a name to a function that, given no arguments, "checks out"
# a connection (or creates one if it's not a pool) and given a connection
# back, "returns it to the pool" (or destroy's it if it's not a pool, etc)
# If only one exists it will become the default driver automatically.  If
# more than one exists then the key "DEFAULT" should point to the default
# driver.
_DRIVERS = {}


def _expand_driver_name(driver_name):
    if driver_name is None:
        if len(_DRIVERS) == 1:
            driver_name = _DRIVERS.keys()[0]
        else:
            driver_name = DEFAULT_DRIVER_NAME
    return driver_name


def register_driver(driver, driver_name=None):
    driver_name = _expand_driver_name(driver_name)
    if driver_name in _DRIVERS:
        raise KeyError("%s already in _DRIVERS" % driver_name)
    _DRIVERS[driver_name] = driver


def unregister_driver(name):
    del _DRIVERS[name]


def clear_drivers():
    global _DRIVERS
    _DRIVERS = {}


class UnexpectedCardinality(Exception):
    pass


def get_connection(driver_name):
    return _DRIVERS[driver_name]()


def put_connection(driver_name, connection):
    return _DRIVERS[driver_name](connection)


def yield_cursor(conn):
    # TODO: Better
    try:
        from queries import sqlite3
        cursor = next(sqlite3.yield_cursor(conn))
    except Exception:
        try:
            from queries import postgres
            cursor = next(postgres.yield_cursor(conn))
        except Exception:
            try:
                from queries import mysql
                cursor = next(mysql.yield_cursor(conn))
            except Exception:
                cursor = conn.cursor()
    yield cursor


def connect(driver_name=None):
    driver_name = _expand_driver_name(driver_name)
    driver = _DRIVERS[driver_name]
    conn = driver()
    return conn


def disconnect(conn, driver_name=None):
    if driver_name is None:
        raise NotImplementedError
    driver = _DRIVERS[driver_name]
    return driver(conn)


@contextmanager
def tx(*args, **kwargs):
    conn = kwargs.pop("_conn", None)
    cursor = kwargs.pop("_cursor", None)

    if conn is None:
        conn = connect()

    try:
        if cursor is None:
            # TODO: Use appropriate arguments depending on driver type
            # ideally in a very nice abstraction
            cursor = next(yield_cursor(conn))
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
        except psycopg2.ProgrammingError, ex:
            results = None
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


def make_create(table):
    def create(dikt):
        names = []
        values = []
        for name, value in dikt.iteritems():
            names.append(name)
            values.append(value)
        sql = "INSERT INTO %s (%s) VALUES (%X) RETURNING *"
        row = do(sql, table, names, values)
        return row
    return create


def make_count(table):
    def count():
        return item("SELECT COUNT(*) FROM %s" % table).count
    return count
