"""Facility for list sorting button widget."""

### standard library imports

from os import linesep

from pprint import pformat

from xml.etree.ElementTree import Element


### local imports

from ..ourstdlibs.behaviour import empty_function

from ..surfsman.draw import blit_aligned, draw_border
from ..surfsman.render import render_rect

from ..classes2d.single import Object2D

from ..our3rdlibs.sortingeditor.main import sort_sequence

from ..textman.render import render_text, fit_text

from ..textman.viewer.main import view_text

from ..surfsman.icon import render_layered_icon

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..colorsman.colors import (
    BLACK,
    LIST_SORTING_BUTTON_FG,
    LIST_SORTING_BUTTON_BG,
)


# XXX in the future maybe implement a tooltip to display
# the contents without having to click the button

# TODO adjust text width to take width from '__init__'
# into account

### constants


## keyword arguments for PathPreview text

TEXT_KWARGS = {
    "font_height": ENC_SANS_BOLD_FONT_HEIGHT,
    "font_path": ENC_SANS_BOLD_FONT_PATH,
    "max_width": 130,
    "ommit_direction": "right",
    "foreground_color": LIST_SORTING_BUTTON_FG,
}


## surface representing list sorting editor

ICON_SURF = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (104, 105)],
    dimension_name="height",
    dimension_value=19,
    colors=[BLACK, (30, 130, 70)],
    background_width=20,
    background_height=20,
)

## message when displaying value of widget

VALUE_DISPLAY_MESSAGE = linesep.join(
    (
        "Below you can see the value stored on the widget.",
        " To change the value, leave this text view and click",
        " on the small icon in the left corner of the",
        " list sorting button widget.",
    )
)

## allowed types for items

ALLOWED_ITEM_TYPE_COMBINATIONS = (
    (str,),
    (
        int,
        float,
    ),
    (int,),
    (float,),
)


### class definition


