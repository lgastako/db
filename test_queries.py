from functools import partial

import sqlite3

import queries as db
from queries import sqlite3 as qsqlite3


###########################
# ACTUAL TEST DEFINITIONS #
###########################


class ExampleDBTests(object):

    def setup_method(self, method):
        db.clear_drivers()
        self.conn = sqlite3.connect(":memory:")
        db.register_driver(lambda *a, **k: self.conn)
        cursor = next(qsqlite3.yield_cursor(self.conn))
        cursor.execute("""CREATE TABLE foo (
                            foo_id INTEGER PRIMARY KEY,
                            bar TEXT
                          )""")
        cursor.execute("INSERT INTO foo VALUES (1, 'bar')")
        self.conn.commit()
        self.cursor = self.conn.cursor()

    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)

    def commit(self, *args, **kwargs):
        self.conn.commit(*args, **kwargs)
        self.cursor = self.conn.cursor()

    def insert_another(self):
        self.cursor.execute("INSERT INTO foo (foo_id, bar) VALUES (2, 'bam')")


class DoTests(ExampleDBTests):

    def test_insert(self):
        self.execute("DELETE FROM foo")
        self.commit()

        self.do("INSERT INTO foo (foo_id, bar) VALUES (1, 'baz')")

        self.cursor.execute("SELECT * FROM foo")
        rows = self.cursor.fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row.foo_id == 1
        assert row.bar == 'baz'


class ItemTests(ExampleDBTests):

    def test_basic_select(self):
        row = self.item("SELECT * FROM foo")

        assert row.foo_id == 1
        assert row.bar == 'bar'


class ItemsTests(ExampleDBTests):

    def test_basic_select(self):
        rows = self.items("SELECT * FROM foo")

        assert len(rows) == 1
        row = rows[0]
        assert row.foo_id == 1
        assert row.bar == 'bar'

    def test_basic_select_multiple(self):
        self.insert_another()
        self.commit()

        rows = self.items("SELECT * FROM foo")

        assert len(rows) == 2
        row = rows[0]
        assert row.foo_id == 1
        assert row.bar == 'bar'
        row = rows[1]
        assert row.foo_id == 2
        assert row.bar == 'bam'


class CountTests(ExampleDBTests):

    def test_basic_count(self):
        assert self.count("foo") == 1

    def test_basic_count_multiple(self):
        self.insert_another()
        self.commit()
        assert self.count("foo") == 2


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
