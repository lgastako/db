import db


class TestSqlite3x:

    def test_paramstyle_set_properly(self):
        d = db.drivers.sqlite3x.register(":memory:")
        d.do("CREATE TABLE foo (bar)")
        sql = "SELECT COUNT(*) AS n FROM foo WHERE bar = %X"
        assert d.item(sql, "baz").n == 0
