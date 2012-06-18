import db
from db.drivers import Driver

try:
    import psycopg2
    import psycopg2.extras

    def connect(*args, **kwargs):
        kwargs["connection_factory"] = psycopg2.extras.NamedTupleConnection
        conn = psycopg2.connect(*args, **kwargs)
        return conn

    def register(conn_string, name=None, **kwargs):
        driver = PostgresDriver(conn_string, **kwargs)
        return db.drivers.register(driver, name)

    class PostgresDriver(Driver):

        PARAM_STYLE = "pyformat"

        def __init__(self, conn_string):
            self.conn_string = conn_string

        def connect(self):
            return connect(self.conn_string)

        def ignore_exception(self, ex):
            return "no results to fetch" in str(ex)

except ImportError:
    from missing import *
