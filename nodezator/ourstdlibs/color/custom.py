"""Utilities for custom color representation/manipulation.

That is, the tools here are used to treat/represent colors
in custom ways, according to our own design.
"""

### local imports

from .property import get_saturation

from .utils import (
    map_colors_by_hue,
    sort_colors_by_luma,
    validate_hex_color_string,
)

from .conversion import (
    hex_string_to_full_rgb,
    full_rgb_to_hex_string,
)

from ..iterutils import separate_by_condition


### formatting related functions


def get_custom_color_format_info(color_value):
    """Return color format name and length of color value.

    The given color_value can be in different formats which
    are explained below. If the function returns without
    raising a ValueError, than we can say the the color
    value is a valid color representation. This is to say
    that this functions can also be used to validate
    color values, not only to retrieve the specific info.

    Parameters
    ==========
    color_value (string or tuple)
        value representing a color or tuple of colors;
        it can be:

        - a string in hex color format:
          e.g.: '#ff0000' or '#ff0000ff'
        - a tuple of integers from 0 to 255 where
          each integer represents the red, green, blue
          and/or alpha channel of a color.
          e.g.: (255, 0, 0) or (255, 0, 0, 255)
        - a tuple populated with strings or
          tuples in the formats presented above
          (you must use the same type for all values)

          e.g.:

            ('#ff0000', '#00ffffee', ...)

            or

            ((255, 0, 0), (0, 255, 255, 255), ...)

    Return value
    ============

    The return value is a 2-tuple with the following values:

    index 0: name of the format of the color value

       e.g.:

         'single_hex'   for '#ffffff'
         'multiple_hex' for ['#ffffff', '#ff0000', ...]
         'single_rgb'   for [255, 0, 0]
         'multiple_hex' for [[255, 0, 0], [0, 0, 255], ...]

    index 1: integer indicating how much colors the value
             actually represents (a length).
    """
    ### perform specific checks for when the color value is
    ### a tuple

    if isinstance(color_value, tuple):

        ## if all items are integers within a valid range
        ## and the length is either 3 or 4, we have a valid
        ## color representation, so we return its info

        if all(
            isinstance(item, int) and 0 <= item <= 255 for item in color_value
        ) and len(color_value) in (3, 4):

            return ("single_rgb", 1)

        ## if all items are all string which pass a custom
        ## validation, we have a valid color representation,
        ## so we return its info

        elif all(
            isinstance(item, str) and validate_hex_color_string(item)
            for item in color_value
        ):

            return ("multiple_hex", len(color_value))

        ## if all items are tuples of length 3 or 4 and
        ## their subitems are integers within a valid
        ## range, then we have a valid color
        ## representation, so we return its info

        elif all(
            isinstance(item, tuple)
            and len(item) in (3, 4)
            and all(
                isinstance(subitem, int) and 0 <= subitem <= 255 for subitem in item
            )
            for item in color_value
        ):
            return ("multiple_rgb", len(color_value))

    ### perform specific check for when the color value is
    ### a string, returning the info in case we have a
    ### a valid color representation (the test passes)

    elif isinstance(color_value, str) and validate_hex_color_string(color_value):
        return ("single_hex", 1)

    ### if we reach this point in the function, it means
    ### no "return" statement were reached since no test
    ### passed; since we don't have a valid color
    ### representation, we raise a ValueError

    raise ValueError(
        "color value must be either an hex string"
        " representing rgb(a) values ('#ffffff') or"
        " a tuple of rgb(a) values as integers"
        " from 0 to 255; you can also provide a"
        " tuple with such values, as long as"
        " you use the same type for all values"
    )


def custom_format_color(color_value, color_format, alone_when_single):
    """Return color value converted to specified format.

    Parameters
    ==========
    color_value (string or tuple)
        a value representing a color or multiple colors,
        as accepted by the get_custom_color_format_info
        function.
    color_format (string)
        either 'rgb_tuple' or 'hex_string';
        indicates whether individual colors are represented
        by tuples or strings.
    alone_when_single (bool)
        whether an individual color must appear alone
        rather than within a tuple of length 1 when
        it is the only color represented by the color
        value.
    """
    ### retrieve the current format name and length of
    ### color value

    format_name, length = get_custom_color_format_info(color_value)

    ### make it so the color value is treated as multiple
    ### color values if it represents a single color
    if "single" in format_name:
        color_value = (color_value,)

    ### if the requested color format is rgb integers but
    ### the format name indicates the colors are represented
    ### by hex strings, convert each item from hex strings
    ### to rgb(a) colors

    if color_format == "rgb_tuple" and "hex" in format_name:

        color_value = tuple(hex_string_to_full_rgb(item) for item in color_value)

    ### if, otherwise, the requested color format is hex
    ### string, but the format name indicates the colors are
    ### represented by rgb(a) colors (tuples), convert each
    ### string into its respective tuple of rgb(a) values

    elif color_format == "hex_string" and "rgb" in format_name:

        color_value = tuple(full_rgb_to_hex_string(item) for item in color_value)

    ### if the color value represents a single color and
    ### it was requested that the color itself is used when
    ### alone, replace the color value by the single value
    ### it contains

    if length == 1 and alone_when_single:
        color_value = color_value[0]

    ### finally return the color value
    return color_value


