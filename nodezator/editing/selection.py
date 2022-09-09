"""Facility for object selection handling."""

### standard library imports

from itertools import chain
from functools import partialmethod
from collections import deque
from random import sample


### third-party imports

from pygame import Rect, KMOD_SHIFT, KMOD_CTRL

from pygame.key import get_mods as get_mods_bitmask
from pygame.mouse import get_pos as get_mouse_pos
from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS

from ..pygameconstants import SCREEN

from ..ourstdlibs.mathutils import get_rect_from_points

from ..loopman.exception import ContinueLoopException

from ..colorsman.colors import (
    ACTIVE_SELECTION,
    NORMAL_SELECTION,
)


### class definition


class SelectionHandling:
    """Contains data and behaviour to support selection."""

    def __init__(self):
        """Define controls for selection."""
        ### define controls

        self.selected_objs = deque()
        self.active_obj = None

    ### methods supporting selection in general

    def draw_selected(self):
        """Draw outline of selected objects."""
        for obj in self.selected_objs:

            obj.draw_selection_outline(
                ACTIVE_SELECTION if obj is self.active_obj else NORMAL_SELECTION
            )

    def change_selection_state(self, obj):
        """Change object's selection state.

        The change depends on shift key being pressed
        or not and consists of selecting, deselecting or
        turning the object the active selection.
        """
        ### if shift is pressed...

        if KMOD_SHIFT & get_mods_bitmask():

            ## if object isn't event selected,
            ## make it so by appending to
            ## 'selected_objs'; also make it the
            ## active object

            if obj not in self.selected_objs:

                self.selected_objs.append(obj)
                self.active_obj = obj

            ## if it is already selected (since
            ## the previous 'if block' failed) and
            ## not active, just make it the active
            ## selection

            elif obj is not self.active_obj:
                self.active_obj = obj

            ## if the object is the active
            ## selection though, unselect it
            ## and set the active obj to another
            ## object or None

            else:

                self.selected_objs.remove(obj)

                try:
                    self.active_obj = self.selected_objs[-1]

                except IndexError:
                    self.active_obj = None

        ### if shift is not pressed, though...

        else:

            ### unselect all objects and keep
            ### the current obj as the only
            ### selected, active one

            self.selected_objs.clear()

            self.selected_objs.append(obj)
            self.active_obj = obj

    def select_all_toggle(self, should_select):
        """Toggle (de)selection of all objs.

        Parameters
        ==========
        should_select (boolean)
            If true, all objs should be selected,
            otherwise they are all deselected.
        """
        ### clear the selection

        self.selected_objs.clear()
        self.active_obj = None

        ### if we must select...
        if should_select:

            ### select all objects

            self.selected_objs.extend(chain(APP_REFS.gm.nodes, APP_REFS.gm.text_blocks))

            ### try setting the active selection to the last
            ### selected object
            try:
                self.active_obj = self.selected_objs[-1]

            ### otherwise set the active selection to None
            except IndexError:
                self.active_obj = None

    select_all = partialmethod(select_all_toggle, True)
    deselect_all = partialmethod(select_all_toggle, False)

    def add_obj_to_selection(self, obj):
        """Add object to selection, if not selected already.

        Also makes the object the active one.

        Parameters
        ==========
        obj
        ( graphman.callablenode.CallableNode (or subclass)
          or graphman.textblock.TextBlock
          or graphman.proxynode.ProxyNode
          or graphman.proxynode.OperatorNode instance
        )
            obj to be added to selection.
        """
        if obj not in self.selected_objs:
            self.selected_objs.append(obj)

        self.active_obj = obj

    ### additional methods to support box selection

    def start_box_selection(self):
        """Prepare for box selection mode and set it."""
        ### store current mouse pos
        self.initial_box_pos = get_mouse_pos()

        ### get a copy of the scrolling amount by adding
        ### (0, 0) to it and store the copy as the initial
        ### scrolling
        self.initial_scrolling = self.scrolling_amount + (0, 0)

        ### create a rect with arbitrary values,
        ### representing a selection box
        self.selection_box = Rect(0, 0, 0, 0)

        ### set behaviour related to box selection in the
        ### window manager and go to beginning of the app
        ### loop

        APP_REFS.window_manager.set_state("box_selection")
        raise ContinueLoopException

    def cancel_box_selection(self):
        """Delete attributes and exit box selection mode."""
        ### clean attributes which we won't use anymore
        self.clean_selection_box_attrs()

        ### set 'loaded_file' mode back and go to beginning
        ### of loop

        APP_REFS.window_manager.set_state("loaded_file")
        raise ContinueLoopException

    def confirm_box_selection(self):
        """Perform the box selection and needed setups."""
        ### if the smallest dimension of the selection box
        ### is too small, cancel the selecting;
        ###
        ### this will cause the method to stop executing,
        ### by raising an exception indicating the mode
        ### must be changed to the normal 'loaded file'
        ### mode, after doing some clean up;
        ###
        ### check the 'xxx' comment in draw_selection_box()
        ### method to know why we impose this limitation

        if min(self.selection_box.size) < 4:
            self.cancel_box_selection()

        ### get a bitmask and use it to evaluate whether
        ### the shift and ctrl keys are pressed or not

        bitmask = get_mods_bitmask()

        shift = bitmask & KMOD_SHIFT
        ctrl = bitmask & KMOD_CTRL

        ### perform box collision selection according
        ### to suitable scenario defined below depending
        ### on the states of modifier keys;
        ###
        ### note that "ctrl and not shift" condition triggers
        ### segment severing (cutting lines between nodes),
        ### so don't use it here;

        ## extend selection with colliding objects

        if shift and not ctrl:
            self.box_select_extend_colliding()

        ## deselect colliding objects

        elif shift and ctrl:
            self.box_deselect_colliding()

        ## only colliding objects must become/remain selected

        elif not shift and not ctrl:

            self.deselect_all()
            self.box_select_extend_colliding()

        ### clean attributes which we won't use anymore
        self.clean_selection_box_attrs()

        ### set 'loaded_file' mode back and go to beginning
        ### of loop

        APP_REFS.window_manager.set_state("loaded_file")
        raise ContinueLoopException

    def get_box_colliding(self):
        """Return set of objs colliding w/ selection box."""
        ### reference collision operation locally
        collides = self.selection_box.colliderect

        ### return set with each colliding object

        return {
            ## store an object...
            obj
            ## for each obj among the function nodes and
            ## text blocks...
            for obj in chain(APP_REFS.gm.nodes, APP_REFS.gm.text_blocks)
            ## if that object collides with the selection box
            if collides(obj.rect)
        }

    def box_select_extend_colliding(self):
        """Add objs colliding w/ box to selection."""
        ### get objects colliding with box selection
        colliding_objs = self.get_box_colliding()

        ### if there are no colliding objects, there's
        ### no point in keep going, so return early
        if not colliding_objs:
            return

        ### otherwise update the selection and the active
        ### obj

        ## get the union of all objects
        union = set(self.selected_objs).union(colliding_objs)

        ## select objects in the union

        self.selected_objs.clear()
        self.selected_objs.extend(union)

        ### assign a random object among the colliding ones
        ### as the active object

        self.active_obj = sample(list(colliding_objs), 1).pop()

    def box_deselect_colliding(self):
        """Remove objs colliding w/box from selection."""
        ### get objects colliding with box selection
        colliding_objs = self.get_box_colliding()

        ### if there are no colliding objects, there's
        ### no point in keep going, so return early
        if not colliding_objs:
            return

        ### otherwise removing colliding object from
        ### selection and set the active obj

        ## get the difference between the selected objects
        ## and the colliding ones
        difference = set(self.selected_objs) - colliding_objs

        ## select objects in the difference

        self.selected_objs.clear()
        self.selected_objs.extend(difference)

        ### assign a random object among the selected ones
        ### as the active object or use None, depending
        ### on whether there are selected objects or not

        self.active_obj = (
            sample(list(self.selected_objs), 1).pop() if self.selected_objs else None
        )

    def clean_selection_box_attrs(self):
        """Delete unneeded attributes from box selection."""
        del self.initial_box_pos
        del self.initial_scrolling
        del self.selection_box

    def recalculate_selection_box(self):
        """Recalculate selection box w/ specific points."""
        ### calculate the point 1 of the box

        box_point_1 = (
            ## grab the absolute point in the screen where
            ## the box selection started
            self.initial_box_pos
            ## and add the difference between the inital
            ## scrolling and the current scrolling
            + (self.scrolling_amount - self.initial_scrolling)
        )

        ### the point 2 of the box is the current mouse
        ### position
        box_point_2 = get_mouse_pos()

        ### now, using the points, define the data for
        ### the selection box
        left, top, width, height = get_rect_from_points(box_point_1, box_point_2)

        ### and update the selection box

        self.selection_box.topleft = left, top
        self.selection_box.size = width, height

    def draw_selection_box(self):
        """Draw selection box rect on the screen.

        That is, if its smallest dimension is at least
        4 pixels.
        """
        ### XXX the size check below wasn't previously
        ### needed in pygame 1 (at least not in the
        ### version I used), but in pygame 2 drawing
        ### a rect with a dimension too small causes
        ### a weird shape to be drawn instead, so we
        ### added this limitation;
        ###
        ### this is also taken into account when
        ### finishing selecting, where we do not perform
        ### the selection if the selection box is so
        ### small that it isn't drawn; this is probably
        ### the best/less confusing behaviour, since
        ### the selection box isn't visible anyway;
        ###
        ### I also checked the pygame github and saw
        ### that the issue was already reported;

        ### leave the method before drawing the selection
        ### box if its smallest dimension is less than
        ### 4 pixels

        if min(self.selection_box.size) < 4:
            return

        ### otherwise we draw the selection box

        draw_rect(SCREEN, NORMAL_SELECTION, self.selection_box, 2)
