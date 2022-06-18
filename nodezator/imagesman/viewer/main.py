"""Facility for viewing images from given paths."""

### standard library import
from functools import partialmethod


### local imports

from pygameconstants import (
                       FPS,
                       maintain_fps,
                     )

from ourstdlibs.behaviour import empty_function

from classes2d.single      import Object2D
from classes2d.collections import List2D

from surfsman.render import render_rect

from surfsman.cache import (
                      cache_screen_state,
                      draw_cached_screen_state
                    )

from imagesman.cache import IMAGE_SURFS_DB

from colorsman.colors import (
                             IMAGES_VIEWER_FG,
                             IMAGES_VIEWER_BG,
                             THUMB_BG)


from imagesman.viewer.constants import (
                                  VIEWER_RECT,
                                  VIEWER_ICON,
                                  VIEWER_CAPTION,
                                  SMALL_THUMB,
                                  SMALL_THUMB_SETTINGS,
                                  VIEWER_BORDER_THICKNESS,
                                  VIEWER_PADDING)

from imagesman.viewer.normalop import NormalModeOperations
from imagesman.viewer.fullop   import FullModeOperations


### TODO finish subpackage (implementing viewer)


class ImagesViewer(
        NormalModeOperations,
        FullModeOperations
      ):
    """loop holder for viewing images from given paths."""

    def __init__(self):
        """Create/store useful objects."""
        self.rect = VIEWER_RECT

        image = self.image = render_rect(
                               *self.rect.size,
                               color=IMAGES_VIEWER_BG
                             )

        ###

        VIEWER_ICON.draw_relative(self)
        VIEWER_CAPTION.draw_relative(self)

        ###

        self.background = self.image.copy()

        self.thumb_index = 0

        self.hovered_index = None

        self.should_draw_full_rect = False

        self.should_move_with_mouse = False

    def view_images(self, image_paths):
        """Display images from the given paths."""

        cache_screen_state()

        ###

        draw_cached_screen_state()

        ### reset thumb index
        self.thumb_index = 0

        ###
        self.image_paths = (

          [image_paths]
          if isinstance(image_paths, str)

          else image_paths

        )

        ### create image surfaces
        self.create_image_surfaces()

        ###
        self.enable_normal_mode()

        ###

        self.running = True

        while self.running:
            
            maintain_fps(FPS)

            self.handle_input()
            self.draw()

        for name in (
          'full_image',
          'full_rect'
        ):
            try: delattr(self, name)
            except AttributeError: pass

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

                               Object2D(
                                 image = surf,
                                 rect  = surf.get_rect()
                               )

                               for surf in thumb_surfs

                             )

        (
          self
          .thumb_objects
          .rect
          .snap_rects_ip(
             retrieve_pos_from = 'topright',
             assign_pos_to     = 'topleft',
           )
        )

        self.thumb_objects.rect.topleft = \
                                    SMALL_THUMB.rect.topleft

    def set_mode(self, mode_name):
        """Enable mode by assigning related operations."""

        for operation_name in (
          'handle_input',
          'draw',
          'on_mouse_release',
          'on_mouse_motion'
        ):

            full_name = mode_name + '_' + operation_name

            operation = getattr(
                          self, full_name, empty_function
                        )

            setattr(self, operation_name, operation)

        getattr(
          self, mode_name + '_prepare', empty_function
        )()

    enable_normal_mode = partialmethod(set_mode, 'normal')
    enable_full_mode   = partialmethod(set_mode,   'full')

### instantiate the images viewer and store a reference
### to its 'view_images' method in this module so
### it can be easily imported
view_images = ImagesViewer().view_images
