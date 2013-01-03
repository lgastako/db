try:
    from Dee import Relation
    from Dee import Tuple

    def row_to_tuple(row):
        kwargs = {}
        for field in row._fields:
            kwargs[field] = getattr(row, field)
        return Tuple(**kwargs)

except ImportError:

    def row_to_tuple(row):
        raise NotImplementedError


def rows_to_relation(rows):
    if len(rows) < 1:
        return None
    remaining_rows = iter(rows)
    first_row = next(remaining_rows)
    heading = list(first_row._fields)
    tuples = [row_to_tuple(first_row)]
    for row in remaining_rows:
        tuples.append(row_to_tuple(row))
    return Relation(heading, tuples)
