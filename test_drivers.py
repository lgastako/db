import pytest

import db


class DriverTests(object):

    def clear_drivers(self):
        db.drivers._DRIVERS = {}

    def install_one_driver(self):
        db.drivers._DRIVERS = {"only": lambda *a, **k: "connect_one_only"}

    def install_two_drivers(self, second_driver_name="DEFAULT"):
        db.drivers._DRIVERS = {"first": lambda *a, **k: "connect_two_first",
                               second_driver_name:
                                    lambda *a, **k: second_driver_name}


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
        assert db.drivers.connect() == "connect_one_only"

    def test_connect_default_two_drivers(self):
        self.install_two_drivers()
        assert db.drivers.connect() == "DEFAULT"

    def test_connect_non_default(self):
        self.install_two_drivers()
        assert db.drivers.connect("first") == "connect_two_first"
