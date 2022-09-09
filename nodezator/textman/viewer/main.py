"""Facility for text displaying."""

### third-party import
from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygameconstants import SCREEN_RECT

from ...ourstdlibs.collections.general import CallList

from ...ourstdlibs.behaviour import empty_function

from ...surfsman.draw import draw_border

from ...surfsman.render import combine_surfaces

from ...classes2d.single import Object2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..label.main import Label

from ..render import (
    render_text,
    render_multiline_text,
)

from ...surfsman.icon import render_layered_icon
from ...surfsman.cache import RECT_SURF_MAP

from ...colorsman.colors import (
    BLACK,
    WHITE,
    TEXT_VIEWER_HELP_FG,
    TEXT_VIEWER_HELP_BG,
    TEXT_VIEWER_HELP_BORDER,
    TEXT_VIEWER_FG,
    TEXT_VIEWER_BG,
)


## class extensions

from .op import Operations
from .prep import TextPreparation

## common constants
from .constants import (
    TEXT_VIEWER_RECT,
    CUSTOM_STDOUT_RECT,
)


### XXX could the design of the removed module
### appcommon.path.viewer contribute to this one?
### (you can find such module on previous branches)
### I think it cannot, but I didn't want to dismiss
### the possibility without actually verifying;
### see to it when convenient;
###
### edit: it is even more unlikely now, since this code
### evolved so much over the time, whereas the code from
### appcommon.path.viewer was very simple to begin with
### and wasn't touched at all since its removal;


### constants

CAPTION_TEXT_KWARGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": TEXT_VIEWER_FG,
    "background_color": TEXT_VIEWER_BG,
}

HEADER_TEXT_KWARGS = {
    **CAPTION_TEXT_KWARGS,
    "max_width": 500,
}

HELP_TEXT_KWARGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "padding": 5,
    "foreground_color": TEXT_VIEWER_HELP_FG,
    "background_color": TEXT_VIEWER_HELP_BG,
    "retrieve_pos_from": "bottomleft",
    "assign_pos_to": "topleft",
    "text_padding": 6,
}


### help text

HELP_TEXT = """
Use keyboard arrows or WASD keys to scroll.
You can also use the mouse wheel for scrolling.
Also, scrolling only works when there is text
offscreen. Press "Esc" (escape key) to go back.
""".strip()


### class definition


class TextViewer(TextPreparation, Operations):
    """Displays text on screen."""

    def __init__(self):
        """Perform setups."""
        ### store a rect for the text viewer
        self.rect = TEXT_VIEWER_RECT

        ### define a background for the text viewer and
        ### create a copy of it to use as the canvas
        ### (image)

        self.background = RECT_SURF_MAP[
            (
                *self.rect.size,
                TEXT_VIEWER_BG,
            )
        ]

        self.image = self.background.copy()

        ### create a map to store canvas surfaces according
        ### to their size

        self.canvas_map = {self.rect.size: self.image}

        ### build text objects forming a message to be
        ### displayed to the user about the controls
        self.build_message()

        ### create a help icon object

        self.help_icon = Object2D.from_surface(
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (167, 92, 93, 168)],
                dimension_name="height",
                dimension_value=21,
                colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
                background_width=21,
                background_height=21,
            ),
        )

        ### create a flag to indicate whether the help icon
        ### is hovered
        self.hovering_help_icon = False

        ### define handle_input behaviour

        self.handle_input = CallList((self.handle_events, self.handle_key_input))

        ### create a caption for this text viewer

        text_icon = render_layered_icon(
            chars=[chr(ordinal) for ordinal in (37, 36)],
            dimension_name="height",
            dimension_value=26,
            colors=[BLACK, WHITE],
        )

        eye_icon = render_layered_icon(
            chars=[chr(ordinal) for ordinal in (87, 88, 89)],
            dimension_name="height",
            dimension_value=21,
            colors=[BLACK, WHITE, (115, 40, 30)],
        )

        caption_icon = combine_surfaces(
            surfaces=[text_icon, eye_icon],
            retrieve_pos_from="bottomright",
            assign_pos_to="bottomright",
            offset_pos_by=(10, 5),
            padding=2,
        )

        caption_text = render_text(text="Text Viewer", **CAPTION_TEXT_KWARGS)

        self.caption = Object2D.from_surface(
            combine_surfaces(
                surfaces=[caption_icon, caption_text],
                retrieve_pos_from="midright",
                assign_pos_to="midleft",
                padding=4,
                background_color=TEXT_VIEWER_BG,
            )
        )

        draw_border(self.caption.image, thickness=2)

        ### default caption drawing routine
        self.caption_drawing_routine = self.caption.draw

        ### default header drawing routinte
        self.header_drawing_routine = empty_function

        ### create header label

        self.header_label = Label(
            text="",
            **HEADER_TEXT_KWARGS,
        )

        ### center text viewer and also store the
        ### centering method as a window resize setup

        self.center_text_viewer()

        APP_REFS.window_resize_setups.append(self.center_text_viewer)

    def center_text_viewer(self):

        if self.rect is TEXT_VIEWER_RECT:

            diff = Vector2(SCREEN_RECT.center) - self.rect.center

        elif self.rect is CUSTOM_STDOUT_RECT:

            diff = Vector2(SCREEN_RECT.move(0, -80).midbottom) - self.rect.midbottom

        else:
            raise RuntimeError(
                "This else block should not be" " reached, please review the logic."
            )

        TEXT_VIEWER_RECT.center = SCREEN_RECT.center

        CUSTOM_STDOUT_RECT.midbottom = SCREEN_RECT.move(0, -80).midbottom

        if hasattr(self, "scroll_area"):
            self.scroll_area.move_ip(diff)

        if hasattr(self, "lines"):
            self.lines.rect.move_ip(diff)

        if hasattr(self, "lineno_panel"):
            self.lineno_panel.rect.topright = self.rect.topleft

        ### store the inverted self.rect.topleft to use as
        ### an offset to draw lines on self.image
        self.offset = -Vector2(self.rect.topleft)

        ##
        self.caption.rect.bottomleft = self.rect.move(0, -3).topleft

        ##
        self.header_label.rect.move_ip(diff)

        ### position the help icon and help text objects
        ### near the bottomright corner of the text viewer

        self.help_icon.rect.bottomright = self.rect.move(-10, -10).bottomright

        self.help_text_obj.rect.bottomright = self.rect.move(-10, -35).bottomright

    def build_message(self):
        """Build text object to inform user of controls."""
        ### create a single help text object in which
        ### to blit all the text from the text objects,
        ### storing it in its own attribute

        self.help_text_obj = Object2D.from_surface(
            render_multiline_text(
                text=HELP_TEXT,
                **HELP_TEXT_KWARGS,
            )
        )

        ### also draw a border on the help text object

        draw_border(
            self.help_text_obj.image, color=TEXT_VIEWER_HELP_BORDER, thickness=2
        )


view_text = TextViewer().view_text
