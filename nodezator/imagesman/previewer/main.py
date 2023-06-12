"""Facility for viewing images from given paths."""


### third-party import
from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygamesetup import SERVICES_NS, SCREEN_RECT

from ...ourstdlibs.behaviour import empty_function

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...surfsman.render import render_rect

from ...surfsman.cache import cache_screen_state, draw_cached_screen_state

from ..cache import IMAGE_SURFS_DB

from ...colorsman.colors import IMAGES_PREVIEWER_FG, IMAGES_PREVIEWER_BG, THUMB_BG


from .constants import (
    PREVIEWER_RECT,
    PREVIEWER_ICON,
    PREVIEWER_CAPTION,
    PREVIEWER_OBJS,
    SMALL_THUMB,
    SMALL_THUMB_SETTINGS,
    PREVIEWER_BORDER_THICKNESS,
    PREVIEWER_PADDING,
)

from .op import PreviewerOperations


class ImagesPreviewer(PreviewerOperations):
    """loop holder for previewing images from given paths."""

    def __init__(self):
        """Create/store useful objects."""
        self.rect = PREVIEWER_RECT

        image = self.image = render_rect(*self.rect.size, color=IMAGES_PREVIEWER_BG)

        ###

        PREVIEWER_ICON.draw_relative(self)
        PREVIEWER_CAPTION.draw_relative(self)

        ###
        self.running = False

        ###

        self.background = self.image.copy()

        self.thumb_index = 0

        self.hovered_index = None

        ### store the centering method as a
        ### window resize setup
        APP_REFS.window_resize_setups.append(self.center_images_previewer)

    def center_images_previewer(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        ##
        PREVIEWER_OBJS.rect.center = self.rect.center = SCREEN_RECT.center

        ##

        try:
            self.thumb_objects
        except AttributeError:
            pass

        else:
            self.thumb_objects.rect.move_ip(diff)
        ##

        ### if the loop is running, ask to redraw

        if self.running:
            APP_REFS.draw_after_window_resize_setups = self.response_draw

    def preview_images(self, image_paths):
        """Display previews of images from the given paths."""
        ###
        cache_screen_state()

        ### reset thumb index
        self.thumb_index = 0

        ###
        self.image_paths = (
            [image_paths] if isinstance(image_paths, str) else image_paths
        )

        ### create image surfaces
        self.create_image_surfaces()

        ###
        self.prepare()

        ###

        self.running = True

        while self.running:

            ### perform various checkups for this frame;
            ###
            ### stuff like maintaing a constant framerate and more
            SERVICES_NS.frame_checkups()

            self.handle_input()
            self.draw()

    def create_image_surfaces(self):
        """Create surfaces/objects representing images.

        Different sizes are used for specific purposes:

        - thumb: to show at the bottom of the viewer; used
                 to help navigate through images;
        - default: a larger view of the image;
        """
        thumb_surfs = [
            IMAGE_SURFS_DB[image_path][SMALL_THUMB_SETTINGS]
            for image_path in self.image_paths
        ]

        self.thumb_objects = List2D(
            Object2D.from_surface(surf) for surf in thumb_surfs
        )

        (
            self.thumb_objects.rect.snap_rects_ip(
                retrieve_pos_from="topright",
                assign_pos_to="topleft",
            )
        )

        self.thumb_objects.rect.topleft = SMALL_THUMB.rect.topleft


### instantiate the images previewer and store a reference
### to its 'preview_images' method in this module so
### it can be easily imported
preview_images = ImagesPreviewer().preview_images
