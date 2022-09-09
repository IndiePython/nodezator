"""Facility for color visualization.

That is, to help user view and analyse various aspects
of given colors, like their values, names, how they
look next to each other, etc.
"""

### standard library imports

from functools import partial

from operator import methodcaller


### third-party import
from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygameconstants import SCREEN_RECT

from ...ourstdlibs.meta import initialize_bases

from ...ourstdlibs.collections.general import CallList

from ...ourstdlibs.behaviour import (
    empty_function,
    get_oblivious_callable,
)

from ...ourstdlibs.color.custom import custom_format_color

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...loopman.main import LoopHolder

from ...surfsman.draw import draw_border
from ...surfsman.render import render_rect

from ...textman.render import render_text
from ...fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT

from ...surfsman.icon import render_layered_icon

from ...widget.optionmenu.main import OptionMenu

from ..colors import (
    BLACK,
    WHITE,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)

## class extensions

from .modes.colorlist import ColorListMode

from .modes.patterns.main import PatternsMode


### constants

MODE_NAMES = (
    "color_list",
    "patterns",
)

BEHAVIOUR_NAMES = (
    "prepare_mode",
    "event_handling",
    "keyboard_input_handling",
    "update",
    "draw",
    "exit_mode",
    "free_up_memory",
)


### class definition


