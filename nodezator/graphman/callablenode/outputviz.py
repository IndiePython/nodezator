"""Facility with factory function for creating viewer objects."""

### standard library imports

from pathlib import Path

from functools import partial

from xml.etree.ElementTree import Element


### local imports

from ...config import APP_REFS

from ...appinfo import (
    VIEWER_NODE_RELATED_VAR_NAMES,
    VISUAL_FROM_OUTPUT_VAR_NAME,
    LOOP_FROM_OUTPUT_VAR_NAME,
    LOOP_INDICATIVE_VAR_NAMES,
    CUSTOM_VIEWER_LOOP_VAR_NAME,
    VISUAL_FROM_BACKDOOR_VAR_NAMES,
    OUTPUT_INSPECTING_VAR_NAMES,
)

from ...dialog import create_and_show_dialog

from ...ourstdlibs.behaviour import get_oblivious_callable

from ...ourstdlibs.path import get_new_filename

from ...our3rdlibs.behaviour import indicate_unsaved

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...textman.render import render_text

from ...surfsman.render import (
    render_rect,
    render_separator,
    combine_surfaces,
)

from ...surfsman.draw import draw_border, draw_depth_finish

from ...surfsman.cache import CHECKERED_SURF_MAP

from ...surfsman.svgexport import get_not_found_surface_svg_repr

from ...widget.checkbutton import CheckButton

from ...colorsman.colors import (
    PREVIEW_PANEL_CHECKER_A,
    PREVIEW_PANEL_CHECKER_B,
    NODE_LABELS,
    NODE_BODY_BG,
)

from .constants import FONT_HEIGHT

from .surfs import (
    RELOAD_PREVIEW_BUTTON_SURF,
    PREVIEW_PANEL_NOT_FOUND_SURFACE,
)



