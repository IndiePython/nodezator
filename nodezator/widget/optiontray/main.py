"""Facility for OptionTray widget class definition."""

### standard library imports

from itertools import combinations

from ast import literal_eval

from xml.etree.ElementTree import Element


### local imports

from ...ourstdlibs.behaviour import empty_function
from ...ourstdlibs.dictutils import settings_to_hashable_repr


from ...textman.render import get_text_size

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...colorsman.colors import (
    OPTION_TRAY_FG,
    OPTION_TRAY_BG,
    OPTION_TRAY_SELECTED_FG,
    OPTION_TRAY_SELECTED_BG,
)

## class extension
from .op import (
    OptionTrayLifetimeOperations,
)

from .creation import (
    OptionTrayCreationOperations,
)


### constants

## support function


def isliteral(value):

    try:
        literal_eval(repr(value))

    except Exception:
        return False

    return True


## nested dictionary used to store surfaces in its
## innermost level;
##
## here's an example of its contents:
##
##
## {
##
##   ### in the top level of this dict, keys are tuples
##   ### of the options converted to strings
##
##   ('option1', 'option2', 'option3') : {
##
##      ### the dict in this second level, uses a tuple
##      ### which holds strings representing values of
##      ### different text settings for both normal and
##      ### selected surfaces; the values are ordered
##      ### by the name of the setting they represent
##
##      (
##
##        'True',            # antialiased
##        '(38, 38, 38)',    # background_color
##        '17',              # font_height
##        ENC_SANS_BOLD_FONT_PATH,       # font_path
##        '(238, 238, 238)', # foreground_color
##        '(90, 90, 110)',   # selected_background_color
##        '(210, 110, 210)'  # selected_foreground_color
##
##      ) : {
##
##          ### the dict in the third level has strings
##          ### representing the selected option pointing
##          ### to the resulting surface when that option
##          ### is selected and all others, as a result,
##          ### are deselected
##
##          'option1' : surf_when_option1_selected,
##          'option2' : surf_when_option2_selected,
##          'option3' : surf_when_option3_selected
##
##      }
##
##   }
##
## }
OPTIONS_TO_STYLE_DATA = {}

## nested dictionary used to store tuples of right
## coordinates (integers) in its innermost level;
##
## here's an example of its contents:
##
## {
##
##   ### in the top level of this dict, keys are tuples
##   ### of the options converted to strings
##
##   ('option1', 'option2', 'option3') : {
##
##      ### the dict in this second level, uses a tuple
##      ### which holds strings representing values of
##      ### the text settings that affect the size of the
##      ### text surfaces (not the appearance), since we
##      ### are interested only in the right coordinate of
##      ### the surfaces; the strings are also ordered by
##      ### the name of the corresponding text setting
##
##      (
##
##        '17',       # font_height
##        ENC_SANS_BOLD_FONT_PATH # font_path
##
##      ) : (
##
##        ## finally, in this last level, we have a tuple
##        ## with the values of the right coordinates of
##        ## each option in the OptionTray widget
##        50, 100, 150
##
##      )
##
##   }
##
## }
RIGHT_COORDINATES_MAP = {}


### class definition


