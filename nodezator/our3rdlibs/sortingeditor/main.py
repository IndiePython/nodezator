"""Facility with mvc manager for manually sorting lists."""

### standard library imports

from random import shuffle

from functools import partial, partialmethod


### third-party imports

from pygame.math import Vector2

from pygame.draw import rect as draw_rect


### local imports

from ...config import APP_REFS

from ...pygameconstants import (
    SCREEN_RECT,
    FPS,
    maintain_fps,
)

from ...ourstdlibs.behaviour import get_oblivious_callable

from ...ourstdlibs.collections.general import CallList

from ..behaviour import watch_window_size

from ...surfsman.draw import blit_aligned
from ...surfsman.render import render_rect

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D, Set2D

from ...surfsman.icon import render_layered_icon

from ...textman.render import render_text

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ...colorsman.colors import (
    BLACK,
    BUTTON_FG,
    BUTTON_BG,
    WINDOW_FG,
    WINDOW_BG,
    AREA_LABEL,
    SORTED_ITEMS_AREA,
    ITEM_POOL_AREA,
)

## class extension
from .modes import SortingEditorModes


### TODO make sure items from available items are
### duplicated when grabbed;
###
### make sure items from the sorted sequence are gone
### when dropped anywhere outside the sorted sequence
### boundaries;


### utility function


def sort_by_value(a_list):
    """Sort list with the "value" attribute of its items."""
    a_list.sort(key=lambda item: item.value)


### class definition


