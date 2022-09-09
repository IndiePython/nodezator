"""Conversion between common color systems/formats."""

### standard library imports

from colorsys import (
    hls_to_rgb,
    rgb_to_hls,
    hsv_to_rgb,
    rgb_to_hsv,
    rgb_to_yiq,
)

from functools import partial


### local imports

from .largemaps import (
    HTML_COLOR_MAP,
    PYGAME_COLOR_MAP,
)

from .constants import (
    RGBA_FACTOR,
    HLS_FACTORS,
    HSV_FACTORS,
)


### other colorsystem conversions

hls_to_hsv = lambda h, l, s: rgb_to_hsv(*hls_to_rgb(h, l, s))
hsv_to_hls = lambda h, s, v: rgb_to_hls(*hsv_to_rgb(h, s, v))


### common conversions

full_to_unit_rgba = lambda color: tuple(value / RGBA_FACTOR for value in color)

unit_to_full_rgba = lambda color: tuple(round(value * RGBA_FACTOR) for value in color)

full_to_unit_hls = lambda color: tuple(
    value / factor for value, factor in zip(color, HLS_FACTORS)
)

unit_to_full_hls = lambda color: tuple(
    round(value * factor) for value, factor in zip(color, HLS_FACTORS)
)

full_to_unit_hsv = lambda color: tuple(
    value / factor for value, factor in zip(color, HSV_FACTORS)
)

unit_to_full_hsv = lambda color: tuple(
    round(value * factor) for value, factor in zip(color, HSV_FACTORS)
)

full_rgb_to_hsv = lambda color: unit_to_full_hsv(rgb_to_hsv(*full_to_unit_rgba(color)))

full_rgb_to_hls = lambda color: unit_to_full_hls(rgb_to_hls(*full_to_unit_rgba(color)))

full_hls_to_rgb = lambda color: unit_to_full_rgba(hls_to_rgb(*full_to_unit_hls(color)))

full_hls_to_hsv = lambda color: unit_to_full_hsv(hls_to_hsv(*full_to_unit_hls(color)))

full_hsv_to_rgb = lambda color: unit_to_full_rgba(hsv_to_rgb(*full_to_unit_hsv(color)))

full_hsv_to_hls = lambda color: unit_to_full_hls(hsv_to_hls(*full_to_unit_hsv(color)))


### map to store specific conversion functions for colors
### represented by sequence of values in different color
### systems

COLOR_CONVERSION_MAP = {
    ## conversions from rgb
    "rgb": {
        "hls": full_rgb_to_hls,
        "hsv": full_rgb_to_hsv,
    },
    ## conversions from hls
    "hls": {
        "rgb": full_hls_to_rgb,
        "hsv": full_hls_to_hsv,
    },
    ## conversions from hsv
    "hsv": {"rgb": full_hsv_to_rgb, "hls": full_hsv_to_hls},
}

### yiq colorsystem

full_rgba_to_yiq = lambda full_rgba: rgb_to_yiq(*full_to_unit_rgba(full_rgba[:3]))

full_rgba_to_luma = lambda full_rgba: (round(full_rgba_to_yiq(full_rgba[:3])[0] * 255))

full_rgba_to_luma_grey = lambda full_rgba: (full_rgba_to_luma(full_rgba),) * 3

yiq_to_full_rgb = lambda yiq: unit_to_full_rgba(yiq_to_rgb(*yiq))


### common conversion/validation/formatting operations


def hex_string_to_full_rgb(hex_string):
    """Convert hex string into RGB(A) tuple and return it.

    RGB(A) values are integers in the range(256).

    Parameters
    ==========
    hex_string (string)
        string in the '#XXXXXX' or '#XXXXXXXX' format,
        where each pair of characters (excluding the '#')
        is an hexadecimal representation of an integer in
        the range(256), which represents one of the red,
        green and blue channels (maybe alpha as well)
        of a color.
    """
    ### remove '#' from string
    hex_string = hex_string[1:]

    ### convert each pair of characters into its
    ### respective integer (of base 16) value and return
    ### the resulting tuple

    return tuple(int(hex_string[i : i + 2], 16) for i in range(0, len(hex_string), 2))


def int_to_custom_hex(integer):
    """Return custom hex string representation for integer.

    Parameters
    ==========
    integer (integer)
        value to be converted.

    Doctests
    ========

    >>> int_to_custom_hex(100)
    '64'
    >>> int_to_custom_hex(4)
    '04'
    >>> int_to_custom_hex(12)
    '0c'
    >>> white = (255, 255, 255)
    >>> '#' + ''.join(int_to_custom_hex(i) for i in white)
    '#ffffff'
    """
    return hex(integer)[2:].rjust(2, "0")


def full_rgb_to_hex_string(full_rgba):
    """Return '#XXXXXX' formated string representing color.

    Parameters
    ==========
    full_rgba (sequence of integers)
        integers are in the range(256) and represent the
        values of the red, green and blue channel of a
        color; a fourth integer may also be present,
        representing the value for the color's alpha
        channel.
    """
    return (
        ### start string with a '#' character
        "#"
        ### then add a string obtained by converting each
        ### integer from the full rgba color into a custom
        ### hexadecimal representation
        + "".join(int_to_custom_hex(value) for value in full_rgba)
    )


def full_rgb_to_color_name(color_map, full_rgba):
    """Return string representing name of color.

    If a name is not assigned to such color, 'unamed' is
    returned instead.

    Parameters
    ==========
    full_rgba (sequence of integers)
        integers are in the range(256) and represent the
        values of the red, green and blue channel of a
        color; a fourth integer may also be present,
        representing the value for the color's alpha
        channel.
    """
    ### convert color into tuple, using only the three first
    ### values (red, blue and green)
    color = tuple(full_rgba[:3])

    ### iterate over the items of the color map,
    ### checking whether the color match with any listed
    ### color, returning the corresponding name in such case

    for name, value in color_map.items():

        if color == value:
            return name

    ### if no name is found instead, we return the 'unamed'
    ### string
    else:
        return "unamed"


full_rgb_to_html_name = partial(
    full_rgb_to_color_name,
    HTML_COLOR_MAP,
)

full_rgb_to_pygame_name = partial(
    full_rgb_to_color_name,
    PYGAME_COLOR_MAP,
)
