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
        with pytest.raises(KeyError):
            db.drivers.expand_name(None)
