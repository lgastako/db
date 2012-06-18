from collections import namedtuple
from functools import partial

import sqlite3

import pytest

import db


#########################
# BASE TEST DEFINITIONS #
#########################

CREATE_FOO_SQL = """CREATE TABLE foo (
                        foo_id INTEGER PRIMARY KEY,
                        value TEXT
                    )
                 """


class ExampleDBTests(object):

    def setup_method(self, method):
        db.drivers.clear()
        self.conn = db.drivers.sqlite3x.connect(":memory:")
        self.cursor = self.conn.cursor()
        db.drivers.sqlite3x.register(":memory:")
        db.do(CREATE_FOO_SQL)
        db.do("INSERT INTO foo VALUES (1, 'foo')")

    def insert_another(self):
        db.do("INSERT INTO foo (foo_id, value) VALUES (2, 'bar')")


class DoTests(ExampleDBTests):

    def test_insert(self):
        db.do("DELETE FROM foo")
        db.do("INSERT INTO foo (foo_id, value) VALUES (1, 'baz')")

        rows = self.items("SELECT * FROM foo")
        assert len(rows) == 1
        row = rows[0]
        assert row.foo_id == 1
        assert row.value == 'baz'


class ItemTests(ExampleDBTests):

    def test_basic_select(self):
        row = self.item("SELECT * FROM foo")

        assert row.foo_id == 1
        assert row.value == 'foo'


class ItemsTests(ExampleDBTests):

    def test_basic_select(self):
        rows = self.items("SELECT * FROM foo")

        assert len(rows) == 1
        row = rows[0]
        assert row.foo_id == 1
        assert row.value == 'foo'

    def test_basic_select_multiple(self):
        self.insert_another()

        rows = self.items("SELECT * FROM foo")

        assert len(rows) == 2
        row = rows[0]
        assert row.foo_id == 1
        assert row.value == 'foo'
        row = rows[1]
        assert row.foo_id == 2
        assert row.value == 'bar'


class CountTests(ExampleDBTests):

    def test_basic_count(self):
        assert self.count("foo") == 1

    def test_basic_count_multiple(self):
        self.insert_another()
        assert self.count("foo") == 2

    def test_complex_count(self):
        db.do("""CREATE TABLE bar (
                     bar_id INTEGER PRIMARY KEY,
                     value TEXT
                 )""")
        db.do("INSERT INTO foo VALUES (2, 'bar')")
        db.do("INSERT INTO foo VALUES (3, 'baz')")
        db.do("INSERT INTO foo VALUES (4, 'bim')")

        db.do("INSERT INTO bar VALUES (1, 'foo')")
        db.do("INSERT INTO bar VALUES (2, 'bart')")
        db.do("INSERT INTO bar VALUES (3, 'bazzle')")
        db.do("INSERT INTO bar VALUES (4, 'bim')")

        assert self.count("foo, bar WHERE foo.value = bar.value") == 2


############
# CONTEXTS #
############


class ExplicitConnection(object):

    def setup_method(self, method):
        super(ExplicitConnection, self).setup_method(method)
        self.do = partial(db.do, _conn=self.conn)
        self.item = partial(db.item, _conn=self.conn)
        self.items = partial(db.items, _conn=self.conn)
        self.count = partial(db.count, _conn=self.conn)


class ImplicitConnection(object):

    def setup_method(self, method):
        super(ImplicitConnection, self).setup_method(method)
        self.do = db.do
        self.item = db.item
        self.items = db.items
        self.count = db.count


######################################
# COMBINATIONS OF TESTS AND CONTEXTS #
######################################


class TestDoExplicit(ExplicitConnection, DoTests):
    pass


class TestDoImplicit(ImplicitConnection, DoTests):
    pass


class TestItemExplicit(ExplicitConnection, ItemTests):
    pass


class TestItemImplicit(ImplicitConnection, ItemTests):
    pass


class TestItemsExplicit(ExplicitConnection, ItemsTests):
    pass


class TestItemsImplicit(ImplicitConnection, ItemsTests):
    pass


class TestCountExplicit(ExplicitConnection, CountTests):
    pass


class TestCountImplicit(ImplicitConnection, CountTests):
    pass


#########################
# ONE-OFF / OTHER TESTS #
#########################

class TestMultipleDatabases(ExampleDBTests):

    def test_create_and_connect_to_two_separately(self):
        conn1 = db.drivers.sqlite3x.connect(":memory:")
        conn2 = db.drivers.sqlite3x.connect(":memory:")

        db.drivers.register(lambda *a, **k: conn1, "manual1")
        db.drivers.register(lambda *a, **k: conn2, "manual2")

        db1 = db.get("manual1")
        db2 = db.get("manual2")

        db1.do(CREATE_FOO_SQL)
        db2.do(CREATE_FOO_SQL)

        db1.do("INSERT INTO foo (value) VALUES (1)")
        db1.do("INSERT INTO foo (value) VALUES (2)")
        db1.do("INSERT INTO foo (value) VALUES (3)")

        db2.do("INSERT INTO foo (value) VALUES (4)")
        db2.do("INSERT INTO foo (value) VALUES (5)")
        db2.do("INSERT INTO foo (value) VALUES (6)")

        assert db1.item("SELECT SUM(value) AS n FROM foo").n == 6
        assert db2.item("SELECT SUM(value) AS n FROM foo").n == 15
