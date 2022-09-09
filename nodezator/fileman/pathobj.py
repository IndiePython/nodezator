"""Visual representation of a path."""

### standard library import
from functools import partialmethod


### local imports

from ..translation import TRANSLATION_HOLDER as t

from ..pygameconstants import blit_on_screen

from ..appinfo import NATIVE_FILE_EXTENSION

from ..ourstdlibs.behaviour import empty_function

from ..surfsman.cache import RECT_SURF_MAP

from ..textman.cache import TEXT_SURFS_DB

from ..colorsman.colors import (
    NORMAL_PATH_FG,
    SELECTED_PATH_FG,
    NORMAL_PATH_BG,
    SELECTED_PATH_BG,
)

from .surfs import (
    FILE_ICON,
    FOLDER_ICON,
    TEXT_ICON,
    PYTHON_ICON,
    IMAGE_ICON,
    FONT_ICON,
    AUDIO_ICON,
    VIDEO_ICON,
    PDF_ICON,
    NATIVE_FILE_ICON,
)

from .constants import (
    FONT_HEIGHT,
    PATH_OBJ_PARENT_TEXT,
)


### constants

## common keyword arguments for text

NORMAL_KWARGS = {
    "font_height": FONT_HEIGHT,
    "foreground_color": NORMAL_PATH_FG,
    "padding": 0,
}


SELECTED_KWARGS = {
    "font_height": FONT_HEIGHT,
    "foreground_color": SELECTED_PATH_FG,
    "padding": 0,
}


## icon map for file extensions

ICON_MAP = {
    ".txt": TEXT_ICON,
    ".py": PYTHON_ICON,
    ".png": IMAGE_ICON,
    ".jpg": IMAGE_ICON,
    ".jpeg": IMAGE_ICON,
    ".ttf": FONT_ICON,
    ".otf": FONT_ICON,
    ".mp3": AUDIO_ICON,
    ".wav": AUDIO_ICON,
    ".ogg": AUDIO_ICON,
    ".mp4": VIDEO_ICON,
    ".mov": VIDEO_ICON,
    ".mkv": VIDEO_ICON,
    ".ogv": VIDEO_ICON,
    ".pdf": PDF_ICON,
    NATIVE_FILE_EXTENSION: NATIVE_FILE_ICON,
}


### class definition