class SortingButton(Object2D):
    """Button-like widget for sorting a sequence."""

    def __init__(
        self,
        value=("a",),
        available_items={"a", "b", "c"},
        width=155,
        name="sorting_button",
        command=empty_function,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store value and define button image and label.

        value (sequence)
            initial value of the widget.
        available_items (set)
            additional values that can compose the list.
        name (string)
            an arbitrary name to help identify the widget.
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (list/tuple/vector w/ 2 integers)
            represents the x and y coordinates of a
            position in 2d space.
        """
        ### validate arguments
        self.validate_value(value, available_items)

        ### store arguments

        self.value = value
        self.available_items = available_items

        self.name = name
        self.command = command

        ### create a surface to clean the image attribute
        ### surface every time the value changes

        ### TODO make this 155 to be the result of some
        ### meaningful calculation; probably a new max width
        ### argument minus the width of the icon;

        self.clean_surf = render_rect(width, 19, LIST_SORTING_BUTTON_BG)

        draw_border(self.clean_surf, LIST_SORTING_BUTTON_FG)

        ### create an image from the clean surf
        self.image = self.clean_surf.copy()

        ### update the image contents with the value
        self.update_image()

        ### create rect from the image attribute and
        ### position it

        self.rect = self.image.get_rect()
        setattr(self.rect, coordinates_name, coordinates_value)

    def validate_value(self, value, available_items):
        """Check whether value is of allowed type."""
        if not isinstance(value, (list, tuple)):

            raise TypeError("'value' must be of type 'list'" " or 'tuple'")

        if not isinstance(available_items, set):

            raise TypeError("'available_items' must be of type 'set'")

        if len(value) and not set(value).issubset(available_items):

            raise ValueError(
                "if 'value' isn't empty, items must be" " a subset of available items"
            )

        if len(available_items) == 0:

            raise ValueError("'available_items' must not be empty")

        item_types_set = {
            type(item) for obj in (value, available_items) for item in obj
        }

        if not any(
            item_types_set == set(combination)
            for combination in ALLOWED_ITEM_TYPE_COMBINATIONS
        ):

            raise TypeError(
                "items must either all be instances of 'str'"
                " type or any combination of 'int' and 'float'"
                " instances"
            )

    def on_mouse_release(self, event):
        """Act according to mouse release position.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONUP type)

            It is required in order to comply with
            protocol used. We retrieve the mouse position
            from its "pos" attribute.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        x, _ = event.pos

        ### if click was more to the left, where the icon
        ### is, we call the method responsible for
        ### calling the list sorting manager for sorting
        ### the list
        if x < (self.rect.x + ICON_SURF.get_width()):
            self.change_value()

        ### otherwise the user clicked on the portion of
        ### the button which hints the contents of the
        ### widget, so we display the widget value
        ### as a list of paths
        else:
            self.display_value()

    def display_value(self):
        """"""
        text = ""

        for title, a_list in (
            ("Value:", self.value),
            ("Available items:", self.available_items),
        ):

            text += title + linesep

            text += pformat(
                a_list,
                indent=2,
            ) + (linesep * 2)

        text = VALUE_DISPLAY_MESSAGE + (linesep * 2) + text

        view_text(text)

    def get(self):
        """Return the widget value."""
        return self.value

    def set(self, value, custom_command=True):
        """Set the value of the widget.

        value (string or list of strings representing paths)
            new value for widget.
        custom_command (boolean)
            indicates whether the custom command stored
            upon instantiation should be called after
            updating the value.
        """
        ### validate values received
        try:
            self.validate_value(value, self.available_items)

        ### if it doesn't validate, report error and exit
        ### method by returning

        except (TypeError, ValueError) as err:

            print(err)
            return

        ### changes are only performed if the new value is
        ### indeed different from the current one

        if self.value != value:

            ### store new value
            self.value = value

            ### update the widget image
            self.update_image()

            ### if requested, execute the custom command
            if custom_command:
                self.command()

    def update_image(self):
        """Update widget image."""
        ### clean image surface
        self.image.blit(self.clean_surf, (0, 0))

        ### use blit aligned to blit icon aligned to the
        ### midleft of the surface in the image attribute,
        ### just one extra pixel to the left

        # TODO it would probably be better to blit this
        # icon in the 'clean_surf' itself, since it
        # doesn't change anyway
        blit_aligned(ICON_SURF, self.image, "midleft", "midleft", offset_pos_by=(1, 0))

        ### render a text surface from the retrieved text

        text_surf = render_text(text=str(self.value), **TEXT_KWARGS)

        ### use blit aligned to blit text surface aligned to
        ### the midleft of the surface in the image
        ### attribute, a bit more to the left, so it sits
        ### beside the icon

        blit_aligned(text_surf, self.image, "midleft", "midleft", offset_pos_by=(22, 0))

    def change_value(self):
        """Sort the values.

        If None is returned from the sort_sequence function,
        the widget isn't updated.
        """
        ### retrieve new values from the sort_list function

        output = sort_sequence(
            self.value,
            self.available_items,
        )

        ### if the output is not None, update the value
        ### and available items in the widget

        if output is not None:

            value = output
            self.set(value)

    def reset_value_and_available_items(
        self,
        value,
        available_items,
        custom_command=True,
    ):
        """Reset available items and set given value."""
        ## check whether the value and options are valid

        try:
            self.validate_value(value, available_items)
        except (ValueError, TypeError) as err:

            print(err)
            return

        ## set the value and the options

        self.value = value
        self.available_items = available_items

        ##
        self.update_image()

        ## execute custom command if requested
        if custom_command:
            self.command()

    def get_expected_type(self):
        return type(self.value)

    def svg_repr(self):

        g = Element("g", {"class": "sorting_button"})

        g.append(
            Element(
                "rect",
                {
                    attr_name: str(getattr(self.rect, attr_name))
                    for attr_name in ("x", "y", "width", "height")
                },
            )
        )

        ###

        x, y = self.rect.topleft

        for path_directives, style in (
            (
                ("m1 1" "l4 0" "l0 3" "l-4 0" " Z"),
                "fill:rgb(30, 130, 70); stroke:black; stroke-width:2px",
            ),
            (
                ("m1 7" "l6 0" "l0 3" "l-6 0" " Z"),
                "fill:rgb(30, 130, 70); stroke:black; stroke-width:2px",
            ),
            (
                ("m1 13" "l10 0" "l0 3" "l-10 0" " Z"),
                "fill:rgb(30, 130, 70); stroke:black; stroke-width:2px",
            ),
            (
                ("m13 2" "l0 4" "l-4 0" "l6 6" "l6 -6" "l-4 0" "l0 -4" " Z"),
                (
                    "fill:rgb(30, 130, 70);"
                    "stroke:black;"
                    "stroke-width:2px;"
                    "stroke-linejoin:round;"
                ),
            ),
        ):

            path_directives = f"M{x} {y}" + path_directives

            g.append(
                Element(
                    "path",
                    {
                        "d": path_directives,
                        "style": style,
                    },
                )
            )

        ###

        (
            text_x_str,
            text_y_str,
        ) = map(str, self.rect.move(23, -5).bottomleft)

        text_element = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "start",
            },
        )

        text_element.text = fit_text(
            text=str(self.value),
            font_path=ENC_SANS_BOLD_FONT_PATH,
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            padding=1,
            max_width=143 - 20,
            ommit_direction="right",
        )

        g.append(text_element)

        return g
