DEFAULT_DRIVER_NAME = "DEFAULT"

# A mapping from a name to a function that, given no arguments, "checks out"
# a connection (or creates one if it's not a pool) and given a connection
# back, "returns it to the pool" (or destroy's it if it's not a pool, etc)
# If only one exists it will become the default driver automatically.  If
# more than one exists then the key "DEFAULT" should point to the default
# driver.
_DRIVERS = {}


def expand_name(driver_name):
    if driver_name is None:
        if len(_DRIVERS) == 1:
            driver_name = _DRIVERS.keys()[0]
        else:
            driver_name = DEFAULT_DRIVER_NAME
    return driver_name


def register(driver, driver_name=None):
    driver_name = expand_name(driver_name)
    if driver_name in _DRIVERS:
        raise KeyError("%s already in _DRIVERS" % driver_name)
    _DRIVERS[driver_name] = driver


def deregister(driver_name):
    del _DRIVERS[driver_name]


def clear():
    global _DRIVERS
    _DRIVERS = {}


def count():
    return len(_DRIVERS)


def connect(driver_name=None):
    driver_name = expand_name(driver_name)
    driver = _DRIVERS[driver_name]
    conn = driver()
    return conn


def disconnect(conn, driver_name=None):
    driver_name = expand_name(driver_name)
    driver = _DRIVERS[driver_name]
    return driver(conn)


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


import sqlite3
import psycopg2
import mysql

__all__ = [
    # Functions
    "expand_name",
    "register",
    "deregister",
    "clear",
    "connect",
    "disconnect",
    # Drivers
    "sqlite3",
    "psycopg2",
    "mysql"
]