### TODO explain parameters in docstring below


def validate_custom_color_format(color_value, color_format, alone_when_single):
    """Raise error if value or its type isn't valid.

    This is different from the validation provided by
    the get_custom_color_format_info function, cause it
    evaluates an specific subset of the possible valid color
    representations.
    """
    ### get the format name and length of the color value
    format_name, length = get_custom_color_format_info(color_value)

    ### if the color format requested is rgb integers but
    ### the color value isn't or doesn't contain rgb
    ### values, raise a TypeError

    if color_format == "rgb_tuple" and "rgb" not in format_name:

        raise TypeError(
            "since the 'color_format' argument"
            " was set to 'rgb_tuple', individual"
            " colors must be represented by a tuple"
            " of integers representing rgb(a) values"
            " with 0 <= integer <= 255"
        )

    ### if the color format requested is hex string but
    ### the color value isn't or doesn't contain hex
    ### strings, raise a TypeError

    elif color_format == "hex_string" and "hex" not in format_name:

        raise TypeError(
            "since the 'color_format' was set to"
            " 'hex_string', individual colors must be"
            " represented by a string formated as an "
            " hex color string; for instance, '#ffffff'"
            " or '#ffffffff'"
        )

    ### if the color value represents a single color
    ### and is requested to use the color itself as
    ### the color value (the alone_when_single is True),
    ### but instead it is represented by a tuple of color
    ### values (thus containing the 'multiple' substring in
    ### its format_name), raise a ValueError

    if length == 1 and alone_when_single and "multiple" in format_name:

        raise ValueError(
            "when color value represents a single"
            " color, it must be the color itself,"
            " not a tuple of colors of length 1"
        )

    ### if the color value represents a single color but
    ### otherwise it is requested to not use the color
    ### itself as the color value (the alone_when_single
    ### is False) and it is not represented by a tuple
    ### of color values but rather the color itself (thus
    ### containing the 'single' substring in its
    ### format_name), raise a ValueError

    elif length == 1 and not alone_when_single and "single" in format_name:

        raise ValueError(
            "when the color value represents a single"
            " color, it must still be a tuple of"
            " colors with length 1, not the color"
            " itself"
        )

    ### if we reach this point in the function, it means
    ### no error was raised; we return the format name and
    ### length of the color value to indicate the validation
    ### was sucessful (since we can return any "truthful"
    ### value, we decide on this info, so it can optionally
    ### be reused when needed after validating a color value)
    return format_name, length


### custom sorting function
###
### ideal for sorting somewhat large collections of colors
### of varying hues (as opposed to small color palletes,
### for instance)


