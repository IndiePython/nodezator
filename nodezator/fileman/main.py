"""Facility with class for filesystem browsing.

This module contains code relative to instantiation
and setup of the file manager class.
"""

### third-party imports

from pygame.math import Vector2
from pygame.draw import rect as draw_rect


### local imports

from translation import TRANSLATION_HOLDER as t

from pygameconstants import SCREEN_RECT

from ourstdlibs.behaviour import (
                            empty_function,
                            get_oblivious_callable,
                          )

from surfsman.draw import draw_border
from surfsman.render import render_rect

from surfsman.icon import render_layered_icon

from widget.stringentry import StringEntry

from classes2d.single      import Object2D
from classes2d.collections import Set2D

from textman.render import render_text

from textman.label.main import Label

from colorsman.colors import (
                        BLACK,
                        CONTRAST_LAYER_COLOR,
                        NORMAL_PATH_FG,
                        NORMAL_PATH_BG,
                        BUTTON_BG, BUTTON_FG,
                        WINDOW_BG, WINDOW_FG,
                      )

from fileman.constants import FILEMAN_SIZE, FONT_HEIGHT

## class extension
from fileman.op import FileManagerOperations

## classes for composition

from fileman.dirpanel.main      import DirectoryPanel
from fileman.bookmarkpanel.main import BookmarkPanel


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
        ### create image and rect attributes and position

        self.image = render_rect(
                        *FILEMAN_SIZE, WINDOW_BG)

        draw_border(self.image)

        self.rect        = self.image.get_rect()
        self.rect.center = SCREEN_RECT.center

        ### set controls

        ## control for storing current mode
        self.current_mode = None
        
        ## control for storing the path selection
        self.path_selection = []

        ### store semitransparent object the size of
        ### this widget's rect

        self.rect_size_semitransp_obj = \
          Object2D.from_surface(
            surface=render_rect(
                   *self.rect.size,
                   (*CONTRAST_LAYER_COLOR, 130),
                 ),
            coordinates_name='topleft',
            coordinates_value=self.rect.topleft
          )

        ### build widget structure and assign variables

        self.blit_static_surfs_on_image()
        self.build_labels()
        self.instantiate_and_store_widgets()

        ### assign update behaviour
        self.update = empty_function

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
                       chars = [
                         chr(ordinal)
                         for ordinal in (33, 34)
                       ],

                       dimension_name  = 'height',
                       dimension_value = 30,

                       colors = [BLACK, (30, 130, 70)],

                       background_width  = 32,
                       background_height = 32
                     )
                   )

        title_obj = Object2D.from_surface(
                      render_text(
                        t.file_manager.caption + " -",
                        font_height      = FONT_HEIGHT,
                        foreground_color = WINDOW_FG,
                        background_color = WINDOW_BG,
                        padding          = 5
                      )
                    )

        ## store them in a special set
        app_objs = Set2D((icon_obj, title_obj))

        ## align title midleft with icon midright
        title_obj.rect.midleft = icon_obj.rect.midright

        ## now move the objects together, so they sit near
        ## the topleft corner of our background
        app_objs.rect.topleft = (5, 5)

        ## finally, draw them on our background
        app_objs.draw_on_surf(self.image)

        ### also store the midright coordinates of the
        ### whole area occupied by the app objects
        ### defined above;
        ### 
        ### it will be used as the midleft position of
        ### a label for custom captions which we'll create
        ### further ahead
        self.caption_label_midleft = \
            app_objs.rect.move(self.rect.topleft).midright

        ### draw text objects on background

        ## parameters for objects to be created

        surf_params = [

          (
             t.file_manager.current + ":",
             self.rect.move(  5, 40).topleft,
          ),

          (
            t.file_manager.bookmarks,
            self.rect.move(  5, 70).topleft,
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
        ## and blit it on self.image after offset it

        for text, topleft in surf_params:

            surf = render_text(
                     text, font_height=FONT_HEIGHT,
                     foreground_color=WINDOW_FG,
                     background_color=WINDOW_BG,
                     padding=5
                   )

            surf_offset = topleft + fileman_offset

            self.image.blit(surf, surf_offset)

            temp_container.append(surf)

        ### store the topright of the first surface
        ### as a topleft coordinate for the "current
        ### path label" (a label from the directory
        ### panel object which we'll instantiate in
        ### another method)

        ## retrieve topleft coordinates of first surf
        x, y = surf_params[0][1]

        ## get width of first surf
        surf_width = temp_container[0].get_width()

        ## increment x
        x += surf_width

        ## finally store the new coordinates
        self.current_path_label_topleft = x, y

    def build_labels(self):
        """Build and store label objects."""
        ### create a special set to store labels
        self.labels = Set2D()

        ### caption label (caption can be set when
        ### summoning the file manager)

        ## define maximum width

        max_width = (
          self.rect.right
          - self.caption_label_midleft[0]
          - 20
        )

        ## instantiate and store it

        self.caption_label = \
          Label(
            t.file_manager.caption,
            font_height=FONT_HEIGHT,
            padding=0,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
            coordinates_name='midleft',
            coordinates_value=self.caption_label_midleft,
            max_width=max_width
          )

        self.labels.add(self.caption_label)

        ### create a label to help identify the purpose of
        ### the widget beside it; its text will be changed
        ### according to the current mode; that is, it will
        ### be either 'Selected:' or 'New path:'

        bottomleft = self.rect.move(5, -10).bottomleft

        self.widget_label = \
          Label(
            t.file_manager.selected + ":",
            font_height=FONT_HEIGHT,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
            coordinates_name='bottomleft',
            coordinates_value=bottomleft
          )

        self.labels.add(self.widget_label)
        
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
          'current_path_lb'

        ):
            attribute = getattr(dir_panel, attribute_name)
            setattr(self, attribute_name, attribute)

        ## reposition the current path label with the
        ## topleft coordinate we saved for it
        self.current_path_lb.rect.topleft = \
                        self.current_path_label_topleft

        ## also store the current path label in the
        ## labels special collection
        self.labels.add(self.current_path_lb)

        ### instantiate and store the bookmark panel,
        ### passing along references to the directory
        ### panel and our rect sized semitransparent
        ### object

        self.bkm_panel = BookmarkPanel(
                           self.dir_panel,
                           self.rect_size_semitransp_obj
                         )

        ### also reference bookmark panel buttons

        for attr_name in (
          'bookmark_button', 'unbookmark_button'
        ):
            button = getattr(self.bkm_panel, attr_name)
            setattr(self, attr_name, button)

        ### store panels

        self.panels = Set2D()
        self.panels.update((self.dir_panel, self.bkm_panel))

        ### draw background of panels on our own background,
        ### so we don't need to draw them every loop

        offset = -Vector2(self.rect.topleft)

        for panel in self.panels:

            offset_rect = panel.rect.move(offset)

            draw_rect(self.image, NORMAL_PATH_BG, offset_rect)
            draw_rect(self.image, BLACK, offset_rect, 1)

        ### reposition buttons relative to the right side
        ### of the file manager and the top of the
        ### directory panel

        ## retrieve a bottomright coordinate

        bottomright = (
          self.rect.move(-10, 0).right,
          self.dir_panel.rect.move(0, -5).top
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
          self.home_button
        ):
            button.rect.bottomright = bottomright
            bottomright = button.rect.move(-5, 0).bottomleft

        ### create a submit button and a cancel button (we
        ### use text objects with a simple finish to give
        ### them depth)

        ## submit button

        bottomright = self.rect.move(-10, -10).bottomright

        self.submit_button = \
          Object2D.from_surface(
            surface=render_text(
                      t.file_manager.submit,
                      font_height=FONT_HEIGHT,
                      foreground_color=BUTTON_FG,
                      background_color=BUTTON_BG,
                      padding=5,
                      depth_finish_thickness=1,
                    ),
            coordinates_name='bottomright',
            coordinates_value=bottomright
          )

        self.submit_button.on_mouse_release = (
          get_oblivious_callable(self.submit_selected)
        )

        ## cancel button

        topright = \
            self.submit_button.rect.move(-5, 0).topleft

        self.cancel_button = \
          Object2D.from_surface(
            surface=render_text(
                   t.file_manager.cancel,
                   font_height=FONT_HEIGHT,
                   foreground_color=BUTTON_FG,
                   background_color=BUTTON_BG,
                   padding=5,
                   depth_finish_thickness=1
                 ),
            coordinates_name='topright',
            coordinates_value=topright
          )

        self.cancel_button.on_mouse_release = \
                         get_oblivious_callable(self.cancel)


        ### create an entry widget;
        ###
        ### no need to position it, since it is repositioned
        ### every time the file manager is entered;

        self.entry = StringEntry(
                       value=t.file_manager.pathname,
                       loop_holder=self,
                       font_height=FONT_HEIGHT,
                       width=550
                     )

        ### create a label to show the current path(s)
        ### selected when in 'select_path' mode (it appears
        ### in the same spot as the entry when in such mode,
        ### and the entry is not displayed)

        self.selection_label = \
            Label(
              text=t.file_manager.no_path_selected,
              font_height=FONT_HEIGHT,
              padding=0,
              max_width=550,
              foreground_color=NORMAL_PATH_FG,
              background_color=NORMAL_PATH_BG
            )

        ### reference all buttons together in a set

        self.buttons = Set2D((
          self.home_button,
          self.reload_dir_button,
          self.parent_button,
          self.new_file_button,
          self.new_folder_button,
          self.bookmark_button,
          self.unbookmark_button,
          self.cancel_button,
          self.submit_button,
        ))

_ = FileManager()

select_path  = _.select_path
create_path  = _.create_path
