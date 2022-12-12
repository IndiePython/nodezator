"""Directory loading operations for the directory panel."""

### standard library imports

from pathlib import Path
from collections import deque


### utility function


def alphabetical_sorting_with_folders_first(path):
    """Return tuples used to sort paths.

    Paths are sorted in case-insensitive alphabetical
    order, with folders appearing first.
    """
    return path.is_file(), str(path).lower()


### class definition


class LoadingOperations:
    """Methods related to directory loading."""

    def load_current_dir_contents(self):
        """Load contents from current directory.

        A lot of setups are executed as well to guarantee
        the paths are ready to be browsed and de/selected.
        """
        ### if current dir doesn't exist anymore or isn't
        ### a directory, use the home directory instead
        if not self.current_dir.is_dir():
            self.current_dir = Path.home()

        ### gather directories and files from current dir
        ### sorting them alphabetically, folder first

        paths = sorted(
            (
                item
                for item in self.current_dir.iterdir()
                if not item.name.startswith(".")
            ),
            key=alphabetical_sorting_with_folders_first,
        )

        ## also insert the parent directory, at the beginning
        ## of the list, so the parent folder can be easily
        ## accessed by the user whenever desired
        paths.insert(0, self.current_dir.parent)

        ### reference paths in their own attribute
        self.paths = paths

        ### create a deque from the paths
        self.paths_deque = deque(paths)

        ### assign paths to the path objects
        self.update_path_objects_paths()

        ### create a new list containing only the
        ### selectable paths, that is, all paths, except
        ### the first one, since it is the parent directory
        ### and cannot be selected (it is just used as an
        ### easy way to access the parent folder)
        self.selectable_paths = paths[1:]

        ### create a new list in wherein to store the
        ### selection states (boolean values) of each
        ### selectable path

        self.selection_states = [False for _ in self.selectable_paths]

        ### since setting all selection states to False,
        ### as we just did above, make it so they are
        ### all deselected...

        ## make it so the file manager updates its path
        ## selection;
        self.fm.store_current_selection()

        ## update appearance on the path objects (so they
        ## appear deselected)
        self.update_path_objs_appearance()

        ## also update appearance of bookmark objs, in case
        ## the current dir is a bookmarked path as well
        ## (when we load the contents of a folder, if it is
        ## bookmarked, its bookmark item appears as though
        ## selected/highlighted)
        self.fm.bkm_panel.update_bookmark_objs_appearance()

        ### update text on the current path entry (if not already)

        string_dirpath = str(self.current_dir)

        if self.navigation_entry.get() != string_dirpath:
            self.navigation_entry.set(string_dirpath, False)

        ### set a value for the last selected index property,
        ### to keep track of the last selected index and
        ### update the outline rect attribute whenever such
        ### index changes
        self.last_selected_index = None

    def load_from_entry(self):
        """Load path typed on the navigation_entry."""
        self.change_current_dir(Path(self.navigation_entry.get()))

    def load_selected(self):
        """Load single selected path.

        Note that the call to the change_current_dir method
        only has effect if the path is a directory and
        exists.
        """
        ### don't proceed if number of selected paths isn't
        ### one
        if sum(self.selection_states) != 1:
            return

        ### otherwise retrieve the selected path and load it

        index = self.selection_states.index(True)
        selected_path = self.selectable_paths[index]

        self.change_current_dir(selected_path)

    def load_parent(self):
        """Load the parent folder of current directory.

        This also makes the child appear selected, if it
        is not the same as its parent (happens when we
        try accessing the parent of the root directory).
        """
        ### reference current directory locally as a
        ### child directory and also its parent

        child_dir = self.current_dir
        parent_dir = child_dir.parent

        ### load the parent
        self.change_current_dir(parent_dir)

        ### make it so the child directory is selected
        ### and appears on the directory display if it
        ### is not the same as its parent

        if child_dir != parent_dir:
            self.jump_to_path(child_dir)

    def load_home(self):
        """Load the home folder.

        I also could have used a functools.partialmethod
        version of self.change_current_dir() with the
        result of pathlib.Path.home(), insted of calling
        it here every time the method is executed, but I'm
        not 100% sure whether there is an use-case where
        the home folder ever changes.

        I strongly believe such use-case doesn't exist
        or is so rare as to be not worth considering, but
        I refuse the temptation to guess. And besides,
        the current implementation is both simple and
        quick enough as to be harmless, anyway.
        """
        self.change_current_dir(Path.home())
