### standard library imports

from string import Template

from inspect import signature, getsource


### local imports

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_PATH,
    ENC_SANS_BOLD_FONT_HEIGHT,
)

from ...colorsman.colors import (
    OPERATION_NODE_NORMAL_BG,
    OPERATION_NODE_NORMAL_FG,
    OPERATION_NODE_COMMENTED_OUT_BG,
    OPERATION_NODE_COMMENTED_OUT_FG,
)


OPERATIONS_MAP = {
    "a + b": lambda a, b: a + b,
    "a - b": lambda a, b: a - b,
    "a / b": lambda a, b: a / b,
    "a // b": lambda a, b: a // b,
    "a * b": lambda a, b: a * b,
    "a ** b": lambda a, b: a**b,
    "a % b": lambda a, b: a % b,
    "+a": lambda a: +a,
    "-a": lambda a: -a,
    "a[b]": lambda a, b: a[b],
    "a @ b": lambda a, b: a @ b,
    "a & b": lambda a, b: a & b,
    "a ^ b": lambda a, b: a ^ b,
    "~a": lambda a: ~a,
    "a | b": lambda a, b: a | b,
    "a << b": lambda a, b: a << b,
    "a >> b": lambda a, b: a >> b,
    "a is b": lambda a, b: a is b,
    "a is not b": lambda a, b: a is not b,
    "not a": lambda a: not a,
    "a and b": lambda a, b: a and b,
    "a or b": lambda a, b: a or b,
    "a < b": lambda a, b: a < b,
    "a <= b": lambda a, b: a <= b,
    "a == b": lambda a, b: a == b,
    "a != b": lambda a, b: a != b,
    "a >= b": lambda a, b: a >= b,
    "a > b": lambda a, b: a > b,
}

CHAR_FILTERING_MAP = {
    "a + b": (1, 0, 0, 0, 1),
    "a - b": (1, 0, 0, 0, 1),
    "a / b": (1, 0, 0, 0, 1),
    "a // b": (1, 0, 0, 0, 0, 1),
    "a * b": (1, 0, 0, 0, 1),
    "a ** b": (1, 0, 0, 0, 0, 1),
    "a % b": (1, 0, 0, 0, 1),
    "+a": (0, 1),
    "-a": (0, 1),
    "a[b]": (1, 0, 1, 0),
    "a @ b": (1, 0, 0, 0, 1),
    "a & b": (1, 0, 0, 0, 1),
    "a ^ b": (1, 0, 0, 0, 1),
    "~a": (0, 1),
    "a | b": (1, 0, 0, 0, 1),
    "a << b": (1, 0, 0, 0, 0, 1),
    "a >> b": (1, 0, 0, 0, 0, 1),
    "a is b": (1, 0, 0, 0, 0, 1),
    "a is not b": (1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    "not a": (0, 0, 0, 0, 1),
    "a and b": (1, 0, 0, 0, 0, 0, 1),
    "a or b": (1, 0, 0, 0, 0, 1),
    "a < b": (1, 0, 0, 0, 1),
    "a <= b": (1, 0, 0, 0, 0, 1),
    "a == b": (1, 0, 0, 0, 0, 1),
    "a != b": (1, 0, 0, 0, 0, 1),
    "a >= b": (1, 0, 0, 0, 0, 1),
    "a > b": (1, 0, 0, 0, 1),
}

OPERATIONS_SIGNATURE_MAP = {
    key: signature(callable_obj) for key, callable_obj in OPERATIONS_MAP.items()
}


FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT
AB_CHARS_HEIGHT = 70
OP_CHARS_HEIGHT = 90
LABEL_AREA_HEIGHT = FONT_HEIGHT // 2

NODE_OUTLINE_THICKNESS = 2
NODE_PADDING = NODE_OUTLINE_THICKNESS + 4

MAX_WIDTH = 155 - (2 * NODE_OUTLINE_THICKNESS) - 4

GENERAL_PARAMETER_TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 0,
}

NORMAL_PARAMETER_TEXT_SETTINGS = {
    "foreground_color": OPERATION_NODE_NORMAL_FG,
    "background_color": OPERATION_NODE_NORMAL_BG,
    **GENERAL_PARAMETER_TEXT_SETTINGS,
}


COMMENTED_OUT_PARAMETER_TEXT_SETTINGS = {
    "foreground_color": OPERATION_NODE_COMMENTED_OUT_FG,
    "background_color": OPERATION_NODE_COMMENTED_OUT_BG,
    **GENERAL_PARAMETER_TEXT_SETTINGS,
}


def treat_params(operation_id):

    chars = list(operation_id)

    param_char_indices = [
        index for index, flag in enumerate(CHAR_FILTERING_MAP[operation_id]) if flag
    ]

    for index in reversed(param_char_indices):
        chars.insert(index, "$")

    return "".join(chars)


OPERATION_ID_TO_SUBSTITUTION_CALLABLE_MAP = {
    operation_id: Template("$output = " + treat_params(operation_id)).substitute
    for operation_id in OPERATIONS_MAP
}

###


def get_operator_node_source(callable_obj):

    source = getsource(callable_obj).strip()
    i = source.find("lambda")

    return source[i:][:-1] if source.endswith(",") else source[i:]


OPERATION_ID_TO_SOURCE_VIEW_TEXT = {
    operation_id: f"""
### same as...
{get_operator_node_source(callable_obj)}
""".strip()
    for operation_id, callable_obj in OPERATIONS_MAP.items()
}
