
### standard library imports

from functools import partial

from copy import deepcopy

from contextlib import suppress


### local imports

from config import APP_REFS

from ourstdlibs.behaviour import get_suppressing_callable

from menu.main import MenuManager

from loopman.exception import ContinueLoopException


class TextBlockPopupMenu:

    def __init__(self):

        menu_list = [

          {
             'label': "Edit this block's text",
             'command': self.edit_block_text,
          },

          {
             'label': "Move this block",
             'command': self.move_block,
          },

          {
             'label': "Duplicate this block",
             'command': self.duplicate_block,
          },

          {
             'label'   : "Delete this block",
             'command' : self.delete_block,
          },

        ]

        self.text_block_only_popup = (

          MenuManager(

            menu_list,

            is_menubar  = False,
            use_outline = True,
            keep_focus_when_unhovered=True,

          )

        )

        ###

        menu_list.extend([

          {'label' : "---"},

          {
             'label'   : "Move selected objects",
             'command' : get_suppressing_callable(
                           APP_REFS.ea.start_moving,
                           ContinueLoopException,
                         )
          },

          {
             'label'   : "Duplicate selected objects",
             'command' : get_suppressing_callable(
                           APP_REFS.ea.duplicate_selected,
                           ContinueLoopException,
                         )
          },

          {
             'label'   : "Delete selected objects",
             'command' : APP_REFS.ea.remove_selected,
          },

        ])

        self.text_block_and_selected_popup = (

          MenuManager(

            menu_list,

            is_menubar  = False,
            use_outline = True,
            keep_focus_when_unhovered=True,

          )

        )

    def show(self, text_block, mouse_pos):

        self.text_block_under_mouse = text_block

        if text_block in APP_REFS.ea.selected_objs:

            (
              self
              .text_block_and_selected_popup
              .focus_if_within_boundaries(mouse_pos) 
            )

        else: (
                self
                .text_block_only_popup
                .focus_if_within_boundaries(mouse_pos) 
              )

    def edit_block_text(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(
          self.text_block_under_mouse
        )

        APP_REFS.ea.edit_text_of_selected()

    def move_block(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(
          self.text_block_under_mouse
        )

        with suppress(ContinueLoopException):
            APP_REFS.ea.start_moving()

    def duplicate_block(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(
          self.text_block_under_mouse
        )

        with suppress(ContinueLoopException):
            APP_REFS.ea.duplicate_selected()

    def delete_block(self):

        APP_REFS.ea.deselect_all()

        APP_REFS.ea.add_obj_to_selection(
          self.text_block_under_mouse
        )

        APP_REFS.ea.remove_selected()
