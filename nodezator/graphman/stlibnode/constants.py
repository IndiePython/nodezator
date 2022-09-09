### standard library imports

from collections.abc import (
    Callable,
    Iterable,
)

from types import ModuleType

from itertools import takewhile

from functools import reduce

from inspect import signature, getsource

from contextlib import redirect_stdout

from io import StringIO

## modules from where to retrieve callables to turn
## into nodes
import ast, functools, importlib, itertools, json, pprint


STLIB_IDS_TO_MODULE = {
    "accumulate": itertools,
    "chain": itertools,
    "chain.from_iterable": itertools,
    "combinations": itertools,
    "combinations_with_replacement": itertools,
    "compress": itertools,
    "count": itertools,
    "cycle": itertools,
    "dropwhile": itertools,
    "dumps": json,
    "filterfalse": itertools,
    "groupby": itertools,
    "import_module": importlib,
    "islice": itertools,
    "literal_eval(node_or_string)": ast,
    "literal_eval(node_or_text_string)": ast,
    "loads": json,
    "partial": functools,
    "pprint": pprint,
    "pformat": pprint,
    "product": itertools,
    "permutations": itertools,
    "reduce(function, iterable)": functools,
    "reduce(function, iterable, initializer)": functools,
    "repeat(obj)": itertools,
    "repeat(obj, times)": itertools,
    "starmap": itertools,
    "takewhile": itertools,
    "tee": itertools,
    "zip_longest": itertools,
}


## small utility


def get_callable_from_module(stlib_id, module_obj):

    ### get attributes from where to retrieve
    ### callable

    attr_names = "".join(
        takewhile(
            lambda c: c != "(",
            stlib_id,
        )
    ).split(".")

    ### retrieve callable using getattr
    ### in as much levels as needed
    return reduce(getattr, attr_names, module_obj)


STLIB_IDS_TO_CALLABLES_MAP = {
    stlib_id: get_callable_from_module(stlib_id, module_obj)
    for stlib_id, module_obj in STLIB_IDS_TO_MODULE.items()
}


def _accumulate(
    iterable: Iterable,
    func: Callable = None,
    *,
    initial: int = None,
) -> "iterator":
    pass


def _chain(*iterables: Iterable) -> "iterator":
    pass


def _dumps(
    obj,
    *,
    skipkeys: bool = False,
    ensure_ascii: bool = True,
    check_circular: bool = True,
    allow_nan: bool = True,
    cls: type = None,
    indent: "python_literal" = None,
    separators: {"widget_name": "literal_entry", "type": tuple} = None,
    default: Callable = None,
    sort_keys: bool = False,
    **kw,
) -> [{"name": "string", "type": str}]:
    pass


def _get_iterable_return_iterator(iterable: Iterable) -> ("iterator"):
    pass


def _combinations_with_and_without_replacement(
    iterable: Iterable, r: int = 2
) -> ("iterator"):
    pass


def _compress(data: Iterable, selectors: Iterable) -> ("iterator"):
    pass


def _count(start: (int, float) = 0, step: (int, float) = 1) -> ("iterator"):
    pass


def _dropwhile_and_takewhile(predicate: Callable, iterable: Iterable) -> ("iterator"):
    pass


def _filterfalse(function: Callable, iterable: Iterable) -> ("iterator"):
    pass


def _groupby(iterable: Iterable, key: Callable = None) -> ("iterator"):
    pass


def _import_module(
    name: str = "", package: str = ""
) -> [{"name": "module_obj", "type": ModuleType}]:
    pass


def _islice(
    iterable: Iterable,
    start: "natural_number_or_none" = None,
    stop: "natural_number_or_none" = None,
    step: "positive_integer_or_none" = None,
) -> "iterator":
    pass


def _literal_eval1(
    node_or_string: "python_literal_string" = "''",
) -> [{"name": "python_obj"}]:
    pass


def _literal_eval2(
    node_or_text_string: ("python_literal_text_string") = "''",
) -> [{"name": "python_obj"}]:
    pass


def _loads(
    s: "text_string" = "",
    *,
    cls: type = None,
    object_hook: Callable = None,
    parse_float: Callable = None,
    parse_int: Callable = None,
    parse_constant: Callable = None,
    object_pairs_hook: Callable = None,
    **kw,
) -> [{"name": "obj"}]:
    pass


def _partial(
    func: Callable, *args, **keywords
) -> [{"name": "partial_obj", "type": Callable}]:
    pass


def _pprint(
    object,
    stream=None,
    indent: "natural_number" = 1,
    width: "positive_integer" = 80,
    depth: "positive_integer_or_none" = None,
    *,
    compact: bool = False,
):
    pass


def _pformat(
    object,
    indent: "natural_number" = 1,
    width: "positive_integer" = 80,
    depth: "positive_integer_or_none" = None,
    *,
    compact: bool = False,
):
    pass


def _product(
    *iterables: Iterable,
    repeat: "natural_number" = 1,
) -> "iterator":
    pass


def _permutations(
    iterable: Iterable,
    r: "natural_number_or_none" = None,
) -> "iterator":
    pass


def _reduce1(function: Callable, iterable: Iterable):
    pass


def _reduce2(
    function: Callable,
    iterable: Iterable,
    initializer,
):
    pass


def _repeat1(obj) -> "iterator":
    pass


def _repeat2(
    obj,
    times: "positive_integer" = 1,
) -> "iterator":
    pass


def _starmap(
    function: Callable,
    iterable: Iterable,
) -> "iterator":
    pass


