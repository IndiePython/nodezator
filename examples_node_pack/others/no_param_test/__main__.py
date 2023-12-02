"""Facility for testing function with no parameters."""

from math import pi

def no_params():
    """Return pi."""
    return pi

### callable used must always be aliased as 'main'
main_callable = no_params
