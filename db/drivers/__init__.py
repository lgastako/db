import db

# A mapping from a name to a function that, given no arguments, "checks out"
# a connection (or creates one if it's not a pool) and given a connection
# back, "returns it to the pool" (or destroy's it if it's not a pool, etc)
# If only one exists it will become the default driver automatically.  If
# more than one exists then the key "None" should point to the default
# driver.
_DRIVERS = {}


def get(driver_name=None):
    return _DRIVERS[driver_name]


def register(driver, driver_name=None):
    _DRIVERS[driver_name] = driver
    return db.get(driver_name)


def deregister(driver_name):
    del _DRIVERS[driver_name]


def clear():
    global _DRIVERS
    _DRIVERS = {}


def count():
    return len(_DRIVERS)


class Driver(object):
    PARAM_STYLE = "pyformat"

    def __init__(self, conn_string):
        self.conn_string = conn_string

    def connect(self):
        raise NotImplementedError

    def ignore_exception(self, _ex):
        return False

    def cursor(self, conn):
        return conn.cursor()

    def release(self):
        pass

    @classmethod
    def register(cls, conn_string, name=None, **kwargs):
        driver = cls(conn_string, **kwargs)
        return db.drivers.register(driver, name)


from db.drivers import sqlite3x
from db.drivers import psycopg2x

__all__ = [
    "get",
    "register",
    "deregister",
    "clear",
    "connect",
    "Driver",
    # Drivers
    "sqlite3x",
    "psycopg2x"
]
