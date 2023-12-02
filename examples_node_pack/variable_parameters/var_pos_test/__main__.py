"""Facility for positional variable parameter testing."""

def var_pos_test(*args) -> tuple:
    """Return tuple from positional arguments received."""
    return args

### callable used must always be aliased as 'main'
main_callable = var_pos_test
