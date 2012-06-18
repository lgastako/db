# This driver is used whenever the original driver cannot be loaded, e.g.
# because the underlying libraries like psycopg2 or whatever are not
# installed.
import db

from db.drivers import Driver


def connect(*args, **kwargs):
    raise NotImplementedError


def register(conn_string, name=None, **kwargs):
    driver = MissingDriver(conn_string, **kwargs)
    return db.drivers.register(driver, name)


class MissingDriver(Driver):
    pass
