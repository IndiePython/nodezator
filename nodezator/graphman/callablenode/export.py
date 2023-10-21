"""Node class extesion with exporting support."""

### standard library import

from xml.etree.ElementTree import Element

from itertools import chain


### local imports

from ...rectsman.main import RectsManager

from .constants import (
    NODE_OUTLINE_THICKNESS,
    FONT_HEIGHT,
)

from .surfs import (
    TOP_CORNERS_MAP,
    UNPACKING_ICON_SURFS_MAP,
)

from ...pointsman2d.shape import cross_from_rect
from ...pointsman2d.transform import rotate_points

from ...colorsman.colors import (
    BLACK,
    NODE_BODY_BG,
    COMMENTED_OUT_NODE_BG,
    NODE_CATEGORY_COLORS,
    NODE_OUTLINE,
    NODE_TITLE,
    NODE_LABELS,
    UNPACKING_ICON_COLOR,
)


### constants

(
    CORNER_RADIUS_X_STR,
    CORNER_RADIUS_Y_STR,
) = map(str, (TOP_CORNERS_MAP[NODE_CATEGORY_COLORS[0]][0].get_size()))

UNPACKING_ICON_RECT = UNPACKING_ICON_SURFS_MAP[("var_pos", False)].get_rect()
UNPACKING_ICON_RECT_SMALLER = UNPACKING_ICON_RECT.inflate(-6, -6)

UNPACKING_RECTS = [
    UNPACKING_ICON_RECT,
    UNPACKING_ICON_RECT_SMALLER,
]

UNPACKING_RECTS_MANAGER = RectsManager(UNPACKING_RECTS.__iter__)


def get_unpacking_icon_group():

    rect, small_rect = UNPACKING_RECTS

    lines = [
        (
            rect.midleft,
            rect.midright,
        ),
        (
            rect.midtop,
            rect.midbottom,
        ),
        (
            small_rect.topleft,
            small_rect.bottomright,
        ),
        (
            small_rect.bottomleft,
            small_rect.topright,
        ),
    ]

    g = Element("g", {"class": "unpacking_icon"})

    for line in lines:

        p1, p2 = line

        x1, y1 = map(str, p1)
        x2, y2 = map(str, p2)

        g.append(
            Element(
                "line",
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                },
            )
        )

    return g


FONT_HEIGHT += -4

id_bg_rect_css = "".join(
    f"""g.callable_node > rect.id_bg_rect_{index}
{{
  fill         : rgb{color};
  stroke       : rgb{BLACK};
  stroke-width : 1;
}}

"""
    for index, color in enumerate(NODE_CATEGORY_COLORS)
)

header_fill_css = "".join(
    f"""g.callable_node > path.header_fill_{index}
{{
  fill           : rgb{color};
  stroke         : rgb{NODE_OUTLINE};
  stroke-width   : {NODE_OUTLINE_THICKNESS};
  stroke-opacity : 0;
}}

"""
    for index, color in enumerate(NODE_CATEGORY_COLORS)
)


