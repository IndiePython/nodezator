### third-party import
from pygame.image import load as load_image


### local imports

from ..classes2d.single import Object2D

from ..classes2d.collections import List2D

from ..surfdef import surfdef_obj_from_element

from ..surfsman.render import render_rect

from ..colorsman.colors import HTSL_CANVAS_BG


HTSL_CACHE = {}


def get_image_obj(resource_path, extension):

    if resource_path in HTSL_CACHE:

        surf = HTSL_CACHE[resource_path]
        return Object2D.from_surface(surf)

    ######

    if extension in (".jpg", ".jpeg"):

        image_surf = load_image(resource_path).convert()

        HTSL_CACHE[resource_path] = image_surf

        return Object2D.from_surface(image_surf)

    elif extension == ".png":

        loaded_surf = load_image(resource_path).convert_alpha()

        image_surf = render_rect(
            *loaded_surf.get_size(),
            HTSL_CANVAS_BG,
        )

        image_surf.blit(loaded_surf, (0, 0))

        HTSL_CACHE[resource_path] = image_surf

        return Object2D.from_surface(image_surf)
