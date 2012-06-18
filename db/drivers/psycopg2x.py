from db.drivers import Driver

import psycopg2
import psycopg2.extras


def connect(*args, **kwargs):
    kwargs["connection_factory"] = psycopg2.extras.NamedTupleConnection
    conn = psycopg2.connect(*args, **kwargs)
    return conn


class PostgresDriver(Driver):

    PARAM_STYLE = "pyformat"

    def __init__(self, conn_string):
        self.conn_string = conn_string
        self.conn = connect(self.conn_string)

    def connect(self):
        return conn

    def ignore_exception(self, ex):
        return "no results to fetch" in str(ex)
