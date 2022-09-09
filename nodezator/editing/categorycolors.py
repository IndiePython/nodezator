"""Form for node category colors picking."""

### standard library imports

from os import sep

from functools import partial, partialmethod

from itertools import repeat


### third-paraty imports

from pygame import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from pygame.event import get as get_events
from pygame.display import update
from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..appinfo import NODE_CATEGORY_METADATA_FILENAME

from ..translation import TRANSLATION_HOLDER as t

from ..dialog import create_and_show_dialog

from ..pygameconstants import (
    SCREEN,
    SCREEN_RECT,
    blit_on_screen,
)

from ..ourstdlibs.pyl import load_pyl, save_pyl

from ..ourstdlibs.collections.general import CallList

from ..ourstdlibs.behaviour import (
    empty_function,
    get_oblivious_callable,
)

from ..our3rdlibs.button import Button

from ..our3rdlibs.behaviour import set_status_message


from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ..surfsman.draw import draw_border, draw_depth_finish

from ..surfsman.render import render_rect

from ..pointsman2d.create import get_circle_points

from ..loopman.main import LoopHolder

from ..colorsman.colors import (
    CONTRAST_LAYER_COLOR,
    GRAPH_BG,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
    NODE_CATEGORY_COLORS,
)

from ..colorsman.color2d import Color2D

from ..colorsman.picker.main import pick_colors


### constants

TEXT_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": WINDOW_FG,
    "background_color": WINDOW_BG,
}

BUTTON_SETTINGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "depth_finish_thickness": 1,
    "foreground_color": BUTTON_FG,
    "background_color": BUTTON_BG,
}


### class definition


