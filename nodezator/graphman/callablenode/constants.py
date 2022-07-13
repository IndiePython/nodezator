"""Constants for the callable node class."""

### local import
from ...fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT


FONT_HEIGHT = ENC_SANS_BOLD_FONT_HEIGHT

NODE_WIDTH = 184

NODE_OUTLINE_THICKNESS = 2

## area in the top of the body surface made darker, in order
## to give the illusion the title of the node is merged with
## the top of the body, since the title uses the same
## background color; since part of the title is already
## positioned over the top of the node (and the remaining
## part is positioned over the body of the node), we
## discount just two pixels from the font height used
## as the base for the calculation; this is an aesthetic
## measure
NODE_BODY_HEAD_HEIGHT = FONT_HEIGHT - 2

### distance from top of the body to the first piece of
### content (either a first parameter or first output);
### we position the body content offset two pixels after
### the body head area;
BODY_CONTENT_OFFSET = NODE_BODY_HEAD_HEIGHT + 2

### distance from a variable parameter's label to its
### first subparameter
SUBPARAM_OFFSET_FROM_LABEL = 2

### distance between parameters
DISTANCE_BETWEEN_PARAMS = 4

### distance between subparameters
DISTANCE_BETWEEN_SUBPARAMS = 8

### distance between last input (including the object with
### lowest bottom, whether it is a widget or the label)
### and the first output socket
OUTPUT_OFFSET = 4

### distance between outputs
DISTANCE_BETWEEN_OUTPUTS = 4
