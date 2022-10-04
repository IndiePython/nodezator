### standard library imports

from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Sequence,
)

from inspect import signature, getsource

from contextlib import redirect_stdout

from io import StringIO


BUILTIN_IDS_TO_CALLABLES_MAP = {
    "abs": abs,
    "all": all,
    "any": any,
    "ascii": ascii,
    "bin": bin,
    "bool": bool,
    "bytearray(source)": bytearray,
    "bytearray(source, encoding)": bytearray,
    "bytearray(source, encoding, errors)": bytearray,
    "bytes(source)": bytes,
    "bytes(source, encoding)": bytes,
    "bytes(source, encoding, errors)": bytes,
    "callable": callable,
    "chr": chr,
    "compile": compile,
    "complex(number_or_string)": complex,
    "complex(real, imag)": complex,
    "dict(**kwargs)": dict,
    "dict(mapping_or_iterable, **kwargs)": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "eval(string_source, ...)": eval,
    "eval(text_string_source, ...)": eval,
    "exec(string_source, ...)": exec,
    "exec(text_string_source, ...)": exec,
    "filter": filter,
    "format": format,
    "frozenset": frozenset,
    "float": float,
    "getattr(obj, name)": getattr,
    "getattr(obj, name, default)": getattr,
    "hasattr": hasattr,
    "hash": hash,
    "hex": hex,
    "id": id,
    "int(x)": int,
    "int(x, base)": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "iter(obj)": iter,
    "iter(callable_obj, sentinel)": iter,
    "len": len,
    "list": list,
    "map": map,
    "max(iterable, **kwargs)": max,
    "max(*args, **kwargs)": max,
    "memoryview": memoryview,
    "min(iterable, **kwargs)": min,
    "min(*args, **kwargs)": min,
    "next(iterator)": next,
    "next(iterator, default)": next,
    "oct": oct,
    "open": open,
    "ord": ord,
    "pow": pow,
    "print": print,
    "range(*args)": range,
    "range(stop)": range,
    "range(start, stop)": range,
    "range(start, stop, step)": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str(obj)": str,
    "str(obj, encoding, errors)": str,
    "sum": sum,
    "tuple": tuple,
    "type(obj)": type,
    "type(name, bases, a_dict)": type,
    "vars(obj)": vars,
    "zip": zip,
}


def _abs(x):
    pass


def _all(iterable: Iterable) -> [{"name": "boolean", "type": bool}]:
    pass


def _any(iterable: Iterable) -> [{"name": "boolean", "type": bool}]:
    pass


def _ascii(obj) -> [{"name": "string", "type": str}]:
    pass


def _bin(x) -> [{"name": "string", "type": str}]:
    pass


def _bool(obj=False) -> [{"name": "boolean", "type": bool}]:
    pass


def _bytearray1(source: int = 0) -> [{"name": "bytearray_obj", "type": bytearray}]:
    pass


def _bytearray2(
    source: str = "", encoding: str = "utf-8"
) -> [{"name": "bytearray_obj", "type": bytearray}]:
    pass


def _bytearray3(
    source: str = "", encoding: str = "utf-8", errors: str = "strict"
) -> [{"name": "bytearray_obj", "type": bytearray}]:
    pass


def _bytes1(source: int = 0) -> [{"name": "bytes_obj", "type": bytes}]:
    pass


def _bytes2(
    source: str = "", encoding: str = "utf-8"
) -> [{"name": "bytes_obj", "type": bytes}]:
    pass


def _bytes3(
    source: str = "", encoding: str = "utf-8", errors: str = "strict"
) -> [{"name": "bytes_obj", "type": bytes}]:
    pass


def _callable(obj) -> [{"name": "boolean", "type": bool}]:
    pass


def _chr(
    i: {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "min_value": 0,
            "max_value": 1_114_111,
        },
        "type": int,
    } = 97,
) -> [{"name": "char_string", "type": str}]:
    pass


def _compile(
    source,
    filename,
    mode: {
        "widget_name": "option_tray",
        "widget_kwargs": {
            "options": ["exec", "eval", "single"],
        },
        "type": str,
    } = "exec",
    flags=0,
    dont_inherit=False,
    optimize: {
        "widget_name": "option_tray",
        "widget_kwargs": {
            "options": [-1, 0, 1, 2],
        },
        "type": int,
    } = -1,
) -> [{"name": "code_or_ast_obj"}]:
    pass


def _complex1(
    number_or_string: str = "0j",
) -> [{"name": "complex_number", "type": complex}]:
    pass


def _complex2(
    real: (int, float) = 0,
    imag: (int, float) = 0,
) -> [{"name": "complex_number", "type": complex}]:
    pass


def _dict1(**kwargs) -> [{"name": "dict_obj", "type": dict}]:
    pass


def _dict2(mapping_or_iterable, **kwargs) -> [{"name": "dict_obj", "type": dict}]:
    pass


def _divmod(
    x: (int, float) = 0,
    y: (int, float) = 1,
) -> [{"name": "q_and_r_pair", "type": tuple}]:
    pass


