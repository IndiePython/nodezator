"""Facility for custom alpha masking class.

Module contents
===============

AlphaMask (class)
    custom class representing an alpha mask.


This modules contains a class which abstracts the setup and
operations of a mask. The instances of such class hold
both the original alpha values of the source surface and
also a copy of such values converted to floats in the unit
interval, enabling us to quickly use any of the techniques
described earlier.


Alpha Masking 
=============

Alpha masking here refers to the operation of using the
alpha values of a surface into another. We call the surface
from which the alpha values are retrieved "source surface"
and we call the surface on which we are using the alpha
values "target surface". When this alpha masking is performed,
we say that the target surface had its alpha masked out.

Alpha masking is useful, for instance, to create stencils
for drawing specific shapes with varying colors or to limit
which part of a surface must be subject to an effect.
Though, at least at the beginning, we used this module
solely for stencilling.


Discussion: not using black and white images
============================================

It doesn't seem desirable to enable support for creating
masks from black and white images as sometimes is done
by other software.

If we were to implement such feature, pure black would
represent 100% transparency and pure white would be 100%
opacity (and greys would be the values in-between).

This means an image loaded as a pygame.Surface would not
need an alpha channel anymore to convey transparency and
thus we would be able to use .jpg images to create masks.

However, this method offers no apparent advantages over
using .png images with alpha channels. It is true that
surfaces without alpha channels, converted with
pygame.Surface.convert() are faster to blit than
surfaces with alpha channels converted with
pygame.Surface.convert_alpha(), but blitting has nothing
to do with alpha masking.

Additionally, even if images without alpha channels were 
loaded faster, which we haven't tested, such advantage 
wouldn't be relevant to the masking out operations, which 
are carried out several times during the lifetime of the 
mask, whereas loading is only performed once.

Furthermore, even if loading speed became an issue,
waiting a bit more at startup to pre-load the masks would
still be more desirable than working with the black/white
format which, although simple, isn't as straightforward as
working directly with transparency in .png files.
"""


### local import

from ..imagesman.cache import IMAGE_SURFS_DB

from .utils import (
    size_from_alpha_values,
    unit_from_full_alpha_values,
    full_from_unit_alpha_values,
    full_alpha_values_from_surface,
)

## class extensions

from .basicop import AlphaMaskBasicOperations
from .masksop import AlphaMaskOperationsBetweenMasks


### class definition


class AlphaMask(AlphaMaskBasicOperations, AlphaMaskOperationsBetweenMasks):
    """Stores alpha mask data and provides operations."""

    ### methods to support initialization

    def __init__(self, full_alpha_values, unit_alpha_values):
        """Store alpha values and define size."""
        ### store both lists of lists representing alpha
        ### values in different formats

        self.full_alpha_values = full_alpha_values
        self.unit_alpha_values = unit_alpha_values

        ### store size
        self.size = size_from_alpha_values(full_alpha_values)

        ### store a bounding rect representing the area
        ### occupied by the alpha values different from 0;

        ## XXX profiling note: this should be pretty quick;
        ## would it be quicker though if we calculate this
        ## ourselves?
        self.bounding_rect = self.get_colored_surface((0, 0, 0)).get_bounding_rect()

    @classmethod
    def from_image_name(cls, png_image_name):
        """Return AlphaMask instance using given image name.

        Works by getting a surface from the image name,
        retrieving its alpha values and passing such values
        to the class constructor, returning the resulting
        instance.

        Parameters
        ==========
        png_image_name (string)
            name of .png image representing the mask.
        """
        ### instantiate and return an AlphaMask object
        ### from a surface loaded using the image name;
        ###
        ### the image is loaded with the 'use_alpha' option
        ### on, so the values of the alpha channel are
        ### available

        return cls.from_surface((IMAGE_SURFS_DB[png_image_name][{"use_alpha": True}]))

    @classmethod
    def from_surface(cls, surf):
        """Return AlphaMask isntance from surface's alpha.

        Parameters
        ==========
        surf (pygame.Surface instance)
            surface from which to obtain the alpha values
            for the mask.
        """
        return cls.from_full_alpha_values(full_alpha_values_from_surface(surf))

    @classmethod
    def from_full_alpha_values(cls, full_alpha_values):
        """Return AlphaMask instance from alpha values."""
        ### we create a copy of the alpha values list of
        ### lists, but this time with the items converted
        ### to floats in the unit interval (from 0.000...
        ### to 1.0, that is, fully transparent to fully
        ### opaque)

        unit_alpha_values = unit_from_full_alpha_values(full_alpha_values)

        ### pass both lists of lists representing alpha
        ### values in different formats to the class
        ### and return the resulting instance
        return cls(full_alpha_values, unit_alpha_values)

    @classmethod
    def from_unit_alpha_values(cls, unit_alpha_values):
        """Return AlphaMask object from unit alpha values."""
        ### we create a copy of the unit alpha values list of
        ### lists, but this time with the items converted
        ### to integers in the range(256), where 0 means
        ### full transparency and 255 full opacity
        full_alpha_values = full_from_unit_alpha_values(unit_alpha_values)

        ### pass both lists of lists representing alpha
        ### values in different formats to the class
        ### and return the resulting instance
        return cls(full_alpha_values, unit_alpha_values)
