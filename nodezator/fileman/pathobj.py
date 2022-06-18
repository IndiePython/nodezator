"""Visual representation of a path."""

### standard library import
from functools import partialmethod


### local imports

from translation import TRANSLATION_HOLDER as t

from pygameconstants import blit_on_screen

from appinfo import NATIVE_FILE_EXTENSION

from ourstdlibs.behaviour import empty_function

from surfsman.render import render_rect

from textman.label.main import Label

from colorsman.colors import (
                        NORMAL_PATH_FG, SELECTED_PATH_FG,
                        NORMAL_PATH_BG, SELECTED_PATH_BG,
                      )

from fileman.surfs import (
                     FILE_ICON, FOLDER_ICON, TEXT_ICON,
                     PYTHON_ICON, IMAGE_ICON, FONT_ICON,
                     AUDIO_ICON, VIDEO_ICON, PDF_ICON,
                     NATIVE_FILE_ICON,
                   )

from fileman.constants import (
                         FONT_HEIGHT,
                         PATH_OBJ_PARENT_TEXT,
                       )


### constants

## common keyword arguments for text

NORMAL_KWARGS = {
  'font_height'      : FONT_HEIGHT,
  'foreground_color' : NORMAL_PATH_FG,
  'padding'          : 0,
}


SELECTED_KWARGS = {
  'font_height'      : FONT_HEIGHT,
  'foreground_color' : SELECTED_PATH_FG,
  'padding'          : 0,
}


## icon map for file extensions

ICON_MAP = {

  '.txt'  : TEXT_ICON,
  '.py'   : PYTHON_ICON,
  '.png'  : IMAGE_ICON,
  '.jpg'  : IMAGE_ICON,
  '.jpeg' : IMAGE_ICON,
  '.ttf'  : FONT_ICON,
  '.otf'  : FONT_ICON,
  '.mp3'  : AUDIO_ICON,
  '.wav'  : AUDIO_ICON,
  '.ogg'  : AUDIO_ICON,
  '.mp4'  : VIDEO_ICON,
  '.mov'  : VIDEO_ICON,
  '.mkv'  : VIDEO_ICON,
  '.ogv'  : VIDEO_ICON,
  '.pdf'  : PDF_ICON,

  NATIVE_FILE_EXTENSION : NATIVE_FILE_ICON,

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
          coordinates_name='topleft',
          coordinates_value=(0, 0)
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
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            'coordinates value' argument.
        coordinates_value (iterable with 2 integers)
            position information to be assigned to the
            rect of this path object; such position will
            be assigned to the rect's attribute whose name
            is given as the 'coordinates_name' argument.
        """
        ### assign a text for the widget based on the paths
        ### received

        if path is None: text = t.file_manager.dummy_text

        elif (

             grandparent_path is None
          or path != grandparent_path

        ): text = path.name

        else: text = PATH_OBJ_PARENT_TEXT

        self.text = text

        ### store arguments

        self.path    = path
        self.width   = width
        self.padding = padding

        ### create objects for display
        self.create_visuals()

        ### we use the rect of one of the background
        ### surfaces created as the rect for the whole
        ### path object
        self.rect = self.normal_bg.get_rect()

        ### assign drawing behaviour based on path

        self.draw = (

          empty_function
          if path is None

          else self.draw_objects

        )

        ### assign icon if path is not None

        if path is not None:

            self.icon = (

              ## folder icon if a folder

              FOLDER_ICON
              if path.is_dir()

              ## otherwise custom icon, depending on suffix

              else ICON_MAP.get(
                              path.suffix.lower(),
                              FILE_ICON
                            )
            )

        ### position objects relative to each other

        ## whole object

        setattr(
          self.rect, coordinates_name, coordinates_value
        )

        ## obtain a topleft position for the icon which
        ## is the result of aligning its center vertically
        ## with the whole object, also adding an horizontal
        ## padding from the right of self.rect (the whole
        ## object)

        icon_rect = FILE_ICON.get_rect()

        icon_rect.midleft = (
          self.rect.move(padding, 0).midleft
        )

        self.icon_pos = icon_rect.topleft

        ## assign a midleft position for the label so they
        ## end up with their centers vertically aligned
        ## with the icon (and thus with the vertical
        ## center of the whole object), also adding an
        ## horizontal padding from the icon

        label_midleft = icon_rect.move(padding, 0).midright

        self.normal_label.rect.midleft   = label_midleft
        self.selected_label.rect.midleft = label_midleft

    def create_visuals(self):
        """Create and store objects for display."""
        ### create labels

        ## define max width for labels, by subtracting
        ## the width of the icon and the padding in both
        ## sides of the icon from the self.width argument
        ## defined upon initialization; note we also remove
        ## some extra pixels from the width, using an
        ## amount defined empirically, just for better
        ## aesthetics

        label_max_width = (
          self.width
          - FILE_ICON.get_width() # TODO use constant instead
          - (self.padding * 2)
          - 7 # arbitrary value defined empirically
        )

        ## instantiate and store labels

        self.normal_label = Label(
                              text      = self.text,
                              max_width = label_max_width,
                              **NORMAL_KWARGS
                            )
        
        self.selected_label = Label(
                                text      = self.text,
                                max_width = label_max_width,
                                **SELECTED_KWARGS
                              )

        ### define size for background

        ## the height is the height of the tallest object
        ## plus padding from both vertical ends

        max_height = max(
                       FILE_ICON.get_height(),
                       self.normal_label.rect.height
                     )

        height = max_height + (self.padding * 2)

        ## size is self.width plus the height we just
        ## calculated
        bg_size = self.width, height

        ### create and store backgrounds

        self.normal_bg = render_rect(
                           *bg_size, NORMAL_PATH_BG
                         )
        self.selected_bg = render_rect(
                             *bg_size, SELECTED_PATH_BG
                           )

        ### assign current bg and label

        self.bg    = self.normal_bg
        self.label = self.normal_label

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
        ### an empty function
        if path is None: drawing_behaviour = empty_function
            
        ### otherwise, if path isn't None...

        else:
            
            ## update text attribute and text in labels

            if (

                 grandparent_path is None
              or path != grandparent_path

            ): text = path.name

            else: text = '..'

            self.text = text

            self.normal_label.set(text)
            self.selected_label.set(text)

            ### update icon

            self.icon = (

              ## folder icon if a folder
              FOLDER_ICON
              if path.is_dir()

              ## otherwise custom icon if file, based
              ## on suffix
              else ICON_MAP.get(
                              path.suffix.lower(), FILE_ICON
                            )
            )

            ## set drawing behaviour to draw all objects
            drawing_behaviour = self.draw_objects

        ### finally store the path and drawing behaviour

        self.path = path
        self.draw = drawing_behaviour

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
        prefix = 'selected' if on else 'normal'

        ### put together attribute names for the label
        ### and background using the prefix

        label_attr_name = prefix + '_label'
        bg_attr_name    = prefix + '_bg'

        ### use the attribute names to grab the objects
        ### to be used as 'label' and 'bg'

        self.label = getattr(self, label_attr_name)
        self.bg    = getattr(self, bg_attr_name)

    select = partialmethod(
               change_selection_appearance,  True
             )

    deselect = partialmethod(
                 change_selection_appearance, False
               )

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
        ### draw background
        blit_on_screen(self.bg, self.rect)

        ### draw icon
        blit_on_screen(self.icon, self.icon_pos)

        ### draw label
        self.label.draw()
