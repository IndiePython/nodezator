"""File Manager class extension with operations."""

### standard-library import
from functools import partialmethod


### third-party imports

from pygame import (
              QUIT, KEYDOWN, KEYUP,
              K_UP, K_DOWN,
              K_RETURN, K_KP_ENTER,
              K_a, KMOD_ALT, KMOD_CTRL, KMOD_SHIFT,
              K_HOME, K_END, K_PAGEUP, K_PAGEDOWN,
              MOUSEBUTTONDOWN, MOUSEBUTTONUP,
            )

from pygame.event   import get as get_events
from pygame.display import update


### local imports

from translation import TRANSLATION_HOLDER as t

from pygameconstants import (
                       SCREEN_RECT,
                       FPS,
                       maintain_fps,
                       blit_on_screen,
                     )

from dialog import create_and_show_dialog

from ourstdlibs.behaviour import (
                            empty_function,
                            get_oblivious_callable,
                          )

from loopman.exception import (
                                SwitchLoopException,
                                QuitAppException)

from surfsman.cache import UNHIGHLIGHT_SURF_MAP

from classes2d.single import Object2D


class FileManagerOperations(Object2D):
    """Operations for file manager class."""

    def browse_paths(
          self,
          *,
          mode      = 'select',
          caption   = "",
          path_name = t.file_manager.pathname,
        ):
        """Return selected paths or a new path.

        This method shows the user the file manager
        interface, allowing the user to browse the
        filesystem visually while either:
        
        1) in the 'select' mode: selecting paths to be
           returned;

        2) in the 'create' mode: providing the name for a
           new path which is them used to create a new
           pathlib.Path object as if it exists in the
           current directory the user is navigating; only
           the pathlib.Path object is created, not the
           actual file/folder to which it refers;

        Parameters
        ==========

        mode (string)
            either 'select' or 'create'. Changes the
            behaviour of the file manager to support
            the specified action (either select or create
            path(s))
        caption (string)
            represents a caption for the widget.
        path_name (string)
            only relevant on 'create' mode. It is used
            as the default name of the path being
            created.
        """
        ### blit screen sized semi transparent object

        blit_on_screen(
          UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size],
          (0, 0)
        )

        ### update widget caption label

        if not caption:

            caption = (
              t.file_manager.select_path
              if mode == 'select'
              else t.file_manager.create_new_path
            )

        self.caption_label.set(caption)

        ### perform setups according to given mode
        self.set_mode(mode, path_name)

        ### load paths from the current directory so they
        ### are displayed in the directory panel
        self.dir_panel.load_current_dir_contents()

        ### check whether the current bookmarks still exists
        self.bkm_panel.check_live_bookmarks()

        ### alias self as the loop holder
        loop_holder = self

        ### keep looping the execution the methods
        ### "handle_input", "update" and "drawing" of the
        ### loop holder until running is set to False

        self.running = True

        while self.running:

            ### keep a constant framerate
            maintain_fps(FPS)

            ### run the GUD methods (check the glossary
            ### for loop holder/loop/methods)

            try:

                loop_holder.handle_input()
                loop_holder.update()
                loop_holder.draw()

            ### if a SwitchLoopException occur, set a new
            ### object to become the loop holder

            except SwitchLoopException as err:

                ## use the loop holder in the err
                ## attribute of same name
                loop_holder = err.loop_holder

        ### blit smaller semi transparent object
        self.rect_size_semitransp_obj.draw()

        ### return a copy of the path selection
        return tuple(self.path_selection)

    select_path = partialmethod(browse_paths, mode="select")
    create_path = partialmethod(browse_paths, mode="create")

    def set_mode(self, mode, path_name):
        """Perform setups related to given mode."""
        ### set entry contents if in 'create' mode
        if mode == 'create': self.entry.set(path_name)

        ### if mode didn't change, return earlier
        if mode == self.current_mode: return

        ### otherwise, keep performing changes to accomodate
        ### the new mode...

        ## store the new mode as the current one
        self.current_mode = mode

        ## set widget label text

        widget_label_text = (

          t.file_manager.selected
          if mode == 'select'
          else t.file_manager.new_path

        ) + ":"
        
        self.widget_label.set(widget_label_text)

        ### perform setups to guarantee the appropriate
        ### widget sits beside the widget label according
        ### to the choosen mode

        if mode == 'select':
            
            chosen_widget = self.selection_label

            self.labels.add(self.selection_label)
            self.buttons.discard(self.entry)

        else:

            chosen_widget = self.entry

            self.buttons.add(self.entry)
            self.labels.discard(self.selection_label)

        ## reposition the chosen widget beside the widget
        ## label
        chosen_widget.rect.midleft = \
              self.widget_label.rect.move(5, 0).midright

        ## set 'update_path_selection_on_load' behaviour;
        ##
        ## must be set before reloading the paths in the
        ## directory panel, since this behaviour is called
        ## during such operation;
        ##
        ## we use an empty function in 'create' mode
        ## to prevent changes in the entry widget that
        ## are not directly caused by the user; that is,
        ## we only want the entry to be changed either
        ## when the user types text in it or selects
        ## items in the directory panel, not when loading
        ## a directory

        self.update_path_selection_on_load = (

          self.store_current_selection
          if mode == 'select'

          else empty_function

        )

        ## set 'update_path_selection' behaviour

        self.update_path_selection = (

          self.store_current_selection
          if mode == 'select'

          else self.copy_last_selected_to_entry

        )

        ## set 'on_mouse_release' behaviour for the submit
        ## button

        self.submit_button.on_mouse_release = (

          get_oblivious_callable(

            self.submit_selected
            if mode == 'select'

            else self.submit_from_entry

          )

        )

    def handle_input(self):
        """Handle event queue."""
        for event in get_events():

            if event.type == QUIT: raise QuitAppException

            ### KEYDOWN

            elif event.type == KEYDOWN:

                if event.key == K_UP:

                    ## if alt key is pressed as well, load
                    ## the parent folder

                    if event.mod & KMOD_ALT:
                        self.load_parent()

                    ## otherwise just go to the previous
                    ## item
                    else: self.go_to_previous()

                elif event.key == K_DOWN:
                    self.go_to_next()

            ### KEYUP

            elif event.type == KEYUP:

                if event.key in (K_RETURN, K_KP_ENTER):
                    self.load_selected()

                ## de/select all

                elif event.key == K_a \
                and event.mod & KMOD_CTRL:

                    if event.mod & KMOD_SHIFT:
                         self.deselect_all()

                    else: self.select_all()

                ## jump to first/last item

                elif event.key == K_HOME:

                    # if alt key is pressed as well, load
                    # the parent folder

                    if event.mod & KMOD_ALT:
                        self.load_home()

                    ## otherwise just go to the previous
                    ## item
                    else: self.go_to_first()

                elif event.key == K_END: self.go_to_last()

                ## jump the number of items showing

                elif event.key == K_PAGEUP:
                    self.jump_many_up()

                elif event.key == K_PAGEDOWN:
                    self.jump_many_down()

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.on_mouse_click(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.on_mouse_release(event)

                elif event.button == 4:
                    self.scroll_contents(event.pos, "up")

                elif event.button == 5:
                    self.scroll_contents(event.pos, "down")

    def on_mouse_action(self, method_name, event):
        """Check whether mouse action occurred inside widget.

        Parameters
        ==========
        method_name (string)
            either 'on_mouse_click' or 'on_mouse_release',
            actions which we track in this method.
        event (custom instance)
            pygame.event.Event of type
            pygame.MOUSEBUTTONDOWN or MOUSEBUTTONUP;
            check pygame.event module documentation on
            pygame website for more info about these event
            objects.

        If inside the file manager boundaries, determine
        if it was inside one of the panels or buttons,
        triggering the appropriate action. If outside,
        get out of the file manager loop using the
        'cancel' method.
        """
        mouse_pos = event.pos

        ### if mouse was released inside file manager

        if self.rect.collidepoint(mouse_pos):

            ## see if one of the panels collides

            for panel in self.panels:

                if panel.rect.collidepoint(mouse_pos):

                    try: method = getattr(panel, method_name)

                    except AttributeError: pass

                    else:

                        method(event)
                        return

            ## see if buttons were pressed (mouse released)

            for button in self.buttons:

                if button.rect.collidepoint(mouse_pos):

                    try: method = getattr(button, method_name)
                    except AttributeError: pass

                    else:

                        method(event)
                        return

        ### otherwise trigger the exit of the file manager
        ### loop by cancelling
        else: self.cancel()

    on_mouse_click = \
        partialmethod(on_mouse_action, 'on_mouse_click')

    on_mouse_release = \
        partialmethod(on_mouse_action, 'on_mouse_release')

    def scroll_contents(self, mouse_pos, orientation):
        """Verify if scrolling contents and scroll if so.

        Parameters
        ==========
        mouse_pos (2-tuple of integers)
            represents the point on screen where the object
            was 'scrolled'.
        orientation (string)
            represents a hint indicating the direction of
            the scrolling. If it equals 'up' we perform
            scrolling up, otherwise, whatever the value,
            we perform the scrolling down.
        """
        ### if inside directory panel, scroll it

        if self.dir_panel.rect.collidepoint(mouse_pos):

            if orientation == "up":
                self.dir_panel.scroll_up()

            else: self.dir_panel.scroll_down()

        ### if inside bookmark panel, scroll it

        elif self.bkm_panel.rect.collidepoint(mouse_pos):

            if orientation == "up":
                self.bkm_panel.scroll_up()

            else: self.bkm_panel.scroll_down()

    def draw(self):
        """Draw different objects/groups and update screen."""
        super().draw()

        self.labels.draw()

        self.panels.call_draw()

        self.buttons.draw()

        update() # pygame.display.update

    def store_current_selection(self):
        """Retrieve path info and store it."""
        ### store a list of selected paths in the
        ### path_selection attribute
        self.path_selection = self.dir_panel.get_selection()

        ### admin task:
        ### set the selection label text according to the
        ### path selection, to indicate to user which paths
        ### are selected (or whether there is a selection at
        ### all);
        ###
        ### this is an aesthetic measure to indicate
        ### that there are paths selected, since not all
        ### can be seen in the entry when there are too
        ### many - besides, the user can clearly see which
        ### paths are selected in the directory panel;

        text = self.get_selection_text()
        self.selection_label.set(text)

    def get_selection_text(self):
        """Return custom text according to selected paths."""
        ### reference the path selection in a local variable
        path_selection = self.path_selection

        ### if its has more than one items, the text
        ### is all the names of the paths joined by ', '

        if len(path_selection) > 1:

            text = ', '.join(
                          path.name
                          for path in path_selection
                        )

        ### otherwise...

        else:

            ### try assigning the name of the first path
            ### as the text
            try: text = path_selection[0].name

            ### if it fails, though, then use an empty
            ### string as the text
            except IndexError:
                text = t.file_manager.no_path_selected

        return text

    def store_path_from_entry(self):
        """Build path from entry, store as selected path."""
        ### clear the path selection;
        ###
        ### the name of the last selected path is
        ### automatically set in the entry, so even
        ### though we are clearing the path selection
        ### that path will still be passed to the
        ### path selection inside the 'if block' down
        ### below
        self.path_selection.clear()

        ### get name from entry
        path_name = self.entry.get()

        ### if there is a path name, build a path by joining
        ### the current directory with the path name from
        ### the entry and append such path to the
        ### path_selection list

        if path_name:

            ## build path using the current directory and
            ## the path name from the entry
            path = self.dir_panel.current_dir / path_name

            ### reset the path selection to a new list
            ### containing the path
            self.path_selection.append(path)

    def copy_last_selected_to_entry(self):
        """If a file was selected, copy its name to entry."""
        ### retrieve name of last selected path
        name = self.dir_panel.get_name_of_last_selected()

        ### if such name exists, set it on the entry;
        ###
        ### note that, by default, the 'set' method of the
        ### entry also executes its command automatically,
        ### which in this case is the
        ### self.store_path_from_entry method, which
        ### stores the path formed by the current loaded
        ### folder joined by the entry contents which we
        ### set below
        if name: self.entry.set(name)

    def store_given_path(self, path):
        """Store given path as selected one."""
        ### reset the path selection to a new list
        ### containing the given path
        self.path_selection = [path]

    def submit_selected(self):
        """If a path is stored, exit local loop."""
        if self.path_selection: self.running = False

        else: create_and_show_dialog(
                "No path(s) were selected."
              )

    def submit_from_entry(self):
        """If a entry has a path name, exit local loop."""
        ### store path from entry
        self.store_path_from_entry()

        ### if there's a selection, it means the entry
        ### isn't empty, so we can exit the local loop
        if self.path_selection: self.running = False

        ### otherwise, we display a proper message
        ### explaining that we can't exit the loop yet
        ### because no path was typed in the entry or
        ### selected
        else: create_and_show_dialog(
                "You must either type a name for a new"
                " file/folder in the entry or select an"
                " existing file/folder"
              )

    def cancel(self):
        """Cancel selecting/creating path.

        Works by setting the path selection to an empty
        list, which make it so no path is returned.
        The 'running' attribute is also set to False, which
        triggers the exit of the file manager loop which
        you can find of the browse_paths method.
        """
        self.path_selection = []
        self.running = False
