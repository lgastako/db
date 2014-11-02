db
==

A more programmer friendly interface to databases inspired by Kenneth Reitz's
"requests" library.

I've got a long way to go but I'm using this code in a number of projects
already so I figured I'd put it out there.  Also please note that this is not,
and never will be, an attempt at an ORM (although it may be reasonable to write
one on top of it).


Introduction
------------

The fundamental abstraction provided by the db library is the database handle.
Each database handle represents a lazily instantiated thread-local connection
to the database.  This means that if you never invoke any of the query methods
(item, items, etc) then no connection will ever be created.

You might acquire a handle like this (or any number of other ways which will be
covered below):

    products_db = db.get("products")

From any handle you can obtain a new handle to the same database but with it's
own new dedicated connection via cloning:

    products_db_c2 = products_db.clone()

A handle provides various methods for executing queries and handling various
common cases (counts, expecting exactly 1 row, want the first row back, etc).

For example, a simple query might look like:

    products = products_db.items("SELECT * FROM products")

In addition a handle provides a context manager for managing the lifecycle of
transactions:

    with products_db.tx() as tx:
        best_product = tx.item("SELECT * FROM products ORDER BY total_sales LIMIT 1")
        tx.do("UPDATE products SET price = price + 0.01 WHERE product_id = %X",
              best_product.product_id)

The object returned ("tx") within the with block is database handle scoped to
the transaction.

The db library provides a standard URL-based interface to specifying database
connection parameters as well as mechanisms that automatically handle best
practices (e.g. specifying your primary database connection string in the
environment variable DATABASE_URL, connection pools, etc).


Basic Usage
-----------

TODO: This part of the documentation needs to be updated with regards to
.from_environ() vs from_envvar() etc.

Normally you would set the DATABASE_URL in your environment before running your
program, but for the sake of making this README a valid self-contained
executable doctest:

    >>> import os
    >>> os.environ["DATABASE_URL"] = "sqlite3://doctest.sqlite"

Once your DATABASE_URL is set up, just import the db library and the
appropriate driver(s) and then use the from_environ() helper to create a
default database from that URL:

    >>> import db
    >>> import db_sqlite3
    >>> db.from_environ()                               # doctest: +ELLIPSIS
    <db_sqlite3.Sqlite3Driver object at 0x...>

You can pass the name of a different environment variable to from_environ if
you want to read from a different variable:

    # db.from_environ("PRODUCTION_DATABASE_URL")

You may also specify an name for the database using the db_name keyword
argument to from_environ.  This is useful when you need to access multiple
databases from a single project:

    # db.from_environ(db_name="integration_db")

Or of course combine the two:

    # db.from_environ("PRODUCTION_DATABASE_URL", db_name="prod_db")

If you prefer to get your database URLs from someplace other than the command
line then you can use .from_url() instead of .from_environ():

    # db.from_url("sqlite3:/:memory:", db_name="temp_db")

Now that you have a default database configured, you can use db.item() to
execute a query that you expect to return exactly 1 row (e.g. a SELECT
statement or a stored procedure that you expect to return a single row):

    >>> row = db.item("SELECT * FROM examples WHERE id = 10")

And you can access the fields by name:

    >>> row.example_id
    10
    >>> row.example_name
    u'This is example ID 10'

What a minute, what happened to our fundamental unit of abstraction, the
database handle?  Here we are just calling a method directly on the db module,
aren't we?

Well, yes, the db module acts as a proxy to the default thread-local database
handle for the default database, so in the most common case, you can just use
the db module itself anywhere you need a database handle, like we are in these
examples.

Note that the use of db.do and db.item without an explicit transaction block
will create a new transaction for each statement.

If a call to .item() returns more or less than 1 row then you will receive an
UnexpectedCardinality exception:

    >>> db.item("SELECT * FROM examples")
    UnexpectedCardinality("blah blah")


Bind Parameters
---------------

db uses the execute_f method from the dbapiext module of Martin Blais' antiorm
project to handle parameter binding, so you get all the benefits discussed in
his presentation here:

    http://furius.ca/antiorm/doc/talks/dbapiext/dbapiext-pres.pdf

