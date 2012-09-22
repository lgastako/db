BEGIN;

DROP SCHEMA IF EXISTS psycopg2x_tests CASCADE;
SET search_path = 'public';

DROP TYPE IF EXISTS exrow CASCADE;
CREATE TYPE exrow AS (
    foo INTEGER,
    bar INTEGER
);

DROP FUNCTION IF EXISTS example_double(INTEGER);

CREATE OR REPLACE FUNCTION example_double(xyzzy IN INTEGER)
    RETURNS
        INTEGER
AS $$
    BEGIN
        RETURN 2 * xyzzy;
    END;
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION dup(INTEGER)
    RETURNS TABLE(f1 INTEGER, f2 TEXT)
AS $$
    SELECT $1, CAST($1 AS text) || ' is text'
$$ LANGUAGE SQL;

CREATE SCHEMA psycopg2x_tests;
SET search_path = 'psycopg2x_tests';

CREATE OR REPLACE FUNCTION example_rand(in_n IN INTEGER)
    RETURNS
        INTEGER
AS $$
    BEGIN
        RETURN 4;  -- chosen by fair die roll
                   -- guaranteed to be random
    END;
$$ LANGUAGE 'plpgsql';

SET search_path = 'public';

COMMIT;
