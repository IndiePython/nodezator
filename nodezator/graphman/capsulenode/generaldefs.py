
### standard library imports

from collections.abc import Callable, Iterator

from json import load, dump

from ast import literal_eval

from pprint import pformat



def read_text_file(
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
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
) -> [{"name": "string", "type": str}]:

    with open(
        filepath,
        mode="r",
        encoding=encoding,
        errors=errors,
    ) as f:
        return f.read()


def write_text_file(
    text: "text_string" = "",
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
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
):

    with open(
        filepath,
        mode="w",
        encoding=encoding,
        errors=errors,
    ) as f:
        f.write(text)


def append_to_text_file(
    text: "text_string" = "",
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
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
):

    with open(
        filepath,
        mode="a",
        encoding=encoding,
        errors=errors,
    ) as f:
        f.write(text)


def read_binary_file(
    filepath: "filepath" = ".",
) -> [{"name": "bytes_obj", "type": bytes}]:
    with open(filepath, mode="rb") as f:
        return f.read()


def write_binary_file(
    binary_data: bytes,
    filepath: "filepath" = ".",
):
    with open(filepath, mode="wb") as f:
        f.write(binary_data)


def append_to_binary_file(
    binary_data: bytes,
    filepath: "filepath" = ".",
):

    with open(filepath, mode="ab") as f:
        f.write(text)


def load_pyl_file(
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
):

    with open(filepath, mode="r", encoding=encoding) as f:
        return literal_eval(f.read())


def load_json_file(
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
    cls: type = None,
    object_hook: Callable = None,
    parse_float: Callable = None,
    parse_int: Callable = None,
    parse_constant: Callable = None,
    object_pairs_hook: Callable = None,
    **kw,
) -> [{"name": "obj"}]:

    with open(filepath, mode="r", encoding=encoding) as f:

        return load(
            f,
            cls=cls,
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            object_pairs_hook=object_pairs_hook,
            **kw,
        )


def save_as_pyl_file(
    obj,
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
    indent: "natural_number" = 1,
    width: "positive_integer" = 80,
    depth: "positive_integer_or_none" = None,
    *,
    compact: bool = False,
):

    with open(filepath, mode="w", encoding=encoding) as f:

        f.write(
            pformat(
                obj,
                indent=indent,
                width=width,
                depth=depth,
                compact=compact,
            )
        )


def save_as_json_file(
    obj,
    filepath: "text_filepath" = ".",
    encoding: str = "utf-8",
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
):

    with open(filepath, mode="w", encoding=encoding) as f:

        dump(
            obj,
            f,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            cls=cls,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            **kw,
        )


def print_and_return(obj_in) -> [{"name": "obj_out"}]:
    return print(obj_in) or obj_in

def return_untouched(obj_in) -> [{"name": "obj_out"}]:
    """Return given object.

    Alternative implementation of an identity function in Python.
    """
    return obj_in

def for_item_in_obj_pass(obj:Iterator):
    """Exhaust given iterator by iterating over it."""
    for _ in obj:
        pass

def perform_call(
    func: Callable,
    *args,
    **kwargs,
) -> [{"name": "func_return_value"}]:
    return func(*args, **kwargs)


def perform_attr_call(
    obj,
    attr_name: str = 'attr_name',
    *args,
    **kwargs,
) -> [{"name": "call_return_value"}]:
    """Call attribute/method from object and return the return value"""
    return getattr(obj, attr_name)(*args, **kwargs)


def tuple_from_args(*args) -> [{"name": "a_tuple", "type": tuple}]:  # (a, b, c...)
    return args


def list_from_args(*args) -> [{"name": "a_list", "type": list}]:  # [a, b, c]
    return list(args)


def set_from_args(*args) -> [{"name": "a_set", "type": set}]:  # {a, b, c}
    return set(args)


def get_at_int(obj, integer: int = 0) -> [{"name": "item"}]:
    return obj[integer]


def get_at_string(obj, string: str = "") -> [{"name": "item"}]:
    return obj[string]


def get_at_literal(obj, literal: "python_literal" = None) -> [{"name": "item"}]:
    return obj[literal]


def namespace_from_exec(
    python_source: {
        "widget_name": "text_display",
        "widget_kwargs": {"syntax_highlighting": "python", "font_path": "mono_bold"},
        "type": str,
    } = "",
    **variables,
) -> [{"name": "namespace", "type": dict}]:
    exec(python_source, variables)
    _d = {}
    exec("", _d)
    return {k: v for k, v in variables.items() if k not in _d}


def get_constant_returner(constant_value) -> [
        {"name": "constant_returner", "type": Callable}
    ]:
    """Return function that returns same value, no matter the argument given.

    Alternative implementation of a K combinator in Python.
    """

    def constant_returner(ignored_value):
        """Return same value regardless of given one."""
        return constant_value

    return constant_returner
