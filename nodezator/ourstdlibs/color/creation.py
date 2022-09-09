### standard library imports

from random import choice

from colorsys import (
    rgb_to_hls,
    hls_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_to_yiq,
    yiq_to_rgb,
)


from .constants import HLS_FACTORS, HSV_FACTORS, HLS_NAMES, RGBA_NAMES


### random color generation

## TODO this function should probably be refactored to use
## functions from ourstdlibs.color.conversion instead of
## making all conversion by itself; this would also be
## better because all conversion would be in a single
## place


def random_color_from_existing(color, property_to_randomize):
    """Return new color from given one w/ randomized property.

    Parameters
    ==========
    color (sequence of integers)
        integers representing RGB(A) values so that
        0 <= integer <= 255.
    property_to_randomize (string)
        property of the color one wishes to randomize;
        must be one of the following values: 'hue',
        'lightness', 'saturation', 'value', 'red',
        'green', 'blue' or 'alpha'.
    """
    ### make sure color is a list
    color = list(color)

    ### convert the color into into its "unit" rgb version,
    ### that is, a sequence containing rgb values where
    ### each value is a float such that 0.0 <= float <= 1.0;
    unit_rgb = [value / 255 for value in color[:3]]

    ### perform specific operations if property to randomize
    ### is from the HLS model

    if property_to_randomize in HLS_NAMES:

        ## convert from unit rgb to unit hls
        unit_hls = rgb_to_hls(*unit_rgb)

        ## convert values from floats to integers
        ## using the specific factors

        hls = [round(value * factor) for value, factor in zip(unit_hls, HLS_FACTORS)]

        ## retrieve the index of the given property
        index = HLS_NAMES.index(property_to_randomize)

        ## get the maximum value the property can assume
        maximum = HLS_FACTORS[index]

        ## then pick a random value for the property
        ## within the allowed range
        hls[index] = choice(range(maximum + 1))

        ## when randomizing the lightness (index is 1),
        ## we must prevent the color from going white or
        ## black by clamping the lightness to 1 if 0 and
        ## 99 if 100, otherwise the hue would be lost when
        ## converted

        if index == 1 and hls[1] in (0, 100):
            hls[1] = 1 if hls[1] == 0 else 99

        ## when randomizing the saturation (index is 2),
        ## we must prevent the hue from being lost if the
        ## saturation is 0, by setting it to 1
        if index == 2 and hls[2] == 0:
            hls[2] = 1

        ## now convert back the integers into floats in the
        ## unit interval and then back from unit hls into
        ## unit rgb

        unit_hls = [value / factor for value, factor in zip(hls, HLS_FACTORS)]

        unit_rgb = hls_to_rgb(*unit_hls)

        ## now we just need to convert the rgb values
        ## from floats into integers and add the alpha
        ## back if there was one

        final_color = [round(value * 255) for value in unit_rgb]

        try:
            final_color.append(color[3])
        except IndexError:
            pass

    ### perform specific operations if the property to
    ### randomize is 'value' (from the HSV model)

    elif property_to_randomize == "value":

        ## convert from unit rgb to unit hsv
        unit_hsv = rgb_to_hsv(*unit_rgb)

        ## convert values from floats to integers
        ## using the specific factors

        hsv = [
            round(value * factor) for value, factor in zip(unit_hsv, HLS_HSV_FACTORS)
        ]

        ## get the maximum value the property can assume
        maximum = HSV_FACTORS[2]

        ## then pick a random value for the property
        ## within the allowed range
        hsv[index] = choice(range(maximum + 1))

        ## now convert back the integers into floats in the
        ## unit interval and then back from unit hsv into
        ## unit rgb

        unit_hsv = [value / factor for value, factor in zip(hsv, HSV_FACTORS)]

        unit_rgb = hsv_to_rgb(*unit_hsv)

        ## now we just need to convert the rgb values
        ## from floats into integers and add the alpha
        ## back if there was one

        final_color = [round(value * 255) for value in unit_rgb]

        try:
            final_color.append(color[3])
        except IndexError:
            pass

    ### perform specific operations if the property to
    ### randomize is 'luma' (the 'Y' of the YIQ model)

    elif property_to_randomize == "luma":

        ## convert from unit rgb to yiq values
        y, i, q = rgb_to_yiq(*unit_rgb)

        ## replace y by a random integer in the range(256)
        ## converted to the unit interval
        y = choice(range(256)) / 255

        ## now convert yiq components back to full rgb
        unit_rgb = yiq_to_rgb(y, i, q)

        ## now we just need to convert the rgb values
        ## from floats into integers and add the alpha
        ## back if there was one

        final_color = [round(value * 255) for value in unit_rgb]

        try:
            final_color.append(color[3])
        except IndexError:
            pass

    ### perform specific operations if the property to
    ### randomize is from the RGBA model

    elif property_to_randomize in RGBA_NAMES:

        ## define whether the color has alpha and define
        ## the alpha value based on such information

        has_alpha = len(color) == 4

        rgba = color + [255] if not has_alpha else color[:]

        ## now randomize the requested property

        index = RGBA_NAMES.index(property_to_randomize)
        rgba[index] = choice(range(256))

        ## define the final color based on whether the
        ## original color had alpha or not
        final_color = rgba if has_alpha else rgba[:3]

        ## use the alpha in final color regardless of the
        ## 'has_alpha' value if the property randomized
        ## was the alpha
        if property_to_randomize == "alpha":
            final_color = rgba

    ### if the property to randomize don't fit any of
    ### the models, raise a ValueError explaining the
    ### requirement

    else:

        raise ValueError(
            "'property_to_randomize' must be 'hue',"
            " 'lightness', 'saturation', 'value',"
            " 'red', 'green', 'blue' or 'alpha'"
        )

    ### finally return the randomized color as a tuple
    return tuple(final_color)


### choosing between black and white for contrast


def get_contrasting_bw(color):
    """Return black or white, whichever constrasts more.

    That is, whichever contrasts more with the given color.

    Parameters
    ==========
    color (tuple or list with rgb(a) values)
        values are integers ranging from 0 to 255
        (0 <= integer <= 255) and representing values of
        the RGB(A) channels of a color (though the alpha
        color is ignored here if it exists).
    """
    ### only consider the first three values
    color = color[:3]

    ### make it so the values are within the unit interval
    ### (float such that  0.0 <= float <= 1.0)
    color = tuple(item / 255 for item in color)

    ### get the luma from the rgb color
    luma = rgb_to_yiq(*color)[0]

    ### if luma is greater than 50%, return black,
    ### otherwise return white
    return (0, 0, 0) if luma > 0.5 else (255, 255, 255)
