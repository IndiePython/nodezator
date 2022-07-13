"""Facility with a directory panel for the file manager."""

### standard library imports

from pathlib   import Path
from functools import partialmethod


### third-party imports

from pygame import Rect

from pygame.math import Vector2
from pygame.draw import rect      as draw_rect
from pygame.time import get_ticks as get_milliseconds


### local imports

from ...pygameconstants import SCREEN

from ...dialog import create_and_show_dialog

from ...ourstdlibs.behaviour import get_oblivious_callable

from ...surfsman.draw import (
                     blit_aligned,
                     draw_border,
                     draw_depth_finish,
                   )

from ...surfsman.render import render_rect

from ...classes2d.single      import Object2D
from ...classes2d.collections import List2D

from ...textman.label.main import Label

from ...colorsman.colors import (
                        BUTTON_BG,
                        NORMAL_PATH_FG,
                        NORMAL_PATH_BG,
                        ACTIVE_SELECTION_OUTLINE,
                      )

from ..pathobj import PathObject

from ..constants import (
                         FONT_HEIGHT,
                         PATH_OBJ_QUANTITY,
                         PATH_OBJ_PADDING,
                         PATH_OBJ_PARENT_TEXT,
                         DIR_PANEL_WIDTH,
                         DIR_PANEL_TOPLEFT,
                       )

from .newpathform import get_path

from .surfs import (
                              HOME_BUTTON_SURF,
                              RELOAD_DIR_BUTTON_SURF,
                              PARENT_BUTTON_SURF,
                              NEW_FILE_BUTTON_SURF,
                              NEW_FOLDER_BUTTON_SURF,
                            )

## class extensions

from .loadop  import LoadingOperations
from .mouseop import MouseOperations
from .extraop import ExtraOperations


