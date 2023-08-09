from ..callablenode.constants import NODE_OUTLINE_THICKNESS

from ...colorsman.colors import (
    BLACK,
    NODE_OUTLINE,
    GENVIEWER_NODES_CATEGORY_COLOR,
)

from .constants import GENVIEWER_IDS_TO_PYTHON_SOURCE


GENVIEWER_NODE_CSS = f"""
g.callable_node > path.header_fill_genviewer_node
{{
  fill           : rgb{GENVIEWER_NODES_CATEGORY_COLOR};
  stroke         : rgb{NODE_OUTLINE};
  stroke-width   : {NODE_OUTLINE_THICKNESS};
  stroke-opacity : 0;
}}

g.callable_node > rect.id_bg_rect_genviewer_node
{{
  fill        : rgb{GENVIEWER_NODES_CATEGORY_COLOR};
  stroke      : rgb{BLACK};
  stroke-width: 1;
}}
"""

def get_source_to_export(self):
    """Return callable's source to be exported as python code."""
    return GENVIEWER_IDS_TO_PYTHON_SOURCE[self.data["genviewer_id"]]
