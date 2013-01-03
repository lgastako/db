from db.drivers import Driver

try:
    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions

    def connect(*args, **kwargs):
        kwargs.setdefault("connection_factory",
                          psycopg2.extras.NamedTupleConnection)
        conn = psycopg2.connect(*args, **kwargs)
        return conn

    class PostgresDriver(Driver):

        PARAM_STYLE = "pyformat"

        def connect(self):
            return connect(*self.conn_args, **self.conn_kwargs)

        def ignore_exception(self, ex):
            return "no results to fetch" in str(ex)

        def setup_cursor(self, cursor):
            psycopg2.extensions.register_type(psycopg2.extensions.UNICODE,
                                              cursor)

    register = PostgresDriver.register

except ImportError:
    from missing import connect
    from missing import register

all = [connect.__name__, register.__name__]