def _enumerate(
    iterable: Iterable, start: int = 0
) -> [{"name": "enumerate_obj", "type": Iterator}]:
    pass


def _eval1(
    string_source: "python_literal_string" = "''",
    globals=None,
    locals=None,
) -> [{"name": "python_obj"}]:
    pass


def _eval2(
    text_string_source: ("python_literal_text_string") = "''",
    globals=None,
    locals=None,
) -> [{"name": "python_obj"}]:
    pass


def _exec1(
    string_source: str = "",
    globals=None,
    locals=None,
):
    pass


def _exec2(
    text_string_source: {
        "widget_name": "text_display",
        "widget_kwargs": {
            "syntax_highlighting": "python",
            "font_path": "mono_bold",
        },
        "type": str,
    } = "",
    globals=None,
    locals=None,
):
    pass


def _filter(
    function: Callable,
    iterable: Iterable,
) -> [{"name": "filter_obj", "type": Iterator}]:
    pass


def _float(number_or_string: str = "0.0") -> [{"name": "float_obj", "type": float}]:
    pass


def _format(value, format_spec: str = "") -> [{"name": "formatted_repr", "type": str}]:
    pass


def _frozenset(
    iterable: Iterable = (),
) -> [{"name": "frozentset_obj", "type": frozenset}]:
    pass


def _getattr1(obj, name: str = ""):
    pass


def _getattr2(
    obj,
    name: str = "",
    default: "python_literal" = None,
):
    pass


def _hasattr(obj, name: str = "") -> [{"name": "boolean", "type": bool}]:
    pass


def _hash(obj) -> [{"name": "hash_value", "type": int}]:
    pass


def _hex(x: int = 0) -> [{"name": "hex_string", "type": str}]:
    pass


def _id(obj) -> [{"name": "identity_int", "type": int}]:
    pass


def _int1(
    number_or_string: "python_literal" = "0",
) -> [{"name": "int_obj", "type": int}]:
    pass


def _int2(
    number_or_string: "python_literal" = "0",
    base: int = 10,
) -> [{"name": "int_obj", "type": int}]:
    pass


def _isinstance(obj, class_or_tuple) -> [{"name": "boolean", "type": bool}]:
    pass


def _issubclass(obj, class_or_tuple) -> [{"name": "boolean", "type": bool}]:
    pass


def _iter1(obj) -> [{"name": "iterator", "type": Iterator}]:
    pass


def _iter2(
    callable_obj: Callable, sentinel
) -> [{"name": "iterator", "type": Iterator}]:
    pass


def _len(obj) -> [{"name": "length_int", "type": int}]:
    pass


def _list(iterable: Iterable = ()) -> [{"name": "list_obj", "type": list}]:
    pass


def _map(
    function: Callable,
    *iterables: Iterable,
) -> [{"name": "map_obj", "type": Iterator}]:
    pass


def _max1(iterable: Iterable, **kwargs):
    pass


def _max2(*args, **kwargs):
    pass


def _min1(iterable: Iterable, **kwargs):
    pass


def _min2(*args, **kwargs):
    pass


def _memoryview(obj) -> [{"name": "memoryview_obj", "type": memoryview}]:
    pass


def _next1(iterator: Iterator):
    pass


def _next2(iterator: Iterator, default: "python_literal" = None):
    pass


def _oct(x: int = 0) -> [{"name": "oct_string", "type": str}]:
    pass


def _open(
    file,
    mode: str = "r",
    buffering: {
        "widget_name": "int_float_entry",
        "widget_kwargs": {
            "min_value": -1,
        },
        "type": int,
    } = -1,
    encoding: "python_literal" = None,
    errors: {
        "widget_name": "option_menu",
        "widget_kwargs": {
            "options": [
                None,
                "strict",
                "ignore",
                "replace",
                "surrogateescape",
                "xmlcharrefreplace",
                "backslashreplace",
                "namereplace",
            ],
        },
    } = None,
    newline: "python_literal" = None,
    closefd: bool = True,
    opener: Callable = None,
) -> [{"name": "file_obj"}]:
    pass


def _ord(char: str = "a") -> [{"name": "codepoint_int", "type": int}]:
    pass


def _pow(
    base: (int, float) = 0,
    exp: (int, float) = 0,
    mod: (int, float) = None,
) -> [{"name": "number", "type": (int, float)}]:
    pass


def _print(
    *objects,
    sep: "python_literal" = " ",
    end: "python_literal" = "\n",
    file=None,
    flush: bool = False,
):
    pass


def _range1(*args: int) -> [{"name": "range_obj", "type": Iterable}]:
    pass


def _range2(stop: int = 0) -> [{"name": "range_obj", "type": Iterable}]:
    pass


def _range3(
    start: int = 0,
    stop: int = 0,
) -> [{"name": "range_obj", "type": Iterable}]:
    pass


def _range4(
    start: int = 0,
    stop: int = 0,
    step: int = 1,
) -> [{"name": "range_obj", "type": Iterable}]:
    pass


def _repr(obj) -> [{"name": "string", "type": str}]:
    pass


def _reversed(sequence: Sequence) -> [{"name": "iterator", "type": Iterator}]:
    pass


