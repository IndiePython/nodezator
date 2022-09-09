"""Class for common color representation."""

### third-party import
from pygame import Surface


### local imports

from ..ourstdlibs.collections.general import FactoryDict

from ..ourstdlibs.color.creation import get_contrasting_bw

from ..classes2d.single import Object2D

from ..surfsman.draw import draw_checker_pattern
from ..surfsman.render import render_rect

# TODO render_rect usage throughout the module should
# probably be replaced by usage of the RECT_SURF_MAP
# from surfsman/cache.py, which caches the surface;

from .colors import TRANSP_COLOR_A, TRANSP_COLOR_B


### constant: contrasting color map
###
### a map containing the color which contrasts more with
### the given one, based on luma, being either black or
### white
CONTRASTING_COLOR_MAP = FactoryDict(get_contrasting_bw)


### utility function


def new_checkered_surf_from_size(size):
    """Return surface of given size with checker pattern.

    Parameters
    ==========
    size (sequence w/ 2 integers)
        represent the size of the surface, where each
        integer represents the number of pixels in each
        dimension of the surface.
    """
    ### create the surface with the given size
    checkered_surf = Surface(size).convert()

    ### draw the checker pattern on it

    draw_checker_pattern(checkered_surf, TRANSP_COLOR_A, TRANSP_COLOR_B, 16, 16)

    ### return the surface
    return checkered_surf


### class definition


class Color2D(Object2D):
    """Common color representation.

    Used alone or together with other objects to
    represent a color.

    It is usually only a surface with a solid color, but
    when the color has transparency it also displays a
    checkered pattern visible through the color's
    transparency to make the transparency apparent.
    """

    ### class attribute containing a dictionary used to
    ### map a given size to a surface of that size with a
    ### checkered pattern

    # TODO this map should probably be a module level
    # constant
    SIZE_TO_CHECKERED_SURF = FactoryDict(new_checkered_surf_from_size)

    def __init__(
        self, width, height, color, coordinates_name="topleft", coordinates_value=(0, 0)
    ):
        """Store arguments and perform setups.

        Parameters
        ==========

        width, height (integers)
            represent the size of each dimension of
            the widget in pixels.
        color (sequence of integers)
            represent a single color; the integers, in the
            range(256) represent the values of the red,
            green and blue channels, respectively; a fourth
            integer may also exist, representing the value
            for an alpha channel (used for transparency).
        coordinates_name (string)
            name of a pygame.Rect attribute wherein used
            to set a position in that attribute.
        coordinates_value (sequence with 2 integers)
            represents a position in 2d space used to
            position the widget; the attribute named in
            the coordinates_name attribute is set to the
            value of this argument.
        """
        ### store the width and height in a tuple
        ### representing the size
        self.size = width, height

        ### set the color and create widget's surface
        ### based on it
        self.set_color(color)

        ### create and store a rect for this widget, from
        ### its surface and position that rect

        self.rect = self.image.get_rect()

        setattr(self.rect, coordinates_name, coordinates_value)

    def set_color(self, color):
        """Store color and create surface representing it.

        Check the __init__ method for an explanation of
        the color parameter.

        Quick discussion
        ================

        Instead of arbitrarily creating/referencing/copying
        the checkered surface, I could first check whether
        the surface has transparency or not, so the step
        could be skipped if it didn't have.

        However, after trying the implementation, it wasn't
        obviously apparent whether or not this would save
        a significant amount of time (or even whether it
        would save time any time at all), since so many
        operations take place. For instance, even taking
        the speed of the operations into account, this
        class was made, at least initially, to produce
        relatively small widgets, thus not much time is
        spent in the creation of surfaces to begin with.

        In the future, when convenient, we could profile
        such operations within typical use-cases in order
        to decide whether to implement the additional checks
        and operations to skip checkered surface creation/
        copy when the color has no transparency.

        For now, I believe the method is fine as it is
        and doesn't hinder the application at all.
        """
        ### store the color and its contrasting counterpart
        ### (either black or white)

        self.color = color

        self.contrasting_color = CONTRASTING_COLOR_MAP[color]

        ### obtain a checkered surface with this widget size
        checkered_surf = self.SIZE_TO_CHECKERED_SURF[self.size]

        ### copy the checkered surface in the 'image'
        ### attribute
        self.image = checkered_surf.copy()

        ### obtain a surface representing a rect filled
        ### with this widget's color
        color_surf = render_rect(*self.size, color)

        ### blit the color surface over the checkered
        ### surface we copied (if the color has transparency,
        ### the checker pattern underneath will be visible,
        ### making the transparency apparent)
        self.image.blit(color_surf, (0, 0))

    ### TODO refactor

    def set_size(self, size):

        if size != self.rect.size:

            self.size = size
            self.image = render_rect(*size, self.color)
            self.rect.size = size