class PathObject:
    """Visual representation of a path."""

    def __init__(
        self,
        path,
        grandparent_path=None,
        width=200,
        padding=3,
    ):
        """Store arguments and perform setups.

        Parameters
        ==========
        path (pathlib.Path or None)
            if it is a pathlib.Path, it will be the path
            this PathObject represents. If None, it causes
            this object to not blit itself anymore,
            appearing as if invisible.
        grandparent_path (pathlib.Path or None)
            used to determine whether we'll use special
            text indicating that this path object
            actually gives access to the grandparent
            directory of the 'path' argument.
        width (integer)
            fixed width to be assumed by this path object.
        padding (integer)
            padding used for various calculations within
            this object. The padding doesn't affect the
            final width of the path object, defined by
            the 'width' argument described above.
        """
        ### store arguments

        self.path = path
        self.width = width
        self.padding = padding

        ### prepare objects and values for display
        self.prepare_visuals()

        ### we use the rect of one of the background
        ### surfaces created as the rect for the whole
        ### path object
        self.rect = self.normal_bg.get_rect()

        ##
        self.update_path(path, grandparent_path)

    def prepare_visuals(self):
        """Prepare objects and values for display."""

        ### define max width for text surfaces, by
        ###  subtracting the width of the icon and the
        ### padding in both sides of the icon from the
        ### self.width argument defined upon
        ### initialization; note we also remove some
        ### extra pixels from the width, using an amount
        ### defined empirically, just for better aesthetics

        max_text_width = (
            self.width
            - FILE_ICON.get_width()  # TODO use constant instead
            - (self.padding * 2)
            - 7  # arbitrary value defined empirically
        )

        ### create new text settings that include the max
        ### text width

        self.normal_text_settings = {
            **NORMAL_KWARGS,
            "max_width": max_text_width,
        }

        self.selected_text_settings = {
            **SELECTED_KWARGS,
            "max_width": max_text_width,
        }

        ### define size for background

        ## the height is the height of the tallest object
        ## plus padding from both vertical ends

        max_height = max(
            FILE_ICON.get_height(),
            NORMAL_KWARGS["font_height"],
        )

        height = max_height + (self.padding * 2)

        ## size is self.width plus the height we just
        ## calculated
        bg_size = self.width, height

        ### create and store backgrounds

        self.normal_bg = RECT_SURF_MAP[(*bg_size, NORMAL_PATH_BG)]

        self.selected_bg = RECT_SURF_MAP[(*bg_size, SELECTED_PATH_BG)]

        ### assign current bg
        self.bg = self.normal_bg

    def update_path(self, path, grandparent_path=None):
        """Update label and icon according to given paths.

        Parameters
        ==========
        path (pathlib.Path or None)
            if it is a pathlib.Path, it will be the path
            this PathObject represents. If None, it causes
            this object to not blit itself anymore,
            appearing as if invisible.
        grandparent_path (pathlib.Path or None)
            used to determine whether we'll use special
            text indicating that this path object
            actually gives access to the grandparent
            directory of the 'path' argument.
        """
        ### if path is None, set the drawing behaviour to
        ### an empty function and the text attribute to
        ### an empty string

        if path is None:

            drawing_behaviour = empty_function
            self.text = ""

        ### otherwise, if path isn't None...

        else:

            ## update text attribute and text in labels

            if grandparent_path is None or path != grandparent_path:
                text = path.name

            else:
                text = PATH_OBJ_PARENT_TEXT

            self.text = text

            self.normal_text_surf = TEXT_SURFS_DB[self.normal_text_settings][
                "surf_map"
            ][text]

            self.selected_text_surf = TEXT_SURFS_DB[self.selected_text_settings][
                "surf_map"
            ][text]

            ### update icon

            self.icon = (
                ## folder icon if a folder
                FOLDER_ICON
                if path.is_dir()
                ## otherwise custom icon if file, based
                ## on suffix
                else ICON_MAP.get(path.suffix.lower(), FILE_ICON)
            )

            self.icon_rect = self.icon.get_rect()

            self.icon_rect.midleft = self.rect.move(self.padding, 0).midleft

            self.text_rect = self.normal_text_surf.get_rect()

            self.text_rect.midleft = self.icon_rect.move(self.padding, 0).midright

            ## set drawing behaviour to draw all objects
            drawing_behaviour = self.draw_objects

        ### finally store the path and drawing behaviour

        self.path = path
        self.draw = drawing_behaviour

    def reposition_icon_and_text(self):
        """Reposition icon and text rects, if it has."""
        if self.draw == empty_function:
            return

        self.icon_rect.midleft = self.rect.move(self.padding, 0).midleft

        self.text_rect.midleft = self.icon_rect.move(self.padding, 0).midright

    def change_selection_appearance(self, on):
        """Make object appear as selected/deselected.

        Do so by changing which label and background
        is used.

        Parameters
        ==========
        on (boolean)
            indicates which appearance the object will
            assume; if True, the object appears as selected;
            if False, it appears as normal/deselected.
        """
        ### define a prefix according to the value of the
        ### 'on' argument
        prefix = "selected" if on else "normal"

        ### put together attribute names for the text
        ### surface and background using the prefix

        text_attr_name = f"{prefix}_text_surf"
        bg_attr_name = f"{prefix}_bg"

        ### use the attribute names to grab the objects
        ### to be used as text surface and bg

        if self.path is not None:

            self.text_surface = getattr(self, text_attr_name)

        self.bg = getattr(self, bg_attr_name)

    select = partialmethod(change_selection_appearance, True)

    deselect = partialmethod(change_selection_appearance, False)

    def load(self):
        """Load path using special callable.

        The special callable sits at the 'load_directory'
        class attribute and must be stored there by
        whichever object is loading the directories.

        In the case of the fileman subpackage, such
        object is the fileman.dirpanel.main.DirectoryPanel.
        """
        self.load_directory(self.path)

    def draw_objects(self):
        """Draw objects representing by this path object."""
        for surf, rect in (
            (self.bg, (self.rect)),
            (self.icon, (self.icon_rect)),
            (self.text_surface, (self.text_rect)),
        ):
            blit_on_screen(surf, rect)