def _tee(
    iterable: Iterable,
    n: "natural_number" = 2,
) -> [{"name": "tuple_of_iterators", "type": tuple}]:
    pass


def _zip_longest(
    *iterables: Iterable,
    fillvalue=None,
) -> "iterator":
    pass


STLIB_IDS_TO_SIGNATURE_CALLABLES_MAP = {
    "accumulate": _accumulate,
    "chain": _chain,
    "chain.from_iterable": (_get_iterable_return_iterator),
    "combinations": (_combinations_with_and_without_replacement),
    "combinations_with_replacement": (_combinations_with_and_without_replacement),
    "compress": _compress,
    "count": _count,
    "cycle": _get_iterable_return_iterator,
    "dropwhile": _dropwhile_and_takewhile,
    "dumps": _dumps,
    "filterfalse": _filterfalse,
    "groupby": _groupby,
    "import_module": _import_module,
    "islice": _islice,
    "literal_eval(node_or_string)": (_literal_eval1),
    "literal_eval(node_or_text_string)": (_literal_eval2),
    "loads": _loads,
    "partial": _partial,
    "pprint": _pprint,
    "pformat": _pformat,
    "product": _product,
    "permutations": _permutations,
    "reduce(function, iterable)": _reduce1,
    "reduce(function, iterable, initializer)": (_reduce2),
    "repeat(obj)": _repeat1,
    "repeat(obj, times)": _repeat2,
    "starmap": _starmap,
    "takewhile": _dropwhile_and_takewhile,
    "tee": _tee,
    "zip_longest": _zip_longest,
}

STLIB_IDS_TO_SIGNATURES_MAP = {
    "accumulate": signature(_accumulate),
    "chain": signature(_chain),
    "chain.from_iterable": (signature(_get_iterable_return_iterator)),
    "combinations": signature(_combinations_with_and_without_replacement),
    "combinations_with_replacement": (
        signature(_combinations_with_and_without_replacement)
    ),
    "compress": signature(_compress),
    "count": signature(_count),
    "cycle": signature(_get_iterable_return_iterator),
    "dropwhile": signature(_dropwhile_and_takewhile),
    "dumps": signature(_dumps),
    "filterfalse": signature(_filterfalse),
    "groupby": signature(_groupby),
    "import_module": signature(_import_module),
    "islice": signature(_islice),
    "literal_eval(node_or_string)": (signature(_literal_eval1)),
    "literal_eval(node_or_text_string)": (signature(_literal_eval2)),
    "loads": signature(_loads),
    "partial": signature(_partial),
    "pprint": signature(_pprint),
    "pformat": signature(_pformat),
    "product": signature(_product),
    "permutations": signature(_permutations),
    "reduce(function, iterable)": signature(_reduce1),
    "reduce(function, iterable, initializer)": (signature(_reduce2)),
    "repeat(obj)": signature(_repeat1),
    "repeat(obj, times)": signature(_repeat2),
    "starmap": signature(_starmap),
    "takewhile": signature(_dropwhile_and_takewhile),
    "tee": signature(_tee),
    "zip_longest": signature(_zip_longest),
}

STLIB_IDS_TO_SIGNATURES_MAP = {
    stlib_id: signature(callable_obj)
    for stlib_id, callable_obj in STLIB_IDS_TO_SIGNATURE_CALLABLES_MAP.items()
}

STLIB_IDS_TO_STLIB_IMPORT_TEXTS = {
    "accumulate": "from itertools import accumulate",
    "chain": "from itertools import chain",
    "chain.from_iterable": "from itertools import chain",
    "combinations": ("from itertools import combinations"),
    "combinations_with_replacement": (
        "from itertools import combinations_with_replacement"
    ),
    "compress": "from itertools import compress",
    "count": "from itertools import count",
    "cycle": "from itertools import cycle",
    "dropwhile": "from itertools import dropwhile",
    "dumps": "from json import dumps",
    "filterfalse": "from itertools import filterfalse",
    "groupby": "from itertools import groupby",
    "import_module": "from importlib import import_module",
    "islice": "from itertools import islice",
    "literal_eval(node_or_string)": "from ast import literal_eval",
    "literal_eval(node_or_text_string)": "from ast import literal_eval",
    "loads": "from json import loads",
    "partial": "from functools import partial",
    "pprint": "from pprint import pprint",
    "pformat": "from pprint import pformat",
    "product": "from itertools import product",
    "permutations": "from itertools import permutations",
    "reduce(function, iterable)": ("from functools import reduce"),
    "reduce(function, iterable, initializer)": ("from functools import reduce"),
    "repeat(obj)": "from itertools import repeat",
    "repeat(obj, times)": "from itertools import repeat",
    "starmap": "from itertools import starmap",
    "takewhile": "from itertools import takewhile",
    "tee": "from itertools import tee",
    "zip_longest": "from itertools import zip_longest",
}

###

string_stream = StringIO()


def get_help_text(callable_obj):
    content_length = len(string_stream.getvalue())

    with redirect_stdout(string_stream):
        help(callable_obj)

    return string_stream.getvalue()[content_length:].strip()


STLIB_IDS_TO_SOURCE_VIEW_TEXT = {
    stlib_id: f'''
### signature used:

{getsource(STLIB_IDS_TO_SIGNATURE_CALLABLES_MAP[stlib_id])}

### help text:

"""
{get_help_text(STLIB_IDS_TO_CALLABLES_MAP[stlib_id])}
"""
'''.strip()
    for stlib_id in STLIB_IDS_TO_MODULE.keys()
}

string_stream.close()
