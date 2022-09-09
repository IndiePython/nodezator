"""Node class extesion with exporting support."""

### standard library import

from xml.etree.ElementTree import Element

from itertools import chain


### third-party import
from pygame.math import Vector2


### local imports

from .constants import (
    OP_CHARS_HEIGHT,
    AB_CHARS_HEIGHT,
    NODE_OUTLINE_THICKNESS,
    FONT_HEIGHT,
    CHAR_FILTERING_MAP,
)

from .surfs import CHAR_CENTERXS_MAP

from ...colorsman.colors import (
    BLACK,
    PROXY_NODE_NORMAL_FG,
    PROXY_NODE_NORMAL_BG,
    PROXY_NODE_NORMAL_OUTLINE,
    OPERATION_NODE_NORMAL_AB_CHARS,
    OPERATION_NODE_NORMAL_OP_CHARS,
    PROXY_NODE_COMMENTED_OUT_FG,
    PROXY_NODE_COMMENTED_OUT_BG,
    PROXY_NODE_COMMENTED_OUT_OUTLINE,
    OPERATION_NODE_COMMENTED_OUT_AB_CHARS,
    OPERATION_NODE_COMMENTED_OUT_OP_CHARS,
)


### constants

SMALL_FONT_HEIGHT = FONT_HEIGHT + -4

BIG_AB_HEIGHT = AB_CHARS_HEIGHT + -10
BIG_OP_HEIGHT = OP_CHARS_HEIGHT + -10


OPERATOR_NODE_CSS = f"""

g.operator_node > rect.normal_body
{{
  fill         : rgb{PROXY_NODE_NORMAL_BG};
  stroke       : rgb{PROXY_NODE_NORMAL_OUTLINE};
  stroke-width : {NODE_OUTLINE_THICKNESS};
}}

g.operator_node > rect.commented_out_body
{{
  fill         : rgb{PROXY_NODE_COMMENTED_OUT_BG};
  stroke       : rgb{PROXY_NODE_COMMENTED_OUT_OUTLINE};
  stroke-width : {NODE_OUTLINE_THICKNESS};
}}

g.operator_node > text.normal_small_text
{{
  font: bold {SMALL_FONT_HEIGHT}px sans-serif;
  fill: rgb{PROXY_NODE_NORMAL_FG};
}}

g.operator_node > text.commented_out_small_text
{{
  font: bold {SMALL_FONT_HEIGHT}px sans-serif;
  fill: rgb{PROXY_NODE_COMMENTED_OUT_FG};
}}

g.operator_node > text.normal_big_ab_text
{{
  font: bold {BIG_AB_HEIGHT}px sans-serif;
  fill: rgb{OPERATION_NODE_NORMAL_AB_CHARS};
}}

g.operator_node > text.normal_big_op_text
{{
  font: bold {BIG_OP_HEIGHT}px sans-serif;
  fill: rgb{OPERATION_NODE_NORMAL_OP_CHARS};
}}

g.operator_node > text.commented_out_big_ab_text
{{
  font: bold {BIG_AB_HEIGHT}px sans-serif;
  fill: rgb{OPERATION_NODE_COMMENTED_OUT_AB_CHARS};
}}

g.operator_node > text.commented_out_big_op_text
{{
  font: bold {BIG_OP_HEIGHT}px sans-serif;
  fill: rgb{OPERATION_NODE_COMMENTED_OUT_OP_CHARS};
}}
"""


class Exporting:
    """Manages export operations on node."""

    def svg_repr(self):
        """Return node as an svg group element.

        Used to represent the node and its elements when
        exporting the node graph to a .svg file.
        """
        ### group containing node subelements
        node_g = Element("g", {"class": "node operator_node"})

        ###

        outline_deflation = NODE_OUTLINE_THICKNESS * 2

        body_rect = self.body.rect.inflate(
            -outline_deflation,
            -outline_deflation,
        )

        x, y, width, height = body_rect

        ###

        is_commented_out = self.data.get("commented_out", False)

        ### body

        node_g.append(
            Element(
                "rect",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": str(width),
                    "height": str(height),
                    "class": (
                        "commented_out_body" if is_commented_out else "normal_body"
                    ),
                },
            )
        )

        ### big chars

        string = self.data["operation_id"]
        centerxs = CHAR_CENTERXS_MAP[string]
        flags = CHAR_FILTERING_MAP[string]

        char_flag_pairs = [
            (char, flag) for char, flag in zip(string, flags) if char != " "
        ]

        x_offset = self.rect.left + 20
        bottom = self.rect.bottom - 22

        state = "commented_out_big_" if is_commented_out else "normal_big_"

        for ((char, flag), centerx) in zip(char_flag_pairs, centerxs):

            class_name = state + ("ab_text" if flag else "op_text")

            tx_str, ty_str = map(str, (centerx + x_offset, bottom))

            char_text = Element(
                "text",
                {
                    "x": tx_str,
                    "y": ty_str,
                    "text-anchor": "middle",
                    "class": class_name,
                },
            )

            char_text.text = char

            node_g.append(char_text)

        ### node's label

        tx_str, ty_str = map(
            str,
            self.label.rect.move(0, -6).midbottom,
        )

        label = Element(
            "text",
            {
                "x": tx_str,
                "y": ty_str,
                "text-anchor": "middle",
                "class": (
                    "commented_out_small_text"
                    if is_commented_out
                    else "normal_small_text"
                ),
            },
        )

        label.text = f"{self.id}"

        node_g.append(label)

        ### input sockets and param text

        for socket in self.input_sockets:

            node_g.append(socket.svg_repr())

            tx_str, ty_str = map(
                str,
                socket.rect.move(0, -3).bottomright,
            )

            param_text = Element(
                "text",
                {
                    "x": tx_str,
                    "y": ty_str,
                    "class": (
                        "commented_out_small_text"
                        if is_commented_out
                        else "normal_small_text"
                    ),
                },
            )

            param_text.text = socket.parameter_name

            node_g.append(param_text)

        ### output socket
        node_g.append(self.output_socket.svg_repr())

        ##
        return node_g

    def draw_on_surf(self, surf):
        """Draw node elements on provided surf.

        Used to draw the node and its elements on another
        surface when exporting the node graph to an image
        file.
        """
        blit_on_surf = surf.blit

        for obj in self.visual_objects:
            blit_on_surf(obj.image, obj.rect)
