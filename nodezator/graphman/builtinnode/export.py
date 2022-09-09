from ..callablenode.constants import NODE_OUTLINE_THICKNESS

from ...colorsman.colors import (
    BLACK,
    NODE_OUTLINE,
    BUILTIN_NODES_CATEGORY_COLOR,
)

BUILTIN_NODE_CSS = f"""
g.callable_node > path.header_fill_builtin_node
{{
  fill           : rgb{BUILTIN_NODES_CATEGORY_COLOR};
  stroke         : rgb{NODE_OUTLINE};
  stroke-width   : {NODE_OUTLINE_THICKNESS};
  stroke-opacity : 0;
}}

g.callable_node > rect.id_bg_rect_builtin_node
{{
  fill        : rgb{BUILTIN_NODES_CATEGORY_COLOR};
  stroke      : rgb{BLACK};
  stroke-width: 1;
}}
"""
