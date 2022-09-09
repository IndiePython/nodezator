"""Facility for pygame.font.Font objects storage/sharing.

This module provides 01 object of interest for when
we want to reuse font. The other objects are support
objects not meant to be imported/touched in any way.

The one you want to import is:

The FontsDatabase instance called FONTS_DB, which is
created and stored near the end of the module;

   This is an example of its usage:

   font = FONTS_DB[font_path][size]

   In other words, here we obtain a cached image surface
   for the image in the given path, rendered according to
   the given image settings.
"""

### third-party import
from pygame.font import Font


### local import
from .exception import UnattainableFontHeight


class FontsDatabase(dict):
    """Dict used to store maps related to font files.

    Extends the built-in dict.
    """

    def __missing__(self, key):
        """Create, store and return dict for given key.

        That is, the key is a string representing a path
        wherein to find a font file.

        Parameters
        ==========
        key (string)
            represents the path wherein to find the image.
        """
        ### we create a font map for the key, store and
        ### return it
        font_map = self[key] = FontsMap(key)

        return font_map


FONTS_DB = FontsDatabase()


class FontsMap(dict):
    """Map to store pygame.font.Font instances."""

    def __init__(self, font_path):
        """Store image path.

        Parameters
        ==========
        font_path (string)
            represents path of image to be loaded.
        """
        self.font_path = font_path

    def __missing__(self, height):
        """Store and return font rendered w/ given height.

        Parameters
        ==========
        height (positive integer)
            define at which height the font must be rendered.
        """
        font = get_font(self.font_path, height)
        return font


def get_font(font_path, desired_height):
    """Return font obj whose surfaces are of desired height.

    Or as close as possible without surpassing it.

    The font object is a pygame.font.Font instance.

    This is achieved by trial and error, that is,
    instantiating fonts and using their 'size' method.
    This is so because each font has a different ratio
    between the size provided and the height in pixels
    of its rendered text surfaces. Such ratio even
    changes within the font itself depending on the
    specific size used.

    Since instantiating pygame.font.Font and using its
    'size' method is very quick, this is fast enough as
    to not be noticeable.

    Furthermore, this is done only once per font and
    desired height, since the resulting font object
    is stored for future reference (as can be seen in
    the get_font function).

    Coming up with a font which renders text surfaces
    of the exact desired height is not always possible.
    This is why sometimes we have to use the one which
    gets closer.

    For instance, you cannot have a pygame.font.Font
    from an "ubuntu medium" font file with surfaces of
    height 36. This is so because such font, when
    instantiated with size 31 renders surfaces of
    height 35 and when instantiated with size 32
    renders surfaces with height 37.

    In such case, we'll use the closest one which doesn't
    surpass the desired height, that is, the font with
    surfaces of height 35.
    """
    ### create a set to keep track of the attempted sizes
    attempted_sizes = set()

    ### create variable to store the chosen font
    chosen_font = None

    ### create variable to store highest height achieved
    ### which doesn't surpass the desired height (but
    ### can be equal)
    highest_achieved = 0

    ### before searching for the perfect font size inside
    ### the "while loop", define an initial size that takes
    ### into account the difference between the value used
    ### for the font size (here we use the desired height)
    ### and the actual height of a produced surface

    font = Font(font_path, desired_height)
    _, surf_height = font.size(" ")

    diff = desired_height - surf_height

    size = desired_height + diff

    ### we'll now enter a "while loop" with 02 exit points:
    ###
    ### 1) if while trying different sizes, we come up with
    ###    one we already attempted, it means that we are
    ###    out of viable options, so we have no choice but
    ###    to exit the loop; this condition is the one
    ###    passed to the "while" statement;
    ###
    ### 2) if we find a size which produces the desired
    ###    height; this condition is inside the body of
    ###    the "while loop" (in an "if block" with a
    ###    "break" statement)

    while size not in attempted_sizes:

        ### create font and calculate the height of the
        ### surface of an arbitrary character (space) when
        ### rendered

        font = Font(font_path, size)
        _, surf_height = font.size(" ")

        ### store current size as an attempted one since
        ### we just tried it
        attempted_sizes.add(size)

        ### if we reached a font whose rendered surface
        ### satisfies our height requirement, we can break
        ### out of the loop after storing the surf height
        ### as the highest achieved one and the font as the
        ### chosen one

        if surf_height == desired_height:

            highest_achieved = surf_height
            chosen_font = font

            break

        ### otherwise, we come up with another value for
        ### the size by incrementing/decrementing the
        ### current one according to whether the height
        ### of the surface we obtained is lower/higher
        ### than the desired one;

        else:

            size += 1 if surf_height < desired_height else -1

        ### if the height of the text surface is higher
        ### than the ones achieved until now but still
        ### below the desired height, consider it the
        ### highest height achieved until now, and its
        ### font as the chosen one (at least for now)

        if highest_achieved < surf_height < desired_height:

            highest_achieved = surf_height
            chosen_font = font

    ### if the highest height achieved isn't the desired
    ### one, raise an error to notify the user

    if highest_achieved != desired_height:

        raise UnattainableFontHeight(font_path, desired_height)

    ### finally return the chosen font
    return chosen_font