class SortingEditor(SortingEditorModes):
    """loop holder for assisting in sorting sequences."""

    def __init__(self):
        """Store args, create widgets."""
        ### create a surface to represent the entire widget
        image = render_rect(800, 270, WINDOW_BG)

        ### load/create more surfaces and blit them into
        ### the image

        icon = render_layered_icon(
            chars=[chr(ordinal) for ordinal in (104, 105)],
            dimension_name="height",
            dimension_value=30,
            colors=[BLACK, (30, 130, 70)],
            background_width=32,
            background_height=32,
        )

        title = render_text(
            text="List Sorting Editor",
            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
        )

        for surf, surf_offset in (
            (icon, (10, 10)),
            (title, (50, 15)),
        ):

            blit_aligned(
                surface_to_blit=surf,
                target_surface=image,
                retrieve_pos_from="topleft",
                assign_pos_to="topleft",
                offset_pos_by=surf_offset,
            )

        ### define a rect for the widget
        rect = self.rect = image.get_rect()

        ### define and store rects for 02 different areas
        ### in the widget, blitting filled areas into the
        ### image so these areas are visible

        self.items_area = rect.copy()
        self.items_area.height = 70
        self.items_area.top = rect.top + 90

        self.available_items_area = self.items_area.copy()
        self.available_items_area.top = self.items_area.bottom

        draw_rect(image, SORTED_ITEMS_AREA, self.items_area)

        draw_rect(image, ITEM_POOL_AREA, self.available_items_area)

        ### blitting text surfaces into the image marking
        ### the meaning of each area

        for label_text, area in (
            ("Sorted items", self.items_area),
            ("Available items", self.available_items_area),
        ):

            label = Object2D.from_surface(
                surface=(
                    render_text(
                        text=label_text,
                        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                        font_path=ENC_SANS_BOLD_FONT_PATH,
                        padding=5,
                        foreground_color=AREA_LABEL,
                    )
                ),
                coordinates_name="topleft",
                coordinates_value=area.topleft,
            )

            image.blit(label.image, label.rect)

        ### store the image on its own attribute and
        ### as well as a copy which we'll use to clean
        ### the widget surface to redraw on top of it
        ### each loop

        self.image = image
        self.clean_bg = image.copy()

        ### create the buttons used by this widget
        self.create_buttons()

        ### center sorting editor and append centering
        ### method as a window resize setup

        self.center_sorting_editor()

        APP_REFS.window_resize_setups.append(self.center_sorting_editor)

        ### finally enable normal behaviour
        self.enable_normal_mode()

    def center_sorting_editor(self):
        rect = self.rect

        diff = Vector2(SCREEN_RECT.center) - rect.center

        ###

        rect.center = SCREEN_RECT.center

        ### also define and store an offset equivalent to
        ### the inverted topleft position
        self.offset = -Vector2(rect.topleft)

        ###
        self.items_area.move_ip(diff)
        self.available_items_area.move_ip(diff)

        ###

        self.sorting_buttons.rect.topleft = rect.move(5, 50).topleft

        self.session_buttons.rect.bottomright = rect.move(-5, -5).bottomright

        ###

        try:
            self.items
        except AttributeError:
            pass

        else:

            if self.items:
                self.items.rect.move_ip(diff)

            self.available_items.rect.move_ip(diff)

    def create_buttons(self):
        """Create button objects."""
        ### define behaviours for buttons

        confirm = partial(setattr, self, "running", False)

        cancel = CallList(
            [
                partial(setattr, self, "cancel", True),
                confirm,
            ]
        )

        ### create buttons using pairs of strings/callables
        ### as the text and command of the button
        ### respectively (the command is stored in the
        ### 'on_mouse_release' attribute of the button
        ### object via the 'attributes_dict' parameter)
        ###
        ### the buttons are stored in an instance of
        ### a custom list subclass, which is stored in its
        ### own attribute as well as being referenced locally

        buttons = self.buttons = List2D(
            Object2D.from_surface(
                surface=render_text(
                    text=text,
                    font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                    padding=5,
                    depth_finish_thickness=1,
                    foreground_color=BUTTON_FG,
                    background_color=BUTTON_BG,
                ),
                # note that we pass the command through
                # the get_oblivious_callable function
                # so the resulting callable ignores any
                # given argument when executing
                on_mouse_release=get_oblivious_callable(command),
            )
            for text, command in (
                ("Value Sort", self.sort_items_by_value),
                ("Reverse", self.reverse_items),
                ("Shuffle", self.shuffle_items),
                ("Cancel", cancel),
                ("Ok", confirm),
            )
        )

        ### now divide the buttons in two different
        ### temporary groups in order to easily align then

        ## first group

        self.sorting_buttons = List2D(buttons[:3])
        self.sorting_buttons.rect.snap_rects_ip(
            retrieve_pos_from="topright", assign_pos_to="topleft", offset_pos_by=(5, 0)
        )

        ## second group

        self.session_buttons = List2D(buttons[3:])

        self.session_buttons.rect.snap_rects_ip(
            retrieve_pos_from="topright", assign_pos_to="topleft", offset_pos_by=(5, 0)
        )

    def sort_items(self, sorting_callable):
        """Sort items w/ callable and reposition them.

        Parameters
        ==========
        sorting_callable (callable)
            callable used to sort the items.
        """
        ### sorting makes no sense when there aren't any
        ### items, so we return early
        if not self.items:
            return

        ### otherwise we proceed realigning and repositioning
        ### the items

        ## backup topleft
        topleft = self.items.rect.topleft

        ## sort items
        sorting_callable(self.items)

        ## reposition items relative to each other

        self.items.rect.snap_rects_ip(
            retrieve_pos_from="topright", assign_pos_to="topleft", offset_pos_by=(5, 0)
        )

        ## restore topleft
        self.items.rect.topleft = topleft

    sort_items_by_value = partialmethod(sort_items, sort_by_value)

    reverse_items = partialmethod(sort_items, list.reverse)
    shuffle_items = partialmethod(sort_items, shuffle)

    def sort_sequence(self, sorted_items, available_items):
        """Prepare objects for edition and start loop.

        Parameters
        ==========
        sorted_items (list or tuple)
            list representing current sorted items.
        available_items (set)
            set representing available items to include
            and sort in the sorted_items sequence.
        """
        ### store type of sorted items
        _type = type(sorted_items)

        ### isntantiate special objects representing the
        ### items to be sorted and the available ones
        self.prepare_objs(sorted_items, available_items)

        ### create flags

        self.cancel = False
        self.running = True

        ### start the widget loop

        while self.running:

            ## maintain a constant framerate
            maintain_fps(FPS)

            ## watch out for when window is resized
            watch_window_size()

            ## perform GUD operations (initials of the
            ## methods; see also the loop holder definition
            ## on the glossary)

            self.handle_input()
            self.update()
            self.draw()

        ### once the loop is exited, return the appropriate
        ### value according to the whether the 'cancel'
        ### flag is set or not

        return (
            ## if the flag is on, return None, indicating
            ## the edition was cancelled
            None
            if self.cancel
            ## otherwise return a sequence with the sorted
            ## values in the type they were received
            else _type(item.value for item in self.items)
        )

    def prepare_objs(self, sorted_items, available_items):
        """Instantiate special objects representing items.

        Parameters: see "sort_sequence" method docstring.
        """
        ### for each list, attribute name and area listed,
        ### define a new List2D instance containing
        ### the items of the list, align such items and
        ### position them according to the given area and
        ### finally store the List2D instance in the
        ### attribute

        for class_, collection, attr_name, area in (
            (List2D, sorted_items, "items", self.items_area),
            (Set2D, available_items, "available_items", self.available_items_area),
        ):

            ## instantiate collection

            items = class_(
                Object2D.from_surface(
                    surface=(
                        render_text(
                            text=repr(item),
                            font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                            padding=5,
                            depth_finish_thickness=1,
                            foreground_color=(0, 0, 190),
                            background_color=(255,) * 3,
                            border_color=(0, 0, 190),
                            border_thickness=2,
                        )
                    ),
                    value=item,
                )
                for item in collection
            )

            ## align its items and position the instance
            ## if not empty

            if items:

                items.rect.snap_rects_ip(
                    retrieve_pos_from="topright",
                    assign_pos_to="topleft",
                    offset_pos_by=(5, 0),
                )

                items.rect.midleft = area.move(30, 7).midleft

            ## store the instance in an attribute
            setattr(self, attr_name, items)

    def reposition_list(self, a_list, obj):
        """Reposition items in given list.

        Parameters
        ==========
        a_list (List2D instance)
            list whose items are to be repositioned/aligned.
        obj (Object2D instance)
            item of the list used as reference the position
            the list horizontally.
        """
        ### backup the x coordinate of the object center
        centerx = obj.rect.centerx

        ### reference the rect of the list locally
        rect = a_list.rect

        ### align the items in the list relative to one
        ### another (one beside the other)

        rect.snap_rects_ip(
            retrieve_pos_from="topright", assign_pos_to="topleft", offset_pos_by=(5, 0)
        )

        ### set the center y coordinate of the list
        ### to the center y coordinate of the area
        ### to which the list corresponds, with just a
        ### bit of vertical offset

        rect.centery = (
            ## pick the center y of the items area if the
            ## list is the list of items
            self.items_area.centery
            if a_list is self.items
            ## otherwise pick the center y of the pool area
            ## (list refers to the pool of available items)
            else self.available_items_area.centery
        ) + 7  # vertical offset

        ### move the list by the horizontal difference
        ### between the original and current center x
        ### coordinate of the given object

        x_difference = centerx - obj.rect.centerx
        rect.move_ip(x_difference, 0)

        ### perform extra setups to ensure the given object
        ### stay visible (within a pre-defined boundary)

        ## define a rect representing the scrolling
        ## boundaires
        scroll_boundary = self.rect.inflate(-40, 0)

        ## obtain a copy of the object rect, but clamped
        ## to the defined boundary
        clamped_obj = obj.rect.clamp(scroll_boundary)

        ## if the clamped copy ended up in a different
        ## position, move the entire list by that
        ## difference

        if obj.rect.x != clamped_obj.x:

            x_difference = clamped_obj.x - obj.rect.x
            a_list.rect.move_ip(x_difference, 0)


sort_sequence = SortingEditor().sort_sequence
