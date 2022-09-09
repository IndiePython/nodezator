"""Facility w/ operations between masks for AlphaMask class.

Module contents
===============

AlphaMaskOperationsBetweenMasks (class)
    class used as an extension for the AlphaMask class;
    it contains operations one can perform between 02 or
    more masks.

Besides the class defined here, there are also other
functions to support the class' operations, which are
pretty self-contained and will be presented in their
own docstrings rather than here.


Class operations
================

The operations between masks presented here are akin to
common arithmetic operations performed between numbers.
The difference is that the numbers are the alpha values
(either in their full or unit form) from different masks.

In other words, the operating between masks consists of
taking the alpha values of the instance and those of other
given masks and applying operations on the alpha values
situated at the same position, generating a new alpha
value for each position. For regular operations, these
new values are used to return a new masks and, for the
in-place operations, these new values replace the original
values in the instance performing the operation.
"""

### standard library imports

from functools import reduce, partialmethod

from operator import sub, mul


### local imports

from .utils import (
    size_from_alpha_values,
    unit_from_full_alpha_values,
    full_from_unit_alpha_values,
)


### support operations (there are more after class
### definition; these ones are defined first cause
### they are needed in the class definition just below)

multiply_values = lambda values: reduce(mul, values)
subtract_values = lambda values: max(reduce(sub, values), 0)


### class definition


class AlphaMaskOperationsBetweenMasks:
    """Provides operations between AlphaMask instances."""

    ### methods for operating on full alpha values and
    ### unit alpha values from multiple masks, as well as
    ### their partial implementations;

    ## notes about the partial implementations:
    ##
    ## the max() operation and its in-place version is
    ## good to combine different masks into one, like
    ## obtaining an union of the masks' areas;
    ##
    ## the min() and multiply() operations, and their
    ## in-place versions, are good to obtain the area of
    ## intersection between masks;
    ##
    ## the subtract() operation and its in-place version is
    ## good to obtain the area representing the difference
    ## between the given masks;

    def operate_on_full(self, operation, *alpha_masks):
        """Return new mask by operating on full alpha values.

        Works by traversing the full alpha values of all
        masks performing an operation in the values in the
        same position, using the results as the full alpha
        values for a new mask which is returned.

        This method is used to produce partial
        implementations for specific operations.

        Parameters
        ==========

        operation (callable)
            the full alpha values in the same position,
            from the masks, are passed to this function
            in the form of a tuple; thus, it must accept
            a single argument.
        alpha_masks (masking.alpha.AlphaMask instances)
            one or more alpha masks instances which, along
            with this instance, will have their full alpha
            values in the same position passed together to
            the given operation.
        """
        return (
            ### return new AlphaMask instance from the full
            ### alpha values obtained
            self.__class__.from_full_alpha_values(
                ## get full alpha values from
                ## this function
                map_alpha_at_same_positions(
                    ## which, receives an operation
                    operation,
                    ## and also the full alpha
                    ## values from this mask as
                    ## well as from the given ones
                    *(mask.full_alpha_values for mask in (self, *alpha_masks))
                )
            )
        )

    maximum = partialmethod(operate_on_full, max)
    minimum = partialmethod(operate_on_full, min)
    subtract = partialmethod(operate_on_full, subtract_values)

    def operate_on_full_ip(self, operation, *alpha_masks):
        """In-place equivalent of operate_on_full().

        That is, works just like operate_on_full(), but
        instead of returning a new mask, the full alpha
        values replace the full alpha values of this
        instance, and the unit alpha values are updated by
        converting such values as well.

        Parameters
        ==========
        Same parameters as operate_on_full().
        """
        ### grab full alpha values by operating on full
        ### alpha values from this mask along with values
        ### from the given one(s)

        full_alpha_values = map_alpha_at_same_positions(
            operation, *(mask.full_alpha_values for mask in (self, *alpha_masks))
        )

        ### obtain size of full alpha values
        size = size_from_alpha_values(full_alpha_values)

        ### if the size is different, it means the width
        ### or height of a given mask is smaller that
        ### the width or height of this one, which isn't
        ### allowed, so we raise an error explaining the
        ### problem

        if size != self.size:

            raise ValueError(
                "the width and height of the given"
                " mask(s) must not be smaller that the"
                " width and height of this one"
            )

        ### store full alpha values
        self.full_alpha_values = full_alpha_values

        ### store unit alpha values obtained by converting
        ### the full values
        self.unit_alpha_values = unit_from_full_alpha_values(full_alpha_values)

    maximum_ip = partialmethod(operate_on_full_ip, max)
    minimum_ip = partialmethod(operate_on_full_ip, min)
    subtract_ip = partialmethod(operate_on_full_ip, subtract_values)

    def operate_on_unit(self, operation, *alpha_masks):
        """Same as operate_on_full(), but w/ unit values.

        Paremeters
        ==========

        Same parameters as operate_on_full(), but operation
        is applied in unit alpha values from the masks.
        """
        return (
            ### return new AlphaMask instance from the unit
            ### alpha values obtained
            self.__class__.from_unit_alpha_values(
                ## get unit alpha values from
                ## this function
                map_alpha_at_same_positions(
                    ## which, receives an operation
                    operation,
                    ## and also the full alpha
                    ## values from this mask as
                    ## well as from the given ones
                    *(mask.full_alpha_values for mask in (self, *alpha_masks))
                )
            )
        )

    multiply = partialmethod(operate_on_unit, multiply_values)

    def operate_on_unit_ip(self, operation, *alpha_masks):
        """In-place equivalent of operate_on_unit().

        That is, works just like operate_on_unit(), but
        instead of returning a new mask, the unit alpha
        values replace the unit alpha values of this
        instance, and the full alpha values are updated by
        converting such values as well.

        Parameters
        ==========
        Same parameters as operate_on_unit().
        """
        ### grab unit alpha values by operating on unit
        ### alpha values from this mask along with values
        ### from the given one(s)

        unit_alpha_values = map_alpha_at_same_positions(
            operation, *(mask.unit_alpha_values for mask in (self, *alpha_masks))
        )

        ### obtain size of unit alpha values
        size = size_from_alpha_values(unit_alpha_values)

        ### if the size is different, it means the width
        ### or height of a given mask is smaller that
        ### the width or height of this one, which isn't
        ### allowed, so we raise an error explaining the
        ### problem

        if size != self.size:

            raise ValueError(
                "the width and height of the given"
                " mask(s) must not be smaller that the"
                " width and height of this one"
            )

        ### store unit alpha values
        self.unit_alpha_values = unit_alpha_values

        ### store full alpha values obtained by converting
        ### the unit values

        self.full_alpha_values = full_from_unit_alpha_values(unit_alpha_values)

    multiply_ip = partialmethod(operate_on_unit_ip, multiply_values)


