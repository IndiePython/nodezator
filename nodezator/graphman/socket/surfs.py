"""Surfaces for sockets and related tools."""

### standard library imports

from inspect import Parameter

from collections.abc import Iterable, Iterator


### local imports

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    ## hollow socket
    HOLLOW_SOCKET_OUTLINE,
    ## input and output sockets
    STR_TYPE_OUTLINE,
    STR_TYPE_FILL,
    BOOL_TYPE_OUTLINE,
    BOOL_TYPE_FILL,
    NUMBER_TYPE_OUTLINE,
    NUMBER_TYPE_FILL,
    DICT_TYPE_OUTLINE,
    DICT_TYPE_FILL,
    LIST_TYPE_OUTLINE,
    LIST_TYPE_FILL,
    TUPLE_TYPE_OUTLINE,
    TUPLE_TYPE_FILL,
    ITERABLE_TYPE_OUTLINE,
    ITERABLE_TYPE_FILL,
    ITERATOR_TYPE_OUTLINE,
    ITERATOR_TYPE_FILL,
    NOT_SPECIFIED_TYPE_OUTLINE,
    NOT_SPECIFIED_TYPE_FILL,
    OTHER_TYPE_OUTLINE,
    OTHER_TYPE_FILL,
)


### constant
SOCKET_DIAMETER = 16

### surface for hollow sockets
###
### hollow sockets outline color is defined by the
### application theme (hollow sockets don't have
### a fill color);

HOLLOW_SOCKET_CIRCLE_SURF = render_layered_icon(
    chars=[chr(98)],
    dimension_name="height",
    dimension_value=SOCKET_DIAMETER,
    colors=[HOLLOW_SOCKET_OUTLINE],
    background_width=SOCKET_DIAMETER,
    background_height=SOCKET_DIAMETER,
)

### dict to map expected types to hint codename

TYPE_TO_CODENAME_MAP = {
    str: "str",
    bool: "bool",
    dict: "dict",
    # number types plus NoneType
    int: "number",
    float: "number",
    frozenset((int, type(None))): "number",
    frozenset((int, None)): "number",
    frozenset((float, type(None))): "number",
    frozenset((float, None)): "number",
    frozenset((int, float)): "number",
    frozenset((int, float, type(None))): "number",
    frozenset((int, float, None)): "number",
    # list and tuple related
    list: "list",
    tuple: "tuple",
    # iterable and iterator
    Iterable: "iterable",
    Iterator: "iterator",
    # parameter not specified
    Parameter.empty: "not_specified",
}


### create a dict to map codename to style objects related
### to them;
###
### start by populating it with colors and an svg class
### name related to the type(s)

CODENAME_TO_STYLE_MAP = {
    "str": (
        STR_TYPE_OUTLINE,
        STR_TYPE_FILL,
    ),
    "bool": (
        BOOL_TYPE_OUTLINE,
        BOOL_TYPE_FILL,
    ),
    "dict": (
        DICT_TYPE_OUTLINE,
        DICT_TYPE_FILL,
    ),
    "number": (
        NUMBER_TYPE_OUTLINE,
        NUMBER_TYPE_FILL,
    ),
    # list and tuple related
    "list": (
        LIST_TYPE_OUTLINE,
        LIST_TYPE_FILL,
    ),
    "tuple": (
        TUPLE_TYPE_OUTLINE,
        TUPLE_TYPE_FILL,
    ),
    # iterable and iterator
    "iterable": (
        ITERABLE_TYPE_OUTLINE,
        ITERABLE_TYPE_FILL,
    ),
    "iterator": (
        ITERATOR_TYPE_OUTLINE,
        ITERATOR_TYPE_FILL,
    ),
    # parameter not specified
    "not_specified": (
        NOT_SPECIFIED_TYPE_OUTLINE,
        NOT_SPECIFIED_TYPE_FILL,
    ),
    # any other possible type
    "other": (
        OTHER_TYPE_OUTLINE,
        OTHER_TYPE_FILL,
    ),
}


### create a surface with the specified colors for
### each value within the map

CODENAME_TO_STYLE_MAP.update(
    (
        codename,
        (
            outline_color,
            fill_color,
            codename,  # also used as svg class name
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (98, 99)],
                dimension_name="height",
                dimension_value=SOCKET_DIAMETER,
                colors=[
                    outline_color,
                    fill_color,
                ],
                background_width=SOCKET_DIAMETER,
                background_height=SOCKET_DIAMETER,
            ),
        ),
    )
    for codename, (outline_color, fill_color) in (list(CODENAME_TO_STYLE_MAP.items()))
)


### utility function to be used by nodes to retrieve
### style codenames for their sockets


def type_to_codename(type_):
    """Return string representing type.

    Parameters
    ==========
    type_ (any Python value; usually a type)
        type_ for which a suitable codename will be
        picked or a default will be returned.
    """
    ### try obtaining a frozenset from the type_ received

    try:
        type_ = frozenset(type_)
    except:
        pass

    ### regardless of whether the attemp above succeed
    ### or not, get the style objects from the map if
    ### the type_ is present, otherwise use 'other'
    return TYPE_TO_CODENAME_MAP.get(type_, "other")


### svg css

SOCKET_AND_LINE_CSS = f"""

line {{stroke-width: 4;}}

g.node > circle
{{stroke-width: 2;}}

g.node > circle.hollow_socket
{{

  fill         : rgb(0, 0, 0);
  fill-opacity : 0;

  stroke : rgb{HOLLOW_SOCKET_OUTLINE};

}}

g.node > circle.other
{{
  fill   : rgb{OTHER_TYPE_FILL};
  stroke : rgb{OTHER_TYPE_OUTLINE};
}}

line.other
{{stroke : rgb{OTHER_TYPE_FILL};}}

"""

for (outline_color, fill_color, svg_class_name, *_) in CODENAME_TO_STYLE_MAP.values():

    SOCKET_AND_LINE_CSS += f"""
g.node > circle.{svg_class_name}
{{
  fill   : rgb{fill_color};
  stroke : rgb{outline_color};
}}

line.{svg_class_name}
{{stroke : rgb{fill_color};}}
"""