class OutputVisualization:

    def check_preview_objects(self):

        ###
        node_defining_object = self.node_defining_object

        ###

        viewer_related_var_names = (
            set(node_defining_object)
            .intersection(VIEWER_NODE_RELATED_VAR_NAMES)
        )

        if not viewer_related_var_names:
            return

        ### if callable to grab full surface/visual from node output
        ### is specified, a callable to grab the preview surface/visual
        ### must be provided as well

        if (
            (LOOP_FROM_OUTPUT_VAR_NAME in viewer_related_var_names)
            and not (VISUAL_FROM_OUTPUT_VAR_NAME in viewer_related_var_names)
        ):
            return

        ### if a custom visualization loop is provided, must ensure loop data
        ### will be provided by either of the available methods

        if CUSTOM_VIEWER_LOOP_VAR_NAME in viewer_related_var_names:

            if not any(
                var_name in viewer_related_var_names
                for var_name in LOOP_INDICATIVE_VAR_NAMES
            ):
                return

        ### methods for grabbing visuals must not be mixed, that is, we
        ### either grab visuals for the viewer node from the backdoor
        ### or from the node's output

        if (

            any(
                var_name in viewer_related_var_names
                for var_name in VISUAL_FROM_BACKDOOR_VAR_NAMES
            )

            and any(
                var_name in viewer_related_var_names
                for var_name in OUTPUT_INSPECTING_VAR_NAMES
            )
        ):

            return

        ### store viewer related functions

        for var_name in viewer_related_var_names:
            setattr(self, var_name, node_defining_object[var_name])

        ### create preview objects

        self.create_preview_toolbar()
        self.create_preview_panel()

    def show_preview_objects(self):
        """Store previewer objects so they become visible."""
        APP_REFS.gm.preview_toolbars.append(self.preview_toolbar)
        APP_REFS.gm.preview_panels.append(self.preview_panel)

    def hide_preview_objects(self):
        APP_REFS.gm.preview_toolbars.remove(self.preview_toolbar)
        APP_REFS.gm.preview_panels.remove(self.preview_panel)

    def create_preview_toolbar(self):

        reload_label_surf = (
            render_text(
                'Reload',
                font_height=FONT_HEIGHT,
                foreground_color=NODE_LABELS,
                background_color=NODE_BODY_BG,
            )
        )


        reload_button = Object2D.from_surface(
            combine_surfaces(
                [reload_label_surf, RELOAD_PREVIEW_BUTTON_SURF],
                retrieve_pos_from='midright',
                assign_pos_to='midleft',
                offset_pos_by=(2, 0),
                padding = 2,
                background_color=NODE_BODY_BG,
            )
        )

        draw_depth_finish(reload_button.image)

        ###

        reload_button.on_mouse_release = (
            get_oblivious_callable(
                partial(APP_REFS.gm.execute_node_after_upstream_ones, self)
            )
        )

        ###

        has_loop_data = any(
            hasattr(self, var_name)
            for var_name in LOOP_INDICATIVE_VAR_NAMES
        )

        ###

        if has_loop_data:

            toolbar = List2D()

            ###

            separator = Object2D.from_surface(
                render_separator(
                    length = reload_button.rect.height - 4,
                    is_horizontal = False,
                    padding=0,
                    thickness=12,
                    background_color = NODE_BODY_BG,
                )
            )

            ###

            loop_toggle_label = Object2D.from_surface(
                render_text(
                    'Loop on execution',
                    font_height=FONT_HEIGHT,
                    padding=2,
                    foreground_color=NODE_LABELS,
                    background_color=NODE_BODY_BG,
                )
            )

            check_button = toolbar.check_button = (
                CheckButton(
                    value=self.data.get('loop_on_execution', False),
                    command = self.update_loop_on_execution_flag,
                )
            )

            toolbar.extend((
                reload_button,
                separator,
                loop_toggle_label,
                check_button,
            ))

            toolbar.rect.snap_rects_ip('midright', 'midleft', (2, 0))

            toolbar_bg = Object2D.from_surface(
                render_rect(*toolbar.rect.inflate(8, 8).size, NODE_BODY_BG)
            )

            draw_border(toolbar_bg.image, thickness=2)

            toolbar.rect.center = toolbar_bg.rect.center

            ###
            toolbar_bg.image.blit(separator.image, separator.rect)
            toolbar.remove(separator)

            buttons = list(toolbar)

            toolbar.insert(0, toolbar_bg)

            ###
            loop_toggle_label.on_mouse_release = check_button.toggle_value
            check_button.on_mouse_release = check_button.toggle_value
            ###

            def on_mouse_release(event):

                mouse_pos = event.pos

                for obj in buttons:

                    if obj.rect.collidepoint(mouse_pos):
                        break

                else: return

                obj.on_mouse_release(event)

            toolbar.on_mouse_release = on_mouse_release

        ###
        else:
            toolbar = reload_button

        ###
        self.preview_toolbar = toolbar

        ###
        self.preview_toolbar.node = self

        self.preview_toolbar.draw_on_surf = partial(
            draw_toolbar_on_surf, self.preview_toolbar
        )

        self.preview_toolbar.svg_repr = partial(
            preview_toolbar_svg_repr, self.preview_toolbar
        )


    def create_preview_panel(self):

        self.preview_panel = Object2D.from_surface(PREVIEW_PANEL_NOT_FOUND_SURFACE)

        ###

        if any(

            ## item
            hasattr(self, var_name)

            ## source
            for var_name in LOOP_INDICATIVE_VAR_NAMES

        ):

            loop_entering_command = (

                ##
                self.enter_custom_loop
                if hasattr(self, CUSTOM_VIEWER_LOOP_VAR_NAME)

                ##
                else self.enter_loop

            )

            on_mouse_release = (
                get_oblivious_callable(loop_entering_command)
            )

        else:
            def on_mouse_release(event):
                pass

        self.preview_panel.on_mouse_release = on_mouse_release

        ###

        self.preview_panel.node = self

        self.preview_panel.draw_on_surf = partial(
            draw_panel_on_surf, self.preview_panel
        )

        self.preview_panel.svg_repr = partial(
            preview_panel_svg_repr, self.preview_panel
        )

    def update_loop_on_execution_flag(self):

        ###

        self.data['loop_on_execution'] = (
            self.preview_toolbar.check_button.get()
        )

        ###
        indicate_unsaved()

    def set_visual(self, visual):
        """Store visual in preview panel and update rect's size

        Parameters
        ==========
        visual (pygame.Surface)
            A surface to use in the preview panel.

            In the future maybe it could receive other kinds of data
            that could be turned into a surface, like text.
        """
        ### get visual size
        size = visual.get_size()

        ### get a new surface which is a copy of a checkered surf
        ### with the same size as the visual

        new_surf = CHECKERED_SURF_MAP[(
            size,  # surf size
            PREVIEW_PANEL_CHECKER_A, # checker color a
            PREVIEW_PANEL_CHECKER_B, # checker color b
            10,    # checker rect width
            10,    # checker rect height
        )].copy()

        ### blit visual over new surface
        new_surf.blit(visual, (0, 0))

        ### update preview panel's image and rect's size
        ### taking new surface into account

        self.preview_panel.image = new_surf
        self.preview_panel.rect.size = size

    def enter_custom_loop(self):

        if hasattr(self, 'loop_data'):
            self.enter_viewer_loop(self.loop_data)

        else:

            create_and_show_dialog(
                "Node needs to be executed at least once"
                " to be able to display data in custom loop."
            )

    def enter_loop(self):

        if hasattr(self, 'loop_data'):
            raise NotImplemented

        else:

            create_and_show_dialog(
                "Node needs to be executed at least once"
                " to be able to display visual in loop."
            )