def _round(
    number: float = 0.0,
    ndigits: int = None,
) -> [{"name": "number", "type": (int, float)}]:
    pass


def _sorted(
    iterable: Iterable,
    *,
    key: Callable = None,
    reverse: bool = False,
) -> [{"name": "sorted_list", "type": list}]:
    pass


def _set(iterable: Iterable = ()) -> [{"name": "set_obj", "type": set}]:
    pass


def _slice(
    start: int = None,
    stop: int = None,
    step: int = None,
) -> [{"name": "slice_obj", "type": slice}]:
    pass


def _str1(obj="") -> [{"name": "str_obj", "type": str}]:
    pass


def _str2(
    obj: "python_literal" = b"",
    encoding: str = "utf-8",
    errors: str = "strict",
) -> [{"name": "str_obj", "type": str}]:
    pass


def _sum(iterable: Iterable, start: int = 0):
    pass


def _tuple(iterable: Iterable = ()) -> [{"name": "tuple_obj", "type": tuple}]:
    pass


def _type1(obj) -> [{"name": "type_obj", "type": type}]:
    pass


def _type2(
    name: str = "",
    bases: tuple = (),
    a_dict: dict = {},
) -> [{"name": "type_obj", "type": type}]:
    pass


def _vars(obj) -> [{"name": "a_dict", "type": dict}]:
    pass


def _zip(*iterables: Iterable) -> [{"name": "zip_obj", "type": Iterator}]:
    pass


BUILTIN_IDS_TO_SIGNATURE_CALLABLES_MAP = {
    "abs": _abs,
    "all": _all,
    "any": _any,
    "ascii": _ascii,
    "bin": _bin,
    "bytearray(source)": _bytearray1,
    "bytearray(source, encoding)": (_bytearray2),
    "bytearray(source, encoding, errors)": (_bytearray3),
    "bytes(source)": _bytes1,
    "bytes(source, encoding)": _bytes2,
    "bytes(source, encoding, errors)": (_bytes3),
    "bool": _bool,
    "callable": _callable,
    "chr": _chr,
    "compile": _compile,
    "complex(number_or_string)": _complex1,
    "complex(real, imag)": _complex2,
    "dict(**kwargs)": _dict1,
    "dict(mapping_or_iterable, **kwargs)": (_dict2),
    "divmod": _divmod,
    "enumerate": _enumerate,
    "eval(string_source, ...)": _eval1,
    "eval(text_string_source, ...)": _eval2,
    "exec(string_source, ...)": _exec1,
    "exec(text_string_source, ...)": _exec2,
    "filter": _filter,
    "format": _format,
    "frozenset": _frozenset,
    "float": _float,
    "getattr(obj, name)": _getattr1,
    "getattr(obj, name, default)": _getattr2,
    "hasattr": _hasattr,
    "hash": _hash,
    "hex": _hex,
    "id": _id,
    "int(x)": _int1,
    "int(x, base)": _int2,
    "isinstance": _isinstance,
    "issubclass": _issubclass,
    "iter(obj)": _iter1,
    "iter(callable_obj, sentinel)": _iter2,
    "len": _len,
    "list": _list,
    "map": _map,
    "max(iterable, **kwargs)": _max1,
    "max(*args, **kwargs)": _max2,
    "memoryview": _memoryview,
    "min(iterable, **kwargs)": _min1,
    "min(*args, **kwargs)": _min2,
    "oct": _oct,
    "open": _open,
    "ord": _ord,
    "next(iterator)": _next1,
    "next(iterator, default)": _next2,
    "pow": _pow,
    "print": _print,
    "range(*args)": _range1,
    "range(stop)": _range2,
    "range(start, stop)": _range3,
    "range(start, stop, step)": _range4,
    "repr": _repr,
    "reversed": _reversed,
    "round": _round,
    "set": _set,
    "slice": _slice,
    "sorted": _sorted,
    "str(obj)": _str1,
    "str(obj, encoding, errors)": _str2,
    "sum": _sum,
    "tuple": _tuple,
    "type(obj)": _type1,
    "type(name, bases, a_dict)": _type2,
    "vars(obj)": _vars,
    "zip": _zip,
}

BUILTIN_IDS_TO_SIGNATURES_MAP = {
    builtin_id: signature(callable_obj)
    for builtin_id, callable_obj in BUILTIN_IDS_TO_SIGNATURE_CALLABLES_MAP.items()
}

###


string_stream = StringIO()


def get_help_text(callable_obj):
    content_length = len(string_stream.getvalue())

    with redirect_stdout(string_stream):
        help(callable_obj)

    return string_stream.getvalue()[content_length:].strip()


BUILTIN_IDS_TO_SOURCE_VIEW_TEXT = {
    builtin_id: f'''
### signature used:

{getsource(BUILTIN_IDS_TO_SIGNATURE_CALLABLES_MAP[builtin_id])}

### help text:

"""
{get_help_text(BUILTIN_IDS_TO_CALLABLES_MAP[builtin_id])}
"""
'''.strip()
    for builtin_id in BUILTIN_IDS_TO_CALLABLES_MAP.keys()
}

string_stream.close()
