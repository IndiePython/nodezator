"""Extra operations to support the directory panel."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### third-party imports

from pygame import KMOD_SHIFT

from pygame.key import get_mods as get_key_mods


### local import
from ..constants import PATH_OBJ_QUANTITY


class ExtraOperations:
    """Extra methods to support directory panel operations."""

    def select_in_range(self):
        """Select paths between first and last selected.

        Works by obtaining the lowest and highest indices
        among selected objects and making it so all paths
        whose indices are inside that range are selected.
        """
        ### get all indices from the values in the selection
        ### state which are True

        indices = [index for index, value in enumerate(self.selection_states) if value]

        ### if the difference between the highest and
        ### lowest indices is higher than one, it means
        ### there are indices between them;
        ### make sure all paths whose indices lie in such
        ### range are selected;

        lowest, highest = min(indices), max(indices)

        if highest - lowest > 1:

            self.selection_states[lowest : highest + 1] = [True] * (
                (highest - lowest) + 1
            )

    def scroll(self, up):
        """Scroll paths on path objects.

        up (boolean)
            indicates whether the orientation of the
            scrolling is up or not.
        """
        ### according to value of the 'up' argument

        ## scroll up

        if up:

            ## if the first path is on the first path obj,
            ## then there's no further item above, so we
            ## return earlier to avoid scrolling
            if self.path_objs[0].path == self.paths[0]:
                return

            ## otherwise we define the rotation amount
            ## to rotating the paths up one path
            else:
                rotation_amount = 1

        ## scroll down

        else:

            ## reference the path in the last path obj
            last_path = self.path_objs[-1].path

            ## if such path is last path available or None,
            ## then there's no further item below, so we
            ## return earlier to avoid scrolling
            if last_path == self.paths[-1] or last_path is None:
                return

            ## otherwise we define the rotation amount
            ## to rotating the paths down one path
            else:
                rotation_amount = -1

        ### we then perform the rotation using the defined
        ### amount
        self.paths_deque.rotate(rotation_amount)

        ### reassign the rotated paths to the path objects
        self.update_path_objects_paths()

        ### update appearance of all paths
        self.update_path_objs_appearance()

        ### update outline rect attribute
        self.update_outline_rect()

    scroll_up = partialmethod(scroll, True)
    scroll_down = partialmethod(scroll, False)

    def bulk_selection_change(self, should_select):
        """De/select all paths at once.

        Parameters
        ==========

        should_select (boolean)
            indicates whether all paths must be selected
            or deselected.
        """
        ### apply the should_select argument (a boolean)
        ### to the selection states of all paths (works
        ### even if there's no selectable paths)
        self.selection_states[:] = [should_select] * len(self.selection_states)

        ### update appearance of all paths
        self.update_path_objs_appearance()

        ### since the selection may have changed, make it
        ### so the file manager updates its path selection
        self.fm.update_entry_with_selected()

    select_all = partialmethod(bulk_selection_change, True)
    deselect_all = partialmethod(bulk_selection_change, False)

    def move_selection(self, amount):
        """Jump a number of paths up or down.

        User may optionally extend the selection with
        the items between the path from where we jump
        and the path where we land, by keeping the
        shift key pressed.

        Parameters
        ==========

        amount (integer)
            indicates amount of items to jump back (when
            negative) or forward (when positive).
        """
        ### if there's no paths to be selected, there's
        ### no point in walking any items, so return earlier
        if not self.selectable_paths:
            return

        ### store the length of the selectable paths
        n_of_selectables = len(self.selectable_paths)

        ### store value indicating whether the shift key
        ### was pressed
        shift_pressed = get_key_mods() & KMOD_SHIFT

        ### reference last selected index in local variable
        last_selected_index = self.last_selected_index

        ### if shift is not pressed deselect all paths

        if not shift_pressed:

            self.selection_states[:] = [False] * len(self.selection_states)

        ### calculate start index (from where we'll move
        ### the selection) depending on the value of the
        ### last selected index and/or the direction of the
        ### movement

        start_index = (
            ## use the index itself if not None
            last_selected_index
            if last_selected_index is not None
            ## otherwise, define an index based on the
            ## whether you're jumping forward or back
            else (
                # zero
                0
                if amount > 0
                # or the last index
                else -1 % n_of_selectables
            )
        )

        ### calculate the destination index

        destination_index = (
            ## if there were no last selected index before
            ## (it is None) and we are moving a single step
            ## (regardless of direction), make it so the
            ## destination is the start index itself, since
            ## it means we are beginning to select items,
            ## the first one being the start index itself
            start_index
            if last_selected_index is None and abs(amount) == 1
            ## otherwise, the destination index is the start
            ## index plus the amount we'll jump
            else start_index + amount
        )

        ### of course, don't forget to clamp the value to
        ### limit it to the range of selectable paths

        clamped_index = max(0, min(destination_index, n_of_selectables - 1))

        ### make sure the clamped destination index is
        ### selected and marked as the last selected one

        self.selection_states[clamped_index] = True
        self.last_selected_index = clamped_index

        ### if shift is pressed, also select the start
        ### index and then extend the selection

        if shift_pressed:

            self.selection_states[start_index] = True
            self.select_in_range()

        ### perform scrolling if needed in order for the
        ### path of the last selected index to appear on
        ### the screen, storing the return value of the
        ### operation (a boolean indicating whether the
        ### scrolling was performed or not)
        normal_scrolling_needed = self.needed_scrolling()

        ### check whether the destination index was
        ### originally lower than 0 (that is, before
        ### being clampled); if such is the case, it
        ### means that we need to scroll just one
        ### extra path up, so that the first path,
        ### the parent path, appears (the reason the
        ### 'needed_scrolling' method doesn't scroll
        ### per se is that the parent path isn't
        ### selectable, so it is never considered
        ### for selection/jump; it just appears in the
        ### folder as an easy way to get to the parent
        ### folder, so in the end we need to scroll it
        ### ourselves)
        extra_scrolling_needed = destination_index < 0

        ### if such extra scrolling is needed, perform it
        if extra_scrolling_needed:
            self.scroll_up()

        ### if any kind of scrolling was needed, update
        ### the path in each path object and also the
        ### outline rect

        if normal_scrolling_needed or extra_scrolling_needed:

            ## update path of each path object
            self.update_path_objects_paths()

            ## update outline rect attribute
            self.update_outline_rect()

        ### update appearance of all paths
        self.update_path_objs_appearance()

        ### since the selection may have changed, make it
        ### so the file manager updates its path selection
        self.fm.update_entry_with_selected()

    go_to_previous = partialmethod(move_selection, -1)
    go_to_next = partialmethod(move_selection, 1)

    jump_many_up = partialmethod(move_selection, -PATH_OBJ_QUANTITY)
    jump_many_down = partialmethod(move_selection, PATH_OBJ_QUANTITY)

    go_to_first = partialmethod(move_selection, -INFINITY)
    go_to_last = partialmethod(move_selection, INFINITY)

    def needed_scrolling(self):
        """Return whether scrolling was performed or not.

        Works by checking whether the last selected path
        is appearing on the directory panel or not. If not
        than we scroll it so it appears. In the end, we
        always return whether such scrolling was needed
        (and thus performed) or not, in the form of a
        boolean.
        """
        ### reference useful data/operation

        last_selected_index = self.last_selected_index
        get_selectable_index = self.selectable_paths.index

        ### retrieve indices of paths being displayed

        displayed_indices = [
            get_selectable_index(path_obj.path)
            for path_obj in self.path_objs
            if path_obj.path in self.selectable_paths
        ]

        ### if last selected path is showing (its index is
        ### among the indices of the paths being displayed
        ### in the directory panel), then there's no need
        ### for scrolling, so you can leave the method and
        ### signal you didn't need to scroll by returning
        ### False

        if self.last_selected_index in displayed_indices:
            return False

        ### otherwise, we perform the amount of scrolling
        ### needed to make the last selected path appear
        ### in the directory panel

        ## retrieve index of paths appearing on top and
        ## bottom of the directory panel

        top_index = min(displayed_indices)
        bottom_index = max(displayed_indices)

        ## define amount of scrolling based on position
        ## of last selected index relative to the top index

        scrolling_amount = (
            # we use the difference between the top index
            # and the last selected index if the last
            # selected one comes before the top index
            top_index - last_selected_index
            if last_selected_index < top_index
            # otherwise it means the last selected index
            # appears after the bottom index, so we use
            # the difference between them
            else bottom_index - last_selected_index
        )

        self.paths_deque.rotate(scrolling_amount)

        ### finally, we return True to indicate we
        ### scrolled the paths
        return True

    def jump_to_path(self, path):
        """Select path and ensure it appears on panel."""
        ### deselect all paths

        self.selection_states[:] = [False] * len(self.selection_states)

        ### perform tasks to make the path selected

        index = self.selectable_paths.index(path)
        self.selection_states[index] = True

        self.last_selected_index = index

        ### perform scrolling if needed in order for the
        ### path of the last selected index to appear on
        ### the screen (the path we just made selected),
        ### storing the return value of the operation
        ### (a boolean indicating whether the scrolling
        ### was performed or not)
        needed_scrolling = self.needed_scrolling()

        ### if we needed to scroll, update the path in each
        ### path object
        if needed_scrolling:
            self.update_path_objects_paths()

        ### update outline rect attribute
        self.update_outline_rect()

        ### update appearance of all paths
        self.update_path_objs_appearance()

        ### since the selection may have changed, make it
        ### so the file manager updates its path selection
        self.fm.update_entry_with_selected()
