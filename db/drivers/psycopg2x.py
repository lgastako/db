import db
from db.drivers import Driver

try:
    import psycopg2
    import psycopg2.extras

    def connect(*args, **kwargs):
        kwargs["connection_factory"] = psycopg2.extras.NamedTupleConnection
        conn = psycopg2.connect(*args, **kwargs)
        return conn

    class PostgresDriver(Driver):

        PARAM_STYLE = "pyformat"

        def connect(self):
            return connect(self.conn_string)

        def ignore_exception(self, ex):
            return "no results to fetch" in str(ex)

    register = PostgresDriver.register

except ImportError:
    from missing import *
