"""Facility for object repositioning."""

### standard library import
from functools import partialmethod


### third-party imports

from pygame.draw import line as draw_line
from pygame.mouse import get_pos as get_mouse_pos


### local imports

from ..config import APP_REFS

from ..pygameconstants import (
    SCREEN,
    SCREEN_RECT,
)

from ..ourstdlibs.mathutils import offset_point

from ..our3rdlibs.behaviour import indicate_unsaved, saved_or_unsaved_state_kept

from ..loopman.exception import ContinueLoopException

from ..colorsman.colors import YELLOW


class Repositioning:
    """Contains data and behaviour for repositioning."""

    def __init__(self):
        """Define controls to support repositioning."""
        ### define controls

        self.relative_pos_map = None
        self.mouse_pos_backup = None

        self.translation_factor = 1
        self.x_axis_factor = self.y_axis_factor = 1

    def start_moving(self):
        """Start moving selected objs."""
        ### return earlier if no obj is selected
        if not self.selected_objs:
            return

        ### otherwise perform operations to support moving

        ## backup position of objects relative to the
        ## moving origin

        self.relative_pos_map = {
            obj: (obj.rectsman.midtop if hasattr(obj, "rectsman") else obj.rect.midtop)
            for obj in self.selected_objs
        }

        ## backup mouse position
        self.mouse_pos_backup = get_mouse_pos()

        ## set window manager state
        APP_REFS.window_manager.set_state("moving_object")

        ### restart the loop
        raise ContinueLoopException

    def track_mouse(self):
        """Transfer mouse relative pos to selected objs."""
        current_x, current_y = get_mouse_pos()
        start_x, start_y = self.mouse_pos_backup

        delta_x = current_x - start_x
        delta_y = current_y - start_y

        ### control translation finesse

        delta_x //= self.translation_factor
        delta_y //= self.translation_factor

        ### control axis restraining

        delta_x *= self.x_axis_factor
        delta_y *= self.y_axis_factor

        ### iterate over selected objs setting the
        ### resulting relative positions

        for obj in self.selected_objs:

            rel_pos = self.relative_pos_map[obj]

            final_deltas = offset_point(rel_pos, (delta_x, delta_y))

            try:
                obj.rectsman.midtop = final_deltas
            except AttributeError:
                obj.rect.midtop = final_deltas

    def constrain_axes(self, relative_to_x):
        """Constrain amount of translation to axis.

        relative_to_x
            Boolean. If True, constraining is being made
            relative to the x axis. Else, such constraining
            is relative to the y axis.
        """
        ### for each axis toggled, cover the three possible
        ### cases:
        # 1) axis in question is on,  other  is on
        # 2) axis in question is on,  other  is off
        # 3) axis in question is off, other  is on
        x, y = self.x_axis_factor, self.y_axis_factor

        if relative_to_x:

            if x and y:
                self.y_axis_factor = 0
            elif x and not y:
                self.y_axis_factor = 1
            elif not x and y:
                self.x_axis_factor, self.y_axis_factor = (
                    self.y_axis_factor,
                    self.x_axis_factor,
                )

        else:

            if y and x:
                self.x_axis_factor = 0
            elif y and not x:
                self.x_axis_factor = 1
            elif not y and x:
                self.x_axis_factor, self.y_axis_factor = (
                    self.y_axis_factor,
                    self.x_axis_factor,
                )

    constrain_to_x = partialmethod(constrain_axes, True)
    constrain_to_y = partialmethod(constrain_axes, False)

    def check_axis_line(self):
        """If only one axis is used, draw line to indicate.

        Such line is parallel to the axis being used and
        touches the center of the obj being translated.
        """
        ### return earlier if moving with all axes in use

        if self.x_axis_factor and self.y_axis_factor:
            return

        ### draw line

        elif self.x_axis_factor and not self.y_axis_factor:

            y = self.active_obj.rect.centery
            start, end = (0, y), (SCREEN_RECT.right, y)

        elif self.y_axis_factor and not self.x_axis_factor:

            x = self.active_obj.rect.centerx
            start, end = (x, 0), (x, SCREEN_RECT.bottom)

        draw_line(SCREEN, YELLOW, start, end, 2)

    def unconstrain_axes(self):
        """Remove constraints on axes."""
        self.x_axis_factor = self.y_axis_factor = 1

    def cancel_moving(self):
        """Return selected obj(s) to initial position."""
        ### return objs to initial positions

        for obj in self.selected_objs:

            relative_midtop = obj.data["midtop"]

            absolute_midtop = tuple(relative_midtop + self.scrolling_amount)

            try:
                obj.rectsman.midtop = absolute_midtop
            except AttributeError:
                obj.rect.midtop = absolute_midtop

        ### admin task: restore controls/behaviours

        ## controls

        self.unconstrain_axes()
        self.translation_factor = 1

        ## set window manager state
        APP_REFS.window_manager.set_state("loaded_file")

        ### if the moving_from_duplication flag is on,
        ### it means the objects where duplicate objects
        ### that were being moved; when the user cancels
        ### moving them in this specific case we assume
        ### the user wants to cancel the duplication, so
        ### the duplicate objects (the selected ones) are
        ### removed and the flag is set to False

        if self.moving_from_duplication:

            ## remove selected objects without changing
            ## the saved/unsaved state

            with saved_or_unsaved_state_kept():
                self.remove_selected()

            ## set flag off
            self.moving_from_duplication = False

        ### restart the loop
        raise ContinueLoopException

    def confirm_moving(self):
        """Store current objs positions value."""
        ### store the midtop position of each object,
        ### relative to the moving origin into the
        ### 'midtop' field of their data

        for obj in self.selected_objs:

            absolute_midtop = (
                obj.rectsman.midtop if hasattr(obj, "rectsman") else obj.rect.midtop
            )

            relative_midtop = tuple(absolute_midtop - self.scrolling_amount)

            obj.data["midtop"] = relative_midtop

        ### indicate new changes in the data
        indicate_unsaved()

        ### admin task: restore controls/behaviours

        ## controls

        self.unconstrain_axes()
        self.translation_factor = 1

        ## set window manager state
        APP_REFS.window_manager.set_state("loaded_file")

        ### if the moving_from_duplication flag is on,
        ### it means the objects where duplicate objects
        ### that were being moved; since the user confirmed
        ### the position of the new, duplicate objects, we
        ### assume the user approves the duplication
        ### operation, so we can finally set the flag off
        ### (leaving it on would make it so the next
        ### cancelled moving operation would delete
        ### the selected objects, which isn't a desired
        ### behaviour)

        if self.moving_from_duplication:
            self.moving_from_duplication = False

        ### restart the loop
        raise ContinueLoopException

    ### XXX
    ### note that the method below isn't refactored nor
    ### used yet; it came from the package from which
    ### the node editor was forked and is kept here
    ### for when I refactor and integrate it in the
    ### current active features;

    def move_objs(
        self,
        obj_pos_pairs,
        update_pos_on_screen=False,
        change_caption=True,
        undo_redo_admin=True,
    ):
        """Move objs.

        obj_pos_pairs (iterable)
            Contains pairs referencing an obj and the new
            position value to be assigned respectively.
        update_pos_on_screen (boolean)
            Whether to update the position of the objs
            on the screen or not (if the objs are already
            in their final positions, then just use False).
        change_caption
            Boolean indicating whether the change made must
            be indicated in the window caption.
        undo_redo_admin
            Boolean indicating whether undo/redo
            administration tasks must be performed
        """
        ### assign new positions
        APP_REFS.gm.update_pos_values(obj_pos_pairs)

        ### if requested, update position of objs on
        ### the screen too

        if update_pos_on_screen:

            for obj, pos in obj_pos_pairs:
                obj.set_pos(pos)

        ### if requested, indicate in the window caption
        ### that a change has been made
        if change_caption:
            indicate_unsaved()

        ### if requested, perform undo/redo administration
        ### tasks

        if undo_redo_admin:

            ## gather data

            anim_name = APP_REFS.gm.anim_name
            frame_no = APP_REFS.gm.get_current_frame()

            ## record change

            self.change_stack.append(
                {
                    "operation": "movement",
                    "from": self.relative_pos_map.items(),
                    "to": obj_pos_pairs,
                }
            )

            ## clear redo_stack
            self.redo_stack.clear()

    def move_from_click_and_drag(self, obj):
        """Move object target of a click and drag action.

        If it is selected, the entire selection is moved,
        otherwise, the selection is cleared and the object
        is selected and moves alone.
        """
        ### if obj is not selected, deselected all
        if obj not in self.selected_objs:
            APP_REFS.ea.deselect_all()

        ### regardless of being selected or not,
        ### add it to selection, since it becomes
        ### the active object anyway
        self.add_obj_to_selection(obj)

        ## start moving the selection
        self.start_moving()
