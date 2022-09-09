"""Entry widgets creation for the colors editor class."""

### local imports

from .constants import FONT_HEIGHT

## extra utilities
from ....ourstdlibs.color.utils import (
    validate_hex_color_string,
    validate_html_color_name,
    validate_pygame_color_name,
    format_color_name,
)

## widgets

from ....widget.stringentry import StringEntry

from ....widget.intfloatentry.main import IntFloatEntry


def setup_entries(self):
    """Create and set up entry widgets.

    Function meant to be injected in the ColorsEditor
    class. Handles the creation of entry widgets.

    Since entry widgets also work as buttons, they are
    stored in the list of buttons in the 'buttons'
    attribute at the end.
    """
    ### instantiate entries

    ## list operations to be used for entries

    operations = (
        self.update_from_hls_entry,
        self.update_from_hls_entry,
        self.update_from_hls_entry,
        self.update_from_hsv_entry,
        self.update_from_rgb_entry,
        self.update_from_rgb_entry,
        self.update_from_rgb_entry,
        self.update_from_alpha_entry,
    )

    ## iterate over pairs formed by each scale and its
    ## respective operation to build an entry for each
    ## scale

    entries = [
        IntFloatEntry(
            value=scale.get(),
            loop_holder=self,
            font_height=FONT_HEIGHT,
            draw_on_window_resize=self.draw,
            width=170,
            numeric_classes_hint="int",
            min_value=0,
            max_value=scale.max_value,
            name=scale.name,
            command=routine,
            coordinates_name="midleft",
            coordinates_value=scale.rect.move(105, -2).midright,
        )
        for scale, routine in zip(self.scales, operations)
    ]

    ### build map to store specific groupings of
    ### entries (notice the alpha entry isn't grouped
    ### with any other entry, because it operates
    ### independently from all of them)

    self.entry_map = {
        "hls": entries[:3],
        "hsv": [entries[i] for i in (0, 2, 3)],
        "rgb": entries[4:7],
        "alpha": entries[7],
    }

    ### instantiate other special entries

    ## hex entry

    hex_topleft = self.scales[-1].rect.move(-69, 35).bottomleft

    self.hex_entry = StringEntry(
        value="#ff0000",
        loop_holder=self,
        font_height=FONT_HEIGHT,
        width=85,
        draw_on_window_resize=self.draw,
        command=self.update_from_hex_entry,
        validation_command=validate_hex_color_string,
        formatting_command=str.lower,
        coordinates_name="topleft",
        coordinates_value=hex_topleft,
    )

    ## html name entry

    entry_midleft = self.hex_entry.rect.move(135, 0).midright

    self.html_name_entry = StringEntry(
        value="red",
        loop_holder=self,
        font_height=FONT_HEIGHT,
        width=170,
        draw_on_window_resize=self.draw,
        command=self.update_from_html_name_entry,
        validation_command=validate_html_color_name,
        formatting_command=format_color_name,
        coordinates_name="midleft",
        coordinates_value=entry_midleft,
    )

    ## pygame name entry

    entry_midleft = self.html_name_entry.rect.move(154, 0).midright

    self.pygame_name_entry = StringEntry(
        value="red",
        loop_holder=self,
        font_height=FONT_HEIGHT,
        width=170,
        command=self.update_from_pygame_name_entry,
        draw_on_window_resize=self.draw,
        validation_command=validate_pygame_color_name,
        formatting_command=format_color_name,
        coordinates_name="midleft",
        coordinates_value=entry_midleft,
    )

    ### add entries to the buttons custom list,
    ### since they work as buttons too (they have a
    ### mouse action method)

    self.buttons.extend(entries)
    self.buttons.extend(
        (
            self.hex_entry,
            self.html_name_entry,
            self.pygame_name_entry,
        )
    )
