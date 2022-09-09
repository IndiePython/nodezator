"""Facility w/ basic operations for AlphaMask class.

Module contents
===============

AlphaMaskBasicOperations (class)
    class used as an extension for the AlphaMask class;
    it contains basic operations for AlphaMask instances.


Class operations
================

Both the mask_by_replacing() and mask_by_multiplying()
methods can be used to mask out the alpha of a surface
received as their sole argument. They use the first and
second techniques of alpha masking, respectively. Such
techniques are explained further below in the next section.

The get_colored_surface() method receives a color and returns
a new surface filled with that color and with the alpha
masked out using one of the existing techniques we just
mentioned, whichever is most suitable depending on whether
or not the color used has any transparency to it.

The class also has a method to return a new pygame.Rect
representing the dimensions of the source surface, the
get_rect() method. The size of that surface is also stored
in the "size" attribute. The source surface itself isn't
stored anywhere, since we are only interested in its alpha
values and size.

The masking operations carried out in this module are 
different from the ones carried out by pygame.mask module 
because pygame.mask only deals with bitmasks (a pixel is 
either fully opaque or fully transparent), while the mask 
operations here doesn't rely on bitmasks and work with
pixels in all ranges of transparency, (fully opaque, fully
transparent and partially transparent pixels).

We use 02 different techniques of alpha masking here, both
suitable for different situations:

1) The first one, the most simple, consists of assigning
   the alpha values of the source surface to the target
   surface. That is, each alpha value is used as-is.

   In practice, we don't spend time retrieving the alpha
   values of the source surface, because this is step
   is performed much earlier and the alpha values are
   stored so they can be used/reused whenever needed.
   That is, when masking out, we only need to worry about
   applying the alpha values to the target surface.

   This first technique is assumed to be faster than the
   second one, because this technique only uses a subset
   of the steps used in the second one.

   Technique 1 is best suited for usage in target surfaces
   which only have solid colors, that is, surfaces whose
   all alpha values equal 255.
   
   This is usually so because source surfaces usually have
   their visible area (or at least most of it) rendered with
   solid colors (alpha is 255) and when such values are
   applied in target surfaces with semitransparent areas
   such areas would then be rendered solid.
   
   In other words, if the target surface had alpha values
   different than 255, they would be reverted back to the
   full 255 alpha value, that is, the alpha of the source
   surface would cause semitransparent portions of the
   target surface to appear as having solid colors, which
   may be undesirable.

   In yet another words, think of this operation as one
   that completely ignores the original alpha information
   of the target surface by replacing it with the alpha
   from our mask, whereas the technique 2, as we'll soon
   see, does take into account the alpha information of
   the target surface.

   Whether technique 1 or 2 is better suited for the
   mask operation we are planning to perform, it all
   ultimately depends on what we want to achieve, so
   there isn't really an absolute better technique.

   When we apply the technique 1, we say that we
   are replacing the alpha of the target surface.

2) The 2nd technique converts the alpha values from the
   source surface into floats in the unit interval (real
   numbers from 0.000... to 1.0) and multiply them by the
   respective alpha values of the target surface. Only then,
   after the result is rounded to the nearest integer is
   that the resulting alpha value is assigned to the target
   surface.

   When such multiplications are carried out, the pixels of 
   the target surface whose alpha are multiplied by 0 
   become completely transparent. Naturally, the pixels
   whose alpha is multiplied by a number between 0 and 1
   retain only a percentage of its original alpha value.
   and those whose alpha is multiplied by 1 don't have
   their alpha value altered.

   This technique isn't as fast as the first one since
   instead of just assigning the alpha, we have the extra
   steps of multiplication and rounding described earlier.

   Like the first technique, we also retrieve the alpha
   values of the source surface in anticipation and also
   convert them to floats in the unit interval, leaving
   the values stored so they can be used/reused whenever
   needed. This way, when applying the alpha values from
   the source surface, we only need to worry about the
   multiplication and rounding step.

   This technique is suitable for usage in any kind of
   target surface, regardless of whether it has
   semitransparent areas or not, because it doesn't cause
   semitransparent portions of target surfaces to become
   solid.

   In other words, this technique takes into account the
   original alpha values of the target surface.
   
   However, when dealing with target surfaces that only have
   solid colors, the first technique is preferable, since it
   achieves the same effect with less steps.

   When we apply the technique 2, we say that we
   are multiplying the alpha of the target surface.
"""

### third-party imports

from pygame import Rect, Surface

from pygame.surfarray import pixels_alpha


### class definition