class DirectoryPanel(
      LoadingOperations,
      MouseOperations,
      ExtraOperations,
    ):
    """A panel to show the current directory contents."""

    def __init__(self, file_manager):
        """Assign variables, perform setups.

        Parameters
        ==========
        file_manager (fileman.main.FileManager instance)
        """
        self.fm = file_manager

        ### assign behaviour to an attribute of the
        ### PathObject class
        PathObject.load_directory = self.change_current_dir

        ### create a current directory attribute, using
        ### the pathlib.Path to the home directory
        self.current_dir = Path.home()

        ### build objects composing this instance
        self.build_widget_structure()

        ### create a rect attribute

        self.rect = Rect(

                      ## position
                      DIR_PANEL_TOPLEFT,

                      ## size
                      (DIR_PANEL_WIDTH, self.height)

                    )

        ### store an initial value for the index of the
        ### last selected path in the directory panel
        self._last_selected_index = None

    def build_widget_structure(self):
        """Create objects which compose the panel."""
        ### create a current path label

        ## max width is the length between the left of
        ## the current path label defined on the file
        ## manager and the right of the file manager
        ## (with a bit of padding)

        max_width = (
          self.fm.rect.move(-18, 0).right
          - self.fm.current_path_label_topleft[0]
        )

        ## creation

        self.current_path_lb = \
               Label(
                 str(self.current_dir),
                 font_height=FONT_HEIGHT,
                 foreground_color=NORMAL_PATH_FG,
                 background_color=NORMAL_PATH_BG,
                 max_width=max_width,
                 ellipsis_at_end=False
               )

        ### create and store buttons

        for button_fg_surf, button_attr_name, behaviour \
        in (

          (
            HOME_BUTTON_SURF,
            'home_button',
            self.load_home
          ),
          (
            RELOAD_DIR_BUTTON_SURF,
            'reload_dir_button',
            self.load_current_dir_contents
          ),
          (
            PARENT_BUTTON_SURF,
            'parent_button',
            self.load_parent
          ),
          (
            NEW_FILE_BUTTON_SURF,
            'new_file_button',
            self.present_new_file_form
          ),
          (
            NEW_FOLDER_BUTTON_SURF,
            'new_folder_button',
            self.present_new_folder_form
          )

        ):

            ## create button

            # button with surface filled with background
            # color

            button = Object2D.from_surface(
                       render_rect(
                         *button_fg_surf.get_size(),
                         color = BUTTON_BG,
                       )
                     )

            # combine both surfs

            blit_aligned(

              surface_to_blit = button_fg_surf,
              target_surface  = button.image,

              retrieve_pos_from = 'center',
              assign_pos_to     = 'center'

            )

            # improve style
            draw_depth_finish(button.image)

            ## assign behaviour
            button.on_mouse_release = (
                     get_oblivious_callable(behaviour)
                   )

            ## store button in attribute
            setattr(self, button_attr_name, button)

        ### create a control variable to keep track of time
        ### when mouse release events happen
        self.last_release_msecs = get_milliseconds()

        ### create path objects
        self.create_path_objects()

        ### create and store surface to use as background

        self.image = render_rect(
                       *self.path_objs.rect.size,
                       NORMAL_PATH_BG
                     )

        draw_border(self.image)

        ### save height of self.path_objs plus 2
        self.height = self.path_objs.rect.height + 2

    def create_path_objects(self):
        """Instantiate and store path objects."""
        ### create special list to hold the path objects
        path_objs = List2D()

        ### define a topleft position and width for the
        ### path objects

        topleft = Vector2(DIR_PANEL_TOPLEFT) + (1, 1)
        width = DIR_PANEL_WIDTH - 2

        ### create as much path objects as the defined
        ### quantity

        for _ in range(PATH_OBJ_QUANTITY):

            ## instantiate path object

            path_obj = PathObject(
                         path=None,
                         width=width,
                         padding=PATH_OBJ_PADDING,
                         coordinates_name='topleft',
                         coordinates_value=topleft
                       )

            ## store it
            path_objs.append(path_obj)

            ## update the topleft coordinates
            topleft[1] += path_obj.rect.height

        ### reference the path objects in their own
        ### attribute
        self.path_objs = path_objs

    @property
    def last_selected_index(self):
        """Return the last selected index."""
        return self._last_selected_index

    @last_selected_index.setter
    def last_selected_index(self, value):
        """Store last selected index and update outline rect.

        Parameters
        ==========
        value (integer >= 0; None)
            represents index of last path selected. Or, if
            there's no last selected path, it is None.
        """
        ### set value of last selected index
        self._last_selected_index = value

        ### update outline rect attribute.
        self.update_outline_rect()

    def update_outline_rect(self):
        """Update outline rect attribute.

        The outline rect is the rect of a path object when
        its path was the last selected one. When there's
        no such path (for instance, in freshly loaded
        directories), it is set to None.
        """
        index = self._last_selected_index

        ### check whether the index corresponds to a path
        ### in the self.selectable_paths

        try: path = self.selectable_paths[index]

        ### if a TypeError is raised, then it is None,
        ### in which case we set the outline rect to None
        except TypeError: self.outline_rect = None

        ### otherwise we check whether any of the path
        ### object holds that path

        else:

            ## if a path obj has such path, use its rect
            ## as the outline rect and break out of the
            ## loop

            for path_obj in self.path_objs:

                if path_obj.path == path:

                    self.outline_rect = path_obj.rect
                    break

            ## otherwise set the outline rect to None
            else: self.outline_rect = None

    def update_path_objects_paths(self):
        """Update the paths of each path object.

        Each path object receives a path corresponding
        to its index in the paths deque (or None, if such
        path doesn't exists) plus the parent directory.
        """
        ### reference the parent dir of the current
        ### directory
        parent_dir = self.current_dir.parent

        ### for each path object, assign one item from
        ### the paths deque (or None, if not available)

        for index, path_obj in enumerate(self.path_objs):

            try: path = self.paths_deque[index]

            except IndexError: path = None

            path_obj.update_path(path, parent_dir)

    def update_path_objs_appearance(self):
        """Update path objects to reflect selection state."""
        for path_obj in self.path_objs:

            ### try retrieving the index of the path
            try: index = self.selectable_paths.index(
                                            path_obj.path)


            ### in case a value error occurs, it means
            ### the path isn't selectable (it is either
            ### the parent path or None); when the path
            ### is the parent path, we must make sure that
            ### it appears as deselected, since it mustn't
            ### be selected; when the path is None, though,
            ### no further action is needed, since it isn't
            ### a visible object anyway (its drawing
            ### operation is set to an empty function);

            except ValueError:

                if path_obj.text == PATH_OBJ_PARENT_TEXT:
                    path_obj.deselect()

            ### otherwise, with the index you just obtained,
            ### retrieve the selected state and use it to
            ### change the selection appearance of the path
            ### obj

            else:

                selected_state = self.selection_states[index]
                path_obj.change_selection_appearance(
                                             selected_state)

    def draw(self):
        """Draw objects."""
        ### draw path objects
        for obj in self.path_objs: obj.draw()

        ### draw outline rect, if it is not None

        try: draw_rect(
               SCREEN,
               ACTIVE_SELECTION_OUTLINE,
               self.outline_rect,
               2,
             )

        except TypeError: pass

    def change_current_dir(self, new_dir):
        """Change directory and rebuild content widgets.

        That is, if given dir exists.
        """
        ### if new_dir is falsy or it isn't even a directory
        ### or doesn't exist, cancel execution of the rest
        ### of the method by returning earlier
        if not new_dir or not new_dir.is_dir(): return

        ### otherwise, try loading the new directory,
        ### if you have the needed permission

        ## backup current dir in a local variable
        current_dir = self.current_dir

        ## set the new directory as the current one
        self.current_dir = new_dir

        ## try loading the contents of the new directory,
        ## which is now the current one
        try: self.load_current_dir_contents()

        ## if you don't have the needed permission, inform
        ## the user and set the previous directory back
        ## as the current one

        except PermissionError as err:

            ## put an error message together explaining
            ## the error

            error_msg = (
              "It seems we don't have permission to access"
              " the directory. The following error was"
              " issued: {}: {}"
            ).format(
                err.__class__.__name__,
                str(err)
              )

            ## present the dialog
            create_and_show_dialog(error_msg)

            ## set the previous directory back as the
            ## current one
            self.current_dir = current_dir

    def get_selection(self):
        """Return list of selected paths."""
        ### return list...

        return [

          ## of paths
          path

          ## from pairs of path + selection state

          for path, selection_state

          in zip(
               self.selectable_paths,
               self.selection_states
             )

          ## if said selection state is True
          if selection_state

        ]

    def get_name_of_last_selected(self):
        """Return name of last selected path."""
        ### try retrieving last selected path, if there
        ### is one
        try: last_selected_path = \
             self.selectable_paths[self.last_selected_index]

        ### if a TypeError is raised, then the index of
        ### last selected path is None, which means no path
        ### was selected yet, in which case we return an
        ### empty string
        except TypeError: return ''

        ### otherwise we return the name of the retrieved
        ### path
        else: return last_selected_path.name

    def present_new_path_form(self, is_file):
        """Present form to get a new path and pick action.

        The action picked will determine what will be
        done with the path we get.

        Parameters
        ==========
        is_file (boolean)
            whether path being create must be treated as
            file or directory.
        """
        ### present form to user by using get_path,
        ### passing the current directory and whether the
        ### new path is supposed to be a file or not;
        ### store the form data once you leave the form
        form_data = get_path(self.current_dir, is_file)

        ### if the form data is None, it means the user
        ### cancelled the action, so return now to prevent
        ### any action from happening
        if form_data is None: return

        ### otherwise we proceed according to the requested
        ### action

        ## reference the action name and the new path

        action_name = form_data['action_name']
        path        = form_data['path']

        ## act according to requested action

        if action_name == 'return_path':

            ## make it so the file manager has the path
            ## in its selection, then submit the selection

            self.fm.store_given_path(path)
            self.fm.submit_selected()

        elif action_name == 'create_path':

            ## pick path creation operation according to
            ## kind of path chosen

            creation_operation = (
              Path.touch if is_file else Path.mkdir
            )

            ## try creating path ('exist_ok' set to False
            ## causes an error to be raised if path already
            ## exists)
            try: creation_operation(path, exist_ok=False)

            ## report error message if error occurs

            except Exception as err:

                # pick name for kind of path depending on
                # is_file argument
                path_kind = "file" if is_file else "folder"

                # put an error message together explaining
                # the error

                error_msg = (
                  "The following error prevented the {}"
                  " from being created: {}: {}"
                ).format(
                    path_kind,
                    err.__class__.name,
                    str(err)
                  )

                # present the dialog
                create_and_show_dialog(error_msg)

            ## if the path is created, though, just reload
            ## the current directory, then jump to the path,
            ## leaving it selected

            else:

                self.load_current_dir_contents()
                self.jump_to_path(path)

        ## if the action name is none of the above, the
        ## logic went wrong somewhere, so we raise an
        ## error explaining it

        else:

            raise RuntimeError((
              "'action_name' must be either 'return path'"
              " or 'create path'"
            ))

    present_new_file_form = (
      partialmethod(present_new_path_form, True)
    )

    present_new_folder_form = (
      partialmethod(present_new_path_form, False)
    )