class CategoryColorsPicking(Object2D, LoopHolder):
    """Form for choosing category colors."""

    def __init__(self):
        """Setup form objects."""
        ### build widgets
        self.build_form_widgets()

        ### assign rect and surf for background

        self.widgets.rect.center = SCREEN_RECT.center

        self.rect = self.widgets.rect.inflate(20, 20)
        self.image = render_rect(*self.rect.size, WINDOW_BG)

        draw_border(self.image)

        ### store a semitransparent object

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=render_rect(*self.rect.size, (*CONTRAST_LAYER_COLOR, 130)),
            coordinates_name="center",
            coordinates_value=SCREEN_RECT.center,
        )

        ### assign behaviour
        self.update = empty_function

        ### create/restart tracking variable
        self.hovered_rect = None

        ### center form and append centering method as
        ### a window resize setup, if not appended already

        self.center_category_colors_form()

        if self.center_category_colors_form not in (APP_REFS.window_resize_setups):

            APP_REFS.window_resize_setups.append(self.center_category_colors_form)

    def center_category_colors_form(self):

        self.widgets.rect.center = self.rect.center = SCREEN_RECT.center

    def build_form_widgets(self):
        """Build widgets to hold settings for edition."""
        ### create list to hold widgets
        widgets = self.widgets = List2D()

        ### instantiate a caption for the form

        caption_label = Object2D.from_surface(
            surface=(
                render_text(
                    text=(t.editing.category_colors_form.caption),
                    border_thickness=2,
                    border_color=TEXT_SETTINGS["foreground_color"],
                    **TEXT_SETTINGS
                )
            ),
        )

        widgets.append(caption_label)

        ### create specific widgets to pick color index
        ### for each existing node category

        ## number of categories

        no_of_categories = len(NODE_CATEGORY_COLORS)

        for (category_id, index) in APP_REFS.category_index_map.items():

            color_widget = Color2D(
                width=30,
                height=30,
                color=NODE_CATEGORY_COLORS[index],
            )

            ###
            color_widget.category_id = category_id

            ###
            color_setting_command = get_oblivious_callable(
                partial(set_color, color_widget)
            )

            color_widget.on_mouse_release = color_setting_command

            ###
            category_label = Object2D.from_surface(
                surface=(render_text(text=sep.join(category_id), **TEXT_SETTINGS))
            )

            category_label.on_mouse_release = color_setting_command

            ###
            category_widgets = List2D(
                [
                    color_widget,
                    category_label,
                ]
            )

            ###

            category_widgets.rect.snap_rects_ip(
                retrieve_pos_from="midright",
                assign_pos_to="midleft",
                offset_pos_by=(5, 0),
            )

            widgets.append(category_widgets)

        widgets.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft",
            assign_pos_to="topleft",
            offset_pos_by=(0, 5),
        )

        ### create, position and store form related buttons

        ## submit button

        self.finish_button = Button.from_text(
            text=(t.editing.category_colors_form.finish),
            command=CallList(
                [
                    self.finish_form,
                    self.exit_loop,
                ]
            ),
            **BUTTON_SETTINGS
        )

        draw_depth_finish(self.finish_button.image)

        self.finish_button.rect.topright = widgets.rect.move(0, 5).bottomright

        ## cancel button

        self.cancel_button = Button.from_text(
            text=(t.editing.category_colors_form.cancel),
            command=self.exit_loop,
            **BUTTON_SETTINGS
        )

        draw_depth_finish(self.cancel_button.image)

        self.cancel_button.rect.midright = self.finish_button.rect.move(-5, 0).midleft

        ## store

        widgets.extend((self.cancel_button, self.finish_button))

    def change_category_colors(self):

        ###
        try:
            node_packs = APP_REFS.data["node_packs"]

        except KeyError:

            create_and_show_dialog(
                "Can't pick colors for node categories,"
                " cause the file hasn't any node packs"
                " associated with it, thus no node"
                " categories either."
            )

            return

        else:

            if not node_packs:

                create_and_show_dialog(
                    "Can't pick colors for node categories,"
                    " cause the file hasn't any node packs"
                    " associated with it, thus no node"
                    " categories either."
                )

                return

        ### blit the screen-size semitransparent surf in the
        ### canvas to increase constrast

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ###
        self.loop()

        ### blit semitransparent surface over area occupied
        ### by self.rect so the form appears unhighlighted
        self.unhighlight()

    def handle_input(self):
        """Process events from event queue."""
        for event in get_events():

            ### QUIT
            if event.type == QUIT:
                self.quit()

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    if self.rect.collidepoint(event.pos):
                        self.on_mouse_release(event)

                    ## cancel editing form if mouse left
                    ## button is released out of boundaries
                    else:
                        self.exit_loop()

            ### MOUSEMOTION

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event)

    def mouse_method_on_collision(self, method_name, event):
        """Invoke inner widget if it collides with mouse.

        Parameters
        ==========

        method_name (string)
            name of method to be called on the colliding
            widget.
        event (event object of MOUSEBUTTON[...] type)
            it is required in order to comply with
            mouse interaction protocol used; here we
            use it to retrieve the position of the
            mouse when the first button was released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve position from attribute in event obj
        mouse_pos = event.pos

        ### search for a colliding obj among the widgets

        for obj in self.widgets:

            if obj.rect.collidepoint(mouse_pos):

                colliding_obj = obj
                self.unhighlight()
                break

        else:
            return

        ### if you manage to find a colliding obj, execute
        ### the requested method on it, passing along the
        ### received event

        try:
            method = getattr(colliding_obj, method_name)
        except AttributeError:
            pass
        else:
            method(event)

    on_mouse_click = partialmethod(
        mouse_method_on_collision,
        "on_mouse_click",
    )

    on_mouse_release = partialmethod(
        mouse_method_on_collision,
        "on_mouse_release",
    )

    def on_mouse_motion(self, event):

        mouse_pos = event.pos
        ### if a color widget or its label are hovered,
        ### they are highlighted

        for widget in self.widgets:

            if not isinstance(widget, List2D):
                continue

            if widget.rect.collidepoint(mouse_pos):
                self.hovered_rect = widget.rect
                break

        else:
            self.hovered_rect = None

    def finish_form(self):
        """Assign new category indices and exit loop."""
        ### reference category path map locally for quick
        ### and easier access
        category_path_map = APP_REFS.category_path_map

        ### iterate over color widgets, assigning the
        ### color indices to the respectives categories

        for widget in self.widgets:

            if not isinstance(widget, List2D):
                continue

            color_widget = widget[0]
            widget_color = color_widget.color

            index = next(
                index
                for index, color in (enumerate(NODE_CATEGORY_COLORS))
                if color == widget_color
            )

            ###

            category_id = color_widget.category_id

            category_path = category_path_map[category_id]

            category_metadata_path = category_path / NODE_CATEGORY_METADATA_FILENAME

            if category_metadata_path.is_file():

                try:
                    metadata = load_pyl(category_metadata_path)

                except Exception:

                    create_and_show_dialog(
                        ("Error while loading category" " metadata."),
                        level_name="error",
                    )

                    return

                metadata["color_index"] = index

            else:
                metadata = {"color_index": index}

            ###

            try:
                save_pyl(metadata, category_metadata_path)

            except Exception:

                create_and_show_dialog(
                    ("Error while loading category" " metadata."),
                    level_name="error",
                )

                return

        ### notify user via dialog and status message

        message = (
            "Category colors changed. Restart the application" " to see the changes."
        )

        set_status_message(message)
        create_and_show_dialog(message)

    def draw(self):
        """Draw itself and widgets.

        Extends Object2D.draw.
        """
        ### draw self (background)
        super().draw()

        ### draw widgets
        self.widgets.call_draw()

        ### if a hover rect exists, draw it on the screen

        if self.hovered_rect:

            draw_rect(SCREEN, (30, 130, 70), self.hovered_rect, 2)

        ### update screen (pygame.display.update)
        update()

    def unhighlight(self):
        """Draw semitransparent surface on self.rect area.

        Done to make form appear unhighlighted.
        """
        blit_on_screen(UNHIGHLIGHT_SURF_MAP[self.rect.size], self.rect)


_ = CategoryColorsPicking()

rebuild_category_color_form = _.__init__
change_category_colors = _.change_category_colors


### utility function

CIRCLE_POINTS = list(
    get_circle_points(
        len(NODE_CATEGORY_COLORS),
        120,
    )
)


def set_color(color_widget):

    colors = pick_colors(
        NODE_CATEGORY_COLORS,
        position_method_name=("snap_rects_to_points_ip"),
        position_method_kwargs={
            "attributes_names": repeat("center"),
            "points": CIRCLE_POINTS,
        },
    )

    if not colors:
        return

    elif len(colors) != 1:

        create_and_show_dialog(
            "You must pick a single color",
            level_name="info",
        )

        return

    color_widget.set_color(colors[0])
