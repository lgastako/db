import db
RAW = db.RAW

TEST_DRIVER = "test_driver"


class TestPsycopg2x:

    def setup_method(self, method):
        db.drivers.psycopg2x.register(dbname="db_test",
                                      host="localhost",
                                      driver_name=TEST_DRIVER)
        self._db = db.get(TEST_DRIVER)

    def test_f_call_with_raw(self):
        res = self._db.c.extract(
            RAW("hour FROM timestamp '2001-02-16 20:38:40'"))
        assert res == 20

    def test_sp_call_with_default_schema(self):
        assert self._db.c.example_double(3) == 6

    def test_sp_call_with_alt_schema(self):
        assert self._db.c.psycopg2x_tests.example_rand(3) == 4

    def test_sp_returns_tables(self):
        res = self._db.cs.dup(9, oparens=False)
        assert len(res) == 1
        res = res[0]
        assert res.f1 == 9
        assert res.f2 == '9 is text'