class AlphaMaskBasicOperations:
    """Provides basic operations for AlphaMask's instances."""

    ### method to get a rect the size of the mask

    def get_rect(self):
        """Return new rect the size of the mask."""
        return Rect(0, 0, *self.size)

    ### masking methods;
    ###
    ### you'll notice that instead of having 02 masking
    ### methods, we could have a single method with 02
    ### functools.partialmethod implementations by
    ### encapsulating the alpha processing/assigning step
    ### (performed inside the "for loops") into specific
    ### functions;
    ###
    ### this way we wouldn't need to repeat the first and
    ### last lines of code in both methods, which are the
    ### same;
    ###
    ### we decided against this, though, since putting the
    ### code from the "for loops", which is executed several
    ### times, inside a function, would introduce undesired
    ### speed loss;
    ###
    ### that is, sometimes, to speed up execution of Python
    ### code, it is better to "inline" the code instead of
    ### encapsulating it in a function, specially when
    ### iterating over the code

    def mask_by_replacing(self, surf):
        """Mask out pixels by replacing alpha values.

        Best suited to use in surfaces which, despite having
        an alpha channel, all of its alpha values are 255.
        That is, all of its pixels have solid colors.

        Parameters
        ==========
        surf (pygame.Surface instance)
            surface to be masked out by having its alpha
            values replaced by the alpha from the mask.
        """
        ### create an array which directly references the
        ### surface's alpha values;
        ###
        ### that is, changes in the values of this array
        ### are reflected in the alpha of the pixels in
        ### the surface;
        ###
        ### the surface remains locked for the lifetime of
        ### this array (which is why we'll soon delete it
        ### once we don't need it anymore)
        surf_alpha_values = pixels_alpha(surf)

        ### iterate over the columns of full alpha values
        ### from both the surface and this alpha mask,
        ### using slice assignment to replace the values
        ### from each surf's column by the values from
        ### each mask's column

        for surf_alpha_column, mask_full_alpha_column in zip(
            surf_alpha_values, self.full_alpha_values
        ):

            surf_alpha_column[:] = mask_full_alpha_column

        ### delete references to the array so the surface is
        ### unlocked;
        ###
        ### the array would be automatically garbage
        ### collected anyway once the method returned,
        ### but we prefer to be explicit about this,
        ### especially given the importance of this operation
        del surf_alpha_column, surf_alpha_values

    def mask_by_multiplying(self, surf):
        """Mask out pixels by multiplying alpha values.

        Can be used in surfaces with and without
        semitransparent areas, but if the surface
        has only solid colors, that is, all alpha values
        are 255, then using mask_by_replacing() is
        recommended instead.

        Parameters
        ==========
        surf (pygame.Surface instance)
            surface to be masked out by having its
            alpha values multiplied by the alpha from the
            mask.
        """
        ### create an array which directly references the
        ### surface's alpha values;
        ###
        ### that is, changes in the values of this array are
        ### reflected in the alpha of the pixels in the
        ### surface;
        ###
        ### the surface remains locked for the lifetime of
        ### this array (which is why we'll soon delete it
        ### once we don't need it anymore)
        surf_alpha_values = pixels_alpha(surf)

        ### multiply the alpha of each pixel in the surface
        ### by the respective unit value in the mask,
        ### rounding the result so that it remains an
        ### integer in the range(256), which is how full
        ### alpha values are stored in surfaces

        for y, column in enumerate(self.unit_alpha_values):

            for x, alpha_factor in enumerate(column):

                surf_alpha_values[y][x] = round(surf_alpha_values[y][x] * alpha_factor)

        ### delete the array so the surface is unlocked;
        ###
        ### the array would be automatically garbage
        ### collected anyway once the method returned,
        ### but we prefer to be explicit about this,
        ### especially given the importance of this
        ### operation
        del surf_alpha_values

    ### other common useful operation

    def get_colored_surface(self, color):
        """Return new colored surface w/ alpha masked out.

        Parameters
        ==========
        color (sequence of integers)
            represent a color with which to fill the surface
            before masking out the alpha/transparency;

            the integers, in the range(0, 256) interval,
            represent values of red, green and blue channels
            of a color; a fourth integer can optionally be
            provided as well, which represents the alpha.
        """
        ### create a surface with an alpha channel, having
        ### the same size as the mask and fill it with the
        ### given color

        surf = Surface(self.size).convert_alpha()
        surf.fill(color)

        ### mask the transparency out of the surface using
        ### the best masking method according to whether
        ### the color has transparency or not, that is,
        ### whether it has a fourth value lower than 255

        ## check whether the color has an alpha value
        try:
            alpha = color[3]

        ## if it hasn't, it means it is a solid color, so
        ## so we use the masking operation which replaces
        ## the alpha values
        except IndexError:
            self.mask_by_replacing(surf)

        ## otherwise, pick the operation according to the
        ## value of the alpha

        else:

            ### pick operation

            (
                ## if alpha is lower than 255, it means the
                ## color has some transparency to it,
                ## so we pick the operation suitable for such
                ## kind of color
                self.mask_by_multiplying
                if alpha < 255
                ## otherwise we use the one best suited to
                ## mask surfaces with solid colors
                else self.mask_by_replacing
                ## we then pass the surface to the
                ## operation we just chose
            )(surf)

        ### finally, return the surface
        return surf
