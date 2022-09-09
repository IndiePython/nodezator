"""Color-related utilities."""

### standard library imports

from string import hexdigits

from collections import OrderedDict

from functools import partial


### local imports

from ..iterutils import get_type_yielder

from .largemaps import (
    HTML_COLOR_MAP,
    PYGAME_COLOR_MAP,
)

from .constants import HUE_SETS_MAP

from .property import (
    PROPERTY_GETTER_MAP,
    get_hue,
)


def validate_hex_color_string(hex_string):
    """Return True if received a valid hex color string.

    Parameters
    ==========
    hex_string (string)
        string in '#XXXXXX' or '#XXXXXXXX' format, where
        each pair of characters (except the leading '#')
        is the hexadecimal representation of an integer
        from 0 to 255 (all inclusive) further representing
        the value of a channel of a RGB(A) color.
    """
    ### string can't be empty
    if not hex_string:
        return False

    ### first character must be '#'
    if hex_string[0] != "#":
        return False

    ### remove '#' before continuing
    hex_string = hex_string[1:]

    ### remaining characters must count 6 or 8 (that is,
    ### there must be 2 characters for each channel,
    ### red, green, blue and, in some cases, alpha too)
    if not len(hex_string) in (6, 8):
        return False

    ### before continuing, make string all lowercase
    hex_string = hex_string.lower()

    ### characters must all be characters used in
    ### hexadecimal representations

    if any(char not in hexdigits for char in hex_string):
        return False

    ### if every test above passed (none of them returned),
    ### it means the string is valid, so return True
    return True


def validate_color_name(valid_names, color_name):
    """Return True if string is a valid color name."""
    ### remove spaces and make string all lowercase
    color_name = color_name.replace(" ", "").lower()

    ### if name of color is a key in our collection of
    ### valid names then we have a valid color name,
    ### so we return True
    if color_name in valid_names:
        return True

    ### even though 'unamed' doesn't represent an existing
    ### color, we consider it a valid name, so we return True
    ### as well
    elif color_name == "unamed":
        return True

    ### otherwise the name is not valid, so False is returned
    else:
        return False


validate_html_color_name = partial(
    validate_color_name,
    HTML_COLOR_MAP.keys(),
)

validate_pygame_color_name = partial(
    validate_color_name,
    PYGAME_COLOR_MAP.keys(),
)


def format_color_name(color_name):
    """Remove spaces, make lowercase and return string."""
    return color_name.replace(" ", "").lower()


### utility function to custom display full color values


def get_int_sequence_repr(values):
    """Return custom string representing integer sequence.

    The custom format is obtained by justifying the spacing
    between the values so they are equal, even when the
    values have a different number of digits originally.

    It is intended to use with lists, tuples and other
    sequences, even though we use square brackets to
    surround the values, since the important thing here
    is to correctly space the integer values for easier
    viewing.

    Handy to display the value of colors in their full
    forms (when they are not in unit interval).

    Parameters
    ==========
    values (iterable of integers)
    """
    return (
        ### opening square bracket
        "["
        ### comma separated values (with a space after each
        ### comma), right-justified to always occupy 03 spaces
        + ", ".join(str(value).rjust(3, " ") for value in values)
        ### closing square bracket
        + "]"
    )


### color sorting

string_yielder = get_type_yielder(types_to_yield=(str))


def get_color_sorter_by_properties(*property_names):
    """Return color sorter function which uses properties.

    Parameters
    ==========
    *property_names (strings)
        names of color properties to retrieve from the
        given color;

        the strings can be delivered as different arguments,
        in the same iterable, in different iterables and
        even further nested in complex structures.
    """
    ### guarantee that property_names is an tuple that
    ### contains strings
    ###
    ### this is the measure that allows the property_names
    ### argument to be so flexible is its format; as long
    ### you provide strings, we find them
    property_names = tuple(string_yielder(property_names))

    ### define the function to process each given color

    def color_sorter(rgba_color):
        """Return tuple w/ requested properties from color.

        Parameters
        ==========
        rgba_color (list of integers)
            integers are in the range(256) and represent
            values from red, green and blue channels,
            respectively;
            a fourth integer may also be present, representing
            the value of the alpha channel of the color.
        """
        ### return a tuple with the values of each requested
        ### property

        return tuple(
            ## using the name of the property, get a function
            ## to retrieve such property from the color, passing
            ## the color to the function...
            PROPERTY_GETTER_MAP[property_name](rgba_color)
            ## ...for each listed property
            for property_name in property_names
        )

    ### finally return the defined function
    return color_sorter


## function to sort colors by their luma
sort_colors_by_luma = get_color_sorter_by_properties("luma")


### color mapping


def get_color_mapper_by_range(range_map, property_getter):
    """Return function to map colors into specific ranges.

    Such ranges are arbitrary ranges defined for a requested
    property.

    Parameters
    ==========

    range_map (dict)
        a dict where each key is a string representing
        a name for the specific range and the respective
        value is a range object (or other iterable with
        integers) representing the possible full values
        the property of a color can assume to be considered
        a member of that range;

        note that the "full value" of the property is used,
        rather than its "unit value" (its value in the
        unit interval).

        that is, the value is used for membership test
        (using the 'in' operation);

    property_getter (callable)
        callable which, given a color, returns the value
        of the requested property;

        in other words, the property requested is chosen
        by passing the appropriate getter.
    """
    ### define the color mapper function

    def color_mapper(colors):
        """Map colors according to specified settings.

        Parameters
        ==========

        colors (iterable of colors)
            we iterate over this argument, append each color
            to its corresponding range depending on the
            value of the requested property;

            each color is a sequence of integers in the
            range(256), representing the values of the
            red, green and blue channel of a color;
            a fourth integer may also be present,
            representing the value for the color's alpha
            channel.
        """
        ### create an ordered dict and fill it using names
        ### provided in the range map as the keys and
        ### empty lists as values

        name_to_list = OrderedDict()
        for name in range_map:
            name_to_list[name] = []

        ### iterate over the given colors, appending them to
        ### the appropriate lists depending on the value of
        ### the requested property, that is, depending on
        ### which range they fit

        for rgba_color in colors:

            ### retrieve value of the property (it is in its
            ### unit form here, that is, in the unit interval)
            property_value = property_getter(rgba_color)

            ### iterate over the items from the range map,
            ### until you find the item whose range has the
            ### value we retrieved from the property

            for name, range_obj in range_map.items():
                if property_value in range_obj:
                    break

            ### now that we found the range in which our
            ### property value fits, we append the color
            ### to the list associated with the name of
            ### that range
            name_to_list[name].append(rgba_color)

        ### once finished, return the dictionary we created
        return name_to_list

    ### return the defined color mapper function
    return color_mapper


## function to map colors by their hue

map_colors_by_hue = get_color_mapper_by_range(HUE_SETS_MAP, get_hue)
