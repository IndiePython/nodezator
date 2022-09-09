"""Mode-related class extension for the SeqSortingEditor."""

### standard library imports

from functools import partialmethod
from itertools import chain


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_LEFT,
    K_a,
    K_RIGHT,
    K_d,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from pygame.math import Vector2

from pygame.event import get as get_events

from pygame.key import get_pressed as get_pressed_keys

from pygame.mouse import (
    get_pos as get_mouse_pos,
    set_visible as set_mouse_visibility,
)

from pygame.draw import (
    line as draw_line,
    rect as draw_rect,
)

from pygame.display import update


### local imports

from ...ourstdlibs.behaviour import empty_function

from ...ourstdlibs.collections.general import CallList

from ...surfsman.draw import draw_border

from ...classes2d.single import Object2D

from ...loopman.exception import QuitAppException

from ...colorsman.colors import ITEM_OUTLINE


### constant
SCROLL_X_SPEED = 20

### utility function


def draw_vertical_lines(image, offset_rect):
    """Draw vertical lines above and below given rect.

    The lines are draw above and below the central vertical
    section of the given rect.

    Parameters
    ==========
    image (pygame.Surface instance)
        surface wherein to draw the lines.
    offset_rect (pygame.Rect instance)
        rect positioned relative to the given image's origin.
    """
    ### retrieve the top, centerx and bottom coordinates
    ### of the rect

    top, centerx, bottom = (
        getattr(offset_rect, attr_name) for attr_name in ("top", "centerx", "bottom")
    )

    ### iterate over values representing the starting and
    ### ending values of the y coordinate of the lines
    ### to be draw, drawing such lines

    for y_start, y_end in ((top - 1, top - 20), (bottom + 1, bottom + 20)):

        draw_line(image, ITEM_OUTLINE, (centerx, y_start), (centerx, y_end), 2)


### class definition


