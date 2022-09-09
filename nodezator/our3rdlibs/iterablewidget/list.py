"""Facility for editable list widget class."""

### standard library import
from math import inf as INFINITY


### local imports

from ...ourstdlibs.behaviour import (
    empty_function,
    get_oblivious_callable,
)

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...rectsman.main import RectsManager, rect_property

from .surfs import ADD_BUTTON_SURF

## class extension
from .op import (
    ListWidgetLifetimeOperations,
)


class ListWidget(ListWidgetLifetimeOperations):
    """Widget which represents a list of values.

    The values, on the other hand, are represented by
    widgets.
    """

    def __init__(
        self,
        widget_factory,
        default_factory,
        value=(),
        min_len=0,
        max_len=INFINITY,
        name="widget_list",
        command=empty_function,
        quantity_command=empty_function,
        vertical_padding=5,
        coordinates_name="topleft",
        coordinates_value=(0, 0),
    ):
        """
        item_factory (callable)
            used as a factory function to generate a new
            widget.
        value (iterable of values)
            collection of values used in each widget.
        min_len (integer, defaults to 0)
            optional minimum length of the list. If a
            min_len above 0 is provided, the widget won't
            let the user remove items when it will make
            the list to have less than the minimum amount
            of items.
        max_len (integer or math.inf, which is default)
            optional maximum length of the list. If math.inf
            is given, no maximum number of items is set.
            Otherwise, if an integer is provided, the widget
            won't let the user add new items when doing so
            will increase the number of items above the
            maximum length allowed.
        name (string)
            an arbitrary name to help identify the widget.
        command (callable)
            callable to be execute after setting the value.
            It is also assigned to each widget.
        quantity_command (callable)
            callable to be executed every time the quantity
            of items change. This widget changes its the
            height whenever items are added or removed.
            Whenever you want to respond to such changes
            in height, assign the desired behaviour to
            this parameter.
        vertical_padding (integer)
            amount of pixels between an item and the next
            one below it.
        coordinates_name (string)
            represents attribute name of rect wherein
            to store the position information from the
            coordinates value parameter.
        coordinates_value (2-tuple of integers)
            represents a position in 2d space; the values of
            x and y axes, respectively.
        """
        ### store value
        self.value = value

        ### store a minimum and maximum length

        self.min_len = min_len
        self.max_len = max_len

        ### perform preliminary length checks

        length = len(self.value)

        if not length >= self.min_len:

            msg = (
                "length of 'value' provided is lower than the"
                " specified minimum length ({} < {})"
            ).format(length, self.min_len)

            raise ValueError(msg)

        if not length <= self.max_len:

            msg = (
                "length of 'value' provided is higher than"
                " the specified maximum length ({} > {})"
            ).format(length, self.max_len)

            raise ValueError(msg)

        ### store the commands

        self._command = command
        self.quantity_command = quantity_command

        ### store the vertical padding
        self.vertical_padding = vertical_padding

        ### store name
        self.name = name

        ### store the widget and default factory callables

        self.widget_factory = widget_factory
        self.default_factory = default_factory

        ### create a list to hold all objects
        self.all_objects = List2D()

        ### instantiate and store an "add button"

        add_on_mouse_release = get_oblivious_callable(self.add_item)

        self.add_button = Object2D(
            image=ADD_BUTTON_SURF,
            rect=ADD_BUTTON_SURF.get_rect(),
            on_mouse_release=add_on_mouse_release,
        )

        ### also append it to the list of objects and
        ### clickable
        self.all_objects.append(self.add_button)

        ### build a rects manager according to the
        ### rectsman protocol (check rectsman subpackage
        ### for more info on that);
        ###
        ### also, though I can control all items plus the
        ### add button with the rects manager of the
        ### List2D instance in the "all_objects"
        ### attribute, having a dedicated rects manager
        ### instance may be useful in case I decide to add
        ### other aesthetic elements, like a custom
        ### background (in which case I'd need a create an
        ### additional "rect" and would not want to add it
        ### to the "all_objects" list, I'd just keep it
        ### elsewhere as yield it in the "get_all_rects"
        ### method)
        self._rects_man = RectsManager(self.get_all_rects)

        ### create items for each value and reference
        ### the clickable objects within each item

        for value in self.value:
            self.add_item(value, False, False, False, False)

        self.reference_clickables()

        ### position this instance using its rect property
        ### and the given coordinates

        setattr(self.rect, coordinates_name, coordinates_value)

    rect = rect_property

    def get_all_rects(self):
        """Return all relevant rects in this instance."""
        yield self.all_objects.rect

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        ### store command
        self._command = value

        ### set command in all widgets

        ## filter self.add_button out of items and get
        ## the widget which sits at the index 2 of each
        ## item

        widgets = (item[2] for item in self.all_objects if item is not self.add_button)

        ## set the command of each widget to the new one
        for widget in widgets:
            widget.command = self._command
