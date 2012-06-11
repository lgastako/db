import urlparse

import db

from functools import partial

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


__all__ = [
    "expand_name",
    "register",
    "deregister",
    "clear",
    "connect",
    "disconnect",
]
