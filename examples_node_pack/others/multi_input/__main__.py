"""Facility for simple node test."""

from collections.abc import Callable, Iterable, Iterator

def multi_input(
    a_list               : list,
    a_tuple              : tuple,
    a_dict               : dict,
    a_boolean            : bool,
    a_string             : str,
    number               : int,
    also_a_number        : float,
    iterable             : Iterable,
    iterator             : Iterator,
    other_type           : range,
    type_not_specified,
    callable_obj         : Callable
    ):
    """Print obj, then return it."""
    pass

### the callable used must always be aliased as
### 'main'
main_callable = multi_input
