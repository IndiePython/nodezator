"""Utilities for handling strings."""

### standard-library imports

from ast import literal_eval
from json import loads as load_json_string
from collections import OrderedDict
from itertools import count


### local import
from .exceptionutils import bool_func_from_raiser


### validation command map

VALIDATION_COMMAND_MAP = OrderedDict()

## populate with boolean function which always
## evaluates to True
VALIDATION_COMMAND_MAP[None] = lambda value: True

## populate with boolean functions from str builtin

VALIDATION_COMMAND_MAP.update(
    (word, getattr(str, word)) for word in sorted(dir(str)) if word.startswith("is")
)


## populate with custom boolean funcs

VALIDATION_COMMAND_MAP["json"] = bool_func_from_raiser(load_json_string)
# TODO log change: key name from 'pyl' to 'literal_eval'
VALIDATION_COMMAND_MAP["literal_eval"] = bool_func_from_raiser(literal_eval)


### functions


def check_contains_non_whitespace(string):
    """If non-white space chars == 0, raise ValueError.

    Used to indicate a string must have at least 1 character
    which is not white space.

    Adheres to the "expected exceptions" protocol by
    referencing expected errors in the 'expected_exceptions'
    attribute of the function.

    Parameters
    ==========
    string (string)
        string to be checked.

    """
    ### XXX
    ### There's still other unicode characters which could
    ### be considered whitespace, that is, characters which
    ### don't have a visual representation. Think of how to
    ### consider them as well

    ### if string doesn't have at least one character which
    ### is not white space, raise ValueError with custom
    ### message
    if not string.strip():

        raise ValueError(
            "string must have at least one character which is"
            " not considered white space"
        )


check_contains_non_whitespace.expected_exceptions = ValueError