def map_alpha_at_same_positions(callable_obj, *alpha_values_from_multiple_masks):
    """Return values by operating on multiple alpha values.

    That is, we take the alpha values of multiple masks
    and return a new alpha values list by grabbing the
    alpha values at the same positions and creating a new
    one from them using a given callable.

    Parameters
    ==========

    callable_obj (callable)
        operation which returns a new alpha value, given
        an tuple with all the alpha values for pixels in
        the same position.
    alpha_values_from_multiple_masks (sequence)
        contains alpha values of from multiple masks;
        the values may all be in their full format (integers
        in range(256)) or all in their unit format (floats
        from 0.000... to 1.0).

        the alpha values may have different sizes, resulting
        in alpha values whose dimensions are the smallest
        dimensions among the dimensions of the given alpha
        values.
    """
    ### return a list of lists representing the resulting
    ### alpha values

    return [
        ## inner list represents the alpha values (either in
        ## full or unit format) for a column of pixels
        [
            ## each item in this inner list is an alpha value
            ## resulting from a call to the given callable
            ## with a tuple containing all alpha values in that
            ## position from each mask
            callable_obj(values)
            for values in zip(*columns)
        ]
        ## the columns of pixels are retrieved from the
        ## collections representing alpha values from
        ## multiple masks, zipped together so columns in
        ## the same position are processed together
        for columns in zip(*alpha_values_from_multiple_masks)
    ]
