from functools import partial

import sqlite3

import pytest

import db


#########################
# BASE TEST DEFINITIONS #
#########################


class ExampleDBTests(object):

    def setup_method(self, method):
        db.drivers.clear()
        self.conn = sqlite3.connect(":memory:")
        db.drivers.register(lambda *a, **k: self.conn)
        cursor = next(db.drivers.sqlite3.yield_cursor(self.conn))
        cursor.execute("""CREATE TABLE foo (
                            foo_id INTEGER PRIMARY KEY,
                            value TEXT
                          )""")
        cursor.execute("INSERT INTO foo VALUES (1, 'foo')")
        self.conn.commit()
        self.cursor = self.conn.cursor()

    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)

    def commit(self, *args, **kwargs):
        self.conn.commit(*args, **kwargs)
        self.cursor = self.conn.cursor()

    def insert_another(self):
        self.cursor.execute("INSERT INTO foo (foo_id, value) VALUES (2, 'bar')")


class DoTests(ExampleDBTests):

    def test_insert(self):
        self.execute("DELETE FROM foo")
        self.commit()

        self.do("INSERT INTO foo (foo_id, value) VALUES (1, 'baz')")

        self.cursor.execute("SELECT * FROM foo")
        rows = self.cursor.fetchall()
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
        self.commit()

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
        self.commit()
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
