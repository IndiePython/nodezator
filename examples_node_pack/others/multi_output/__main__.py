"""Facility for multi output testing building."""

from collections.abc import Callable, Iterable, Iterator

def multi_output() -> [
    
      {"name": "str",           "type": str},
      {"name": "tuple",         "type": tuple},
      {"name": "list",          "type": list},
      {"name": "dict",          "type": dict},
      {"name": "bool",          "type": bool},
      {"name": "number",        "type": int},
      {"name": "also_a_number", "type": float},
      {"name": "iterable",      "type": Iterable},
      {"name": "iterator",      "type": Iterator},
      {"name": "other",         "type": range},

      # specifying type is optional, though; this output
      # has no type specified
      {"name": "type_not_specified"},

      # and this is yet another possible annotation
      {"name": "callable_obj", "type": Callable},
      
    ]:
    """Gather arguments on dict and return."""
    d = {
      "str": "",
      "tuple": (),
      "list": [],
      "dict": {},
      "bool": False,
      "number": 0,
      "iterable" : set(),
      "iterator" : [1, 2, 3].__iter__(),
      "other": range(2),
      "type_not_specified": None,
      "callable_obj": lambda: None,
    }
    return d

### the callable used must always be aliased as
### 'main'
main_callable = multi_output
