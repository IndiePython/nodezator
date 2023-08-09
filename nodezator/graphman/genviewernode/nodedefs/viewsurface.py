"""Facility for pygame-ce surface visualization."""


### third-party imports

from pygame import Surface

from pygame.math import Vector2

from pygame.transform import (
    scale as scale_surface,
    smoothscale as smoothscale_surface,
)



### main callable

def view_surface(

    surface: Surface,
    preview_scaling: {
        'widget_name': 'option_tray',
        'widget_kwargs': {
            'options': ['normal', 'smooth'],
        },
        'type': str,
    } = 'smooth',
    max_preview_size: 'natural_number' = 600,

) -> [

    {'name': 'full_surface', 'type': Surface, 'viz': 'loop'},
    {'name': 'preview_surface', 'type': Surface, 'viz': 'side'},

]:
    """Return dict with pygame-ce surfaces.

    Parameters
    ==========
    surface
        pygame-ce surface to be displayed as the full surface and from
        which we'll create a preview version (if needed).
    preview_scaling
        Whether to use smooth or normal scaling to scaled down surface
        to obtain preview. Only used if the surface needs to be scaled down
        to fit the 'max_preview_size'.
    max_preview_size
        maximum diagonal length of the preview surface. Must be >= 0.
        If 0, just use the full surface.
    """
    ### raise error if value of max preview size is not allowed

    if max_preview_size < 0:
        raise ValueError("'max_preview_size' must be >= 0")

    ### alias the surface as our full surface
    full_surface = surface

    ### if the max preview size is 0, it means the preview doesn't need
    ### to be below a specific size, so we can use the full surface
    ### as the preview

    if not max_preview_size:

        preview_surface = full_surface

        return {
            'full_surface': full_surface,
            'preview_surface': preview_surface,
        }

    ### otherwise, we must create a preview surface within the allowed size,
    ### if the full surface surpasses such allowed size

    ## create a 2D vector representing the topleft coordinate of the
    ## full surface, which is (0, 0)
    topleft = Vector2(0, 0)

    ## obtain the bottom right coordinate of the surface, which is
    ## equivalent to its size
    bottomright = full_surface.get_size()

    ## use the bottom right to calculate its diagonal length
    diagonal_length = topleft.distance_to(bottomright)

    ## if the diagonal length of the full surface is higher than the
    ## maximum allowed size, we create a new smaller surface within
    ## the allowed size to use as the preview

    if diagonal_length > max_preview_size:

        size_proportion = max_preview_size / diagonal_length
        new_size = topleft.lerp(bottomright, size_proportion)

        if preview_scaling == 'smooth':
            scaling_operation = smoothscale_surface

        else:
            scaling_operation = scale_surface

        preview_surface = scaling_operation(full_surface, new_size)


    ### otherwise, just alias the full surface as the preview surface;
    ###
    ### that is, since the full surface didn't need to be downscaled,
    ### it means it is small enough to be used as an in-graph visual
    ### already

    else:
        preview_surface = full_surface

    ### finally, return a dict containing both surfaces;
    ###
    ### you can return the surfaces in any way you want, inside a list,
    ### inside a tuple or a dictionary, etc.; the format isn't important,
    ### because we specify functions further below in the script to fetch
    ### them for us regardless of where we placed them anyway

    return {
        'full_surface': full_surface,
        'preview_surface': preview_surface,
    }
