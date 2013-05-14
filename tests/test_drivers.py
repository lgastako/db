import pytest

import db
import db_sqlite3


class DriverTests(object):

    def clear_drivers(self):
        db._NAMED_DRIVERS = {}
        db.drivers._DRIVERS = {}

    def make_driver(self, label):

        class TestDriver(db.drivers.Driver):
            URL_SCHEME = "test"
            PARAM_STYLE = "qmark"

            def __init__(self, *args, **kwargs):
                super(TestDriver, self).__init__(*args, **kwargs)
                self.driver_label = label
                self.invocations = []

            def connect(self, *args, **kwargs):
                invocation = (label, args, kwargs)
                self.invocations.append(invocation)
                return invocation

        db.drivers.autoregister_class(TestDriver)
        driver = TestDriver("test_none")
        return driver

    def install_one_driver(self):
        db.clear()
        self.only_db = db.register(self.make_driver("connect_one_only"),
                                   db_name="only")

    def install_one_default_driver(self):
        db.clear()
        self.default_db = db.register(self.make_driver("connect_default_only"))

    def install_two_drivers(self):
        db.clear()
        self.first_db = db.register(self.make_driver("connect_two_first"),
                                    db_name="first")
        self.second_db = db.register(self.make_driver("connect_two_second"),
                                     db_name="second")


class TestCount(DriverTests):

    def test_none(self):
        self.clear_drivers()
        assert db.count_dbs() == 0

    def test_one(self):
        self.install_one_driver()
        assert db.count_dbs() == 1

    def test_two(self):
        self.install_two_drivers()
        assert db.count_dbs() == 2


class TestClear(DriverTests):

    def test_already_clear(self):
        self.clear_drivers()
        db.clear()
        assert db.count_dbs() == 0

    def test_not_already_clear(self):
        self.install_one_driver()
        db.clear()
        assert db.count_dbs() == 0

    def test_not_already_clear_multiple(self):
        self.install_two_drivers()
        db.clear()
        assert db.count_dbs() == 0


class TestGet(DriverTests):

    def test_default_one_default_driver(self):
        self.install_one_default_driver()
        default_db = db.get()
        assert default_db.driver.driver_label == "connect_default_only"

    def test_default_one_non_default_driver(self):
        self.install_one_driver()
        default_db = db.get()
        with pytest.raises(db.NoDefaultDatabase):
            default_db.items("SELECT * FROM foo")

    def test_named_one_named_driver(self):
        self.install_one_driver()
        named_db = db.get("only")
        assert named_db.driver.driver_label == "connect_one_only"

    def test_each_of_two_named_drivers(self):
        self.install_two_drivers()
        first_db = db.get("first")
        assert first_db.driver.driver_label == "connect_two_first"
        second_db = db.get("second")
        assert second_db.driver.driver_label == "connect_two_second"

    def test_no_such_db(self):
        # TODO: Is lazy the right behavior here?
        lazy = db.get("does_not_exist")
        with pytest.raises(db.NoSuchDatabase):
            lazy.do("SELECT 1")


class TestMisc(DriverTests):

    def setup_method(self, method):
        db.drivers.autoregister_class(db_sqlite3.Sqlite3Driver)

    def test_registering_returns_db(self):
        test_db = db.from_url("sqlite3:///:memory:", db_name="test_db")

        assert test_db is not None

        test_db.do("""CREATE TABLE foo (
            foo_id INTEGER PRIMARY KEY,
            bar TEXT NOT NULL
        )""")
        test_db.do("INSERT INTO foo (foo_id, bar) VALUES (1, 'a')")
        test_db.do("INSERT INTO foo (foo_id, bar) VALUES (2, 'b')")
        test_db.do("INSERT INTO foo (foo_id, bar) VALUES (3, 'c')")

        assert test_db.item("SELECT COUNT(*) AS n FROM foo").n == 3


#class TestByURL(object):
#
#    def setup_method(self, method):
#        db.clear()
#
#    def test_set_url_parser_override(self):
#        fake_driver1 = 5
#        fake_driver2 = 6
#        db.drivers.set_url_parser("postgresql",
#                                  lambda *args, **kwargs: fake_driver1)
#        db.drivers.set_url_parser("postgresql",
#                                  lambda *args, **kwargs: fake_driver2)
#        thedb = db.drivers.register_url("postgresql://user:pass@host/dbname")
#        assert thedb.driver == fake_driver2
#
#    def test_remove_url_parser_none(self):
#        db.drivers.remove_url_parser("SHESNOTTHERE")
#        assert "SHESNOTTHERE" not in db.drivers._URL_PARSERS
#
#    def test_remove_url_parser_override(self):
#        db.drivers.set_url_parser("postgresql",
#                                  lambda *args, **kwargs: fake_driver1)
#        db.drivers.remove_url_parser("postgresql")
#        assert "postgresql" not in db.drivers._URL_PARSERS
#
#    def setup_env(self, monkeypatch, env_name, driver):
#        db.drivers.set_url_parser("scheme", lambda *a, **k: driver)
#        monkeypatch.setenv(env_name, "scheme://user:pass@host/path")
#
#    def test_register_env_url_defaults(self, monkeypatch):
#        fake_driver = 7
#        self.setup_env(monkeypatch, "DATABASE_URL", fake_driver)
#        thedb = db.drivers.register_env_url()
#        assert thedb.driver == fake_driver
#
#    def test_register_env_url_diff_db_name(self, monkeypatch):
#        fake_driver = 8
#        self.setup_env(monkeypatch, "DATABASE_URL", fake_driver)
#        thedb = db.drivers.register_env_url(db_name="xyz")
#        assert thedb.driver == fake_driver
#
#    def test_register_env_url_diff_name(self, monkeypatch):
#        fake_driver = 9
#        self.setup_env(monkeypatch, "HEROKU_POSTGRESQL_NAVY_URL", fake_driver)
#        thedb = db.drivers.register_env_url("HEROKU_POSTGRESQL_NAVY_URL",
#                                            db_name="xyz")
#        assert thedb.driver == fake_driver
#
#
# These actually pass even if they aren't included in __all__ so I'm
# commenting them out until I can investigate (so as to not give a
# misleading impression that they are doing something).
#
# class TestDefaultDriversAreIncluded:
#
#     def test_sqlite3(self):
#         db.drivers.sqlite3.connect
#
#     def test_psycopg2(self):
#         db.drivers.psycopg2.connect