The short story is that you use %X (or %(name)X for named parameters) to
auto-escape values.

You can use the db.transmogrify function to get a compiled query without
executing it.


Transactions
------------

To explicitly control transactions, use a with block with the transaction
context manager:

    >>> with db.tx() as tx:
    ...     row = tx.item("SELECT * FROM examples")
    ...     tx.do("INSERT INTO examples (name) VALUES ('foo')")
    ...
    >>> row.id
    >>> row.example_id
    10

In this case, a new transaction wraps the with block.  If the transaction
issues a ROLLBACK statement, the with block will return with no error, but
if the transaction aborts causing a rollback, then the with block will raise
the appropriate exception.

The use of the individual query methods (.do, .item and .items) without an
explicit transaction block results in a new transaction for each statement.


Multiple Databases
------------------

In the examples above we registered a single database driver and since then
every interaction we've had with the db module has used this default driver to
obtain a connection.

You can register multiple databases by providing a name for any non-default
databases:

    >>> db.from_url("postgresql://tweeter:pw140@localhost:5432/tweetsdb",
    ...             db_name="tweets")
    >>> db.from_url("postgresql://dsgnr:pretty@localhost:5432/tweetsdb",
    ...             db_name="images")

Then access them individually later:

    >>> tweets_db = db.get("tweets")
    >>> images_db = db.get("images")

And use all of the same functions on them:

    >>> row = tweetsdb.item("SELECT * FROM tweet_examples")
    >>> row.example_id
    11

    >>> with imagesdb.tx() as tx:
    ...     row = tx.item("SELECT * FROM image_examples")
    ...     tx.do("INSERT INTO image_examples (name) VALUES ('bar')")
    ...
    >>> row.example_id
    11

etc.

Drivers
-------

Drivers for the db module are very simple.  They are objects which provide:

    .PARAM_STYLE
        A string defining the paramstyle, e.g. "pyformat", "qmark", etc

    .URL_SCHEME
        A string containing the default scheme of URLs this driver is meant to
        handle (e.g. "postgresql" or "sqlite3" in "sqlite3://blah").

    .acquire()
        A method for acquiring a new connection to the underlying database.

    .release(conn)
        A method for releasing a connection to the underlying database.

    .ignore_exception(ex)
        A method for checking whether an exception from the underlying driver
        is safe to ignore.

    .cursor(conn)
        A method for obtaining a cursor from the given connection.

    .from_url(url)
        An alternate constructor to instantiate a driver from a URL.

The db.drivers.Driver class provides an base class to make it easier to
implement new drivers.  Most drivers will/should extend from this class.

The two methods that MUST be implemented to make a driver useful are the
from_url() class method and the acquire() method.

Driver provides a default implementation of release() which does
nothing.  If your driver needs to free resources when a connection is no longer
in use (for example if it is a Pool driver that needs to return the connection
to the pool) then you must also override this method.

Driver provides a default implementation of ignore(ex) which always returns
False.  If there are any exceptions that are safe to ignore in your driver then
you must override this method.

Driver provides a default implementation of cursor() which delegates driver-specific
cursor setup to the method 'setup_cursor(cursor)' which has a no-op default
implementation.

The Driver class provides default implementations of cursor(), ... FINISH ME.


Pools
-----

TODO: Actually, this isn't quite implemented yet.  Coming soon.  But I expect
      it to end up something like this:

Connection pools are simply implemented as new drivers, e.g.
    "antipool+postgresql://user:pass@host/db?min_conn=10&max_conn=50"




Exceptions:
-----------

Currently there are four custom exceptions that the db module might raise,
all of which are a subclass of db.DBError (which currently is never raised
directly):

    NoDefaultDatabase
        Raised when an attempt to access the default database is made before a
        driver is registered for the default database.

    NoSuchDatabase
        Raised when an attempt to access a named database is made but no driver
        has been registered for that name.

    UnexpectedCardinality
        Raised when .one() or .tuple() is called and the query returns more or
        less than 1 result.  Taking suggestions for a better name before 1.0
        release sets it in stone :)

    NoDriverForURL
        Raised when there is no driver registered to handle the scheme of a
        database URL.

