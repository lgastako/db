try:
    from Dee import Relation
    DEE = True
except ImportError:
    DEE = False


if DEE:
    import db

    from test_db import ExampleDBTests

    class TestRelations(ExampleDBTests):

        def test_basic(self):
            rel = db.relation("SELECT * FROM foo")

            assert len(rel) == 1
            tup = rel.toTuple()

            assert tup.foo_id == 1
            assert tup.value == 'foo'

        def test_shorthand(self):
            rel = db.relation("foo")

            assert len(rel) == 1
            tup = rel.toTuple()

            assert tup.foo_id == 1
            assert tup.value == 'foo'

        def test_basic_multiple(self):
            self.insert_another()

            rel = db.relation("SELECT * FROM foo")

            assert len(rel) == 2
            tups = rel.toTupleList()
            tups.sort(key=lambda t: t.foo_id)

            tup = tups[0]
            assert tup.foo_id == 1
            assert tup.value == 'foo'

            tup = tups[1]
            assert tup.foo_id == 2
            assert tup.value == 'bar'

    class TestTuples(ExampleDBTests):

        def test_basic_select(self):
            row = db.tuple("SELECT * FROM foo")

            assert row.foo_id == 1
            assert row.value == 'foo'

    class TestRelCount(ExampleDBTests):

        def test_basic_count(self):
            rel = db.rel_count("foo")
            assert rel.heading() == frozenset(["foo_count"])
            tup = rel.toTuple()
            assert tup.foo_count == 1

        def test_basic_name_overriding(self):
            rel = db.rel_count("foo", count_name="blah")
            assert rel.heading() == frozenset(["blah"])
            tup = rel.toTuple()
            assert tup.blah == 1

        def test_basic_count_multiple(self):
            self.insert_another()
            rel = db.rel_count("foo")
            assert rel.heading() == frozenset(["foo_count"])
            tup = rel.toTuple()
            assert tup.foo_count == 2

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

            rel = db.rel_count("foo, bar WHERE foo.value = bar.value")
            assert rel.heading() == frozenset(["foo_bar_count"])
            tup = rel.toTuple()
            assert tup.foo_bar_count == 2
