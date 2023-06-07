"""Facility with factory function for creating viewer objects."""

### standard library import
from functools import partial


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

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...textman.render import render_text

from ...surfsman.render import (
    render_rect,
    render_separator,
    combine_surfaces,
)

from ...surfsman.draw import (
    draw_border,
    draw_not_found_icon,
    draw_depth_finish,
)

from ...surfsman.cache import CHECKERED_SURF_MAP

from ...widget.checkbutton import CheckButton

from ...colorsman.colors import (
    PREVIEW_PANEL_CHECKER_A,
    PREVIEW_PANEL_CHECKER_B,
    NODE_LABELS,
    NODE_BODY_BG,
)

from .constants import FONT_HEIGHT

from .surfs import RELOAD_PREVIEW_BUTTON_SURF



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

            check_button = toolbar.check_button = CheckButton(value=False)

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


    def create_preview_panel(self):

        self.preview_panel = Object2D.from_surface(render_rect(256, 256, (0, 0, 0)))
        draw_not_found_icon(self.preview_panel.image, (235, 0, 0))

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
