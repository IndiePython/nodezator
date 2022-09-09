"""Facility for video previews storage and sharing.

This module provides 02 objects of interest for when
we want to reuse video previews. The other objects are
support objects not meant to be imported/touched in
any way.

The ones you want to import are:

1) The VideosDatabase instance called VIDEO_DATA_DB,
   which is created and stored at the end of the module;

     This is an example of its usage:

     video_data = VIDEO_DATA_DB[video_path][video_settings]

     In other words, here we obtain a cached object
     for the video in the given path, rendered according to
     the given video settings.

02) The CachedVideoObject class

      A Object2D subclass representing a video.

      video_obj = CachedVideoObject(
                    video_path, video_settings
                  )
"""

### TODO check textman/cache.py for more content/insights
### for module's docstring above

### standard library imports

from pathlib import Path

from collections import deque


### local imports

from ..classes2d.single import Object2D

from ..ourstdlibs.dictutils import (
    settings_to_hashable_repr,
    hashable_repr_to_settings,
)

from ..surfsman.render import render_rect

from ..surfsman.draw import blit_aligned

from .render import render_video_data


VIDEO_METADATA_MAP = {}


class VideoDatabase(dict):
    """Dict used store maps related to videos data.

    Extends the built-in dict.
    """

    def __missing__(self, key):
        """Create, store and return dict for given key.

        That is, the key is a string representing a path
        wherein to find a video to be loaded/rendered
        according to specific render settings.

        Parameters
        ==========
        key (string)
            represents the path wherein to find the video.
        """
        ### we create a video version map for the key, store and
        ### return it
        video_versions_map = self[key] = VideoVersionsMap(key)

        return video_versions_map


VIDEO_DATA_DB = VideoDatabase()


class VideoVersionsMap(dict):
    """Map to store different versions of video."""

    def __init__(self, video_path):
        """Store video path.

        Parameters
        ==========
        video_path (string)
            represents path of video to be loaded.
        """
        self.video_path = video_path

    def __getitem__(self, video_settings):
        """Return surface rendered with given settings.

        Parameters
        ==========
        video_settings (dict)
            contains settings defining how the video must
            be rendered;
        """
        ### convert the render settings (a dict) to a custom
        ### tuple representing them, to use as dictionary key
        tuple_key = settings_to_hashable_repr(video_settings)

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
                render_video_data(
                    self.video_path, VIDEO_METADATA_MAP, **video_settings
                ),
            )


class CachedVideoObject(Object2D):
    """An video object whose data is cached."""

    def __init__(
        self,
        video_path,
        video_settings,
        width,
        height,
        background_color=(128, 128, 128),
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """Store arguments, set image and rect."""
        ### store arguments

        self.video_path = video_path
        self.video_settings = video_settings

        ### set image and rect

        self.image = render_rect(width, height, background_color)

        self.clean_image = self.image.copy()

        self.video_data = VIDEO_DATA_DB[video_path][video_settings]

        self.frames = deque(self.video_data)

        blit_aligned(
            self.frames[0],
            self.image,
            retrieve_pos_from="center",
            assign_pos_to="center",
        )

        rect = self.rect = self.image.get_rect()
        setattr(rect, coordinates_name, coordinates_value)

    ### XXX what to do about resizing and
    ### repositioning after using methods below?

    def change_video_settings(self, video_settings):
        """Change video settings and replace surface.

        Only does so if the given video settings are
        different than the ones currently in use.
        """
        if self.video_settings == video_settings:
            return

        self.video_data = VIDEO_DATA_DB[self.video_path][video_settings]

        self.frames = deque(self.video_data)

        self.image.blit(self.clean_image, (0, 0))

        blit_aligned(
            self.frames[0],
            self.image,
            retrieve_pos_from="center",
            assign_pos_to="center",
        )

        self.video_settings = video_settings

    def change_video_path(self, video_path):
        """Change video path and replace surface.

        Only does so if the given video path is
        different than the one currently in use.
        """
        if self.video_path == video_path:
            return

        self.video_data = VIDEO_DATA_DB[video_path][self.video_settings]

        self.frames = deque(self.video_data)

        self.image.blit(self.clean_image, (0, 0))

        blit_aligned(
            self.frames[0],
            self.image,
            retrieve_pos_from="center",
            assign_pos_to="center",
        )

        self.video_path = video_path

    def update(self):

        self.frames.rotate(-1)

        self.image.blit(self.clean_image, (0, 0))

        blit_aligned(
            self.frames[0],
            self.image,
            retrieve_pos_from="center",
            assign_pos_to="center",
        )


def update_video_metadata_and_previews(video_path):

    try:
        del VIDEO_METADATA_MAP[video_path]
    except KeyError:
        pass

    ###

    vid_versions_map = VIDEO_DATA_DB[video_path]
    existing_keys = list(vid_versions_map)

    for key in existing_keys:

        video_settings = hashable_repr_to_settings(key)

        vid_versions_map[key] = render_video_data(
            video_path, VIDEO_METADATA_MAP, **video_settings
        )
