"""Facility with class for filesystem browsing.

This module contains code relative to instantiation
and setup of the file manager class.
"""

### third-party imports

from pygame.math import Vector2

from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..pygamesetup import SCREEN_RECT

from ..translatedtext import TRANSLATIONS

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

from ..textman.render import render_text, get_text_size

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

from .initialpositioning import position_elements_and_get_height

from .constants import (
    FONT_HEIGHT,
    FILEMAN_WIDTH,
    BKM_PANEL_WIDTH,
)

## class extension
from .op import FileManagerOperations

## classes for composition

from .dirpanel.main import DirectoryPanel
from .bookmarkpanel.main import BookmarkPanel



### translations
t = TRANSLATIONS.file_manager


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

        ### set controls

        ## control for storing current mode
        self.current_mode = None

        ## control for storing selected paths
        self.path_selection = []

        ### flag to change behaviour when selecting only files
        ### (not folders); check the select_paths method for
        ### extra info on this flag
        self.expecting_files_only = False

        ### build widget structure

        caption_objs = get_caption_objs()

        ## store distance from origin to title obj midright to use as
        ## an offset to position the caption label
        self.caption_label_offset = caption_objs.rect.move(2, 0).midright

        ## store specific measurements in dedicated attributes

        self.current_label_top = caption_objs.rect.bottom
        self.panels_labels_top = self.current_label_top + FONT_HEIGHT + 10

        ##

        self.build_labels(
            FILEMAN_WIDTH - caption_objs.rect.width - 20
        )

        self.instantiate_and_store_widgets()

        ### perform initial positioning of all elements and calculate
        ### height of area occupied by them (since we already know the
        ### width, which is a fixed amount)
        rect_height = position_elements_and_get_height(self)

        ### assign update behaviour
        self.update = empty_function

        ### create image and rect attributes

        self.image = render_rect(FILEMAN_WIDTH, rect_height, WINDOW_BG)

        draw_border(self.image)
        self.rect = self.image.get_rect()

        ###
        self.blit_static_surfs_on_image(caption_objs)

        ### store semitransparent object the size of
        ### this widget's rect

        self.rect_size_semitransp_obj = (

            Object2D.from_surface(
                surface=UNHIGHLIGHT_SURF_MAP[self.rect.size]
            )

        )

        ### reposition objects
        self.reposition_objects()

        ### draw background of panels on our own background, so we don't need
        ### to draw them every loop

        offset = -Vector2(self.rect.topleft)

        for panel in self.panels:

            offset_rect = panel.rect.move(offset)

            draw_rect(self.image, NORMAL_PATH_BG, offset_rect)

            draw_rect(self.image, BLACK, offset_rect, 1)

        ### append repositioning method as a
        ### window resizing setup

        APP_REFS.window_resize_setups.append(self.reposition_objects)

    def blit_static_surfs_on_image(self, caption_objs):
        """Create and blit surfaces on self.image.

        These images never change or move, this is why
        we call them "static". This means we can blit
        them on the background once and for all, instead
        of having to blit them every loop.
        """
        ### draw caption objs on our background
        caption_objs.draw_on_surf(self.image)

        ### blit surfaces on the background representing this file manager icon
        ### plus its name, then an hyphen

        ### draw text objects on background

        for text, topleft in (

            (t.current + ":", (5, self.current_label_top)),
            (t.bookmarks, (5, self.panels_labels_top)),

            (
                t.directory_contents,
                (10 + BKM_PANEL_WIDTH , self.panels_labels_top),
            ),

        ):

            surf = (

                render_text(
                    text,
                    font_height=FONT_HEIGHT,
                    foreground_color=WINDOW_FG,
                    background_color=WINDOW_BG,
                    padding=5,
                )

            )

            self.image.blit(surf, topleft)


    def build_labels(self, caption_label_max_width):
        """Build and store label objects."""
        ### create a special set to store labels
        self.labels = Set2D()

        ### caption label (caption can be set when summoning the file manager)

        ## instantiate and store it

        self.caption_label = (

            Label(
                t.caption,
                font_height=FONT_HEIGHT,
                padding=5,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
                max_width=caption_label_max_width,
            )

        )

        self.labels.add(self.caption_label)

        ### create a label to help identify the purpose of
        ### the widget beside it; its text will be changed
        ### according to the current mode; that is, it will
        ### be either 'Selected:' or 'New path:'

        self.selected_label = (

            Object2D.from_surface(
                render_text(
                    t.selected + ":",
                    font_height=FONT_HEIGHT,
                    foreground_color=WINDOW_FG,
                    background_color=WINDOW_BG,
                )
            )

        )

        self.labels.add(self.selected_label)

    def instantiate_and_store_widgets(self):
        """Instantiate and store panels and other objects."""

        current_label_size = (

            get_text_size(
                text=t.current + ":",
                font_height=FONT_HEIGHT,
                padding=5,
            )

        )

        self.navigation_entry_offset = (

            ### x

            (
                10
                + current_label_size[0]
            ),

            ### y
            self.current_label_top + (current_label_size[1]//2)
        )

        ### instantiate directory panel; store it as attribute and
        ### reference it locally as well
        dir_panel = self.dir_panel = DirectoryPanel(self)

        ### reference relevant directory panel attributes in our own
        ### attributes

        for attribute_name in (
            'go_to_previous',
            'go_to_next',
            'jump_many_up',
            'jump_many_down',
            'go_to_first',
            'go_to_last',
            'select_all',
            'deselect_all',
            'load_parent',
            'load_home',
            'load_selected',
            'parent_button',
            'home_button',
            'reload_dir_button',
            'new_file_button',
            'new_folder_button',
            'navigation_entry'
        ):

            setattr(
                self,
                attribute_name,
                getattr(dir_panel, attribute_name)
            )

        ### instantiate bookmark panel; store it as attribute and
        ### reference it locally as well
        bkm_panel = self.bkm_panel = BookmarkPanel(self, dir_panel)

        ### also reference bookmark panel buttons as our own attributes

        for attr_name in ('bookmark_button', 'unbookmark_button'):

            setattr(
                self,
                attr_name,
                getattr(bkm_panel, attr_name),
            )

        ### store panels

        self.panels = Set2D()
        self.panels.update((self.dir_panel, self.bkm_panel))

        ### create a submit button and a cancel button (we use text objects
        ### with a simple finish to give them depth)

        ## submit button

        self.submit_button = (

            Object2D.from_surface(

                render_text(
                    t.submit,
                    font_height=FONT_HEIGHT,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                    padding=5,
                    depth_finish_thickness=1,
                )

            )

        )

        self.submit_button.on_mouse_release = (
            get_oblivious_callable(self.submit)
        )

        ## cancel button

        self.cancel_button = (

            Object2D.from_surface(

                render_text(
                    t.cancel,
                    font_height=FONT_HEIGHT,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                    padding=5,
                    depth_finish_thickness=1,
                )

            )

        )

        self.cancel_button.on_mouse_release = (
            get_oblivious_callable(self.cancel)
        )

        ### create an entry widget to edit path names;

        entry_width = (
            FILEMAN_WIDTH
            - 40
            - self.selected_label.rect.width
            - self.cancel_button.rect.width
            - self.submit_button.rect.width
        )

        self.selection_entry = (

            StringEntry(
                value='',
                loop_holder=self,
                font_height=FONT_HEIGHT,
                draw_on_window_resize=self.draw,
                width=entry_width,
                command=self.update_selection_from_entry,
            )

        )

        ### reference all buttons together in a set

        self.buttons = (

            Set2D((
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
            ))

        )

    def reposition_objects(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.move_ip(diff)

        self.rect_size_semitransp_obj.rect.move_ip(diff)

        self.dir_panel.reposition(diff)

        # bkm_panel doesn't need diff, as positions itself relative
        # to dir panel
        self.bkm_panel.reposition()

        self.caption_label.rect.move_ip(diff)

        self.selected_label.rect.move_ip(diff)

        self.selection_entry.rect.move_ip(diff)

        self.navigation_entry.rect.move_ip(diff)

        ### reposition buttons relative to the right side
        ### of the file manager and the top of the
        ### directory panel

        ## retrieve a bottomright coordinate
        bottomright = self.dir_panel.rect.move(0, -3).topright

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

        self.submit_button.rect.move_ip(diff)
        self.cancel_button.rect.move_ip(diff)


def get_caption_objs(): 

    icon_obj = (

        Object2D.from_surface(

            render_layered_icon(
                chars=[chr(ordinal) for ordinal in (33, 34)],
                dimension_name="height",
                dimension_value=30,
                colors=[BLACK, (30, 130, 70)],
                background_width=32,
                background_height=32,
            )

        )

    )

    title_obj = (

        Object2D.from_surface(

            render_text(
                t.caption + " -",
                font_height=FONT_HEIGHT,
                foreground_color=WINDOW_FG,
                background_color=WINDOW_BG,
                padding=5,
            )

        )

    )

    ## align title midleft with icon midright
    title_obj.rect.midleft = icon_obj.rect.midright

    ## store them in a special set
    caption_objs = Set2D((icon_obj, title_obj))

    ## now move the objects together, so they sit near the topleft
    ## corner of our background
    caption_objs.rect.topleft = (5, 5)

    return caption_objs


select_paths = FileManager().select_paths
