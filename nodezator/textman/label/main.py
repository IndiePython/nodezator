"""Facility for single line updateable text object."""

### third-party import
from pygame import Rect


### local imports

from ...classes2d.single import Object2D

from ...surfsman.render import render_rect

from ...fontsman.constants import ENC_SANS_BOLD_FONT_PATH

from ..cache import TEXT_SURFS_DB

from ...colorsman.colors import BLACK


# XXX it's not clear why the Label constructor parameters
# 'coordinates_name' and 'coordinates_value' can be
# passed as positional parameters too; it makes more sense
# for everything to be keyword-only instead;


class Label(Object2D):
    """A text widget with automatic surface updating.

    It works similar to tkinter.Label objects since they
    can have text set and reset any time.
    """

    def __init__(
        self,
        text="",
        *,
        name="label",
        font_height=22,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        foreground_color=BLACK,
        background_color=(*BLACK, 0),
        padding=5,
        min_width=0,
        max_width=None,
        ellipsis_at_end=True,
        update_pos_on_change=False,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Perform setups and assign data for reuse.

        text
            string providing text to update surface.
        font_height
            Integer indicating desired font height in pixels.
        font_path
            String representing font style. Check local
            font.py module for available styles. In doubt
            use ENC_SANS_BOLD_FONT_PATH for default font.
        foreground_color
        background_color
            A tuple or list of r, g, b values which are
            integers ranging from 0 to 255. The background
            color can be None, though, in which case the
            background is rendered transparent. For the
            background color, an optional fourth value can
            be passed, which is an integer in the same range
            as the others, representing the image opacity
            (0 for full transparency and 255 for full
            opacity).
        padding (positive integer or 0, defaults to 5)
            amount of padding in all four sides of the
            text surface.
        max_width
        (positive integer or None, defaults to None)
            indicates maximum width to be assumed by the
            label. If None, it can assume any width.
        ellipsis_at_end (bool)
            only relevant if max width was specified.
            Indicates whether ellipsis is shown at the end
            or begginning of the text due to the
            max_width being reached by the content.
            (True = end of content; False = beginning)
        update_pos_on_change (boolean, default to False)
            whether the position of the rect should be
            reassigned using the original coordinates_name
            and coordinates_value whenever the contents
            of the label change or not.
        """
        ### convert the colors passed into tuples for
        ### simplicity (since colors can appear in other
        ### classes like pygame.Color and builtin lists too)

        background_color = tuple(background_color)
        foreground_color = tuple(foreground_color)

        ### store the background in its own attribute
        self.bg_color = background_color

        ### gather the remaining text rendering settings
        ### in a dictionary inside its own attribute;
        ### notice we left the background color data out
        ### of the map, due to the fact that it's data
        ### is handled separately (which is why it was
        ### already stored in its own attribute in the
        ### previous step)

        render_settings = {
            "font_height": font_height,
            "font_path": font_path,
            "foreground_color": foreground_color,
        }

        ### get char map for render settings then store
        ### its surf and width map

        text_map = TEXT_SURFS_DB[render_settings]

        self.surf_map = text_map["surf_map"]
        self.width_map = text_map["width_map"]

        ### store the padding
        self.padding = padding

        ### store a height taking the padding into account

        self.height = (
            ## get the height from a surface of a space
            ## character
            self.surf_map[" "].get_height()
            ## add the padding two times, to account for
            ## the padding on top and bottom
            + (self.padding * 2)
        )

        ### store the name
        self.name = name

        ### store the minimum width
        self.min_width = min_width

        ### store max width if not None, along with
        ### the ellipsis_at_end flag and additional data
        ### calculated on the spot

        if max_width is not None:

            self.max_width = max_width

            self.ellipsis_at_end = ellipsis_at_end

            self.ellipsis_width = self.width_map["."] * 3

        ### create an attribute with a string to store the
        ### text of the label
        self.contents = ""

        ### create a rect attribute holding a pygame.Rect
        ### instance
        self.rect = Rect(0, 0, 0, 0)

        ### add text the text passed as argument (this is
        ### also needed in order to create an image
        ### attribute and thus prevent errors)
        self.add_text(text)

        ### position rect
        setattr(self.rect, coordinates_name, coordinates_value)

        ### if update_pos_on_change flag is on, store
        ### the position related arguments

        if update_pos_on_change:
            self.coordinates_name = coordinates_name
            self.coordinates_value = coordinates_value

    def get(self):
        """Return text content of widget."""
        return self.contents

    def set(self, text):
        """Set obj text.

        text (string)
            value to be used as label text.
        """
        ### return earlier if text is already set
        if text == self.contents:
            return

        ### otherwise "clear" contents and add text

        self.contents = ""
        self.add_text(text)

    def add_text(self, text):
        """Add text to the label.

        text (string)
            text to be added.
        """
        ### extend content with text
        self.contents += text

        ### update image
        self.update_image()

        ### if there are position related attributes
        ### available, use them to update the position
        ### of the rect too

        try:
            coordinates_name = self.coordinates_name
            coordinates_value = self.coordinates_value

        except AttributeError:
            pass

        else:
            setattr(self.rect, coordinates_name, coordinates_value)

    def update_image(self):
        """Update image surface attribute."""
        ### reference the width map locally
        width_map = self.width_map

        ### create new surface for image attribute

        ## calculate width
        ## (if there are no contents, width might even be
        ## zero at this point)

        width = sum(width_map[char] for char in self.contents)

        ## add padding to width (multiplied by 2 to account
        ## for both left and right padding)
        width += self.padding * 2

        ## define characters from content which should be
        ## used in the label surface, according to
        ## the max_width setting or lack thereof

        try:
            max_width = self.max_width

        except AttributeError:
            chars = self.contents

        else:

            if width > max_width:

                width = max_width
                chars = self.get_chars_within_width()

            else:
                chars = self.contents

        ## use minimum width to boost the actual width
        width = max(width, self.min_width)

        ## generate and store surface
        self.image = render_rect(width, self.height, self.bg_color)

        ### iterate over contents blitting surfaces

        ## define a starting x and y for blitting characters;
        ## notice they start with 5, to give the surface a
        ## small padding
        x = y = self.padding

        ## blit characters while incrementing the x position

        # reference surf map locally (width map is already
        # referenced)
        surf_map = self.surf_map

        # blit each char

        for char in chars:

            # blit surf
            self.image.blit(surf_map[char], (x, y))

            # increment x
            x += width_map[char]

        ### admin task: update rect dimensions
        self.rect.size = self.image.get_size()

    def get_chars_within_width(self):
        """Return chars for label with max width."""
        ### get the max width minus double the padding (to
        ### compensate for the left and right padding
        max_width = self.max_width - (self.padding * 2)

        ### get the available width for characters by
        ### removing the width taken by the ellipsis
        available_width = max_width - self.ellipsis_width

        ### get the chars and combine with the ellipsis
        ### according to the "ellipsis_at_end" flag

        ## define variables needed to perform calculations

        # an accumulator to store the total width used by
        # the character used as we add them one by one
        width_amount = 0

        # a string to store each character as we add
        # them one by one until we use all the available
        # width
        chars = ""

        # the string representing the ellipsis itself
        ellipsis = "..."

        ## reference the char map locally
        width_map = self.width_map

        ## now iterate over the contents, adding forming
        ## the final string containing the characters and
        ## the ellipsis

        if self.ellipsis_at_end:

            for char in self.contents:

                # calculate the resulting width from
                # adding the character

                char_width = width_map[char]
                resulting_width = width_amount + char_width

                # if the resulting width surpasses the
                # available width, we break out of the
                # loop
                if resulting_width > available_width:
                    break

                # otherwise it is ok to add the character
                # to the text; we also update the
                # amount of width used
                else:
                    chars += char
                    width_amount = resulting_width

            chars = chars + ellipsis

        else:

            for char in self.contents[::-1]:

                # calculate the resulting width from
                # adding the character

                char_width = width_map[char]
                resulting_width = width_amount + char_width

                # if the resulting width surpasses the
                # available width, we break out of the
                # loop
                if resulting_width > available_width:
                    break

                # otherwise it is ok to add the character
                # to the text; we also update the
                # amount of width used
                else:
                    chars = char + chars
                    width_amount = resulting_width

            chars = ellipsis + chars

        ### finally return the characters
        return chars
