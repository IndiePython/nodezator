### standard library imports

from collections.abc import Callable

from json import load, dump

from ast import literal_eval

from pprint import pformat

from string import Template

from inspect import signature, getsource


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


def perform_call(
    func: Callable,
    *args,
    **kwargs,
) -> [{"name": "func_return_value"}]:
    return func(*args, **kwargs)


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


CAPSULE_IDS_TO_CALLABLES_MAP = {
    "read_text_file": read_text_file,
    "write_text_file": write_text_file,
    "append_to_text_file": append_to_text_file,
    "read_binary_file": read_binary_file,
    "write_binary_file": write_binary_file,
    "append_to_binary_file": append_to_binary_file,
    "load_pyl_file": load_pyl_file,
    "save_as_pyl_file": save_as_pyl_file,
    "load_json_file": load_json_file,
    "save_as_json_file": save_as_json_file,
    "print_and_return": print_and_return,
    "perform_call": perform_call,
    "tuple_from_args": tuple_from_args,
    "list_from_args": list_from_args,
    "set_from_args": set_from_args,
    "get_at_int": get_at_int,
    "get_at_string": get_at_string,
    "get_at_literal": get_at_literal,
    "namespace_from_exec": namespace_from_exec,
}

CAPSULE_IDS_TO_SIGNATURES_MAP = {
    capsule_id: signature(callable_obj)
    for capsule_id, callable_obj in CAPSULE_IDS_TO_CALLABLES_MAP.items()
}

CAPSULE_IDS_TO_SUBSTITUTION_CALLABLE_MAP = {
    "read_text_file": Template(
        """

with open(

  $filepath,
  mode='r',
  encoding=$encoding,
  errors=$errors,

) as f:

    $string = f.read()

""".strip()
    ).substitute,
    "write_text_file": Template(
        """

with open(
  $filepath,
  mode='w',
  encoding=$encoding,
  errors=$errors,
) as f:
    f.write($text)

$output = None

""".strip()
    ).substitute,
    "append_to_text_file": Template(
        """

with open(
  $filepath,
  mode='a',
  encoding=$encoding,
  errors=$errors,
) as f:
    f.write($text)

$output = None

""".strip()
    ).substitute,
    "read_binary_file": Template(
        """

with open($filepath, mode='rb') as f:
    $bytes_obj = f.read()

""".strip()
    ).substitute,
    "write_binary_file": Template(
        """

with open($filepath, mode='wb') as f:
    f.write($binary_data)

$output = None

""".strip()
    ).substitute,
    "append_to_binary_file": Template(
        """

with open($filepath, mode='ab') as f:
    f.write($binary_data)

$output = None

""".strip()
    ).substitute,
    "load_pyl_file": Template(
        """

with open($filepath, mode='r', encoding=$encoding) as f:
    $output = literal_eval(f.read())

""".strip()
    ).substitute,
    "save_as_pyl_file": Template(
        """

with open($filepath, mode='w', encoding=$encoding) as f:
    
    f.write(

        pformat(
          $obj,
          indent=$indent,
          width=$width,
          depth=$depth,
          compact=$compact,
        )

    )

$output = None

""".strip()
    ).substitute,
    "load_json_file": Template(
        """

with open($filepath, mode='r', encoding=$encoding) as f:

    $obj = load(

             f,
             cls=$cls,
             object_hook=$object_hook,
             parse_float=$parse_float,
             parse_int=$parse_int,
             parse_constant=$parse_constant,
             object_pairs_hook=$object_pairs_hook,
             **$kw,

           )

""".strip()
    ).substitute,
    "save_as_json_file": Template(
        """

with open($filepath, mode='w', encoding=$encoding) as f:
    
    dump(
      $obj,
      f,
      skipkeys=$skipkeys,
      ensure_ascii=$ensure_ascii,
      check_circular=$check_circular,
      allow_nan=$allow_nan,
      cls=$cls,

      indent=$indent,

      separators=$separators,
      default=$default,
      sort_keys=$sort_keys,
      **$kw,
    )

$output = None

""".strip()
    ).substitute,
    "print_and_return": Template(
        """

$obj_out = print($obj_in) or $obj_in

""".strip()
    ).substitute,
    "perform_call": Template(
        """
$func_return_value = $func(*$args, **$kwargs)
""".strip()
    ).substitute,
    "tuple_from_args": Template(
        """
$a_tuple = $args
""".strip()
    ).substitute,
    "list_from_args": Template(
        """
$a_list = list($args)
""".strip()
    ).substitute,
    "set_from_args": Template(
        """
$a_set = set($args)
""".strip()
    ).substitute,
    "get_at_int": Template(
        """
$item = $obj[$integer]
""".strip()
    ).substitute,
    "get_at_string": Template(
        """
$item = $obj[$string]
""".strip()
    ).substitute,
    "get_at_literal": Template(
        """
$item = $obj[$literal]
""".strip()
    ).substitute,
    "namespace_from_exec": Template(
        """

_vars = $variables
exec($python_source, _vars)
_d = {}
exec('', _d)
$namespace = {k:v for k, v in _vars.items() if k not in _d}

""".strip()
    ).substitute,
}

CAPSULE_IDS_TO_STLIB_IMPORT_MAP = {
    "load_pyl_file": "from ast import literal_eval",
    "save_as_pyl_file": "from pprint import pformat",
    "load_json_file": "from json import load",
    "save_as_json_file": "from json import dump",
}

CAPSULE_IDS_TO_SOURCE_VIEW_TEXT = {
    capsule_id: (
        (
            CAPSULE_IDS_TO_STLIB_IMPORT_MAP[capsule_id]
            + ("\n" * 2)
            + getsource(callable_obj)
        )
        if capsule_id in CAPSULE_IDS_TO_STLIB_IMPORT_MAP
        else getsource(callable_obj)
    )
    for capsule_id, callable_obj in CAPSULE_IDS_TO_CALLABLES_MAP.items()
}
