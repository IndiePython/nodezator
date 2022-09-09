"""Facility for bookmark display and management."""

### standard library imports

from pathlib import Path
from functools import partialmethod
from collections import deque


### third-party imports

from pygame import Rect

from pygame.math import Vector2
from pygame.time import get_ticks as get_milliseconds


### local imports

from ...userprefsman.main import BOOKMARKS_FILE

from ...dialog import create_and_show_dialog

from ...ourstdlibs.pyl import load_pyl, save_pyl

from ...ourstdlibs.behaviour import get_oblivious_callable

from ...surfsman.draw import (
    blit_aligned,
    draw_border,
    draw_depth_finish,
)

from ...surfsman.render import render_rect

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...colorsman.colors import BUTTON_BG

from ..pathobj import PathObject

from ..constants import (
    PATH_OBJ_QUANTITY,
    PATH_OBJ_PADDING,
    BKM_PANEL_WIDTH,
    MAX_MSECS_TO_2ND_MOUSE_EVENT,
)

from .surfs import (
    BOOKMARK_BUTTON_SURF,
    UNBOOKMARK_BUTTON_SURF,
)


class BookmarkPanel:
    """A panel for displaying and managing bookmarks."""

    def __init__(self, directory_panel, semitransp_obj):
        """Store argument and perform setups.

        Parameters
        ==========
        directory_panel (fileman.dirpanel.DirectoryPanel
        instance)
            object which displays contents from current
            loaded directory and controls it.
        semitransp_obj (custom object)
            object with a draw method which draws a
            semitransparent surface over the file manager,
            making it appear unhighlighted. Used when
            summoning dialog boxes, to unhighlight the
            file manager.
        """
        ### store arguments received

        self.dir_panel = directory_panel
        self.semitransp_obj = semitransp_obj

        ### create a rect attribute

        self.rect = Rect(
            ## position
            (0, 0),
            ## size
            (BKM_PANEL_WIDTH, 0),
        )

        ### Build widget structure
        self.build_widget_structure()

    def build_widget_structure(self):
        """Build widget structure."""
        ### create objects representing bookmarks
        self.create_bookmark_objects()

        ### update widgets to represent existing bookmarks
        self.update_bookmarks()

        ### create and store buttons

        for button_attr_name, button_fg_surf, behaviour in (
            ("bookmark_button", BOOKMARK_BUTTON_SURF, self.add_bookmark),
            ("unbookmark_button", UNBOOKMARK_BUTTON_SURF, self.remove_bookmark),
        ):

            ## create button

            # button with surface filled with background
            # color

            button = Object2D.from_surface(
                render_rect(
                    *button_fg_surf.get_size(),
                    color=BUTTON_BG,
                )
            )

            # combine both surfs

            blit_aligned(
                surface_to_blit=button_fg_surf,
                target_surface=button.image,
                retrieve_pos_from="center",
                assign_pos_to="center",
            )

            # improve style
            draw_depth_finish(button.image)

            ## assign behaviour
            button.on_mouse_release = get_oblivious_callable(behaviour)

            ## store button in attribute
            setattr(self, button_attr_name, button)

        ### create a control variable to keep track of time
        ### when mouse release events happen
        self.last_release_msecs = get_milliseconds()

    def create_bookmark_objects(self):
        """Instantiate and store objects for bookmarks."""
        width = BKM_PANEL_WIDTH - 2

        ### create a special list to hold the objects

        self.bookmark_objs = List2D(
            PathObject(
                path=None,
                width=width,
                padding=PATH_OBJ_PADDING,
            )
            for _ in range(PATH_OBJ_QUANTITY)
        )

        ### position objs relative to each other

        self.bookmark_objs.rect.snap_rects_ip(
            retrieve_pos_from="bottomleft",
            assign_pos_to="topleft",
        )

        ### assign height of self.path_objs plus 2
        ### as the panel's height

        self.rect.height = self.bookmark_objs.rect.height + 2

    def update_bookmarks(self):
        """(Re)load bookmarks from file.

        The bookmarks are them assigned to the path objects
        representing bookmark items in the panel.
        """
        ### retrieve and store bookmarks
        try:
            bookmarks = load_pyl(BOOKMARKS_FILE)

        ### if file doesn't exist, create empty list of
        ### existing bookmarks and create the file by
        ### saving such list as a json file

        except FileNotFoundError:

            existing_bookmarks = []
            save_pyl(existing_bookmarks, BOOKMARKS_FILE)

        ### otherwise check which of the bookmark folders
        ### do exist and use them to build/update objects
        ### used to support operations

        else:

            ### only keep existing bookmarks

            existing_bookmarks = [
                path_string for path_string in bookmarks if Path(path_string).is_dir()
            ]

            ### if existing bookmarks are different than the
            ### listed ones, override the file so it contains
            ### only the existing bookmarks

            if existing_bookmarks != bookmarks:
                save_pyl(existing_bookmarks, BOOKMARKS_FILE)

            ### turn existing bookmarks into pathlib.Path
            ### objects

            existing_bookmarks = [Path(item) for item in existing_bookmarks]

        ### make a deque out of the existing bookmarks
        self.bookmark_paths_deque = deque(existing_bookmarks)

        ### also reference the existing bookmarks list in
        ### an instance attribute
        self.existing_bookmarks = existing_bookmarks

        ### and finally assign the paths to the bookmark
        ### path objects and update their appearance

        self.update_bookmark_objs_paths()
        self.update_bookmark_objs_appearance()

    def update_bookmark_objs_paths(self):
        """Update the path of each bookmark object.

        Each bookmark object receives a path corresponding
        to its index in the bookmarks deque (or None, if such
        path doesn't exists).
        """
        ### update the path of each path obj representing
        ### a bookmark

        for index, path_obj in enumerate(self.bookmark_objs):

            try:
                path = self.bookmark_paths_deque[index]

            except IndexError:
                path = None

            path_obj.update_path(path)

    def update_bookmark_objs_appearance(self):
        """Change appearance of bookmark objects.

        Works by making the bookmark object holding the
        path currently loaded in the directory panel
        appear different from the others (it appears as
        if selected, while the others don't).
        """
        ### retrieve directory currently loaded in the
        ### directory panel
        current_dir = self.dir_panel.current_dir

        ### change appearance of each bookmark object
        ### according to whether they hold the path
        ### currently loaded in the directory panel

        for path_obj in self.bookmark_objs:

            path_obj.change_selection_appearance(path_obj.path == current_dir)

    def check_live_bookmarks(self):
        """Check if the bookmarks still exist.

        If not, the missing ones are removed.
        """
        ### if it is found that any path among the
        ### bookmarks doesn't exist, load the bookmark
        ### objects again with the existing ones only

        if any(path.is_dir() for path in self.existing_bookmarks):

            ## this not only updates the bookmark objects,
            ## but also has the side-effect of updating the
            ## json file too
            self.update_bookmarks()

    def draw(self):
        """Draw widgets."""
        ### draw bookmark objects
        for obj in self.bookmark_objs:
            obj.draw()

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

        ### check whether any bookmark obj was the target of
        ### the mouse release action

        for bookmark_obj in self.bookmark_objs:

            if bookmark_obj.rect.collidepoint(mouse_pos):

                ## get the current millisecond count since
                ## app was started (since pygame was
                ## initialized)
                current_release_msecs = get_milliseconds()

                ## use it to obtain the interval in
                ## milliseconds since the last mouse release

                msecs_since_last = current_release_msecs - self.last_release_msecs

                ## if such time is less than or equal
                ## the maximum time defined for a second
                ## mouse event we consider it as if it
                ## were a double click on the path object,
                ## in which case we load its path; since
                ## this relies on the change_current_dir
                ## method, this operation only makes a
                ## difference if the path is an existing
                ## directory

                if msecs_since_last <= MAX_MSECS_TO_2ND_MOUSE_EVENT:
                    bookmark_obj.load()

                ## finally, we store the measured
                ## milliseconds as the more recent time
                ## measurement of a mouse release event

                self.last_release_msecs = current_release_msecs

                ## finally since you found the colliding
                ## path obj, you know the others didn't
                ## collide, so you can safely break out
                ## of the loop
                break

    def scroll(self, up):
        """Scroll paths along the bookmark objects.

        up (boolean)
            indicates whether the orientation of the
            scrolling is up (True) or not.
        """
        ### if there's no bookmarks, then there's also no
        ### point in scrolling through bookmark paths, so
        ### exit the method earlier by returning
        if not self.existing_bookmarks:
            return

        ### otherwise, check the need to scroll depending
        ### on the direction of the scrolling and associated
        ### pre-condition

        if up:

            ## if the first bookmark path is present in the
            ## first bookmark object, there's no point in
            ## scrolling up, so we just return

            if self.bookmark_objs[0].path == self.existing_bookmarks[0]:
                return

            ## otherwise we define a amount to rotate the
            ## deque according to direction of the scrolling
            rotation_amount = 1

        else:

            ## if the path in the last bookmark object is
            ## also the last bookmark path or None, there's
            ## no point in scrolling down, so we just return

            last_path = self.bookmark_objs[-1].path

            if last_path == self.existing_bookmarks[-1] or last_path is None:
                return

            ## otherwise we define an amount to rotate the
            ## deque according to direction of the scrolling
            rotation_amount = -1

        ### rotate the bookmark paths deque by the defined
        ### amount
        self.bookmark_paths_deque.rotate(rotation_amount)

        ### and finally assign the paths to the bookmark
        ### path objects and update their appearance

        self.update_bookmark_objs_paths()
        self.update_bookmark_objs_appearance()

    scroll_up = partialmethod(scroll, True)
    scroll_down = partialmethod(scroll, False)

    def change_bookmarks(self, should_add):
        """Add/remove current directory from bookmarks."""
        ### retrieve the directory currently loaded in the
        ### directory panel
        current_dir = self.dir_panel.current_dir

        ### retrieve the bookmarks saved on file
        bookmarks = load_pyl(BOOKMARKS_FILE)

        ### if we mean to add the current directory as
        ### a bookmark...

        if should_add:

            ## if the directory is not present in the
            ## bookmarks, add it and sort the bookmarks
            ## by the name of the directory

            if str(current_dir) not in bookmarks:

                bookmarks.append(str(current_dir))
                bookmarks.sort(key=lambda path: Path(path).name)

            ## otherwise there's no need to add what is
            ## already there, so we just notify the user
            ## and leave this method by returning

            else:

                create_and_show_dialog(
                    "Current directory is already bookmarked.",
                    unhighlighter_obj=self.semitransp_obj,
                )

                return

        ### otherwise, if we mean to remove the current
        ### directory from the bookmarks...

        else:

            ## if the directory is present in the
            ## bookmarks, remove it

            if str(current_dir) in bookmarks:
                bookmarks.remove(str(current_dir))

            ## otherwise there's no need to remove what
            ## isn't even there, so we just notify the user
            ## and leave this method by returning

            else:

                create_and_show_dialog(
                    (
                        "Current directory isn't bookmarked, so"
                        " there's no point in removing it from"
                        " bookmarks."
                    ),
                    unhighlighter_obj=self.semitransp_obj,
                )

                return

        ### now that the bookmars were changed, override
        ### the bookmarks file, then update the bookmarks
        ### show on this bookmark panel

        save_pyl(bookmarks, BOOKMARKS_FILE)
        self.update_bookmarks()

    add_bookmark = partialmethod(change_bookmarks, True)
    remove_bookmark = partialmethod(change_bookmarks, False)

    def reposition(self):
        """Reposition panel relative to file manager."""
        self.rect.topright = self.dir_panel.rect.move(-15, 0).topleft

        self.bookmark_objs.rect.topleft = self.rect.move(1, 1).topleft

        for path_obj in self.bookmark_objs:
            path_obj.reposition_icon_and_text()
