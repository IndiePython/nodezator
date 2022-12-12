"""Facility with class for filesystem browsing.

This module contains code relative to instantiation
and setup of the file manager class.
"""

### third-party imports

from pygame.math import Vector2

from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..pygameconstants import SCREEN_RECT

from ..translation import TRANSLATION_HOLDER as t

from ..ourstdlibs.behaviour import (
    empty_function,
    get_oblivious_callable,
)

from ..surfsman.draw import draw_border
from ..surfsman.render import render_rect

from ..surfsman.icon import render_layered_icon

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP, EMPTY_SURF

from ..widget.stringentry import StringEntry

from ..classes2d.single import Object2D
from ..classes2d.collections import Set2D

from ..textman.render import render_text

from ..textman.label.main import Label

from ..colorsman.colors import (
    BLACK,
    NORMAL_PATH_FG,
    NORMAL_PATH_BG,
    BUTTON_BG,
    BUTTON_FG,
    WINDOW_BG,
    WINDOW_FG,
)

from .constants import FILEMAN_SIZE, FONT_HEIGHT

## class extension
from .op import FileManagerOperations

## classes for composition

from .dirpanel.main import DirectoryPanel
from .bookmarkpanel.main import BookmarkPanel


### XXX for extra flexibility, the order in which some
### widgets/objects are created/positioned or have their
### size defined could be improved; I'm not 100% sure,
### though, as other things would have to be balanced and
### end up cancelling the benefits;
###
### this demands a careful study, and is not urgent at all,
### since even if we achieve improvements it isn't clear
### whether they would also improve the workflow of users
### considerably; for now, I'll leave this note here for
### the future;


