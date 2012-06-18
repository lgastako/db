import logging
import string

from contextlib import contextmanager

from dbapiext import execute_f as execute

logger = logging.getLogger(__name__)


TABLE_NAME_CHARS = frozenset(string.ascii_letters + string.digits + "_.")


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
            execute(cursor, sql, *args, **kwargs)
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

    def relation(self, sql, *args, **kwargs):
        import deesupport
        if len(kwargs) == 0 and len(args) == 0 and \
                all(map(lambda c: c in TABLE_NAME_CHARS, sql)):
            sql = "SELECT * FROM %s" % sql
        rows = self.items(sql, *args, **kwargs)
        rel = deesupport.rows_to_relation(rows)
        return rel

    def item(self, sql, *args, **kwargs):
        results = self.items(sql, *args, **kwargs)
        num_results = len(results)
        if num_results != 1:
            raise UnexpectedCardinality(
                "Expected exactly one item but got %d." % num_results)
        return results[0]

    def tuple(self, sql, *args, **kwargs):
        rel = self.relation(sql, *args, **kwargs)
        num_tuples = len(rel)
        if num_tuples != 1:
            raise UnexpectedCardinality(
                "Expected exactly one tuple but got %d." % num_tuples)
        return rel.toTuple()

    def first(self, sql, *args, **kwargs):
        results = self.items(sql, *args, **kwargs)
        if len(results) > 0:
            return results[0]
        return None

    def count(self, from_plus, *args, **kwargs):
        sql = "SELECT COUNT(*) AS n FROM %s" % from_plus
        result = self.item(sql, *args, **kwargs)
        return result.n

    @staticmethod
    def _count_name(from_plus):
        if any(map(lambda c: c not in TABLE_NAME_CHARS, from_plus)):
            left = from_plus.split(" WHERE ", 1)[0]
            normalized_name = left.replace(" ", "_").replace(",", "")
        else:
            normalized_name = from_plus
        return normalized_name + "_count"

    def rel_count(self, from_plus, count_name=None, *args, **kwargs):
        if count_name is None:
            count_name = self._count_name(from_plus)
        sql = "SELECT COUNT(*) AS %s FROM %s" % (count_name, from_plus)
        rel = self.relation(sql, *args, **kwargs)
        return rel


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
relation = defaultdb.relation
tuple = defaultdb.tuple
do = defaultdb.do
first = defaultdb.first
count = defaultdb.count
rel_count = defaultdb.rel_count

import drivers

__all__ = [
    "tx",
    "do",
    "item",
    "items",
    "relation",
    "tuple",
    "count",
    "rel_count",
    "first",
    "drivers",
]