def get_custom_sorted_colors(colors):
    """Return a list of custom-sorted colors from given one.

    A custom algorithm (though I prefer using the word
    "recipe" here) is used based on what we believe to
    be a good way of organizing a somewhat large list of
    colors.

    Parameters
    ==========

    colors (list of colors)
        colors are sequence of integers; such integers
        are in the range(256) and represent the values
        of the red, green and blue channel of a color;

        a fourth integer may also be present, representing
        the value for the color's alpha channel, but we
        don't consider it to be relevant for our sorting
        operation, so it is not taken into account.

    Alternative implementation
    ==========================

    Just thought it would be interesting to mention that
    this function could also be implemented as a
    function to use as the key of list.sort or the
    "sorted" built-in function, instead of returning
    a new list as we in this function.

    However I think presenting the steps as done in this
    function makes it easier to understand and maintain
    this function.

    Nonetheless, the alternative implementation is not only
    interesting, but it also takes only 60% (roughly) of
    the time the current implementation takes to sort the
    colors (maybe cause the current implementation creates
    a new list). The alternative implementation can be
    found below just after the definition of this function,
    commented out.
    """
    ### separate the colors into those which have no
    ### saturation and the ones which have

    no_sat_colors, colors_with_saturation = separate_by_condition(
        colors, get_saturation
    )

    ### sort the colors without saturation by their
    ### luma
    no_sat_colors.sort(key=sort_colors_by_luma)

    ### for the colors with saturation, create a dict
    ### which maps strings like 'red', 'orange', 'yellow',
    ### 'green', etc. (names of basic colors), to a set
    ### of hue values closer to such basic colors;
    ###
    ### for instance, the 'red' field will have a list
    ### of colors whose hues are closer to red;
    ###
    ### the dict is a collections.OrderedDict instance
    ### with items ordered according to how the hue
    ### naturally progresses from 0 to 359
    hue_name_to_colors = map_colors_by_hue(colors_with_saturation)

    ### we are only interested in the values of such
    ### dict (the lists of colors)
    color_lists = hue_name_to_colors.values()

    ### now, iterate over the lists sorting the colors
    ### of that list by luma
    for color_list in color_lists:
        color_list.sort(key=sort_colors_by_luma)

    ### then, concatenate all lists of colors and
    ### also the list of colors with no saturation
    ### into a single list of colors
    ###
    ### this list will have the colors in a logical
    ### and somewhat pleasing distribution: colors
    ### without saturation first, sorted by luma,
    ### then colors with saturation grouped by their
    ### hues and with each of those groups further
    ### sorted by luma
    colors = sum(color_lists, no_sat_colors)

    ### finally, return such list
    return colors


#    Alternative implementation of function above
#    ============================================
#
#    This alternative implementation uses hue and
#    lightness whereas the current implementation uses
#    luma, since I believe using luma results in a more
#    pleasing sorting. If it is ever to be used, just
#    replace the lightness for luma where appropriate.
#
#    Pseudocode
#    **********
#
#    0) convert full rgb color into full hls color
#
#    1) if the color's has no saturation (saturation is 0),
#       return (saturation, lightness)
#
#    2) otherwise, retrieve the name of specific sets of
#       hue values to which the color belongs and attribute
#       an arbitrary index to it, 1 for 'red', 2 for 'orange'
#       and so on, then return (index, lightness);
#
#       note that the hue index begin from 1,
#       in order to guarantee that the colors with
#       saturation always appear after the ones without
#       saturation (since the ones without saturation
#       always have 0 as the first index of the tuple
#       returned to use as their sorting indices)
#
#    Code
#    ****
#
#    from ourstdlibs.color.utils     import full_rgb_to_full_hls
#    from ourstdlibs.color.constants import HUE_SETS_MAP
#
#    def get_custom_color_sorting_indices(color):
#        """Return a tuple with values to sort a given color.
#
#        Sorting is performed according to a custom
#        recipe/algorithm which makes it so colors with no
#        saturation appear first, that is, black, greys and
#        white, and only after the colors with saturation
#        appears, grouped together according to the value of
#        their hue and further sorted according to their
#        lightness.
#        """
#
#        ### obtain the full hls color, divided into variables
#        ### holding the individual values
#
#        (
#          hue,
#          lightness,
#          saturation
#        ) = full_rgb_to_full_hls(color)
#
#        ### if the color has no saturation, return a tuple
#        ### with the saturation and lightness
#        ###
#        ### since the saturation is zero and is used as the
#        ### first index in the tuple returned for sorting,
#        ### colors without saturation will always appear
#        ### before the ones with saturation
#        if not saturation: return (saturation, lightness)
#
#        ### otherwise, if the color has saturation,
#        ### we return a tuple which is comprised by
#        ### an arbitrary index representing a set of
#        ### hue values to which the color belongs and
#        ### the color's lightness
#        ###
#        ### since the hue index is always greater than 0,
#        ### the colors with saturation will appear after
#        ### after all colors without saturation
#        ###
#        ### colors whose hue belong to the same set of
#        ### hue values will be grouped together, further
#        ### sorted by the second value in the tuple,
#        ### which is the lightness
#
#        else:
#
#            ### create an enumeration which we'll use as
#            ### provide of pairs comprised by an arbitrary
#            ### hue index greater than 1 and the range of
#            ### hue values that hue index represents
#            enumeration = enumerate(
#                            HUE_SETS_MAP.values(), start=1
#                          )
#
#            ### if the color's hue is within the given range,
#            ### break out of the "for loop" so that the
#            ### hue_index variable keep representing the
#            ### index for such range of values
#            for hue_index, range_obj in enumeration:
#                if hue in range_obj: break
#
#            ### then return the tuple with the index and
#            ### lightness
#            return (hue_index, lightness)
