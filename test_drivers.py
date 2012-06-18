import pytest

import db


class DriverTests(object):

    def clear_drivers(self):
        db.drivers._DRIVERS = {}

    def make_driver(self, label):
        invocations = []

        def driver(*args, **kwargs):
            invocation = (label, args, kwargs)
            invocations.append(invocation)
            return invocation

        driver.invocations = invocations
        return driver

    def install_one_driver(self):
        db.drivers.clear()
        db.drivers.register(self.make_driver("connect_one_only"), "only")

    def install_two_drivers(self, second_driver_name="DEFAULT"):
        db.drivers.clear()
        db.drivers.register(self.make_driver("connect_two_first"), "first"),
        db.drivers.register(self.make_driver(second_driver_name),
                            second_driver_name)


class TestExpandDriverName(DriverTests):

    def test_not_none_non_existent(self):
        assert db.drivers.expand_name("bar") == "bar"

    def test_not_none_single_driver(self):
        self.install_one_driver()
        assert db.drivers.expand_name("foo") == "foo"

    def test_not_none_multiple_drivers_default_exists(self):
        self.install_two_drivers()
        assert db.drivers.expand_name("foo") == "foo"

    def test_none_single_driver(self):
        self.install_one_driver()
        assert db.drivers.expand_name(None) == "only"

    def test_none_multiple_drivers_default_exists(self):
        self.install_two_drivers()
        assert db.drivers.expand_name(None) == "DEFAULT"

    def test_none_multiple_drivers_no_default_exists(self):
        self.install_two_drivers("bar")
        assert db.drivers.expand_name(None) == "DEFAULT"


class TestCount(DriverTests):

    def test_none(self):
        self.clear_drivers()
        assert db.drivers.count() == 0

    def test_one(self):
        self.install_one_driver()
        assert db.drivers.count() == 1

    def test_two(self):
        self.install_two_drivers()
        assert db.drivers.count() == 2


class TestClear(DriverTests):

    def test_already_clear(self):
        self.clear_drivers()
        db.drivers.clear()
        assert db.drivers.count() == 0

    def test_not_already_clear(self):
        self.install_one_driver()
        db.drivers.clear()
        assert db.drivers.count() == 0

    def test_not_already_clear_multiple(self):
        self.install_two_drivers()
        db.drivers.clear()
        assert db.drivers.count() == 0


class TestConnect(DriverTests):

    def test_connect_default_one_driver(self):
        self.install_one_driver()
        assert db.drivers.connect() == ("connect_one_only", (), {})

    def test_connect_default_two_drivers(self):
        self.install_two_drivers()
        assert db.drivers.connect() == ("DEFAULT", (), {})

    def test_connect_non_default(self):
        self.install_two_drivers()
        assert db.drivers.connect("first") == ("connect_two_first", (), {})


class TestDisconnect(DriverTests):

    def test_disconnect_default_one_driver(self):
        self.install_one_driver()
        db.drivers.disconnect("foo")
        assert db.drivers._DRIVERS["only"].invocations == \
            [("connect_one_only", ("foo",), {})]

    def test_disconnect_default_two_drivers(self):
        self.install_two_drivers()
        db.drivers.disconnect("foo")
        assert db.drivers._DRIVERS["DEFAULT"].invocations == \
            [("DEFAULT", ("foo",), {})]

    def test_disconnect_non_default(self):
        self.install_two_drivers()
        db.drivers.disconnect("foo", "first")
        assert db.drivers._DRIVERS["first"].invocations == \
            [("connect_two_first", ("foo",), {})]


class TestMisc(DriverTests):

    def test_registering_returns_db(self):
        db.drivers.clear()
        assert db.drivers.count() == 0
        test_db = db.drivers.register(self.make_driver("test"), "test")
        assert test_db is not None
        assert hasattr(test_db, "items")
