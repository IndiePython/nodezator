"""Facility for editable list widget class."""

### standard library imports
from functools import partial, partialmethod


### local imports

from ...ourstdlibs.behaviour import get_oblivious_callable

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from .surfs import (
    MOVE_UP_BUTTON_SURF,
    MOVE_DOWN_BUTTON_SURF,
    REMOVE_BUTTON_SURF,
)


### XXX lots of operations of this class could be
### considered editing operations without the need to
### change any of the items themselves;
###
### for instance: changing the item position or
### adding/deleting items; make sure to account for those
### regarding the usage of the custom command

### sentinel class
class Sentinel:
    pass


### class definition


class ListWidgetLifetimeOperations:
    """Operations for lifetime of ListWidget instances."""

    def add_item(
        self,
        value=Sentinel,
        custom_command=True,
        quantity_command=True,
        reference_clickables=True,
        update_value=True,
    ):
        """Create new widget for the widget list.

        Accompanying buttons are also created.
        """
        ### if value is a sentinel, grab a new one from
        ### the default factory
        if value is Sentinel:
            value = self.default_factory()

        ### if the self.value will be updated, and thereby
        ### incremented, since this operation adds an item,
        ### we must only allow it if the resulting length
        ### won't be higher than the maximum allowed

        if update_value:

            ## get the resulting length
            resulting_length = len(self.value) + 1

            ## if resulting length isn't less than or
            ## equal the maximum length defined, we cancel
            ## this operation by returning earlier
            if not resulting_length <= self.max_len:
                return

        ### create a list to hold objects representing
        ### this item
        item_objs = List2D()

        ### instantiate and store moving buttons

        ## move up button

        move_up_on_mouse_release = get_oblivious_callable(
            partial(self.move_item_up, item_objs)
        )

        move_up_button = Object2D(
            image=MOVE_UP_BUTTON_SURF,
            rect=MOVE_UP_BUTTON_SURF.get_rect(),
            on_mouse_release=move_up_on_mouse_release,
        )

        ## move down button

        move_down_on_mouse_release = get_oblivious_callable(
            partial(self.move_item_down, item_objs)
        )

        move_down_button = Object2D(
            image=MOVE_DOWN_BUTTON_SURF,
            rect=MOVE_DOWN_BUTTON_SURF.get_rect(),
            on_mouse_release=move_down_on_mouse_release,
        )

        ### instantiate widget
        widget = self.widget_factory(value=value, command=self.command)

        ### instantiate delete button

        ## on_mouse_release command

        remove_on_mouse_release = get_oblivious_callable(
            partial(self.remove_item, item_objs)
        )

        ## obj

        remove_button = Object2D(
            image=REMOVE_BUTTON_SURF,
            rect=REMOVE_BUTTON_SURF.get_rect(),
            on_mouse_release=remove_on_mouse_release,
        )

        ### store all objects in the list

        item_objs.extend((move_up_button, move_down_button, widget, remove_button))

        ### position the objects side to side, aligning
        ### each object's midright with the next object's
        ### midleft, with just a bit of horizontal offset

        item_objs.rect.snap_rects_ip(
            retrieve_pos_from="midright", assign_pos_to="midleft", offset_pos_by=(5, 0)
        )

        ### align the item's topleft with the topleft of
        ### the add_button
        item_objs.rect.topleft = self.add_button.rect.topleft

        ### and position the add button below the item,
        ### adding a bit of padding
        self.add_button.rect.top = item_objs.rect.bottom + self.vertical_padding

        ### finally insert the item into the all_objects
        ### list, before the last item, which is the
        ### add button
        self.all_objects.insert(-1, item_objs)

        ### execute specific commands, if requested

        if custom_command:
            self.command()
        if quantity_command:
            self.quantity_command()
        if reference_clickables:
            self.reference_clickables()

        ### if requested, update the value of this widget
        if update_value:
            self.value = self.get()

    def remove_item(
        self,
        item,
        custom_command=True,
        quantity_command=True,
    ):
        """Remove given item."""
        ### since this operation removes an item,
        ### we must only allow it if the resulting length
        ### won't be lower than the minimum allowed

        ## get the resulting length
        resulting_length = len(self.value) - 1

        ## if resulting length isn't equal or above the
        ## minimum length allowed, we cancel this
        ## operation by returning earlier
        if not resulting_length >= self.min_len:
            return

        ### store the current topleft of the whole widget
        ### (this is used for repositioning the remaining
        ### items, and must be done before removing an
        ### item because otherwise, if the item removed
        ### is the first one, the top changes and we don't
        ### want that)
        current_topleft = self.all_objects.rect.topleft

        ### remove item from list of objects

        for n, obj in enumerate(self.all_objects):

            ## note that it is ok to change the
            ## self.all_objects while iterating over it
            ## because we break out of the loop right away
            ## (since changing an object while iterating
            ## over it is only harmful if you plan to
            ## keep iterating further)

            if obj is item:

                self.all_objects.pop(n)
                break

        ### reposition remaining items

        (
            self.all_objects.rect.snap_rects_ip(
                retrieve_pos_from="bottomleft",
                assign_pos_to="topleft",
                offset_pos_by=(0, self.vertical_padding),
            )
        )

        self.all_objects.rect.topleft = current_topleft

        ### update the value of this widget to reflect
        ### the change made
        self.value = self.get()

        ### execute specific commands, if requested

        if custom_command:
            self.command()
        if quantity_command:
            self.quantity_command()

        ### admin task: reference clickable items
        self.reference_clickables()

    def call_mouse_method(self, method_name, event):
        """Execute object method if mouse hovers.

        Parameters

            - event (pygame.event.Event of
              pygame.MOUSEBUTTONUP or pygame.MOUSEBUTTONDOWN
              type)

              It is required in order to comply with
              protocol used. We retrieve the mouse position
              from its "pos" attribute.

              Check pygame.event module documentation on
              pygame website for more info about this event
              object.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### iterate over each object in the lists,
        ### until you find the colliding one

        colliding_obj = None

        for obj in self.clickable_objs:

            if obj.rect.collidepoint(mouse_pos):

                colliding_obj = obj

                ### note: we usually use break after
                ### checking for point collision (clicking)
                ### between multiple objects, but here it
                ### is specially important because the
                ### move and delete button operations change
                ### the position of items, which could cause
                ### them to be invoked if we were to
                ### continue interating and they moved
                ### into the colliding spot incidentally
                break

        ### if a colliding object was found, execute the
        ### mouse method requested in the method_name
        ### argument (passing the event object to it), if
        ### it the method exists

        if colliding_obj:

            try:
                mouse_method = getattr(colliding_obj, method_name)
            except AttributeError:
                pass
            else:
                mouse_method(event)

    on_mouse_click = partialmethod(call_mouse_method, "on_mouse_click")

    on_mouse_release = partialmethod(call_mouse_method, "on_mouse_release")

    def reference_clickables(self):
        """Create list w/ references of clickable objects.

        The clickable objects are the "add button" plus
        each individual object stored in each item of the
        list widget.
        """
        ### create a list of clickables
        clickable_objs = []

        ### iterate over all existing objects, appending the
        ### object if it is the add button, extending the
        ### list with it otherwise

        for item in self.all_objects:

            ## append item if it is the add button
            if item is self.add_button:
                clickable_objs.append(item)

            ## if not, them it is an item in the list,
            ## containing a lot of clickable objects,
            ## so we use it to extend the clickable objs
            ## instead of appending it
            else:
                clickable_objs.extend(item)

        ### store the list of clickable objects in its
        ### own attribute
        self.clickable_objs = clickable_objs

    def move_item(self, steps, item_to_move, custom_command=True):
        """Move given item up or down."""
        ### if there's only one value, moving makes no
        ### sense, so cancel the execution of the rest of
        ### the method by returning earlier
        if len(self.value) == 1:
            return

        ### reference all_objects locally for quicker and
        ### easier access
        all_objects = self.all_objects

        ### store the current topleft of the whole widget
        ### (this is used for repositioning the items,
        ### and must be done before moving the items
        ### because otherwise, if the item moved is the
        ### first one, the top changes and we don't
        ### want that)
        current_topleft = all_objects.rect.topleft

        ### excluding the add_button from the existing
        ### items by popping it, since we know it is the
        ### last item
        all_objects.pop()

        ### discover the index of the item to be moved

        for n, item in enumerate(all_objects):
            if item is item_to_move:
                break

        ### calculate its new value by adding the number of
        ### steps to it
        new_index = n + steps

        ### constrain the index to the possible existing
        ### ones by obtain the remainder of dividing it
        ### by the quantity of existing items
        new_index %= len(all_objects)

        ### then pop the item and insert it in the new
        ### index;
        ###
        ### notice that we don't need to catch its reference
        ### from the output of the list.pop() call, because
        ### we already have a reference to it in our
        ### "item_to_move" variable

        all_objects.pop(n)
        all_objects.insert(new_index, item_to_move)

        ### now just append the add button back and
        ### reposition the items

        all_objects.append(self.add_button)

        (
            all_objects.rect.snap_rects_ip(
                retrieve_pos_from="bottomleft",
                assign_pos_to="topleft",
                offset_pos_by=(0, self.vertical_padding),
            )
        )

        all_objects.rect.topleft = current_topleft

        ### update the values so they reflect the new
        ### order
        self.value = self.get()

        ### execute custom command, if requested
        if custom_command:
            self.command()

    move_item_up = partialmethod(move_item, -1)
    move_item_down = partialmethod(move_item, 1)

    def get(self):
        """Return value of widget list (a list of values).

        Works by returning a list with the value of each
        widget.
        """
        ### return a list with values from each widget
        ### in this ListWidget instance

        return [
            ## retrieve the subitem in the index 2 and
            ## grab the return value of its get() method...
            item[2].get()
            ## for each item obtained from the "all_objects"
            ## list, except the last one, which is the add
            ## button
            for item in self.all_objects[:-1]
        ]

    def set(
        self,
        value,
        custom_command=True,
        quantity_command=True,
    ):
        """Set value of this widget.

        By value, we mean a list of values, which is the
        kind of data this widget list object stores.

        Parameters
        ==========
        value (iterable)
            any iterable.
        custom_command (boolean)
            indicates whether to execute the custom command
            or not.
        quantity_command (boolean0
            indicates whether to execute the quantity
            command or not.
        """
        ### turn the received value argument into a list
        value = list(value)

        ### if the value is the same as the current one,
        ### there's no point in executing the operation,
        ### so we return earlier
        if value == self.value:
            return

        ### also, if the length of the specified value
        ### isn't allowed, we also cancel the operation
        ### by returning earlier

        length = len(value)

        if not length >= self.min_len or not length <= self.max_len:
            return

        ### if we reach this point in the method, it means
        ### there were no reasons to not set the new value,
        ### so we do so in the next steps

        ## backup current value
        value_backup = self.value

        ## update the current value
        self.value = value

        ## align the add_button with the topleft
        ## of the rect
        self.add_button.rect.topleft = self.rect.topleft

        ## clear the all_objects items and add the
        ## add_button again

        self.all_objects.clear()
        self.all_objects.append(self.add_button)

        ## try instantiating each widget (this is both
        ## the implementation of changes and the final
        ## check, because things can still go wrong when
        ## instantiating widgets for each item of the
        ## value

        try:

            for item_value in self.value:

                self.add_item(item_value, False, False, False, False)

        ## if anything does fail, print the error and restore
        ## the original value

        except Exception as err:

            print(err)
            self.set(value_backup, False, False)

        ## otherwise, just perform the additional tasks,
        ## if requested

        else:

            if custom_command:
                self.command()
            if quantity_command:
                self.quantity_command()

        ## finally reference the clickable objects,
        ## regardless of whether the 'try' block above
        ## succeeded or not
        self.reference_clickables()

    def draw(self):
        """Draw widgets and buttons."""
        for obj in self.all_objects:
            obj.draw()
