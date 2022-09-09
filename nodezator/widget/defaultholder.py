"""Facility for simple default holder widget class."""

### standard library import
from xml.etree.ElementTree import Element


### local imports

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.label.main import Label

from ..textman.render import fit_text


### XXX the default holder could work as a button,
### displaying a "pretty printed" version of the
### repr string for some common classes like tuples,
### lists, dicts for instance (it could use some
### python modules which help making the output more
### compact (look into the "Fluent Python" book by Ramalho,
### there some examples there), and then you would turn
### the result into a multiline text to be displayed
### on an loop holder similar to the one in the path
### button);

### XXX name default colors in the color.json and
### grab them from colorsman.colors


### class definition


class DefaultHolder(Label):
    """A label used to represent a default value.

    Used to hold default values that are not supposed
    to be edited in a widget.

    When a parameter holds a default value editable by
    widget, then a custom widget is used, and the value
    can be both seen and edited in the widget. However,
    when the default value can't be edited in a widget,
    then this label serves as a displaying widget so that
    the user at least can know what is the default value.

    This widget displays a repr() version of the value
    it holds, so it is advised that you make sure the
    value used have a meaningful __repr__ method.
    """

    def __init__(
        self,
        value,
        name="default_holder",
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        max_width=155,
        padding=1,
        foreground_color=(40, 40, 40),
        background_color=(190, 190, 190),
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Perform setups and assign data for reuse.

        Extends appcommon.text.label.main.Label.__init__

        Parameters
        ==========

        value (any python object)
            value of the widget.
        name (string)
            an arbitrary name to help identify the widget.
        font_height (positive integer)
            indicates desired font height in pixels.
        font_path (string)
            represents the font desired. Check local
            font.py module for available styles. In doubt
            use 'default' for default font.
        padding (positive integer or 0, defaults to 5)
            amount of padding in all four sides of the
            text surface.
        max_width
        (positive integer or None, defaults to None)
            indicates maximum width to be assumed by the
            label. If None, it can assume any width.
        foreground_color
        background_color
        (tuple or list with 3 or 4 integers)
            integers ranging from 0 to 255 representing
            red, green, blue and (optionally) alpha values
            of a color. The foreground color must only hold
            RGB values, while the background may hold an
            alpha value to specify how much opacity
            is desired in the background. The background
            may also be None. If the alpha is 0 or the
            background argument is None,  there will be
            no background at all.
        coordinates_name (string)
            name of pygame.Rect attribute to which the
            coordinates_value argument will be assigned.
        coordinates_value (2-tuple or list with 2 integers)
            value representing a position/point in 2d space
            to be assigned to the pygame.Rect attribute in
            order to position it.
        """
        ### store value and name

        self.value = value
        self.name = name

        ### gather text style related arguments in a
        ### single dictionary

        text_kwargs = {
            "font_height": font_height,
            "font_path": font_path,
            "padding": padding,
            "max_width": max_width,
            "foreground_color": foreground_color,
        }

        if background_color:
            text_kwargs["background_color"] = background_color

        ### initialize superclass

        super().__init__(
            text=repr(self.value),
            coordinates_name=coordinates_name,
            coordinates_value=coordinates_value,
            **text_kwargs,
        )

    def get(self):
        """Return the widget's value.

        Overrides Label.get method.
        """
        return self.value

    def set(self, value):
        """Dummy method. Not supposed to have any effect.

        This method is called for all widgets when
        instantiating a CallableNode in order to replace
        the default value of each widget with the last value
        set by the user.

        Since this widget cannot be edited, but it was
        designed to just display the value it holds, the
        value attempted to be set is the same which is
        already set on it.

        Because of this, the only thing we do here is
        check whether the value which is attempted to
        be set is the same as the one already set and,
        if not the case, report the abnormal circunstance,
        likely generated by a bug.
        """
        if value != self.value:

            msg = "there shouldn't be an attempt to set" " a different value on this"

            print(msg, self.__class__.__name__, "widget")

    def svg_repr(self):
        """Return svg group element representing widget.

        Overrides Object2D.svg_repr().
        """
        rect = self.rect.inflate(-2, -2)
        x_str, y_str, width_str, height_str = map(str, rect)

        ###
        group = Element("g", {"class": "default_holder"})

        group.append(
            Element(
                "rect",
                {
                    "x": x_str,
                    "y": y_str,
                    "width": width_str,
                    "height": height_str,
                },
            )
        )

        (
            text_x_str,
            text_y_str,
        ) = map(str, rect.move(0, -5).bottomleft)

        text_element = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "start",
            },
        )

        text_element.text = fit_text(
            text=repr(self.value),
            max_width=145,
            ommit_direction="right",
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            font_path=ENC_SANS_BOLD_FONT_PATH,
            padding=1,
        )

        group.append(text_element)

        return group