class ColorsViewer(ColorListMode, PatternsMode, LoopHolder):
    """loop holder which provides ways to view colors."""

    def __init__(self):
        """Create structure, perform setups."""
        ### create a surface representing this widget
        ### to store in its 'image' attribute

        surf = self.image = render_rect(820, 650, WINDOW_BG)

        draw_border(surf, thickness=2)

        surf.blit(
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in range(106, 113)],
                dimension_name="height",
                dimension_value=30,
                colors=[
                    BLACK,
                    *(
                        (r, g, b)
                        for r in (0, 255)
                        for g in (0, 255)
                        for b in (0, 255)
                        if sum((r, g, b))
                    ),
                ],
                background_width=32,
                background_height=32,
            ),
            (3, 3),
        )

        surf.blit(
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (87, 88, 89)],
                dimension_name="height",
                dimension_value=21,
                colors=[BLACK, WHITE, (115, 40, 30)],
                background_width=20,
                background_height=20,
            ),
            (20, 20),
        )

        surf.blit(
            render_text(
                "Colors Viewer",
                font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                padding=5,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
            ),
            (40, 8),
        )

        ### create rect for this widget from the surface
        ### we created
        self.rect = surf.get_rect()

        ### build map to store behaviours for each mode
        ### and perform additional setups
        self.build_mode_behaviour_map()

        ### build widgets
        self.build_widgets()

        ### execute __init__ methods of the base classes
        ### (class extensions) which have it
        initialize_bases(self)

        ### assign default behaviour to exit_mode attribute
        self.exit_mode = empty_function

        ### center viewer and append the centering method as
        ### window resize setup

        self.center_colors_viewer()

        APP_REFS.window_resize_setups.append(self.center_colors_viewer)

    def center_colors_viewer(self):

        ## store difference between screen center and
        ## viewer center for centering the viewer on
        ## screen

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ##

        self.rect.center = SCREEN_RECT.center

        self.canvas.rect.center = self.rect.center

        self.mode_options.rect.topright = self.rect.move(-8, 13).topright

        self.go_back_button.rect.bottomright = self.rect.move(-10, -7).bottomright

        self.modes_label.rect.midright = self.mode_options.rect.move(-5, -1).midleft

        self.pattern_label.rect.bottomleft = self.rect.move(5, -7).bottomleft

        ###

        try:
            self.color_list_objs
        except AttributeError:
            pass

        else:

            self.color_list_objs.rect.move_ip(diff)
            self.color_list_bg.rect.move_ip(diff)

        ###

        self.pattern_options.rect.midleft = self.pattern_label.rect.move(5, 0).midright

        self.redraw_pattern_button.rect.midleft = self.pattern_options.rect.move(
            5, 0
        ).midright

    def build_widgets(self):
        """Build widgets to support the colors viewer."""

        ### create and setup a "mode options menu"

        ## instantiate and store the options menu in its
        ## own attribute (also reference it locally)

        mode_options = self.mode_options = OptionMenu(
            loop_holder=self,
            value=MODE_NAMES[0],
            max_width=0,
            options=list(MODE_NAMES),
            draw_on_window_resize=(
                partial(
                    methodcaller("draw"),
                    self,
                )
            ),
        )

        ## define command for the menu and assign it to
        ## its 'command' attribute

        def change_mode():
            """Retrieve mode name from menu and set it."""
            self.set_mode(mode_options.get())

        mode_options.command = change_mode

        ### create and setup a "go back button"

        go_back_button = self.go_back_button = Object2D.from_surface(
            surface=(
                render_text(
                    text="Go back",
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    padding=5,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                    depth_finish_thickness=1,
                )
            ),
        )

        go_back_button.on_mouse_release = get_oblivious_callable(
            partial(setattr, self, "running", False)
        )

        ### create a collection to hold buttons and
        ### add the mode options menu and "go back" button
        ### to it

        self.buttons = List2D()
        self.buttons.extend((mode_options, go_back_button))

        ### create a label for the colors viewer

        ## create and store a collection to store labels
        self.labels = List2D()

        ## append a label to indicate the "mode option menu"
        ## to it (other labels will be appended to this
        ## collection, but by other objects, not here)

        modes_label = self.modes_label = Object2D.from_surface(
            surface=(
                render_text(
                    text="Mode:",
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    padding=5,
                    foreground_color=WINDOW_FG,
                    background_color=WINDOW_BG,
                )
            ),
        )

        self.labels.append(modes_label)

        ### create a pygame.Surface objects to use as a
        ### canvas that can be freely used in different
        ### modes

        canvas_area = self.rect.inflate(-80, -80)

        self.canvas = Object2D.from_surface(
            surface=render_rect(*canvas_area.size),
            coordinates_name="topleft",
            coordinates_value=canvas_area.topleft,
        )

    def build_mode_behaviour_map(self):
        """Build map with behaviours for each mode.

        The memory freeing behaviours for each mode,
        however, should be stored in a list apart, since we
        do not switch between them during the lifetime of the
        colors viewer; instead they are executed together
        whenever the user leaves the colors viewer.

        Both mode exiting (exit_mode) and memory freeing
        operations aim to perform cleanup operations,
        but the cleanup performed by memory freeing
        operations is more deep or definitive,
        since mode exiting operations perform cleanup
        when switching between modes while memory freeing
        operations perform cleanups when leaving the colors
        viewer.
        """
        ### create and store map in its own attribute,
        ### also referencing it in a local variable
        mdb_map = self.mode_behaviour_map = {}

        ### also create a custom list where we'll gather
        ### all memory freeing behaviours, referencing it
        ### locally as well
        memory_freeing_behaviours = self.memory_freeing_behaviours = CallList()

        ### create a behaviour map for each mode, storing
        ### it in the map created above, associated with
        ### a string representing the name of the mode

        for mode_name in MODE_NAMES:

            ## create, store and reference behaviour map
            ## locally
            behaviour_map = mdb_map[mode_name] = {}

            ## for each behaviour name, gather the
            ## corresponding behaviour for the current
            ## mode (or an empty function, if said behaviour
            ## is missing) and assign it to the map using
            ## the behaviour name as a key;
            ##
            ## unless the behaviour is a memory freeing
            ## behaviour, in which case it goes in the
            ## dedicated list for memory freeing operations

            for behaviour_name in BEHAVIOUR_NAMES:

                ## build the attribute name for this
                ## behaviour in this mode
                attr_name = mode_name + "_" + behaviour_name

                ## use the name as an attribute name,
                ## retrieving the corresponding behaviour
                ## from that attribute;
                ##
                ## if the attribute doesn't exist, an empty
                ## function is used instead

                behaviour = getattr(self, attr_name, empty_function)

                ## if we are dealing with a memory freeing
                ## behaviour, store it in the dedicated list

                if behaviour_name == "free_up_memory":
                    memory_freeing_behaviours.append(behaviour)

                ## otherwise, store the behaviour in the map
                ## using the behaviour name as the key

                else:

                    behaviour_map[behaviour_name] = behaviour

    def set_mode(self, mode_name):
        """Assign behaviours according to given mode.

        Parameters
        ==========
        mode_name (string)
            name of mode whose behaviours must be set.
        """
        ### execute the callable sitting in the 'exit_mode'
        ### attribute, so that any setups needed to exit
        ### the current mode are performed, if they exist
        self.exit_mode()

        ### get behaviour map for given mode
        behaviour_map = self.mode_behaviour_map[mode_name]

        ### assign behaviours from the map to their
        ### corresponding attributes

        for behaviour_name, behaviour in behaviour_map.items():
            setattr(self, behaviour_name, behaviour)

        ### gather the "input getting" attributes in a
        ### special container which calls all callables
        ### contained in it when executed and store it
        ### in the 'handle_input' attribute

        self.handle_input = CallList(
            (self.event_handling, self.keyboard_input_handling)
        )

        ### finally, execute the callable sitting in the
        ### 'prepare_mode' attribute so extra setups
        ### are executed for the mode, if they exist
        self.prepare_mode()

    def view_colors(self, color_value, mode=None):
        """Display the given color(s) from color_value."""
        ### convert the color value into a list of
        ### rgba colors and store it its own attribute

        self.colors = custom_format_color(color_value, "rgb_ints", False)

        ### if mode is not specified, use the one set
        ### in the "mode option menu"

        if mode is None:
            mode = self.mode_options.get()

        self.set_mode(mode)

        ### set and start loop
        self.loop()

        ### once you leave the loop, execute the mode
        ### exiting operation of the current mode in use,
        ### in case there's clean up to be performed
        self.exit_mode()

        ### finally, execute the memory freeing operations
        ### for all modes
        self.memory_freeing_behaviours()


### instantiate the colors viewer and store a reference
### to its 'view_colors' method in this module so
### it can be easily imported
view_colors = ColorsViewer().view_colors
