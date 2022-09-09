"""Facility for storing commonly used color values."""

### local imports

from ..config import APP_COLORS_FILE

from ..ourstdlibs.pyl import load_pyl


### utility function


def populate_locals_dict(locals_dict, obj):

    for key, value in obj.items():

        locals_dict[key] = value

        if isinstance(value, dict):
            populate_locals_dict(locals_dict, value)


### process file contents to store colors and color
### collections in the locals dictionary
populate_locals_dict(locals(), load_pyl(APP_COLORS_FILE))

### definition of functional colors;
###
### these are colors which don't depend on the theme used,
### serving an specific purpose

## solid neutral colors for things involving lightness/luma

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

## colors used to indicate transparency in surfaces

# for color surfaces

TRANSP_COLOR_A = (210, 210, 210)
TRANSP_COLOR_B = (120, 120, 120)

# for image surfaces

TRANSP_IMAGE_A = (40, 40, 40)
TRANSP_IMAGE_B = (60, 60, 60)
