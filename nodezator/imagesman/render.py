"""Facility for applying image render settings."""

### standard library imports

from os import linesep

from math import inf as INFINITY


### third-party imports

from pygame import Rect, Surface, error as PygameError

from pygame.image import load as load_image

from pygame.transform import smoothscale as smoothscale_surface


### local imports

from ..surfsman.draw import blit_aligned

from ..surfsman.render import render_rect

from ..surfsman.cache import NOT_FOUND_SURF_MAP, CHECKERED_SURF_MAP

from ..our3rdlibs.userlogger import USER_LOGGER

from ..colorsman.colors import (
    TRANSP_IMAGE_A,
    TRANSP_IMAGE_B,
)


### TODO import and apply constants where appropriate;
### for instance, colors from colorsman.colors;


def render_image_from_original(
    image_path,
    original_image_surfs_map,
    *,
    ### alpha related
    use_alpha=False,
    checkered_alpha=False,
    ### dimension related
    width=0,
    height=0,
    max_width=INFINITY,
    max_height=INFINITY,
    min_width=0,
    min_height=0,
    keep_size_ratio=False,
    ### background related
    background_width=0,
    background_height=0,
    background_color=(255, 255, 255),
    retrieve_pos_from="center",
    assign_pos_to="center",
    offset_pos_by=(0, 0),
    ### when image is not found
    not_found_width=0,
    not_found_height=0,
):

    ### try referencing the original surface
    try:
        surf = original_image_surfs_map[image_path]

    ### if it isn't available, load it from the path,
    ### store it in the map and reference it

    except KeyError:

        ## load surface using proper pygame.Surface
        ## converter function depending on whether the
        ## image has alpha or not

        try:

            surf = original_image_surfs_map[image_path] = (
                load_image(image_path).convert_alpha()
                if use_alpha
                else load_image(image_path).convert()
            )

        ### in case an error occurs...

        except (FileNotFoundError, PygameError) as err:

            ### log it in the user log

            USER_LOGGER.info(
                (
                    "Could not load"
                    + f" {image_path} image from"
                    + " disk;"
                    + linesep
                    + "using a placeholder"
                    + " image instead"
                )
            )

            ### if width and height in case the image file
            ### wasn't found were provided, create a surface
            ### with an drawing indicating the image wasn't
            ### found

            if not_found_width and not_found_height:

                size = get_final_size(
                    not_found_width,
                    not_found_height,
                    not_found_width,
                    not_found_height,
                    max_width,
                    max_height,
                    min_width,
                    min_height,
                    keep_size_ratio,
                )

                return NOT_FOUND_SURF_MAP[size]

            ### otherwise raise a new exception from the existing one

            else:

                raise RuntimeError(
                    "Couldn't load the image and instructions"
                    " to draw a 'not found' surface were not given"
                ) from err

    ### perform size transformations as needed

    actual_width, actual_height = surf.get_size()

    if width * height == 0:
        width, height = actual_width, actual_height

    final_width, final_height = get_final_size(
        width,
        height,
        actual_width,
        actual_height,
        max_width,
        max_height,
        min_width,
        min_height,
        keep_size_ratio,
    )

    if (final_width, final_height) != (actual_width, actual_height):

        surf = smoothscale_surface(surf, (final_width, final_height))

    ### if image has alpha and it must be checkered, blit
    ### the surface over a checker pattern

    if use_alpha and checkered_alpha:

        ## copy cached surface with checker pattern

        bg_surf = (

            # cached checkered surface
            CHECKERED_SURF_MAP[(
                surf.get_size(), # size
                TRANSP_IMAGE_A, # color_a
                TRANSP_IMAGE_B, # color_b
                10, # rect_width
                10, # rect_height
            )]

        ).copy()

        ## blit surface over it
        bg_surf.blit(surf, (0, 0))

        ## alias new surface
        surf = bg_surf

    ### if requested, create a background for the image,
    ### regardless of other dimension requirements (minimum
    ### and maximum widths and heights and whether ratio
    ### must be kept or not)

    if background_width and background_height:

        bg_surf = render_rect(background_width, background_height, background_color)

        blit_aligned(
            surface_to_blit=surf,
            target_surface=bg_surf,
            retrieve_pos_from=retrieve_pos_from,
            assign_pos_to=assign_pos_to,
            offset_pos_by=offset_pos_by,
        )

        surf = bg_surf

    return surf


def get_final_size(
    width,
    height,
    actual_width,
    actual_height,
    max_width,
    max_height,
    min_width,
    min_height,
    keep_size_ratio,
):

    width = max(min_width, min(max_width, width))
    height = max(min_height, min(max_height, height))

    if (width, height) != (actual_width, actual_height):

        ## adjust width and height if the size ratio must
        ## be kept

        if keep_size_ratio:

            ### XXX using a formula would be quicker than
            ### Rect.fit()?
            width, height = (
                Rect(0, 0, actual_width, actual_height).fit(0, 0, width, height).size
            )

    return (width, height)
