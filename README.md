db
==

A more programmer friendly interface to databases inspired by Kenneth Reitz's
"requests" library.  

I've got a long way to go but I'm using this code in a number of projects
already so I figured I'd put it out there.  Also please note that this is
not, and never will be, an attempt at an ORM.


Basic Usage
-----------

    import db

    db.do("DELETE FROM products")
    db.do("INSERT INTO products (name, price) VALUES ('iPod', 69.99)")
    print db.item("SELECT COUNT(*) FROM products").count
    # 1
    products = db.items("SELECT * FROM products")
    print len(products)
    # 1
    product = products[0]
    print product.name
    # "iPod"


Due to the use of db.do/item/items, each SQL statement in the above example
was executed in a separate transaction.


Basic Transactions 
------------------

    import db

    with db.tx() as cx:
        # transaction is opened here, and commited at the end of the with
        # block automatically.  If a rollback is issued, it will return
        # with no error, but if the transaction aborts and is rolled back
        # then the with block will raise the appropriate exception.
        cx.execute("SELECT val1 FROM foo")
        row = cx.fetchone()
        val1 = row[0]
        cx.execute("INSERT INTO bar (val) VALUES (%X)", val1);


So far we've been getting our database connections automatically.  What's
happening behind the scenes is that the do, item(s), etc functions that
exist right on the db module all operate on the default database.


Multiple Databases
------------------

You can get a specific database by name:

    foo_db = db.get("foo_db")

And use all of the same functions on it:

    foo.db.items("SELECT COUNT(*) AS n FROM foos").n

etc.


"Drivers"
---------

Drivers for the DB module are very simple.  They consist of a function,
which, when called with no arguments, returns a new connection ready for use,
and when called with a previously-returned connection as an argument, does
whatever is necessary to dispose of the connection -- returning it to a
connection pool perhaps, etc.

The driver is responsible for making sure that the underlying
connection/cursors are NamedTupleCursors (e.g by setting the appropriate
flag on the connection object or returning a wrapped connection that
sets the appropriate flag on .cursor calls, etc).


TODO
----

- Nested transactions
- Documentation
- Website