class FileManager(FileManagerOperations):
    """A filesystem browser for creating and selecting paths.

    This class is instantiated only once and its main methods
    are aliased in the end of the module, ready to be used
    however needed: to either select existing paths (files,
    folders) or create a new path.
    """

    def __init__(self):
        """Assign variables, perform setups."""
        ### reference itself in APP_REFS
        APP_REFS.fm = self

        ### create image and rect attributes

        self.image = render_rect(*FILEMAN_SIZE, WINDOW_BG)

        draw_border(self.image)

        self.rect = self.image.get_rect()

        ### set controls

        ## control for storing current mode
        self.current_mode = None

        ## control for storing selected paths
        self.path_selection = []

        ### store semitransparent object the size of
        ### this widget's rect

        self.rect_size_semitransp_obj = Object2D.from_surface(
            surface=UNHIGHLIGHT_SURF_MAP[self.rect.size]
        )

        ### build widget structure and assign variables

        self.blit_static_surfs_on_image()
        self.build_labels()
        self.instantiate_and_store_widgets()

        ### assign update behaviour
        self.update = empty_function

        ### reposition objects
        self.reposition_objects()

        ### draw background of panels on our own background,
        ### so we don't need to draw them every loop

        offset = -Vector2(self.rect.topleft)

        for panel in self.panels:

            offset_rect = panel.rect.move(offset)

            draw_rect(self.image, NORMAL_PATH_BG, offset_rect)

            draw_rect(self.image, BLACK, offset_rect, 1)

        ### append repositioning method as a
        ### window resizing setup

        APP_REFS.window_resize_setups.append(self.reposition_objects)

    def blit_static_surfs_on_image(self):
        """Create and blit surfaces on self.image.

        These images never change or move, this is why
        we call them "static". This means we can blit
        them on the background once and for all, instead
        of having to blit them every loop.
        """
        ### blit surfaces on the background representing
        ### this file manager icon plus its name (with
        ### an hyphen)

        ## instantiate objects

        icon_obj = Object2D.from_surface(
            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (33, 34)],
                dimension_name="height",
                dimension_value=30,
                colors=[BLACK, (30, 130, 70)],
                background_width=32,
                background_height=32,
            )
        )

        title_obj = Object2D.from_surface(
            render_text(
                f"{t.file_manager.caption} -",
                font_height=FONT_HEIGHT,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
                padding=5,
            )
        )

        ## store them in a special set
        app_objs = Set2D((icon_obj, title_obj))

        ## align title midleft with icon midright
        title_obj.rect.midleft = icon_obj.rect.midright

        ## store distance from origin to title obj midright
        ## to use as an offset to position the caption
        ## label
        self.caption_label_offset = title_obj.rect.move(2, 5).midright

        ## now move the objects together, so they sit near
        ## the topleft corner of our background
        app_objs.rect.topleft = (5, 5)

        ## finally, draw them on our background
        app_objs.draw_on_surf(self.image)

        ### draw text objects on background

        ## parameters for objects to be created

        surf_params = [
            (
                t.file_manager.current + ":",
                self.rect.move(5, 40).topleft,
            ),
            (
                t.file_manager.bookmarks,
                self.rect.move(5, 70).topleft,
            ),
            (
                t.file_manager.directory_contents,
                self.rect.move(300, 70).topleft,
            ),
        ]

        ## a temporary container
        temp_container = []

        ## obtain the inverted topleft coordinates of the
        ## file manager as a vector, to use as an offset
        ## when drawing surfaces on the self.image surface
        fileman_offset = -Vector2(self.rect.topleft)

        ## create a surf for each pair of parameters
        ## and blit it on self.image after offsetting it

        for text, topleft in surf_params:

            surf = render_text(
                text,
                font_height=FONT_HEIGHT,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
                padding=5,
            )

            surf_offset = topleft + fileman_offset

            self.image.blit(surf, surf_offset)

            temp_container.append(surf)

        ### store the midright of the first surface
        ### as a midleft coordinate for the navigation
        ### entry (an entry from the directory
        ### panel object which we'll instantiate in
        ### another method)

        ## retrieve topleft coordinates of first surf
        x, y = surf_params[0][1]

        ## get size of first surf
        surf_width, surf_height = temp_container[0].get_size()

        ## increment x
        x += surf_width

        ## increment y
        y += (surf_height // 2)

        ## finally store the new coordinates
        self.navigation_entry_offset = x, y

    def build_labels(self):
        """Build and store label objects."""
        ### create a special set to store labels
        self.labels = Set2D()

        ### caption label (caption can be set when
        ### summoning the file manager)

        ## define maximum width

        max_width = self.rect.right - self.caption_label_offset[0] - 20

        ## instantiate and store it

        self.caption_label = Label(
            t.file_manager.caption,
            font_height=FONT_HEIGHT,
            padding=5,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
            max_width=max_width,
        )

        self.labels.add(self.caption_label)

        ### create a label to help identify the purpose of
        ### the widget beside it; its text will be changed
        ### according to the current mode; that is, it will
        ### be either 'Selected:' or 'New path:'

        self.selected_label = Object2D.from_surface(
            render_text(
                t.file_manager.selected + ":",
                font_height=FONT_HEIGHT,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
            )
        )

        self.labels.add(self.selected_label)

    def instantiate_and_store_widgets(self):
        """Instantiate and store panels and other objects."""
        ### instantiate directory panel
        dir_panel = DirectoryPanel(self)

        ### store it in its own attribute in this file
        ### manager, as well as several of its
        ### operations/objects

        ## store panel
        self.dir_panel = dir_panel

        ## for each attribute name, retrieve that attribute
        ## from the directory panel and store that same
        ## attribute, using the same name, on this instance

        for attribute_name in (
            "go_to_previous",
            "go_to_next",
            "jump_many_up",
            "jump_many_down",
            "go_to_first",
            "go_to_last",
            "select_all",
            "deselect_all",
            "load_parent",
            "load_home",
            "load_selected",
            "parent_button",
            "home_button",
            "reload_dir_button",
            "new_file_button",
            "new_folder_button",
            "navigation_entry"
        ):
            attribute = getattr(dir_panel, attribute_name)
            setattr(self, attribute_name, attribute)

        ### instantiate and store the bookmark panel,
        ### passing along references to the directory
        ### panel and our rect sized semitransparent
        ### object

        self.bkm_panel = BookmarkPanel(
            self.dir_panel,
            self.rect_size_semitransp_obj,
        )

        ### also reference bookmark panel buttons

        for attr_name in ("bookmark_button", "unbookmark_button"):
            button = getattr(self.bkm_panel, attr_name)
            setattr(self, attr_name, button)

        ### store panels

        self.panels = Set2D()
        self.panels.update((self.dir_panel, self.bkm_panel))

        ### create a submit button and a cancel button (we
        ### use text objects with a simple finish to give
        ### them depth)

        ## submit button

        self.submit_button = Object2D.from_surface(
            surface=render_text(
                t.file_manager.submit,
                font_height=FONT_HEIGHT,
                foreground_color=BUTTON_FG,
                background_color=BUTTON_BG,
                padding=5,
                depth_finish_thickness=1,
            ),
        )

        self.submit_button.on_mouse_release = get_oblivious_callable(
            self.submit
        )

        ## cancel button

        self.cancel_button = Object2D.from_surface(
            surface=render_text(
                t.file_manager.cancel,
                font_height=FONT_HEIGHT,
                foreground_color=BUTTON_FG,
                background_color=BUTTON_BG,
                padding=5,
                depth_finish_thickness=1,
            ),
        )

        self.cancel_button.on_mouse_release = (
            get_oblivious_callable(self.cancel)
        )

        ### create an entry widget to edit path names;

        self.selection_entry = StringEntry(
            value='',
            loop_holder=self,
            font_height=FONT_HEIGHT,
            draw_on_window_resize=self.draw,
            width=550,
            command=self.update_selection_from_entry,
        )

        ### reference all buttons together in a set

        self.buttons = Set2D(
            (
                self.home_button,
                self.reload_dir_button,
                self.parent_button,
                self.new_file_button,
                self.new_folder_button,
                self.bookmark_button,
                self.unbookmark_button,
                self.navigation_entry,
                self.selection_entry,
                self.cancel_button,
                self.submit_button,
            )
        )

    def reposition_objects(self):

        self.rect.center = SCREEN_RECT.center

        self.rect_size_semitransp_obj.rect.center = self.rect.center

        self.dir_panel.reposition()
        self.bkm_panel.reposition()

        self.caption_label.rect.midleft = self.rect.move(
            self.caption_label_offset
        ).topleft

        self.selected_label.rect.bottomleft = self.rect.move(10, -15).bottomleft
        self.selection_entry.rect.midleft = self.selected_label.rect.move(5, 0).midright

        ## reposition the current path entry with the
        ## offset we saved for it

        self.navigation_entry.rect.midleft = self.rect.move(
            self.navigation_entry_offset
        ).topleft

        ### reposition buttons relative to the right side
        ### of the file manager and the top of the
        ### directory panel

        ## retrieve a bottomright coordinate

        bottomright = (
            self.rect.move(-10, 0).right,
            self.dir_panel.rect.move(0, -5).top,
        )

        ## position each button side by side, using the
        ## bottomleft coordinate of one as the bottomright
        ## coordinate of the other, with a small offset

        for button in (
            self.unbookmark_button,
            self.bookmark_button,
            self.new_folder_button,
            self.new_file_button,
            self.parent_button,
            self.reload_dir_button,
            self.home_button,
        ):
            button.rect.bottomright = bottomright
            bottomright = button.rect.move(-5, 0).bottomleft

        self.submit_button.rect.bottomright = self.rect.move(-10, -10).bottomright

        self.cancel_button.rect.topright = self.submit_button.rect.move(-5, 0).topleft


select_paths = FileManager().select_paths
