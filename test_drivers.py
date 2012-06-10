import pytest

import db


class TestExpandDriverName(object):

    def test_not_none_non_existent(self):
        assert db.drivers.expand_name("bar") == "bar"

    def test_not_none_single_driver(self):
        db.drivers.clear()
        db.drivers.register(lambda *a, **k: None, "foo")
        assert db.drivers.expand_name("foo") == "foo"

    def test_not_none_multiple_drivers_default_exists(self):
        db.drivers.clear()
        db.drivers.register(lambda *a, **k: None, "foo")
        db.drivers.register(lambda *a, **k: None, "DEFAULT")
        assert db.drivers.expand_name("foo") == "foo"

    def test_none_single_driver(self):
        db.drivers.clear()
        db.drivers.register(lambda *a, **k: None, "foo")
        assert db.drivers.expand_name(None) == "foo"

    def test_none_multiple_drivers_default_exists(self):
        db.drivers.clear()
        db.drivers.register(lambda *a, **k: None, "foo")
        db.drivers.register(lambda *a, **k: None, "DEFAULT")
        assert db.drivers.expand_name(None) == "DEFAULT"

    def test_none_multiple_drivers_no_default_exists(self):
        db.drivers.clear()
        db.drivers.register(lambda *a, **k: None, "foo")
        db.drivers.register(lambda *a, **k: None, "bar")
        assert db.drivers.expand_name(None) == "DEFAULT"


class TestCount(object):

    def test_none(self):
        db.drivers._DRIVERS = {}
        assert db.drivers.count() == 0

    def test_one(self):
        db.drivers._DRIVERS = {"foo":"fake"}
        assert db.drivers.count() == 1

    def test_two(self):
        db.drivers._DRIVERS = {"foo":"fake", "bar": "fake2"}
        assert db.drivers.count() == 2


class TestClear(object):

    def test_already_clear(self):
        db.drivers._DRIVERS = {}
        db.drivers.clear()
        assert db.drivers.count() == 0

    def test_not_already_clear(self):
        db.drivers._DRIVERS = {"foo":"fake"}
        db.drivers.clear()
        assert db.drivers.count() == 0

    def test_not_already_clear_multiple(self):
        db.drivers._DRIVERS = {"foo":"fake", "bar": "fake2"}
        db.drivers.clear()
        assert db.drivers.count() == 0
