db
==

A more programmer friendly interface to databases inspired by Kenneth Reitz's
"requests" library.  

I've got a long way to go but I'm using this code in a number of projects
already so I figured I'd put it out there.  Also please note that this is
not, and never will be, an attempt at an ORM.


Basic Usage
-----------


    >>> import db
    >>> db.drivers.psycopg2x.register("dbname=example user=exuser password=pw")
    <db.Database object at 0x102591e90>
    >>> row = db.item("SELECT * FROM examples")
    >>> row.example_id
    10
    >>> row.example_name
    u'This is example ID 10'


Note that the use of db.do and db.item without an explicit transaction
block will create a new transaction for each statement.  


Basic Transactions 
------------------

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


Multiple Databases
------------------

In the example at the top we registered a single database driver and since
then every interaction we've had with the db module has used this default
driver to obtain a connection.

You can register multiple databases by providing a name for any non-default
databases:

    >>> tweetsdb = db.drivers.psycopg2x.register("dbname=tweets user=tweeter password=pw140", "tweetsdb")
    >>> imagesdb = db.drivers.psycopg2x.register("dbname=images user=dsgnr password=pretty", "imagesdb")

You can get a specific database by name later:

    >>> tweetsdb = db.get("tweetsdb")
    >>> imagesdb = db.get("imagesdb")

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


NEW! Experimental support for Dee.
----------------------------------

items -> relation
item -> tuple


TODO
----

- Nested transactions
- Documentation
- Website
