"""Facility with factory function for creating viewer objects."""

### standard library imports

from pathlib import Path

from functools import partial

from xml.etree.ElementTree import Element


### third-party import
from pygame import Surface


### local imports

from ...config import APP_REFS

from ...appinfo import (
    VIEWER_NODE_RELATED_VAR_NAMES,
    SIDEVIZ_FROM_OUTPUT_VAR_NAME,
    LOOPVIZ_FROM_OUTPUT_VAR_NAME,
    LOOP_INDICATIVE_VAR_NAMES,
    CUSTOM_VIEWER_LOOP_VAR_NAME,
    BACKDOOR_INDICATIVE_VAR_NAMES,
    OUTPUT_INSPECTING_VAR_NAMES,
)

from ...logman.main import get_new_logger

from ...dialog import create_and_show_dialog

from ...ourstdlibs.behaviour import get_oblivious_callable
from ...ourstdlibs.path import get_new_filename

from ...our3rdlibs.behaviour import indicate_unsaved
from ...our3rdlibs.userlogger import USER_LOGGER

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...textman.render import render_text
from ...textman.viewer.main import view_text
from ...textman.text import get_normal_lines, get_highlighted_lines

from ...syntaxman.utils import get_ready_theme
from ...syntaxman.exception import SyntaxMappingError

from ...surfsman.render import (
    render_rect,
    render_separator,
    combine_surfaces,
)

from ...surfsman.draw import draw_border, draw_depth_finish

from ...surfsman.cache import CHECKERED_SURF_MAP, cache_screen_state

from ...surfsman.viewer.main import view_surface

from ...surfsman.svgexport import get_not_found_surface_svg_repr

from ...widget.checkbutton import CheckButton

from ...colorsman.colors import (
    PREVIEW_PANEL_CHECKER_A,
    PREVIEW_PANEL_CHECKER_B,
    NODE_LABELS,
    NODE_BODY_BG,
)

from .constants import (
    FONT_HEIGHT,
    SIDEVIZ_TEXT_SETTINGS,
    SIDEVIZ_MONOSPACED_TEXT_SETTINGS,
    SIDEVIZ_PYTHON_SOURCE_SETTINGS,
)

from .surfs import (
    RELOAD_PREVIEW_BUTTON_SURF,
    PREVIEW_PANEL_NOT_FOUND_SURFACE,
)



### create logger for module
logger = get_new_logger(__name__)


### create theme map to render syntax-highlighted python source
THEME_MAP = get_ready_theme("python", SIDEVIZ_PYTHON_SOURCE_SETTINGS)



### class definition

