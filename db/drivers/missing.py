# This driver is used whenever the original driver cannot be loaded, e.g.
# because the underlying libraries like psycopg2 or whatever are not
# installed.

from db.drivers import Driver
from db import DBError


class NativeDriverMissing(DBError):
    pass


def connect(*args, **kwargs):
    raise NativeDriverMissing


class MissingNativeDriver(Driver):

    def connect(self):
        return connect()


register = MissingNativeDriver.register
