"""Mouse-related operations to support the directory panel."""

### third-party imports

from pygame import KMOD_CTRL, KMOD_SHIFT

from pygame.key import get_mods as get_mods_bitmask
from pygame.time import get_ticks as get_milliseconds


### local import
from ..constants import MAX_MSECS_TO_2ND_MOUSE_EVENT


class MouseOperations:
    """Methods for mouse actions in the directory panel."""

    def on_mouse_release(self, event):
        """Act according to mouse release event.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONUP
        type)
              Check pygame.event module documentation on
              pygame website for more info about this event
              object.
        """
        ### retrieve mouse position
        mouse_pos = event.pos

        ### retrieve pressed state of ctrl and shift keys

        mods_bitmask = get_mods_bitmask()
        ctrl = mods_bitmask & KMOD_CTRL
        shift = mods_bitmask & KMOD_SHIFT

        ### check whether any path obj was the target of
        ### the mouse release action

        for path_obj in self.path_objs:

            if path_obj.rect.collidepoint(mouse_pos):

                ## get the current millisecond count since
                ## app was started (since pygame was
                ## initialized)
                current_release_msecs = get_milliseconds()

                ## use it to obtain the interval in
                ## milliseconds since the last mouse release

                msecs_since_last = current_release_msecs - self.last_release_msecs

                ## if such time is less than or equal the
                ## maximum time defined for a second mouse
                ## event we consider it as if it were a
                ## double click on the path object, in
                ## which case we load its path; since this
                ## relies on the change_current_dir method,
                ## this operation only makes a difference
                ## if the path is an existing directory

                if msecs_since_last <= MAX_MSECS_TO_2ND_MOUSE_EVENT:
                    path_obj.load()

                ## otherwise, we consider as if the path
                ## object was clicked

                else:

                    # execute the appropriate operation
                    # for the existing scenarios depending
                    # on the pressed states of the ctrl and
                    # shift keys

                    if not ctrl and not shift:
                        self.select_single_path(path_obj)

                    elif ctrl and not shift:
                        self.revert_selection_state(path_obj)
                    elif shift and not ctrl:
                        self.extend_selection(path_obj)

                ## regardless of the block executed above,
                ## we store the measured milliseconds as
                ## the more recent time measurement of a
                ## mouse release event
                self.last_release_msecs = current_release_msecs

                ## finally since you found the colliding
                ## path obj, you know the others didn't
                ## collide, so you can safely break out
                ## of the loop
                break

    def select_single_path(self, path_obj):
        """Perform setups to make single obj selected.

        Works by deselecting all paths and selecting the
        given one, besides executing other admin tasks.

        Parameters
        ==========
        path_obj (fileman.pathobj.PathObject instance)
            path object targeted by the mouse.
        """
        ### deselect all paths
        self.selection_states[:] = [False] * len(self.selection_states)

        ### reference the path
        path = path_obj.path

        ### if the path is selectable, perform tasks to
        ### make it so it is selected

        if path in self.selectable_paths:

            index = self.selectable_paths.index(path)
            self.selection_states[index] = True

            self.last_selected_index = index

        ### otherwise, just assign None to the
        ### last selected index
        else:
            self.last_selected_index = None

        ### update appearance of all paths
        self.update_path_objs_appearance()

        ### since the selection may have changed, make it
        ### so the file manager updates its path selection
        self.fm.update_entry_with_selected()

    def revert_selection_state(self, path_obj):
        """Revert the selection of the path object.

        That is, if the path is selected, it becomes
        deselected, and vice-versa.

        Parameters
        ==========
        path_obj (fileman.pathobj.PathObject instance)
            path object targeted by the mouse.
        """
        ### reference path
        path = path_obj.path

        ### if it isn't selectable, exit method by returning
        if path not in self.selectable_paths:
            return

        ### otherwise, perform task to make it so the
        ### selection state of the path obj is reversed

        ## retrieve index of path and use it to update
        ## its selection state while referencing the value
        ## of the new selection state

        index = self.selectable_paths.index(path)

        new_selection_state = self.selection_states[index] = not self.selection_states[
            index
        ]

        ## mark the index as the last selected one
        self.last_selected_index = index

        ## change appearance of path object to reflect the
        ## new selection state
        path_obj.change_selection_appearance(new_selection_state)

        ### since the selection changed, make it so the file
        ### manager updates its path selection
        self.fm.update_entry_with_selected()

    def extend_selection(self, path_obj):
        """Trigger selection extension if needed.

        Parameters
        ==========
        path_obj (fileman.pathobj.PathObject instance)
            path object targeted by the mouse.
        """
        ### reference path
        path = path_obj.path

        ### if it isn't selectable, exit method by returning
        if path not in self.selectable_paths:
            return

        ### if there's no selected path, select the given
        ### one only

        if not any(self.selection_states):
            self.select_single_path(path_obj)

        ### otherwise, select the given one and extend the
        ### selection among all the selected paths

        else:

            ## make it so the path of the given path obj
            ## is marked as selected

            index = self.selectable_paths.index(path)
            self.selection_states[index] = True

            ## also mark the path index as the last
            ## selected one
            self.last_selected_index = index

            ## finally perform the extension of the
            ## selection if needed
            self.select_in_range()

            ### update appearance of all paths
            self.update_path_objs_appearance()

            ### since the selection may have changed, make
            ### it so the file manager updates its path
            ### selection
            self.fm.update_entry_with_selected()
