"""Common color property getting operations."""

### local imports

from .conversion import (
    full_rgb_to_hls,
    full_rgb_to_hsv,
    full_to_unit_rgba,
    full_rgba_to_yiq,
)

(
    get_hue,
    get_lightness,
    get_saturation,
    get_value,
    get_red,
    get_green,
    get_blue,
    get_alpha,
    get_luma,
) = (
    lambda full_rgba: full_rgb_to_hls(full_rgba[:3])[0],
    lambda full_rgba: full_rgb_to_hls(full_rgba[:3])[1],
    lambda full_rgba: full_rgb_to_hls(full_rgba[:3])[2],
    lambda full_rgba: full_rgb_to_hsv(full_rgba[:3])[2],
    lambda full_rgba: full_rgba[0],
    lambda full_rgba: full_rgba[1],
    lambda full_rgba: full_rgba[2],
    lambda full_rgba: (full_rgba[3] if len(full_rgba) == 4 else 255),
    lambda full_rgba: full_rgba_to_yiq(full_rgba)[0],
)


### map containing functions to retrieve an specific
### property from a given color

PROPERTY_GETTER_MAP = {
    "hue": get_hue,
    "lightness": get_lightness,
    "saturation": get_saturation,
    "value": get_value,
    "red": get_red,
    "green": get_green,
    "blue": get_blue,
    "alpha": get_alpha,
    "luma": get_luma,
}
