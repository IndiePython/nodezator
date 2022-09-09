"""Common constants."""

### standard library import
from collections import OrderedDict


### factors for converting from unit to full color values

RGBA_FACTOR = 255

HLS_FACTORS = HSV_FACTORS = 360, 100, 100

### names for color models

RGBA_NAMES = "red", "green", "blue", "alpha"
HLS_NAMES = "hue", "lightness", "saturation"


### map arbitrarily associating names of basic colors with
### sets of hue values closest to them

HUE_SETS_MAP = OrderedDict(
    [
        ("red", set.union(set(range(0, 15)), set(range(340, 361)))),
        ("orange", set(range(15, 45))),
        ("yellow", set(range(45, 75))),
        ("green", set(range(75, 159))),
        ("cyan", set(range(159, 195))),
        ("blue", set(range(195, 250))),
        ("magenta", set(range(250, 340))),
    ]
)
