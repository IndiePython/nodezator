"""Facility w/ loop holder for picking color(s)."""

### standard library import
from functools import partial


### local imports

from ...config import APP_REFS

from ...pygameconstants import SCREEN_RECT

from ...ourstdlibs.color.utils import get_int_sequence_repr

from ...ourstdlibs.color.conversion import (
    full_rgb_to_hex_string,
    full_rgb_to_hls,
    full_rgb_to_html_name,
    full_rgb_to_pygame_name,
    full_rgba_to_luma,
)

from ...ourstdlibs.collections.general import (
    CallList,
    FactoryDict,
)

from ...ourstdlibs.behaviour import get_oblivious_callable

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...surfsman.render import render_rect
from ...surfsman.draw import draw_border

from ...textman.render import render_text

from ...textman.label.main import Label

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
    FIRA_MONO_BOLD_FONT_HEIGHT,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ..colors import (
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
)

from .constants import DEFAULT_LABEL_MESSAGE

## class extension
from .op import Operations


### font settings

ENC_SANS_FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT
FIRA_MONO_FONT_HEIGHT = FIRA_MONO_BOLD_FONT_HEIGHT

TEXT_PADDING = 5
LABEL_PADDING = 2
BUTTON_PADDING = 5


### class definition


class ColorsPicker(Operations):
    """loop holder for picking html colors."""

    def __init__(self):
        """Create/set objects to support operations."""
        ### build widgets
        self.build_widgets()

        ### create and store useful collections

        ## map to store information about each color
        self.color_info = FactoryDict(get_color_info)

        ## list to hold color 2d instances
        self.existing_color2d_objs = []

        ## custom list instance to hold color2d instances
        ## used for color picking
        self.color_widgets = List2D()

        ### append color picker centering method as a
        ### window resize setup

        APP_REFS.window_resize_setups.append(self.center_color_picker)

    def center_color_picker(self):
        """Position color picker objects.

        They are positioned relative to each other and
        to the screen as well.
        """
        if not self.color_widgets:
            return

        ### center color widgets on the screen
        self.color_widgets.rect.center = SCREEN_RECT.center

        ### move caption right to their topleft and
        ### buttons right to their bottomright with
        ### a slight offset

        self.caption.rect.bottomleft = self.color_widgets.rect.move(0, -15).topleft

        self.buttons.rect.topright = self.color_widgets.rect.move(0, 15).bottomright

        ### reposition labels near the screen bottomleft

        self.labels.rect.bottomleft = SCREEN_RECT.move(5, -8).bottomleft

        ### if color picker loop is running, request it
        ### to be drawn

        if hasattr(self, "running") and self.running:

            APP_REFS.draw_after_window_resize_setups = self.draw_once

    def build_widgets(self):

        caption_surf = render_text(
            text="Click to select/deselect colors",
            font_path=ENC_SANS_BOLD_FONT_PATH,
            padding=TEXT_PADDING,
            font_height=ENC_SANS_FONT_HEIGHT,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
            border_color=WINDOW_FG,
            border_thickness=2,
        )

        self.caption = Object2D.from_surface(caption_surf)

        ### Create labels to display color information

        ## create and store a custom list of labels
        ## in its own attribute, also referencing it
        ## locally for quick and easier access

        labels = self.labels = List2D(
            Label(
                text="",
                font_height=FIRA_MONO_FONT_HEIGHT,
                font_path=FIRA_MONO_BOLD_FONT_PATH,
                padding=LABEL_PADDING,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
            )
            for _ in range(6)
        )

        ## set a custom message in the last one
        labels[-1].set(DEFAULT_LABEL_MESSAGE)

        ## position labels near the bottom left corner
        ## of the screen

        height_increment = FIRA_MONO_FONT_HEIGHT + (2 * LABEL_PADDING)

        for label, offset in zip(
            labels,
            (
                (5, -5 - height_increment),
                (5, -5),
                (270, -5 - height_increment),
                (270, -5),
                (460, -5 - height_increment),
                (460, -5),
            ),
        ):

            label.rect.bottomleft = SCREEN_RECT.move(offset).bottomleft

        ### create buttons used in the picker

        ## define cancel command

        cancel_command = CallList(
            [self.exit_loop, partial(setattr, self, "cancel", True)]
        )

        ## create a custom list instance containing
        ## a button for each command

        self.buttons = List2D(
            ## create an object representing a text surface
            ## stylized as a button with the command stored in
            ## its 'on_mouse_release' attribute...
            Object2D.from_surface(
                surface=render_text(
                    text=text,
                    font_height=ENC_SANS_FONT_HEIGHT,
                    font_path=ENC_SANS_BOLD_FONT_PATH,
                    padding=BUTTON_PADDING,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                    depth_finish_thickness=1,
                ),
                on_mouse_release=(get_oblivious_callable(command)),
            )
            ## ...for each given pair of text/command
            for text, command in (
                ("Cancel", cancel_command),
                ("Ok", self.exit_loop),
            )
        )

        ## align the buttons side to side (the topright of
        ## one used as the topleft of the other, with a
        ## slight horizontal offset

        self.buttons.rect.snap_rects_ip(
            retrieve_pos_from="topright", assign_pos_to="topleft", offset_pos_by=(5, 0)
        )


### utility function


def get_color_info(color):
    ### gather info in the form of custom
    ### formated text

    ## rgba values
    full_rgba_repr = get_int_sequence_repr(color)

    ## hex string
    hex_repr = full_rgb_to_hex_string(color)

    ## hls values

    full_hls = full_rgb_to_hls(color)
    full_hls_repr = get_int_sequence_repr(full_hls)

    ## names

    html_name = full_rgb_to_html_name(color)
    pygame_name = full_rgb_to_pygame_name(color)

    ## luma
    luma = str(full_rgba_to_luma(color))

    ### create and store a map for the color,
    ### containing all gathered info stored
    ### in their corresponding fields;

    return {
        "hls": full_hls_repr,
        "luma": luma,
        "hex": hex_repr,
        "rgb": full_rgba_repr,
        "html": html_name,
        "pygame": pygame_name,
    }


### instantiate the colors picker, referencing its
### relevant color picking operations at the module
### level so it can be directly imported from wherever
### needed in the package

_ = ColorsPicker()

pick_colors = _.pick_colors
pick_html_colors = _.pick_html_colors
pick_pygame_colors = _.pick_pygame_colors
