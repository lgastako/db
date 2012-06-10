from __future__ import unicode_literals

import logging

from contextlib import contextmanager
from functools import partial

import psycopg2
from psycopg2.extras import NamedTupleCursor

from dbapiext import execute_f

logger = logging.getLogger(__name__)


class UnexpectedCardinality(Exception):
    pass


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

__all__ = [
    "do",
    "item",
    "items",
    "count",
    "drivers",
]

}