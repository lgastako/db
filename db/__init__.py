import logging
import string

from contextlib import contextmanager
from functools import wraps

from dbapiext import execute_f as execute

logger = logging.getLogger(__name__)


TABLE_NAME_CHARS = frozenset(string.ascii_letters + string.digits + "_.")


class DBError(Exception):
    pass


class UnexpectedCardinality(DBError):
    pass


class NoDefaultDatabase(DBError):
    pass


class NoSuchDatabase(DBError):
    pass


class Transaction(object):

    def __init__(self, db, conn, cursor):
        self.db = db
        self.conn = conn
        self.cursor = cursor

    def items(self, sql, *args, **kwargs):
        kwargs.setdefault("paramstyle", self.db.driver.PARAM_STYLE)
        execute(self.cursor, sql, *args, **kwargs)
        try:
            results = self.cursor.fetchall()
        except Exception, ex:
            results = None
            if not self.db.driver.ignore_exception(ex):
                raise
        return results

    def item(self, sql, *args, **kwargs):
        results = self.items(sql, *args, **kwargs)
        num_results = len(results)
        if num_results != 1:
            raise UnexpectedCardinality(
                "Expected exactly one item but got %d." % num_results)
        return results[0]

    def relation(self, sql, *args, **kwargs):
        import deesupport
        if len(kwargs) == 0 and len(args) == 0 and \
                all(map(lambda c: c in TABLE_NAME_CHARS, sql)):
            sql = "SELECT * FROM %s" % sql
        rows = self.items(sql, *args, **kwargs)
        rel = deesupport.rows_to_relation(rows)
        return rel

    def tuple(self, sql, *args, **kwargs):
        rel = self.relation(sql, *args, **kwargs)
        num_tuples = len(rel)
        if num_tuples != 1:
            raise UnexpectedCardinality(
                "Expected exactly one tuple but got %d." % num_tuples)
        return rel.toTuple()

    do = items

    def first(self, sql, *args, **kwargs):
        results = self.items(sql, *args, **kwargs)
        if len(results) > 0:
            return results[0]
        return None

    def count(self, from_plus, count_name=None, *args, **kwargs):
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
        return self.relation(sql, *args, **kwargs)


def delegate_tx(f):

    @wraps(f)
    def wrapper(self, sql, *args, **kwargs):
        with self.tx(*args, **kwargs) as tx:
            m = getattr(tx, f.func_name)
            return m(sql, *args, **kwargs)

    return wrapper


def delegate_db(f):

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        m = getattr(self._getdb(), f.func_name)
        return m(*args, **kwargs)

    return wrapper


class Database(object):

    def __init__(self, driver_name=None):
        self.driver_name = driver_name
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            from db import drivers as _drivers
            self._driver = _drivers.get(self.driver_name)
        return self._driver

    def connect(self):
        return self.driver.connect()

    @contextmanager
    def txc(self, *args, **kwargs):
        conn = kwargs.pop("_conn", None)
        cursor = kwargs.pop("_cursor", None)

        if conn is None:
            conn = self.connect()

        try:
            if cursor is None:
                cursor = self.driver.cursor(conn)
            assert conn is not None
            assert cursor is not None
            yield conn, cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    @contextmanager
    def tx(self, *args, **kwargs):
        with self.txc(*args, **kwargs) as (conn, cursor):
            yield Transaction(self, conn, cursor)

    @delegate_tx
    def items(self, sql, *args, **kwargs):
        pass

    @delegate_tx
    def do(self, sql, *args, **kwargs):
        pass

    @delegate_tx
    def relation(self, sql, *args, **kwargs):
        pass

    @delegate_tx
    def item(self, sql, *args, **kwargs):
        pass

    @delegate_tx
    def tuple(self, sql, *args, **kwargs):
        pass

    @delegate_tx
    def first(self, sql, *args, **kwargs):
        pass

    def count(self, from_plus, *args, **kwargs):
        with self.tx(*args, **kwargs) as tx:
            return tx.count(from_plus, *args, **kwargs)

    def rel_count(self, from_plus, count_name=None, *args, **kwargs):
        with self.tx(*args, **kwargs) as tx:
            return tx.rel_count(sql, *args, **kwargs)


def get(driver_name=None):
    return Database(driver_name)


def put(database):
    database.release()


class DefaultDatabase(object):

    def _getdb(self):
        return get()

    @delegate_db
    def connect(self, *args, **kwargs):
        return self._getdb().connect(*args, **kwargs)

    @delegate_db
    def tx(self, *args, **kwargs):
        return self._getdb().tx(*args, **kwargs)

    @delegate_db
    def txc(self, *args, **kwargs):
        return self._getdb().txc(*args, **kwargs)

    @delegate_db
    def items(self, *args, **kwargs):
        return self._getdb().items(*args, **kwargs)

    @delegate_db
    def item(self, *args, **kwargs):
        return self._getdb().item(*args, **kwargs)

    @delegate_db
    def relation(self, *args, **kwargs):
        return self._getdb().relation(*args, **kwargs)

    @delegate_db
    def tuple(self, *args, **kwargs):
        return self._getdb().tuple(*args, **kwargs)

    @delegate_db
    def do(self, *args, **kwargs):
        return self._getdb().do(*args, **kwargs)

    @delegate_db
    def first(self, *args, **kwargs):
        return self._getdb().first(*args, **kwargs)

    @delegate_db
    def count(self, *args, **kwargs):
        return self._getdb().count(*args, **kwargs)

    @delegate_db
    def rel_count(self, *args, **kwargs):
        return self._getdb().rel_count(*args, **kwargs)


defaultdb = DefaultDatabase()

connect = defaultdb.connect
tx = defaultdb.tx
txc = defaultdb.txc
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
    "connect",
    "tx",
    "txc",
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