CALLABLE_NODE_CSS = f"""

g.callable_node > rect.normal_fill
{{
  fill           : rgb{NODE_BODY_BG};
  stroke         : rgb{NODE_OUTLINE};
  stroke-width   : {NODE_OUTLINE_THICKNESS};
  stroke-opacity : 0;
}}

g.callable_node > rect.commented_out_fill
{{
  fill           : rgb{COMMENTED_OUT_NODE_BG};
  stroke         : rgb{NODE_OUTLINE};
  stroke-width   : {NODE_OUTLINE_THICKNESS};
  stroke-opacity : 0;
}}

{header_fill_css}

g.callable_node > path.header_outline
{{
  fill         : none;
  fill-opacity : 0;
  stroke       : rgb{NODE_OUTLINE};
  stroke-width : {NODE_OUTLINE_THICKNESS};
}}

g.callable_node > path.sigmode_toggle_button
{{
  fill: white;
  stroke: none;
}}

g.callable_node > text
{{
  font: bold {FONT_HEIGHT}px sans-serif;
}}

g.callable_node > text.title
{{fill : rgb{NODE_TITLE};}}

{id_bg_rect_css}

g.callable_node > text.id_text
{{fill : rgb{NODE_TITLE};}}

g.callable_node > rect.outline
{{
  fill         : rgb{NODE_BODY_BG};
  stroke       : rgb{NODE_OUTLINE};
  stroke-width : {NODE_OUTLINE_THICKNESS};
  fill-opacity : 0;
}}

g.callable_node > text.label
{{fill : rgb{NODE_LABELS};}}

g.callable_node > path.subparam_key
{{
  fill: yellow;
  stroke: black;
  stroke-width: 1px;
}}

g.callable_node > circle.normal_subparam_key_hole
{{
  fill: rgb{NODE_BODY_BG};
  stroke: black;
  stroke-width: 1px;
}}

g.callable_node > circle.commented_out_subparam_key_hole
{{
  fill: rgb{COMMENTED_OUT_NODE_BG};
  stroke: black;
  stroke-width: 1px;
}}

g.callable_node > path.add_button
{{
  fill: rgb(180, 255, 180);
  stroke: black;
  stroke-width: 2px;
}}

g.callable_node > path.remove_button
{{
  fill: rgb(204, 0, 0);
  stroke: black;
  stroke-width: 2px;
}}

g.callable_node > rect.subparam_move_button
{{
  fill:grey;
  stroke:white;
  stroke-width:1px;
}}

g.callable_node > path.subparam_move_button
{{
  fill:black;
}}

g.callable_node > g.unpacking_icon > line
{{
  stroke: rgb{UNPACKING_ICON_COLOR};
  stroke-width:2px;
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
        node_g = Element("g", {"class": "node callable_node"})

        ###

        node_rect = self.top_rectsman.copy()
        node_rect.height = self.rect.height

        outline_deflation = NODE_OUTLINE_THICKNESS * 2

        node_rect = node_rect.inflate(
            -outline_deflation,
            -outline_deflation,
        )

        x, y, width, height = node_rect

        ###
        color_identifier = self.get_color_identifier()

        ###

        ### node fill

        node_g.append(
            Element(
                "rect",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": str(width),
                    "height": str(height),
                    "rx": CORNER_RADIUS_X_STR,
                    "ry": CORNER_RADIUS_Y_STR,
                    "class": (
                        "commented_out_fill"
                        if self.data.get("commented_out", False)
                        else "normal_fill"
                    ),
                },
            )
        )

        ### node header

        ## fill

        title_rect = self.title_text_obj.rect

        path_directives = (
            f"M{node_rect.x} {title_rect.move(0, 3).bottom}"
            f" l{node_rect.w} 0"
            f" l0 -{title_rect.h-4}"
            " q0 -8 -8 -8"
            f" l-{node_rect.w-16} 0"
            " q-8 0 -8 8"
            f" l0 {title_rect.h-4}"
            " Z"
        )

        header_fill_class_name = f"header_fill_{color_identifier}"

        node_g.append(
            Element(
                "path",
                {
                    "d": path_directives,
                    "class": header_fill_class_name,
                },
            )
        )

        ## outline

        node_g.append(
            Element(
                "path",
                {
                    "d": path_directives,
                    "class": "header_outline",
                },
            )
        )

        ### id bg rect

        id_text_rect = self.id_text_obj.rect

        id_bg_rect_class_name = f"id_bg_rect_{color_identifier}"

        node_g.append(
            Element(
                "rect",
                {
                    "x": str(id_text_rect.x),
                    "y": str(id_text_rect.y),
                    "width": str(id_text_rect.width),
                    "height": str(id_text_rect.height),
                    "class": id_bg_rect_class_name,
                },
            )
        )

        ### node's id

        idx_str, idy_str = map(
            str,
            id_text_rect.move(0, -4).midbottom,
        )

        id_text = Element(
            "text",
            {
                "x": idx_str,
                "y": idy_str,
                "text-anchor": "middle",
                "class": "id_text",
            },
        )

        id_text.text = str(self.id)

        node_g.append(id_text)

        ### node outline

        node_g.append(
            Element(
                "rect",
                {
                    "x": str(x),
                    "y": str(y),
                    "width": str(width),
                    "height": str(height),
                    "rx": CORNER_RADIUS_X_STR,
                    "ry": CORNER_RADIUS_Y_STR,
                    "class": "outline",
                },
            )
        )

        ###
        self.mode_dependent_elements_svg_repr(node_g)

        ### node's title

        tx_str, ty_str = map(
            str,
            title_rect.move(0, -3).midbottom,
        )

        title = Element(
            "text",
            {
                "x": tx_str,
                "y": ty_str,
                "text-anchor": "middle",
                "class": "title",
            },
        )

        title.text = self.title_text

        node_g.append(title)

        ###
        return node_g

    def expanded_elements_svg_repr(self, node_g):

        ### buttons

        ##

        path_rect = self.sigmode_toggle_button.rect.inflate(-2, -2).move(2, 0)

        path_directives = (
            f"M{path_rect.centerx} {path_rect.bottom}"
            f" L{path_rect.left} {path_rect.top}"
            f" L{path_rect.right} {path_rect.top}"
            " Z"
        )


        node_g.append(
            Element("path", {"d": path_directives, "class": "sigmode_toggle_button"})
        )

        ##

        for button in self.placeholder_add_buttons:

            button_rect = button.rect.inflate(-2, -2)

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

        for button in self.visible_remove_widget_buttons:

            button_rect = button.rect.inflate(-2, -2)

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

        for button in self.subparam_up_buttons:

            button_bg_rect = button.rect.inflate(-2, -2)

            node_g.append(
                Element(
                    "rect",
                    {
                        "x": str(button_bg_rect.x),
                        "y": str(button_bg_rect.y),
                        "width": str(button_bg_rect.width),
                        "height": str(button_bg_rect.height),
                        "class": "subparam_move_button",
                    },
                )
            )

            path_rect = button.rect.inflate(-4, -4)

            path_directives = (
                f"M{path_rect.centerx} {path_rect.top}"
                f" L{path_rect.left} {path_rect.bottom}"
                f" L{path_rect.right} {path_rect.bottom}"
                " Z"
            )

            node_g.append(
                Element("path", {"d": path_directives, "class": "subparam_move_button"})
            )

        for button in self.subparam_down_buttons:

            button_bg_rect = button.rect.inflate(-2, -2)

            node_g.append(
                Element(
                    "rect",
                    {
                        "x": str(button_bg_rect.x),
                        "y": str(button_bg_rect.y),
                        "width": str(button_bg_rect.width),
                        "height": str(button_bg_rect.height),
                        "class": "subparam_move_button",
                    },
                )
            )

            path_rect = button.rect.inflate(-4, -4)

            path_directives = (
                f"M{path_rect.centerx} {path_rect.bottom}"
                f" L{path_rect.left} {path_rect.top}"
                f" L{path_rect.right} {path_rect.top}"
                " Z"
            )

            node_g.append(
                Element("path", {"d": path_directives, "class": "subparam_move_button"})
            )

        ### input/output

        var_kind_map = self.var_kind_map

        ## input sockets

        node_g.extend([socket.svg_repr() for socket in self.input_sockets])

        ## extra references for next blocks

        placeholder_socket_live_map = self.placeholder_socket_live_map

        widget_live_flmap = self.widget_live_flmap

        ## parameter names

        for param_name, value in self.input_socket_live_flmap.items():

            ## variable parameter

            if isinstance(value, dict):

                socket = (
                    value[0] if value else (placeholder_socket_live_map[param_name])
                )

                (
                    text_x_str,
                    text_y_str,
                ) = map(str, socket.rect.move(3, -5).topright)

                text = (
                    f"*{param_name}"
                    if var_kind_map[param_name] == "var_pos"
                    else f"**{param_name}"
                )

            ## regular parameter

            else:

                text = param_name

                text_x_str = str(value.rect.right + 3)

                text_y_str = str(
                    value.rect.top - 5
                    if (
                        param_name in widget_live_flmap
                        and widget_live_flmap[param_name] in self.visible_widgets
                    )
                    else value.rect.centery + 4
                )

            text_element = Element(
                "text",
                {
                    "x": text_x_str,
                    "y": text_y_str,
                    "text-anchor": "start",
                    "class": "label",
                },
            )

            text_element.text = text

            node_g.append(text_element)

        ## unpacking icons and subparam keyword widgets

        ##

        key_hole_class_name = (
            "commented_out_subparam_key_hole"
            if self.data.get("commented_out", False)
            else "normal_subparam_key_hole"
        )

        keyword_variable_objs = [*self.live_keyword_entries]

        for param_name, kind in var_kind_map.items():

            if kind == "var_pos":

                for obj in self.subparam_unpacking_icon_flmap[param_name].values():

                    UNPACKING_RECTS_MANAGER.topleft = obj.rect.topleft

                    node_g.append(get_unpacking_icon_group())

            elif kind == "var_key":

                keyword_variable_objs.extend(
                    self.subparam_unpacking_icon_flmap[param_name].values()
                )

        for obj in keyword_variable_objs:

            (
                path_x,
                path_y,
            ) = obj.rect.move(-6, 5).topleft

            path_directives = (
                f"M{path_x} {path_y}"
                " q0 -5 -5 -5"
                " q-5 0 -5 5"
                " q0 5 5 5"
                " l3 0"
                " l0 3"
                " l3 0"
                " l0 3"
                " l3 0"
                " l0 -3"
                " Z"
            )

            path_element = Element(
                "path",
                {
                    "d": path_directives,
                    "class": "subparam_key",
                },
            )

            node_g.append(path_element)

            node_g.append(
                Element(
                    "circle",
                    {
                        "cx": str(path_x - 5),
                        "cy": str(path_y),
                        "r": "2",
                        "class": key_hole_class_name,
                    },
                )
            )

            ##

            try:
                obj.get

            except AttributeError:

                ##

                UNPACKING_RECTS_MANAGER.topleft = obj.rect.topleft

                node_g.append(get_unpacking_icon_group())

                ##

                UNPACKING_RECTS_MANAGER.topleft = UNPACKING_RECTS_MANAGER.move(
                    3, 0
                ).topright

                node_g.append(get_unpacking_icon_group())

            else:
                node_g.append(obj.svg_repr())

        ## placeholder

        node_g.extend(
            [socket.svg_repr() for socket in placeholder_socket_live_map.values()]
        )

        ### widgets
        node_g.extend([widget.svg_repr() for widget in self.visible_widgets])

        ## output

        for output_name, socket in self.output_socket_live_map.items():

            node_g.append(socket.svg_repr())

            cx, cy = socket.rect.center

            output_label = Element(
                "text",
                {
                    "x": str(cx - 10),
                    "y": str(cy + 4),
                    "text-anchor": "end",
                    "class": "label",
                },
            )

            output_label.text = output_name
            node_g.append(output_label)

    def collapsed_elements_svg_repr(self, node_g):

        ### signature mode button

        path_rect = self.sigmode_toggle_button.rect.inflate(-2, -2).move(2, 0)

        path_directives = (
            f"M{path_rect.left} {path_rect.top}"
            f" L{path_rect.right} {path_rect.centery}"
            f" L{path_rect.left} {path_rect.bottom}"
            " Z"
        )

        node_g.append(
            Element("path", {"d": path_directives, "class": "sigmode_toggle_button"})
        )

        ### input/output

        var_kind_map = self.var_kind_map

        vis = self.visible_input_sockets

        ## input sockets
        node_g.extend([socket.svg_repr() for socket in vis])

        ## parameter names

        for param_name, value in self.input_socket_live_flmap.items():

            ## variable parameter

            if isinstance(value, dict):

                subparam_sockets_dict = value

                if not subparam_sockets_dict:
                    continue

                else:

                    for socket in subparam_sockets_dict.values():
                        if socket in vis:
                            break
                    else:
                        continue

                (
                    text_x_str,
                    text_y_str,
                ) = map(str, socket.rect.move(3, -5).topright)

                text = (
                    f"*{param_name}"
                    if var_kind_map[param_name] == "var_pos"
                    else f"**{param_name}"
                )

            ## regular parameter

            else:

                socket = value

                if socket not in vis:
                    continue

                text = param_name

                (
                    text_x_str,
                    text_y_str,
                ) = map(str, socket.rect.move(3, 4).midright)

            text_element = Element(
                "text",
                {
                    "x": text_x_str,
                    "y": text_y_str,
                    "text-anchor": "start",
                    "class": "label",
                },
            )

            text_element.text = text

            node_g.append(text_element)

        ## unpacking icons and subparam keyword widgets

        ##

        key_hole_class_name = (
            "commented_out_subparam_key_hole"
            if self.data.get("commented_out", False)
            else "normal_subparam_key_hole"
        )

        vws = self.visible_widgets
        vuirs = self.visible_unpacking_icon_rects

        visible_keyword_objects = [
            entry for entry in self.live_keyword_entries
            if entry in vws
        ]

        for param_name, kind in var_kind_map.items():

            if kind == "var_pos":

                for obj in self.subparam_unpacking_icon_flmap[param_name].values():

                    if obj.rect in vuirs:
                        UNPACKING_RECTS_MANAGER.topleft = obj.rect.topleft
                        node_g.append(get_unpacking_icon_group())

            elif kind == "var_key":

                visible_keyword_objects.extend(
                    obj
                    for obj in self.subparam_unpacking_icon_flmap[param_name].values()
                    if obj.rect in vuirs
                )

        ###

        for obj in visible_keyword_objects:

            (
                path_x,
                path_y,
            ) = obj.rect.move(-6, 5).topleft

            path_directives = (
                f"M{path_x} {path_y}"
                " q0 -5 -5 -5"
                " q-5 0 -5 5"
                " q0 5 5 5"
                " l3 0"
                " l0 3"
                " l3 0"
                " l0 3"
                " l3 0"
                " l0 -3"
                " Z"
            )

            path_element = Element(
                "path",
                {
                    "d": path_directives,
                    "class": "subparam_key",
                },
            )

            node_g.append(path_element)

            node_g.append(
                Element(
                    "circle",
                    {
                        "cx": str(path_x - 5),
                        "cy": str(path_y),
                        "r": "2",
                        "class": key_hole_class_name,
                    },
                )
            )

            ##

            try:
                obj.get

            except AttributeError:

                ##

                UNPACKING_RECTS_MANAGER.topleft = obj.rect.topleft

                node_g.append(get_unpacking_icon_group())

                ##

                UNPACKING_RECTS_MANAGER.topleft = UNPACKING_RECTS_MANAGER.move(
                    3, 0
                ).topright

                node_g.append(get_unpacking_icon_group())

            else:
                node_g.append(obj.svg_repr())

        ### keyword entry widgets (if any)
        #node_g.extend([widget.svg_repr() for widget in self.visible_widgets])

        ## output

        vos = self.visible_output_sockets

        for output_name, socket in self.output_socket_live_map.items():

            if socket not in vos:
                continue

            node_g.append(socket.svg_repr())

            cx, cy = socket.rect.center

            output_label = Element(
                "text",
                {
                    "x": str(cx - 10),
                    "y": str(cy + 4),
                    "text-anchor": "end",
                    "class": "label",
                },
            )

            output_label.text = output_name
            node_g.append(output_label)

    def callable_elements_svg_repr(self, node_g):
        node_g.append(self.output_sockets[0].svg_repr())

    def get_color_identifier(self):
        """Return string to identify specific node color.

        This method is meant to be overridden by
        subclasses in order to identify the specific color
        used.
        """
        return str(self.color_index)

    ### methods to draw node in another surface for .png export feature

    def expanded_draw_on_surf(self, surf):
        """Draw expanded signature mode elements on given surf."""
        ###
        blit_on_surf = surf.blit

        ### draw background and text elements, then
        ### widgets, buttons and sockets

        for obj in chain(
            self.background_and_text_elements,
            (self.sigmode_toggle_button,),
            self.visible_widgets,
            self.live_keyword_entries,
            self.unpacking_icons,
            self.placeholder_add_buttons,
            self.visible_remove_widget_buttons,
            self.subparam_up_buttons,
            self.subparam_down_buttons,
            self.input_sockets,
            self.output_sockets,
            self.placeholder_sockets,
        ):

            blit_on_surf(obj.image, obj.rect)

    def collapsed_draw_on_surf(self, surf):
        """Draw collapsed signature mode elements on given surf."""
        ###
        blit_on_surf = surf.blit

        ### draw background and text elements, then
        ### visible objects

        for obj in chain(

            self.background_and_text_elements,
            (self.sigmode_toggle_button,),

            (
                unpacking_icon
                for unpacking_icon in self.unpacking_icons
                if unpacking_icon.rect in self.visible_unpacking_icon_rects
            ),

            self.visible_widgets,
            self.visible_input_sockets,
            self.visible_output_sockets,
        ):

            blit_on_surf(obj.image, obj.rect)

    def callable_draw_on_surf(self, surf):
        """Draw callable mode elements on given surf."""
        ###
        blit_on_surf = surf.blit

        ### draw background and text elements, then
        ### output socket

        for obj in chain(
            self.background_and_text_elements,
            self.output_sockets,
        ):

            blit_on_surf(obj.image, obj.rect)
