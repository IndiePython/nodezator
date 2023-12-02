"""Facility for keyword variable parameter testing."""

def var_key_test(**kwargs) -> dict:
    """Return dict from keyword arguments received."""
    return kwargs

### callable used must always be aliased as 'main'
main_callable = var_key_test