class OutputVisualization:

    def check_preview_objects(self):

        ### gather viewer related var names from node defining object
        ### namespace

        node_defining_object = self.node_defining_object

        viewer_related_var_names = (
            set(node_defining_object)
            .intersection(VIEWER_NODE_RELATED_VAR_NAMES)
        )

        ### gather viewer related var names from preexistent attributes

        preexistent_attr_names = {
            name
            for name in OUTPUT_INSPECTING_VAR_NAMES
            if hasattr(self, name)
        }

        ### check preexistent attributes

        if (

            ## sideviz is present alone

            (
                (SIDEVIZ_FROM_OUTPUT_VAR_NAME in preexistent_attr_names)
                and (LOOPVIZ_FROM_OUTPUT_VAR_NAME not in preexistent_attr_names)
            )

            ## both sideviz and loop viz are present
            or set(OUTPUT_INSPECTING_VAR_NAMES) == preexistent_attr_names

        ):

            ## since we now know that there are preexistent attributes
            ## related to providing visualization data, there must not
            ## be any viewer related var names in the node defining object,
            ## except if it is a callable for entering a custom visualization
            ## loop;
            ##

            n = len(viewer_related_var_names)

            if (
                (n == 1)
                and (CUSTOM_VIEWER_LOOP_VAR_NAME not in viewer_related_var_names)
            ):
                return

            elif n > 1:
                return

            ## create preview objects and exit method by returning earlier

            self.create_preview_toolbar()
            self.create_preview_panel()

            return

        elif (

            ## loopviz alone is not allowed, so return earlier

            (LOOPVIZ_FROM_OUTPUT_VAR_NAME in preexistent_attr_names)
            and (SIDEVIZ_FROM_OUTPUT_VAR_NAME not in preexistent_attr_names)

        ):
            return


        ### if by this point there are no viewer related var names from the
        ### node defining object, return earlier

        if not viewer_related_var_names:
            return

        ## if callable to grab full surface/visual from node output
        ## is specified, a callable to grab the preview surface/visual
        ## must be provided as well

        if (
            (LOOPVIZ_FROM_OUTPUT_VAR_NAME in viewer_related_var_names)
            and not (SIDEVIZ_FROM_OUTPUT_VAR_NAME in viewer_related_var_names)
        ):
            return

        ## if a custom visualization loop is provided, must ensure loop data
        ## will be provided by either of the available methods

        if CUSTOM_VIEWER_LOOP_VAR_NAME in viewer_related_var_names:

            if not any(
                var_name in viewer_related_var_names
                for var_name in LOOP_INDICATIVE_VAR_NAMES
            ):
                return

        ## methods for grabbing visuals must not be mixed, that is, we
        ## either grab visuals for the viewer node from the backdoor
        ## or from the node's output

        if (

            any(
                var_name in viewer_related_var_names
                for var_name in BACKDOOR_INDICATIVE_VAR_NAMES
            )

            and any(
                var_name in viewer_related_var_names
                for var_name in OUTPUT_INSPECTING_VAR_NAMES
            )
        ):

            return

        ## store viewer related functions

        for var_name in viewer_related_var_names:
            setattr(self, var_name, node_defining_object[var_name])

        ## create preview objects

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

            self.loop_entering_command = (

                ##
                self.enter_custom_loop
                if hasattr(self, CUSTOM_VIEWER_LOOP_VAR_NAME)

                ##
                else self.enter_loop

            )

            on_mouse_release = (
                get_oblivious_callable(self.loop_entering_command)
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

    def set_visual(self, visual_data):
        """Store visual in preview panel and update rect's size

        Parameters
        ==========
        visual_data (string, pygame.Surface or dict)
            Data used for displaying visual in the preview panel.
        """

        if isinstance(visual_data, Surface):

            ### get a new surface which is a copy of a checkered surf
            ### with the same size as the visual

            new_surf = CHECKERED_SURF_MAP[(
                visual_data.get_size(),  # surf size
                PREVIEW_PANEL_CHECKER_A, # checker color a
                PREVIEW_PANEL_CHECKER_B, # checker color b
                10,    # checker rect width
                10,    # checker rect height
            )].copy()

            ### blit visual over new surface
            new_surf.blit(visual_data, (0, 0))

        elif isinstance(visual_data, str):
            new_surf = get_text_surf(visual_data, SIDEVIZ_TEXT_SETTINGS)

        elif isinstance(visual_data, dict):

            try:

                data = visual_data['data']
                hint = visual_data['hint']

            except KeyError:

                raise RuntimeError(
                    "Can't set side visual because"
                    " 'data' and/or 'hint' key can't"
                    " be found"
                )

            else:

                if hint == 'text':
                    new_surf = get_text_surf(data, SIDEVIZ_TEXT_SETTINGS)

                elif hint == 'monospaced_text':
                    new_surf = get_text_surf(data, SIDEVIZ_MONOSPACED_TEXT_SETTINGS)

                elif hint == 'python_source':
                    new_surf = get_python_source_surf(data)

                else:

                    raise RuntimeError(
                        "side visual data 'hint' must be"
                        " 'text' or 'python_source'"
                    )

        else:

            raise RuntimeError(
                "Can't set side visual because type is not supported"
            )

        ### update preview panel's image and rect's size
        ### taking new surface into account

        self.preview_panel.image = new_surf
        self.preview_panel.rect.size = new_surf.get_size()

    def enter_custom_loop(self):

        if hasattr(self, 'loop_data'):

            try:
                self.enter_viewer_loop(self.loop_data)

            except Exception as err:

                ## log traceback

                log_message = (
                    "An error occurred when trying to visualize"
                    " the loop data in the custom visualization loop"
                    f" of {self.title_text} node of id {self.id}."
                )

                logger.exception(log_message)
                USER_LOGGER.exception(log_message)

                ## notify user via dialog

                dialog_messsage = log_message + (
                    " Check user log for details (on the graph/canvas, press"
                    " <Shift+Ctrl+j> or access the \"Help > User log\" option"
                    " on menubar)."
                )

                create_and_show_dialog(dialog_message, level_name='error')

        else:

            create_and_show_dialog(
                (
                    "Node needs to be executed at least once"
                    " to be able to display data in custom loop."
                ),
                level_name='info',
            )

    def enter_loop(self):

        if hasattr(self, 'loop_data'):

            cache_screen_state()

            try:
                loop_data = self.loop_data

                if isinstance(loop_data, Surface):
                    view_surface(loop_data)

                elif isinstance(loop_data, str):

                    view_text(
                        text=loop_data,
                        general_text_settings=SIDEVIZ_TEXT_SETTINGS,
                        show_line_number=True,
                    )

                elif isinstance(loop_data, dict):

                    try:

                        data = loop_data['data']
                        hint = loop_data['hint']

                    except KeyError:

                        create_and_show_dialog(
                            (
                                "Can't display loop data because"
                                " 'data' and/or 'hint' key can't"
                                " be found"
                            ),
                            level_name='error',
                        )

                    else:

                        if hint == 'text':

                            view_text(
                                text=data,
                                general_text_settings=SIDEVIZ_TEXT_SETTINGS,
                                show_line_number=True,
                            )

                        elif hint == 'monospaced_text':

                            view_text(
                                text=data,
                                general_text_settings=SIDEVIZ_MONOSPACED_TEXT_SETTINGS,
                                show_line_number=True,
                            )

                        elif hint == 'python_source':

                            view_text(
                                text=data,
                                syntax_highlighting='python',
                                show_line_number=True,
                            )

                        else:

                            create_and_show_dialog(
                                (
                                    "loop data 'hint' must be "
                                    "'text' or 'python_source'"
                                ),
                                level_name='error',
                            )

                else:

                    create_and_show_dialog(
                        "Can't display loop data because type is not supported",
                        level_name='error',
                    )

            except Exception as err:

                ## log traceback

                log_message = (
                    "An error occurred when trying to visualize loop data."
                )

                logger.exception(log_message)
                USER_LOGGER.exception(log_message)

                ## notify user via dialog

                dialog_messsage = log_message + (
                    " Check user log for details (on the graph/canvas, press"
                    " <Shift+Ctrl+j> or access the \"Help > User log\" option"
                    " on menubar)."
                )

                create_and_show_dialog(dialog_message, level_name='error')

        else:

            create_and_show_dialog(
                (
                    "Node needs to be executed at least once"
                    " to be able to display visual in loop."
                ),
                level_name='info',
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


### utility functions

def get_text_surf(text, text_settings):

    lines = get_normal_lines(text, text_settings)

    ### position text objects representing lines one
    ### below the other
    lines.rect.snap_rects_ip(retrieve_pos_from="bottomleft", assign_pos_to="topleft")

    ### text area

    text_area = lines.rect.copy()
    text_area.width += 10
    text_area.height += 10

    surf = render_rect(*text_area.size, text_settings["background_color"])

    ###

    lines.rect.move_ip(5, 5)

    blit_on_surf = surf.blit

    for line in lines:
        blit_on_surf(line.image, line.rect)

    ###
    draw_border(surf, text_settings["foreground_color"])

    ###
    return surf

def get_python_source_surf(python_source):

    try:

        lines = get_highlighted_lines(
            "python",
            python_source,
            syntax_settings_map=THEME_MAP["text_settings"],
        )

    ## if a syntax mapping error occurs...

    except SyntaxMappingError:
        lines = get_normal_lines(python_source, SIDEVIZ_PYTHON_SOURCE_SETTINGS)

        foreground_color = SIDEVIZ_PYTHON_SOURCE_SETTINGS["foreground_color"]
        background_color = SIDEVIZ_PYTHON_SOURCE_SETTINGS["background_color"]

    ##
    else:
        foreground_color = THEME_MAP["text_settings"]["normal"]["foreground_color"]
        background_color = THEME_MAP["background_color"]


    ### position text objects representing lines one below the other
    lines.rect.snap_rects_ip(retrieve_pos_from="bottomleft", assign_pos_to="topleft")

    ###

    code_area = lines.rect.copy()
    code_area.width += 10
    code_area.height += 10

    surf = render_rect(*code_area.size, background_color)

    lines.rect.move_ip(5, 5)

    blit_on_surf = surf.blit

    for line in lines:
        blit_on_surf(line.image, line.rect)

    ###
    draw_border(surf, foreground_color)
    ###

    return surf
