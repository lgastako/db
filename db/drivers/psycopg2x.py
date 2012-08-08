from db.drivers import Driver

try:
    import psycopg2
    import psycopg2.extras

    def connect(*args, **kwargs):
        kwargs["connection_factory"] = psycopg2.extras.NamedTupleConnection
        import logging
        logging.info("Creating connection to: %s %s",  args, kwargs)
        conn = psycopg2.connect(*args, **kwargs)
        return conn

    class PostgresDriver(Driver):

        PARAM_STYLE = "pyformat"

        def connect(self):
            return connect(*self.conn_args, **self.conn_kwargs)

        def ignore_exception(self, ex):
            return "no results to fetch" in str(ex)

    register = PostgresDriver.register

except ImportError:
    from missing import connect
    from missing import register

all = [connect.__name__, register.__name__]