class SortingEditorModes(Object2D):
    """Mode-related operations for the SortingEditor."""

    def normal_mode_handle_events(self):
        """Event handling for the normal mode."""
        for event in get_events():

            ### raise custom exception if user tries to
            ### quit the app
            if event.type == QUIT:
                raise QuitAppException

            ### KEYUP

            elif event.type == KEYUP:

                ## if the escape key is released, turn
                ## the "running" flag off and the
                ## "cancel" flag on;
                ##
                ## this will cause the edition session
                ## to be ended (the widget loop will be
                ## exited in the "sort_sequence" method)

                if event.key == K_ESCAPE:

                    self.running = False
                    self.cancel = True

                ## if one of the enter keys are release,
                ## though, we set the running flag off,
                ## and leave the cancel flag untouched;
                ## since the cancelling flag is off by
                ## default, it means we are confirming
                ## the edition

                elif event.key in (K_RETURN, K_KP_ENTER):
                    self.running = False

            ### execute the respective methods for when
            ### the mouse left button is pressed or released

            ## pressed

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.on_mouse_click(event)

            ## released

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.on_mouse_release(event)

    def on_mouse_click(self, event):
        """If an item was clicked, trigger mode to drag it.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONDOWN
               type)
            We use it to retrieve the mouse position when
            the mouse left button is pressed; it is also
            required in order to comply w/ the protocol used;

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve the mouse postion
        mouse_pos = event.pos

        ### iterate over items

        for item in chain(
            self.items,
            self.available_items,
        ):

            ## if there's a collision, break out of
            ## the current "for loop"

            if item.rect.collidepoint(mouse_pos):
                break

        ### if we didn't break out of the "for loop", it
        ### means we didn't collide with any items, so
        ### we can exit the method by returning
        else:
            return

        ### otherwise, we have hit an item, so we enable
        ### the drag mode passing the references to both
        ### the list and the item which collided with the
        ### mouse

        collection = self.items if item in self.items else self.available_items

        self.enable_drag_mode(collection, item)

    def handle_keyboard_input(self):
        """Act according to the keys' pressed state."""
        ### retrieve a list whose values represent the
        ### pressed state of the keys
        pressed_keys = get_pressed_keys()

        ### retrieve the state of keys representing the
        ### left and right scrolling actions

        scroll_left = any(pressed_keys[i] for i in (K_LEFT, K_a))

        scroll_right = any(pressed_keys[i] for i in (K_RIGHT, K_d))

        ### trigger the corresponding actions according to
        ### the states of the keys retrieved in the previous
        ### step

        if scroll_left and not scroll_right:
            self.scroll_left()

        elif scroll_right and not scroll_left:
            self.scroll_right()

    def scroll(self, speed):
        """Scroll items near the mouse horizontally.

        Parameters
        ==========
        speed (integer)
            amount of pixels to move the items left or right,
            according to signal of the integer.
        """
        ### get vertical position of mouse
        _, y = get_mouse_pos()

        ### pick list according to the area the mouse hovers

        a_list = (
            ## if the mouse is above the bottom of the
            ## items area, use the list of items
            self.items
            if y < self.items_area.bottom
            ## otherwise use the pool of available items
            else self.available_items
        )

        ### if the list has no items, there's no point in
        ### scrolling it, so we return
        if not a_list:
            return

        ### reference useful rects locally

        list_rect = a_list.rect
        scroll_boundary = self.rect.inflate(-40, 0)

        ### obtain a moved copy of the list rect
        moved_rect = list_rect.move(speed, 0)

        ### cancel the movement by returning if the
        ### moved copy of the list rect is beyond
        ### specific boundaries depending on the
        ### direction of the movement

        if speed < 0 and moved_rect.right < scroll_boundary.right:
            return

        elif speed > 0 and moved_rect.left > scroll_boundary.left:
            return

        ### if the movement wasn't cancelled in the previous
        ### step it means no boundaries were violated by
        ### the movement, so we can copy the horizontal
        ### position of the copy rect into the actual list
        ### rect
        list_rect.x = moved_rect.x

    scroll_left = partialmethod(scroll, -SCROLL_X_SPEED)
    scroll_right = partialmethod(scroll, SCROLL_X_SPEED)

    def drag_mode_handle_events(self):
        """Event handling for the drag mode."""
        for event in get_events():

            ### raise specific error if the user attempts
            ### to quit the app
            if event.type == QUIT:
                raise QuitAppException

            ### trigger mouse release action if mouse
            ### left button is released

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.perform_drag_mode_exit_setups()

    def drag_obj(self):
        """Center dragged object on mouse w/ an offset."""
        self.dragged_obj.rect.center = get_mouse_pos() + self.dragged_offset

    def enable_normal_mode(self):
        """Set normal mode behaviours and perform setups."""
        ### set GUD methods to behaviours that correspond
        ### the the normal mode

        self.handle_input = CallList(
            [self.normal_mode_handle_events, self.handle_keyboard_input]
        )

        self.update = empty_function
        self.draw = self.normal_mode_draw

        ### set the mouse visibility on
        set_mouse_visibility(True)

    def enable_drag_mode(self, collection, obj):
        """Set drag mode behaviours and perform setups.

        Parameters
        ==========
        collection (List2D instance)
            list of items containing the item to be
            dragged.
        obj (Object2D instance)
            item to be dragged.
        """
        ### set GUD methods to behaviours that correspond
        ### the the drag mode

        self.handle_input = CallList(
            [
                self.drag_mode_handle_events,
                self.handle_keyboard_input,
            ]
        )

        self.update = self.drag_obj
        self.draw = self.drag_mode_draw

        ### set the mouse visibility off
        set_mouse_visibility(False)

        ###

        if collection is self.items:

            ### find the index of the object to be dragged
            ### and pop it out of the list

            index = collection.index(obj)
            collection.pop(index)

            ### alias the obj as the dragged obj
            self.dragged_obj = obj

            ### if after the operation, the list still has
            ### objects, find the index of the object
            ### nearest to the one we just popped out
            ### and reposition the items of the list
            ### according to the position of that object

            if collection:

                clamped = max(min(len(collection) - 1, index), 0)

                nearest_obj = collection[clamped]

                self.reposition_list(
                    collection,
                    nearest_obj,
                )

            ### if dragged objects wasn't the first or last
            ### object in the list, move it a bit up, so
            ### isn't in front of the remaining objects
            ### (since, if there are those, they were
            ### realigned in the previous step and there
            ### should be gap between them left by the
            ### popped out object)
            if index not in (0, len(collection)):
                self.dragged_obj.rect.move_ip(0, -27)

        else:

            new_obj = Object2D.from_surface(
                surface=obj.image,
                value=obj.value,
            )

            new_obj.rect.center = obj.rect.center

            ### alias the new obj as the dragged obj
            self.dragged_obj = new_obj

        ### store the difference between the mouse position
        ### and the center of the object to be dragged
        ### across the screen

        self.dragged_offset = self.dragged_obj.rect.center - Vector2(get_mouse_pos())

    def perform_drag_mode_exit_setups(self):
        """Perform actions to conclude the dragging action."""
        ### reference the dragged object and its center y
        ### coordinate locally

        dragged_obj = self.dragged_obj
        _, centery = dragged_obj.rect.center

        ### pick a reference to list nearest to where the
        ### dragged object was dropped

        collection = (
            ## if the obj was above the bottom of the items
            ## area, then use the items list
            self.items
            if centery < self.items_area.bottom
            ## otherwise use the pool of available items
            else self.available_items
        )

        if collection is self.items:

            ### append the object to the list and sort the
            ### objects in the list according to the 'x'
            ### coordinate of their centers

            collection.append(dragged_obj)
            collection.sort(key=lambda item: item.rect.centerx)

            ### now align the objects in the list relative
            ### to one another based on the position of
            ### the dragged object
            self.reposition_list(collection, dragged_obj)

        ### finally enable the normal mode behaviours
        self.enable_normal_mode()

    def on_mouse_release(self, event):
        """Invoke a button if mouse hovers it when released.

        Parameters
        ==========
        event (pygame.event.Event of pygame.MOUSEBUTTONUP
               type)
            We use it to retrieve the mouse position when
            the mouse left button is released; it is also
            required in order to comply w/ the protocol used;

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### itertate over the buttons

        for button in self.buttons:

            ### if a button collided with the mouse,
            ### try retrieving the mouse release method,
            ### executing it if available, then break out
            ### of the "for loop"

            if button.rect.collidepoint(mouse_pos):

                try:
                    method = getattr(button, "on_mouse_release")

                except AttributeError:
                    pass

                else:
                    method()

                break

    def normal_mode_draw(self):
        """Draw operations for the normal mode."""
        ### reference objects/data locally for quick access

        image = self.image
        offset = self.offset
        rect = self.rect.inflate(-2, -2)

        ### clean the widget surface
        image.blit(self.clean_bg, (0, 0))

        ### draw buttons on the widget surface

        for button in self.buttons:

            image.blit(button.image, button.rect.move(offset))

        ### iterate over the lists of items, drawing the
        ### items on the widget surface

        for a_list in (self.items, self.available_items):

            for item in a_list.get_colliding(rect):

                image.blit(item.image, item.rect.move(offset))

        ### draw a border around the widget surface
        draw_border(image, thickness=2)

        ### draw the widget's surface on the screen
        super().draw()

        ### finally update the screen
        update()  # pygame.display.update

    def drag_mode_draw(self):
        """Draw operations for the drag mode."""
        ### reference objects/data locally for quick access

        image = self.image
        offset = self.offset
        rect = self.rect.inflate(-2, -2)

        ### clean the widget surface
        image.blit(self.clean_bg, (0, 0))

        ### draw buttons on the widget surface

        for button in self.buttons:

            image.blit(button.image, button.rect.move(offset))

        ### iterate over the lists of items, drawing the
        ### items and additional vertical lines around them
        ### on the widget surface

        for a_list in (self.items, self.available_items):

            for item in a_list.get_colliding(rect):

                offset_rect = item.rect.move(offset)
                image.blit(item.image, offset_rect)

                draw_vertical_lines(image, offset_rect)

        ### reference the dragged object locally and draw
        ### it in the widget surface if it collides with
        ### the widget, along with vertical lines and an
        ### outline around it

        dragged_obj = self.dragged_obj

        if rect.colliderect(dragged_obj.rect):

            offset_rect = dragged_obj.rect.move(offset)
            image.blit(dragged_obj.image, offset_rect)

            draw_vertical_lines(image, offset_rect)

            draw_rect(image, ITEM_OUTLINE, offset_rect.inflate(2, 2), 2)

        ### draw a border around the widget
        draw_border(image, thickness=2)

        ### draw the widget on the screen
        super().draw()

        ### finally update the screen
        update()  # pygame.display.update