### png export utilities

def draw_toolbar_on_surf(toolbar, surf):

    if isinstance(toolbar, Object2D):
        surf.blit(toolbar.image, toolbar.rect)

    else:
        for obj in toolbar:
            surf.blit(obj.image, obj.rect)

def draw_panel_on_surf(panel, surf):
    surf.blit(panel.image, panel.rect)


### svg export utilities

PREVIEW_OBJECTS_CSS = f"""

.preview_toolbar_bg {{
  fill         : rgb{NODE_BODY_BG};
  stroke       : black;
  stroke-width : 2;
}}

.preview_toolbar_reload_button {{
  fill         : rgb{NODE_BODY_BG};
  stroke       : white;
  stroke-width : 1;
}}

.preview_toolbar_text
{{
  font: bold {FONT_HEIGHT-4}px sans-serif;
  fill : rgb{NODE_LABELS};
}}


"""

RELOAD_ICON_PATH_DIRECTIVES = (
    (
        " m 2  1"
        " m 0  6"
        " l 0 -3"
        " q 0 -3 3 -3"
        " l 8  0"
        " q 3  0 3 3"
        " l 0  4"
        " l 3  0"
        " l-5  4"
        " l-5 -4"
        " l 3  0"
        " l 0 -4"
        " l-6  0"
        " l 0  3"
        " Z"
    ),
    (
        " m 0   1"
        " m 0  11"
        " l 5  -4"
        " l 5   4"
        " l-3   0"
        " l 0   4"
        " l 6   0"
        " l 0  -3"
        " l 4   0"
        " l 0   3"
        " q 0   3  -3  3"
        " l-8   0"
        " q-3   0  -3 -3"
        " l 0  -4"
        " Z"
    )
)

RELOAD_ICON_STYLE = (
"fill:rgb(30, 130, 70);stroke:black;stroke-width:2;stroke-linejoin:round;"
)

def preview_toolbar_svg_repr(toolbar):

    rect = toolbar.rect

    g = Element('g')

    ###
    is_single_object = isinstance(toolbar, Object2D)

    ###

    g.append(
        Element(
            "rect",
            {

                **{
                    attr_name: str(getattr(rect, attr_name))
                    for attr_name in ("x", "y", "width", "height")
                },

                "class": (
                    "preview_toolbar_reload_button"
                    if is_single_object
                    else "preview_toolbar_bg"
                )
            },
        ),
    )

    ###

    if not is_single_object:

        g.append(
            Element(
                "rect",
                {
                    **{
                        attr_name: str(getattr(toolbar[1].rect, attr_name))
                        for attr_name in ("x", "y", "width", "height")
                    },
                    "class": "preview_toolbar_reload_button"
                },
            ),
        )

    ###

    reload_button_rect = (
        rect
        if is_single_object
        else toolbar[1].rect
    )

    ###

    x, y = map(str, reload_button_rect.move(0, -8).bottomleft)

    reload_text = Element(
        "text",
        {
            "x": x,
            "y": y,
            "text-anchor": "start",
            "class": "preview_toolbar_text",
        },
    )

    reload_text.text = 'Reload'
    g.append(reload_text)


    ###

    x, y = reload_button_rect.move(-20, 1).topright

    first_directive = f"M {x} {y} "

    for directives in RELOAD_ICON_PATH_DIRECTIVES:

        path_directives = first_directive + directives

        g.append(
            Element(
                "path",
                {
                    "d": path_directives,
                    "style": RELOAD_ICON_STYLE,
                },
            )
        )

    ###

    if not is_single_object:

        ### separator

        rect_copy = toolbar[1].rect.move(4, 0)

        x1, y1 = map(str, rect_copy.topright)
        x2, y2 = map(str, rect_copy.bottomright)

        g.append(
            Element(
                "line",
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "style":"stroke:white;stroke-width:1",
                },
            )
        )

        ### "loop on execution" text

        x, y = map(str, toolbar[2].rect.move(-8, -8).bottomleft)

        loop_on_execution_text = Element(
            "text",
            {
                "x": x,
                "y": y,
                "text-anchor": "start",
                "class": "preview_toolbar_text",
            },
        )

        loop_on_execution_text.text = 'Loop on execution'
        g.append(loop_on_execution_text)

        ### check button
        g.append(toolbar[3].svg_repr())

    ###
    return g

