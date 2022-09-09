"""Facility for image surfaces storage and sharing.

This module provides 03 objects of interest for when
we want to reuse image surfaces. The other objects are
support objects not meant to be imported/touched in
any way.

The ones you want to import are:

1) The ImageSurfacesDatabase instance called
   IMAGE_SURFS_DB

     This is an example of its usage:

     image_surf = IMAGE_SURFS_DB[image_path][image_settings]

     In other words, here we obtain a cached image surface
     for the image in the given path, rendered according to
     the given image settings.

02) The CachedImageObject class

      A Object2D subclass which instantiates objects with
      an image surface and respective rect. This class is
      used to automate the creation of objects which use
      cached image surfaces.

      new_instance = CachedImageObject(
                       image_path, image_settings
                     )

03) the update_cache_for_image() function;
"""

### TODO check textman/cache.py for more content/insights
### for module's docstring above

### standard library import
from pathlib import Path

### local imports

from ..config import IMAGES_DIR

from ..classes2d.single import Object2D

from ..ourstdlibs.dictutils import (
    settings_to_hashable_repr,
    hashable_repr_to_settings,
)

from .render import render_image_from_original


ORIGINAL_IMAGE_SURFS_MAP = {}


class ImageSurfacesDatabase(dict):
    """Dict used store maps related to image surfaces.

    Extends the built-in dict.
    """

    def __missing__(self, key):
        """Create, store and return dict for given key.

        That is, the key is a string representing a path
        wherein to find an image to be loaded/rendered
        according to specific render settings.

        Parameters
        ==========
        key (string)
            represents the path wherein to find the image.
        """
        ### if only the name of the image was provided,
        ### we join it with the path use to store images
        ### used in the app

        if len(Path(key).parts) == 1:
            key = str(IMAGES_DIR / key)

        ### we create a surface map for the key, store and
        ### return it
        image_surf_map = self[key] = ImageSurfaceMap(key)

        return image_surf_map


IMAGE_SURFS_DB = ImageSurfacesDatabase()


class ImageSurfaceMap(dict):
    """Map to store image surfaces; has extra behaviour."""

    def __init__(self, image_path):
        """Store image path.

        Parameters
        ==========
        image_path (string)
            represents path of image to be loaded.
        """
        self.image_path = image_path

    def __getitem__(self, image_settings):
        """Return surface rendered with given settings.

        Parameters
        ==========
        image_settings (dict)
            contains settings defining how the image must
            be rendered;
        """
        ### convert the render settings (a dict) to a custom
        ### tuple representing them, to use as dictionary key
        tuple_key = settings_to_hashable_repr(image_settings)

        ### try returning the value for the tuple we
        ### just obtained, which, if existent, should
        ### be a surface rendered with the corresponding
        ### settings
        try:
            return super().__getitem__(tuple_key)

        ### if such value doesn't exist (a key error is
        ### raised), we create the corresponding surface,
        ### and return it while at the same time creating
        ### a new item using the tuple key

        except KeyError:

            return self.setdefault(
                tuple_key,
                render_image_from_original(
                    self.image_path, ORIGINAL_IMAGE_SURFS_MAP, **image_settings
                ),
            )


class CachedImageObject(Object2D):
    """An image object whose surface is cached."""

    def __init__(
        self,
        image_path,
        image_settings,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store arguments, set image and rect."""
        ### store arguments

        self.image_path = image_path
        self.image_settings = image_settings

        ### set image and rect

        self.image = IMAGE_SURFS_DB[image_path][image_settings]

        rect = self.rect = self.image.get_rect()
        setattr(rect, coordinates_name, coordinates_value)

    ### XXX what to do about resizing and
    ### repositioning after using methods below?

    def change_image_settings(self, image_settings):
        """Change image settings and replace surface.

        Only does so if the given image settings are
        different than the ones currently in use.
        """
        if self.image_settings == image_settings:
            return

        self.image = IMAGE_SURFS_DB[self.image_path][image_settings]

        self.image_settings = image_settings

    def change_image_path(self, image_path):
        """Change image path and replace surface.

        Only does so if the given image path is
        different than the one currently in use.
        """
        if self.image_path == image_path:
            return

        self.image = IMAGE_SURFS_DB[image_path][self.image_settings]

        self.image_path = image_path


###


def update_cache_for_image(image_path):

    ### try removing existing original surf

    try:
        del ORIGINAL_IMAGE_SURFS_MAP[image_path]
    except KeyError:
        pass

    ###

    surf_map = IMAGE_SURFS_DB[image_path]
    existing_keys = list(surf_map)

    for key in existing_keys:

        image_settings = hashable_repr_to_settings(key)

        old_surf = surf_map[image_settings]

        new_surf = render_image_from_original(
            image_path, ORIGINAL_IMAGE_SURFS_MAP, **image_settings
        )

        if old_surf.get_size() == new_surf.get_size():
            old_surf.blit(new_surf, (0, 0))

        else:
            surf_map[key] = new_surf