class OptionTray(OptionTrayLifetimeOperations, OptionTrayCreationOperations):
    """Like an OptionMenu, but w/ values side by side.

    It doesn't collapse like the option menu, so the sum
    of all of its items' widths must fit the maximum width
    allowed.

    Like the OptionMenu, it is used to select a value among
    a finite set of known values.
    """

    def __init__(
        self,
        value="",
        options=("",),
        max_width=155,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        antialiased=True,
        foreground_color=OPTION_TRAY_FG,
        background_color=OPTION_TRAY_BG,
        selected_foreground_color=(OPTION_TRAY_SELECTED_FG),
        selected_background_color=(OPTION_TRAY_SELECTED_BG),
        name="option_tray",
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        command=empty_function,
    ):
        """Store data and perform setups.

        Parameters
        ==========

        value (string, integer, float, bool or None)
            value assumed by the widget. Must be present
            in the 'options' argument.
        options (iterable of values)
            values the widget is allowed to assume. Each
            value in the options must be of type str, int,
            float, bool or must be None.
        max_width (integer)
            maximum widget width in pixels.
        font_path (string)
            a key used to define which font file to used;
            for available keys, check the FONT_PATH_MAP
            dictionary in textman/font.py.
        font_height (integer)
            font height in pixels.
        antialiased (boolean)
            indicates whether the text should be antialiased
            or not.
        foreground_color (sequence of integers)
            the integers represent the values of red, blue
            and green channels respectively, with values
            from 0 to 255, all inclusive; the color is
            used for the text.
        background_color (sequence of integers)
            same as foreground color, but used for the
            background.
        selected_foreground_color (sequence of integers)
            same as foreground color, but used for the
            foreground of the selected option.
        selected_background_color (sequence of integers)
            same as foreground color, but used for the
            background of the selected option.
        name (string)
            an optional arbitrary string which is stored
            in the 'name' attribute of the instance;
            may be used to help identify the widget.
        coordinates_name (string)
            attribute name of pygame.Rect wherein to set the
            position information from the coordinates value
            parameter.
        coordinates_value (2-tuple of integers)
            represents a position in 2d space; the values of
            x and y axes, respectively.
        command (callable)
            callable executed whenever an option is selected.
        """
        ### store max width, font height and font key

        self.max_width = max_width
        self.font_height = font_height
        self.font_path = font_path

        ### make sure options is a list
        options = list(options)

        ### validate value and options
        self.validate_value_and_options(value, options)

        ### store value and options

        self.value = value
        self.options = options

        ### store other attributes

        self.command = command
        self.name = name

        ### gather text style data for each kind of text
        ### surfaces to be created

        self.normal_text_settings = {
            "font_path": font_path,
            "font_height": font_height,
            "antialiased": antialiased,
            "foreground_color": foreground_color,
            "background_color": background_color,
        }

        self.selected_text_settings = {
            "font_path": font_path,
            "font_height": font_height,
            "antialiased": antialiased,
            "foreground_color": selected_foreground_color,
            "background_color": selected_background_color,
        }

        ### set the surface map and right coordinates
        self.set_surface_map_and_right_coordinates()

        ### position the rect
        setattr(self.rect, coordinates_name, coordinates_value)

    def validate_value_and_options(self, value, options):
        """Check whether value and options are valid.

        Parameters
        ==========
        value, options
            same as defined in the __init__() method's
            docstring.
        """
        ### raise an error if the value isn't within the
        ### available options

        if value not in options:
            raise ValueError("'value' must be listed in 'options'")

        ### raise type error if values aren't python
        ### literals

        if any(not isliteral(item) for item in options):

            raise TypeError("each item in 'options' must be a" " python literal")

        ### raise value error if any value is the same/equal
        ### as any other existing value

        if any(a is b or a == b for a, b in combinations(options, 2)):

            raise ValueError(
                "'options' can't have items which are"
                " identical or equal to one another"
            )

        ### if a maximum width was specified, raise a value
        ### error if sum of the options' widths are not
        ### within that maximum width

        if self.max_width:

            ## calculate sum of options' widths

            total_width = sum(
                get_text_size(
                    str(option),
                    font_height=self.font_height,
                    font_path=self.font_path,
                )[0]
                + 6
                for option in options
            )

            ## compare it with the maximum width allowed

            if total_width > self.max_width:

                raise ValueError(
                    "sum of option width's must not"
                    " surpass given 'max_width' when"
                    " max_width > 0"
                )

    def set_surface_map_and_right_coordinates(self):
        """Reference/create maps of surfaces and coordinates.

        Those are nested dictionaries needed to obtain the
        surfaces needed for the OptionTray as well as
        correctly determining the position of each value
        within its rect so the suitable value can be picked
        when the widget is clicked (actually, when the
        mouse is released over it).

        In this method we also update the 'image' attribute
        and create a new rect for the widget from the new
        surface in that attribute.
        """
        ### create a tuple from the options where each item
        ### is converted into a string
        options_tuple = tuple(map(str, self.options))

        ### using the tuple as a key, try retrieving the
        ### needed dicts;
        ###
        ### the first one associates text styles (settings)
        ### to the respective surface map for that styles;
        ###
        ### the second one associates the text styles
        ### (settings) to the right positions of each option
        ### in the option tray surface

        try:

            styles_to_surface_map = OPTIONS_TO_STYLE_DATA[options_tuple]

            styles_to_right_coordinates = RIGHT_COORDINATES_MAP[options_tuple]

        ### if the first dict doesn't exist, the second one
        ### doesn't exist either, so we create and store
        ### new ones, also referencing them locally

        except KeyError:

            styles_to_surface_map = OPTIONS_TO_STYLE_DATA[options_tuple] = {}

            styles_to_right_coordinates = RIGHT_COORDINATES_MAP[options_tuple] = {}

        ### try retrieving both the surface map and right
        ### coordinates tuple needed, creating them if they
        ### don't exist; they must then be referenced in
        ### specific attributes

        ## put together a custom key used to retrieve
        ## the surface map; it consists of a tuple
        ## holding 02 other tuples representing the text
        ## settings for normal and selected text

        styles_key = settings_to_hashable_repr(
            {
                "selected_foreground_color": (
                    self.selected_text_settings["foreground_color"]
                ),
                "selected_background_color": (
                    self.selected_text_settings["background_color"]
                ),
                **self.normal_text_settings,
            }
        )

        ## put together a custom key used to retrieve the
        ## right coordinates tuple; this one just need the
        ## text settings that affect the size of the text
        ## surfaces; we can ignore the settings which only
        ## affect appearance;

        right_key = settings_to_hashable_repr(
            {"font_path": self.font_path, "font_height": self.font_height}
        )

        ## iterate over the gathered data, retrieving and
        ## referencing the collections, creating and storing
        ## them when they don't exist already

        for attr_name, key, a_map, creation_method in (
            ("surface_map", styles_key, styles_to_surface_map, self.create_surface_map),
            (
                "right_coordinates",
                right_key,
                styles_to_right_coordinates,
                self.create_right_coordinates,
            ),
        ):

            ## try retrieving the needed collection
            try:
                needed_collection = a_map[key]

            ## if a key error is raised, it means the
            ## collection must be created, so we do so by
            ## calling the appropriate method and storing
            ## the created collection in the corresponding
            ## dictionary for when it is needed again

            except KeyError:

                needed_collection = creation_method()
                a_map[key] = needed_collection

            ## finally, we reference the collection in a
            ## dedicated attribute
            setattr(self, attr_name, needed_collection)

        ### assign the image surf
        self.update_image()

        ### also create a rect from it
        self.rect = self.image.get_rect()

    def get_expected_type(self):

        classes = set(map(type, self.options))

        return classes.pop() if len(classes) == 1 else tuple(classes)

    def svg_repr(self):
        """"""
        g = Element("g", {"class": "option_tray"})

        ###

        text_args = [
            (
                str(option),
                get_text_size(
                    str(option),
                    font_height=self.font_height,
                    font_path=self.font_path,
                ),
            )
            for option in self.options
        ]

        ### add bgs and text

        r = self.rect.inflate(-2, -2)

        x = r.x
        y = r.y
        bottom = r.move(0, -3).bottom

        height = r.height

        for option_str, (width, _) in text_args:

            class_name = (
                "selected_bg" if option_str == str(self.value) else "not_selected_bg"
            )

            g.append(
                Element(
                    "rect",
                    {
                        "x": f"{x}",
                        "y": f"{y}",
                        "width": str(width + 6),
                        "height": str(height),
                        "class": class_name,
                    },
                ),
            )

            middle = x + (round((width + 6) / 2))

            text_element = Element(
                "text",
                {
                    "x": f"{middle}",
                    "y": f"{bottom}",
                    "text-anchor": "middle",
                },
            )

            text_element.text = option_str

            g.append(text_element)

            x += width + 6

        return g

    @staticmethod
    def free_up_memory():
        """Free unused memory by clearing up unused objects.

        Used just before loading a new file, so data
        accumulated from the edition of the previous file
        (if there was one) isn't kept around now that
        another file is being loaded.

        The previous file edited might be the one being
        loaded (that is, the file is reloaded). However,
        even if it is the case, this measure should still
        save memory, since data/objects present in
        the past session may not be needed anymore in
        the new session.
        """
        ### clear dictionary used to store surfaces and
        ### other data across multiple nested levels
        OPTIONS_TO_STYLE_DATA.clear()

        ### clear dictionary used to store values of
        ### right coordinates and other data across multiple
        ### nested levels
        RIGHT_COORDINATES_MAP.clear()
