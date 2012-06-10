db
==

A more programmer friendly interface to databases inspired by Kenneth Reitz's
"requests" library.


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
exist right on the db module all operate on the default connection.  The
default connection is the first connection registered with the connection
manaager.  The connection manager, connection pool boop de boop.

