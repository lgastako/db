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


class CallProxy(object):

    def __init__(self, target, attr_name, cb, names):
        self.target = target
        self.attr_name = attr_name
        self.cb = cb
        self.names = names

    def __getattr__(self, name):
        return self.__class__(self.target,
                              self.attr_name,
                              self.cb,
                              self.names + [name])

    def __call__(self, *args, **kwargs):
        iparens = kwargs.pop("iparens", True)
        oparens = kwargs.pop("oparens", False)
        db_inst = self.cb(self.target[self.attr_name])
        param_components = []
        param_values = []
        for arg in args:
            if isinstance(arg, RAW):
                param_components.append(str(arg))
                param_values.extend(arg.values)
            else:
                param_components.append("%X")
                param_values.append(arg)

        param_template = ", ".join(param_components)
        name = ".".join(self.names)

        results = self._get_results(db_inst,
                                    name,
                                    param_template,
                                    param_values,
                                    iparens,
                                    oparens)
        return results

    def _get_results(self, db_inst, name, param_template, values,
        iparens, oparens):
        raise NotImplementedError


class CProxy(CallProxy):

    def _get_results(self, db_inst, name, param_template, values,
        iparens,
        oparens):
        if iparens:
            sql = "SELECT %s(%s) AS value" % (name, param_template)
        else:
            sql = "SELECT %s %s" % (name, param_template)
        return db_inst.item(sql, *values).value


class CSProxy(CallProxy):

    def _get_results(self, db_inst, name, param_template, values,
        iparens, oparens):
        if iparens:
            f_call = "%s(%s)"
        else:
            f_call = "%s %s"
        clause = f_call
        if oparens:
            clause = "(%s)" % clause
        clause = clause % (name, param_template)
        sql = "SELECT * FROM %s AS tmp" % clause
        results = db_inst.items(sql, *values)
        return results


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
            yield cursor

    def items(self, sql, *args, **kwargs):
        with self.tx(*args, **kwargs) as cursor:
            kwargs.setdefault("paramstyle", self.driver.PARAM_STYLE)
            execute(cursor, sql, *args, **kwargs)
            try:
                results = cursor.fetchall()
            except Exception, ex:
                results = None
                if not self.driver.ignore_exception(ex):
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

    @property
    def c(self):
        # TODO: Cache?
        return CProxy(locals(), "self", lambda db: db, [])

    @property
    def cs(self):
        # TODO: Cache?
        return CSProxy(locals(), "self", lambda db: db, [])


def get(driver_name=None):
    return Database(driver_name)


def put(database):
    database.release()


class DefaultDatabase(object):

    def __init__(self):
        self._db = None

    def _getdb(self):
        if not self._db:
            self._db = get()
        return self._db

    def connect(self, *args, **kwargs):
        return self._getdb().connect(*args, **kwargs)

    def tx(self, *args, **kwargs):
        return self._getdb().tx(*args, **kwargs)

    def txc(self, *args, **kwargs):
        return self._getdb().txc(*args, **kwargs)

    def items(self, *args, **kwargs):
        return self._getdb().items(*args, **kwargs)

    def item(self, *args, **kwargs):
        return self._getdb().item(*args, **kwargs)

    def relation(self, *args, **kwargs):
        return self._getdb().relation(*args, **kwargs)

    def tuple(self, *args, **kwargs):
        return self._getdb().tuple(*args, **kwargs)

    def do(self, *args, **kwargs):
        return self._getdb().do(*args, **kwargs)

    def first(self, *args, **kwargs):
        return self._getdb().first(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self._getdb().count(*args, **kwargs)

    def rel_count(self, *args, **kwargs):
        return self._getdb().rel_count(*args, **kwargs)

    def __getattribute__(self, name):
        try:
            return super(DefaultDatabase, self).__getattribute__(name)
        except AttributeError:
            if name.startswith("_"):
                raise
            try:
                db_ = self._getdb()
                return getattr(db_, name)
            except AttributeError:
                raise "Boom"


defaultdb = DefaultDatabase()


def clear():
    global defaultdb
    defaultdb = DefaultDatabase()
    drivers._DRIVERS = {}


import drivers
import deesupport

connect = lambda *a, **kw: defaultdb.connect(*a, **kw)
tx = lambda *a, **kw: defaultdb.tx(*a, **kw)
txc = lambda *a, **kw: defaultdb.txc(*a, **kw)
do = lambda *a, **kw: defaultdb.do(*a, **kw)
item = lambda *a, **kw: defaultdb.item(*a, **kw)
items = lambda *a, **kw: defaultdb.items(*a, **kw)
relation = lambda *a, **kw: defaultdb.relation(*a, **kw)
tuple = lambda *a, **kw: defaultdb.tuple(*a, **kw)
count = lambda *a, **kw: defaultdb.count(*a, **kw)
rel_count = lambda *a, **kw: defaultdb.rel_count(*a, **kw)
first = lambda *a, **kw: defaultdb.first


c = CProxy(globals(), "defaultdb", lambda db: db._getdb(), [])
cs = CSProxy(globals(), "defaultdb", lambda db: db._getdb(), [])


class RAW(object):

    def __init__(self, raw_str, *values):
        self.raw_str = raw_str
        self.values = values

    def __str__(self):
        return str(self.raw_str)


__all__ = [
    "from_",
    "drivers",
    "deesupport",
    "get",
    "put",
    "clear",
    "defaultdb"
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
]
