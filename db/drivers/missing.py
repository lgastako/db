# This driver is used whenever the original driver cannot be loaded, e.g.
# because the underlying libraries like psycopg2 or whatever are not
# installed.

from db.drivers import Driver


class DriverMissing(Exception):
    pass


def connect(*args, **kwargs):
    raise DriverMissing


class MissingDriver(Driver):
    pass


register = MissingDriver.register
