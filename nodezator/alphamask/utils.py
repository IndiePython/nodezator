"""Facility w/ utility functions for the AlphaMask class.

Module contents
===============

size_from_alpha_values (function)
    returns size from any collection representing alpha
    values (either in full or unit format)
unit_from_full_alpha_values (function)
    return collection of unit alpha values by converting
    full alpha values.
full_from_unit_alpha_values (function)
    return collection of full alpha values by converting
    unit alpha values.
full_alpha_values_from_surface (function)
    return list of lists representing alpha values.
"""

### standard library import
from math import inf as INFINITY


### third-party imports

from pygame import Rect

from pygame.surfarray import pixels_alpha


def size_from_alpha_values(alpha_values):
    """Return size of alpha mask.

    Parameters
    ==========
    alpha_values (list of lists)
        alpha values, either in full or unit form.
    """
    return (
        ### number of columns == width
        len(alpha_values),
        ### number of items in column == height
        len(alpha_values[0]),
    )


def unit_from_full_alpha_values(full_alpha_values):
    """Return new alpha values converted to unit intervals.

    That is, we create and return a copy of the list of
    lists representing full alpha values, but with the items
    converted to floats in the unit interval (from 0.000...
    to 1.0, that is, fully transparent to fully opaque), or
    in other words, floats representing the percentage of
    the alpha (how much opaque a pixel in that position is).
    """
    ### return new list representing alpha values in their
    ### unit form

    return [
        ## the inner lists represent the alpha values of
        ## each column of pixels, in their unit form
        [
            ## the unit format is obtained by simply dividing
            ## the full alpha values by the maximum value they
            ## can assume, resulting in a float which
            ## represents the percentage of the alpha value
            alpha_value / 255
            for alpha_value in alpha_values_in_column
        ]
        ## the alpha values for each column are retrieved
        ## from the given full alpha values list
        for alpha_values_in_column in full_alpha_values
    ]


def full_from_unit_alpha_values(unit_alpha_values):
    """Return new alpha values converted to full values.

    This is the reverse of the unit_from_full_alpha_values()
    function, which means we convert floats in the unit
    interval to full alpha values, that is, integers in
    range(256), where 0 means fully transparent and 255
    means fully opaque.
    """
    ### return new list representing alpha values in their
    ### full form

    return [
        ## the inner lists represent the alpha values of
        ## each column of pixels, in their full form
        [
            ## the full format is obtained by simply multiplying
            ## the unit alpha values by the maximum value the
            ## full values can assume and rounding the result,
            ## which ultimately results in an integer in the
            ## range(256)
            round(unit_alpha_value * 255)
            for unit_alpha_value in unit_alpha_values_in_column
        ]
        ## the alpha values for each column are retrieved
        ## from the given unit alpha values list
        for unit_alpha_values_in_column in unit_alpha_values
    ]


def full_alpha_values_from_surface(surf):
    """Return list of lists representing alpha values.

    Parameters
    ==========
    surf (pygame.Surface instance)
        surface used as source of alpha values.

    How it works
    ============

    The alpha values are stored as a list containing
    other lists. That is, the top list holds lists
    which represent columns of the source surface
    and hold the alpha value of each pixel in that
    column.

    To be more specific, the columns are listed from
    the leftmost to the rightmost pixel column of the
    source surface and the values within each column
    correspond to the values from the pixel at the top
    of column to the one at its bottom.

    This list of lists is meant to be used in the
    AlphaMask.mask_by_replacing() masking operation
    whenever needed.
    """
    ### copy the alpha values of the surface in a lists
    ### of lists with the same structure as the numpy array
    ### obtained with pixels_alpha(surf)
    ###
    ### why do we copy the values of the array instead
    ### of using the array iteself? we don't do so because
    ### though the array is indeed faster than normal Python
    ### lists for certain operations, it is slower for other
    ### kind of operations;
    ###
    ### since we only want to keep the alpha values to
    ### iterate over them, using normal Python lists is
    ### way faster, which is why we keep the values of
    ### the array as a list of lists;
    ###
    ### additionally, we convert the numpy integers (uint
    ### class) to regular Python integers; we do so because
    ### the AlphaMask.subtract() operation causes an
    ### RuntimeWarning to be issued with the message
    ### "overflow encountered in ubyte_scalars"; though
    ### not versed in the inner workings of uint objects,
    ### the practical effect of this is that such operation
    ### doesn't produce the desired behaviour; converting
    ### the uint instaces to int instances in this method
    ### fixes the problem;
    ###
    ### however, this affects some of the masking operations,
    ### making some operations faster (mask_by_multiplying())
    ### and other operations slower (mask_by_replacing());
    ###
    ### the differences in speed for such operations as well
    ### as for other operations which we didn't measure
    ### aren't considered relevant, though, since no matter
    ### the differences that may exist, they not only may
    ### benefit us (as with the mask_by_multiplying()
    ### method), but even when they would not (as with the
    ### mask_by_replacing() method), the differences
    ### observed in practice cannot be perceived by a human;

    return [
        list(map(int, alpha_values_in_column))
        for alpha_values_in_column in pixels_alpha(surf)
    ]