def preview_panel_svg_repr(panel):

    rect = panel.rect
    ###

    if panel.image is PREVIEW_PANEL_NOT_FOUND_SURFACE:
        return get_not_found_surface_svg_repr(rect)

    ###
    g = Element("g")

    try:

        (
            preview_surf_map,
            preview_name_map,
            parent_dirname,
        ) = APP_REFS.preview_handling_kit

    except AttributeError:

        ##

        g.append(
            Element(
                "rect",
                {
                    **{
                        attr_name: str(getattr(rect, attr_name))
                        for attr_name in ("x", "y", "width", "height")
                    },
                    "style": "fill: rgb(30, 130, 70);",
                },
            ),
        )

        ### big mountain

        big_mountain_rect = rect.copy()
        big_mountain_rect.width *= .7
        big_mountain_rect.height *= .7

        big_mountain_rect.bottom = rect.bottom

        bmr = big_mountain_rect

        directives = f"M{bmr.x} {bmr.y} q{(bmr.w//4)*3} 0 {bmr.w} {bmr.h} l-{bmr.w} 0 Z"

        g.append(
            Element(
                "path",
                {
                    "d": directives,
                    "style": "fill: white;",
                }
            )
        )

        ### small mountain

        small_mountain_rect = rect.copy()
        small_mountain_rect.width *= .3
        small_mountain_rect.height *= .4

        small_mountain_rect.bottomright = rect.bottomright

        smr = small_mountain_rect

        directives = f"M{smr.right} {smr.y} q-{(smr.w//4)*3} 0 -{smr.w} {smr.h} l{smr.w} 0 Z"

        g.append(
            Element(
                "path",
                {
                    "d": directives,
                    "style": "fill: white;",
                }
            )
        )

        ### small white sun

        d1 = round(rect.width * 1/8)
        d2 = round(rect.height * 1/8)

        d = min(d1, d2)

        small_sun_rect = rect.copy()

        small_sun_rect.size = (d*3, d*3)

        small_sun_rect.topright = rect.move(-d*2, d).topright

        ssr = small_sun_rect

        g.append(
            Element(
                "circle",
                {

                    "cx":f"{ssr.centerx}",
                    "cy":f"{ssr.centery}",
                    "r":f"{ssr.w//2}",
                    "style": "fill: white;",
                }
            )
        )


        return g

    else:

        preview_surf_map[panel] = panel.image

        name = f'_node_id_{panel.node.id}_preview.png'

        if name in preview_name_map.values():

            for key, value in preview_name_map.items():

                if value == name and key != panel:

                    ## change value of name variable
                    ## so the name is different

                    name = get_new_filename(name, preview_name_map.values())

                    break

        preview_name_map[panel] = name

        href = str(Path(parent_dirname) / name)

        image_element = (
            Element(
                "image",
                {
                    "href": href,
                    "xlink:href": href,
                    **{
                        attr_name: str(getattr(rect, attr_name))
                        for attr_name in ("x", "y", "width", "height")
                    },
                },
            )
        )

        return image_element

