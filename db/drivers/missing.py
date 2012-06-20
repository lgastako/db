# This driver is used whenever the original driver cannot be loaded, e.g.
# because the underlying libraries like psycopg2 or whatever are not
# installed.

from db.drivers import Driver


def connect(*args, **kwargs):
    raise NotImplementedError


class MissingDriver(Driver):
    pass


register = MissingDriver.register
