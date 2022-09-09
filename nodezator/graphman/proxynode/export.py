"""Node class extesion with exporting support."""

### standard library import

from xml.etree.ElementTree import Element

from itertools import chain


### local imports

from ...pointsman2d.shape import cross_from_rect
from ...pointsman2d.transform import rotate_points

from .constants import (
    NODE_OUTLINE_THICKNESS,
    FONT_HEIGHT,
)

from ...colorsman.colors import (
    BLACK,
    PROXY_NODE_NORMAL_FG,
    PROXY_NODE_NORMAL_BG,
    PROXY_NODE_NORMAL_OUTLINE,
    PROXY_NODE_COMMENTED_OUT_FG,
    PROXY_NODE_COMMENTED_OUT_BG,
    PROXY_NODE_COMMENTED_OUT_OUTLINE,
    PROXY_NODE_WIDGET_ADD_BUTTON_FILL,
    PROXY_NODE_WIDGET_ADD_BUTTON_OUTLINE,
    PROXY_NODE_WIDGET_REMOVE_BUTTON_FILL,
    PROXY_NODE_WIDGET_REMOVE_BUTTON_OUTLINE,
)


### constants

FONT_HEIGHT += -4

PROXY_NODE_CSS = f"""

g.proxy_node > rect.normal_header
{{
  fill         : rgb{PROXY_NODE_NORMAL_BG};
  stroke       : rgb{PROXY_NODE_NORMAL_OUTLINE};
  stroke-width : {NODE_OUTLINE_THICKNESS};
}}

g.proxy_node > rect.commented_out_header
{{
  fill         : rgb{PROXY_NODE_COMMENTED_OUT_BG};
  stroke       : rgb{PROXY_NODE_COMMENTED_OUT_OUTLINE};
  stroke-width : {NODE_OUTLINE_THICKNESS};
}}

g.proxy_node > text
{{
  font: bold {FONT_HEIGHT}px sans-serif;
}}

g.proxy_node > text.normal_label
{{fill : rgb{PROXY_NODE_NORMAL_FG};}}

g.proxy_node > text.commented_out_label
{{fill : rgb{PROXY_NODE_COMMENTED_OUT_FG};}}

g.proxy_node > path.add_button
{{
  fill: rgb{PROXY_NODE_WIDGET_ADD_BUTTON_FILL};
  stroke: rgb{PROXY_NODE_WIDGET_ADD_BUTTON_OUTLINE};
  stroke-width: 2px;
}}

g.proxy_node > path.remove_button
{{
  fill: rgb{PROXY_NODE_WIDGET_REMOVE_BUTTON_FILL};
  stroke: rgb{PROXY_NODE_WIDGET_REMOVE_BUTTON_OUTLINE};
  stroke-width: 2px;
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
        node_g = Element("g", {"class": "node proxy_node"})

        ###

        outline_deflation = NODE_OUTLINE_THICKNESS * 2

        header_rect = self.header.rect.inflate(
            -outline_deflation,
            -outline_deflation,
        )

        x, y, width, height = header_rect

        ###

        is_commented_out = self.data.get("commented_out", False)

        ### header

        node_g.append(
            Element(
                "rect",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": str(width),
                    "height": str(height),
                    "class": (
                        "commented_out_header" if is_commented_out else "normal_header"
                    ),
                },
            )
        )

        ### node's label

        tx_str, ty_str = map(
            str,
            self.label.rect.move(0, -3).midbottom,
        )

        label = Element(
            "text",
            {
                "x": tx_str,
                "y": ty_str,
                "text-anchor": "middle",
                "class": (
                    "commented_out_label" if is_commented_out else "normal_label"
                ),
            },
        )

        label.text = self.get_label_text()

        node_g.append(label)

        ### proxy socket
        node_g.append(self.proxy_socket.svg_repr())

        ### output socket
        node_g.append(self.output_socket.svg_repr())

        ###

        try:
            self.widget

        except AttributeError:

            ###

            button_rect = self.add_button.rect.inflate(-2, -2)

            path_directives = "M"

            for x, y in cross_from_rect(button_rect, 0.3):
                path_directives += f"{x} {y} L"

            path_directives = path_directives[:-1] + " Z"

            node_g.append(
                Element(
                    "path",
                    {
                        "d": path_directives,
                        "class": "add_button",
                    },
                )
            )

        else:

            ### widget
            node_g.append(self.widget.svg_repr())

            ### remove button
            button_rect = self.remove_button.rect.inflate(-2, -2)

            path_directives = "M"

            for x, y in rotate_points(
                cross_from_rect(button_rect, 0.3),
                40,
                button_rect.center,
            ):
                path_directives += f"{x} {y} L"

            path_directives = path_directives[:-1] + " Z"

            node_g.append(
                Element(
                    "path",
                    {
                        "d": path_directives,
                        "class": "remove_button",
                    },
                )
            )

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
