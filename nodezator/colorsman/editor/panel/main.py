"""Facility with panel class to display colors."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod

from collections import deque


### third-party imports

from pygame.math import Vector2

from pygame.draw import rect as draw_rect

from pygame.mouse import (
    get_pos as get_mouse_pos,
    get_pressed as get_mouse_pressed,
)


### local imports

from ....pygameconstants import SCREEN

from ....classes2d.single import Object2D
from ....classes2d.collections import List2D

from ....surfsman.draw import draw_border_on_area
from ....surfsman.render import render_rect

from ....surfsman.icon import render_layered_icon

from ...colors import BLACK, WINDOW_BG

from .constants import COLOR_WIDGET_SIZE

from .data import ImportExportOperations

from .colorsop import ColorsOperations


### module constants

SCROLL_SPEED_PX = 20
SCROLL_BUTTON_WIDTH = 20


### class definition


class ColorsPanel(
    ColorsOperations,
    ImportExportOperations,
    Object2D,
):
    """A panel to hold and display multiple colors."""

    def __init__(
        self,
        colors_editor,
        no_of_visible_colors,
    ):
        """Store editor and set image, rect and buttons.

        Parameters
        ==========

        colors_editor (custom class)
            instance of the colorman.editor.main.ColorsEditor
            class, a loop holder for editing multiple colors.
        no_of_visible_colors (integer)
            number of colors
        coordinates_name (string)
            name of a pygame.Rect attribute to which the
            coordinates_value must be assigned.
        coordinates_value (sequence with 2 integers)
            represents a position in 2d space which will
            be assigned to the coordinates named on the
            coordinates_name attribute.
        """
        ### store the colors editor reference
        self.colors_editor = colors_editor

        ### calculate the width of the panel

        width = (
            ## space for the color widgets
            (
                ## width of color widgets
                COLOR_WIDGET_SIZE[0]
                ## times the number of visible colors
                * no_of_visible_colors
            )
            ## plus space for the scroll buttons (number of
            ## pixels for 02 scroll buttons)
            + (2 * SCROLL_BUTTON_WIDTH)
        )

        ### the height is the same height as a color widget
        height = COLOR_WIDGET_SIZE[1]

        ### create a surface representing the background
        ### of the color, along with a copy of it, which
        ### you'll store so you can use to clean the
        ### original when needed

        self.image = render_rect(width, height, WINDOW_BG)

        self.clean_bg = self.image.copy()

        ### obtain a rect from the surface in self.image
        ### and position it relative to the editor

        self.rect = self.image.get_rect()

        self.rect.midtop = self.colors_editor.rect.move(0, 45).midtop

        ### finally create the scroll buttons
        self.create_scroll_buttons()

    def reposition_and_define_objects_and_values(self):

        self.rect.midtop = self.colors_editor.rect.move(0, 45).midtop

        ### store an offset whose value is the inverse of
        ### the topleft
        ###
        ### this will be used to blit other
        ### surface over self.image relative to the
        ### self.rect position
        self.offset = -Vector2(self.rect.topleft)

        ### create a scroll area equivalent to self.rect
        ### but deflate enough pixels horizontally so the
        ### scroll buttons are excluded from that area
        ###
        ### also store it after performing some admin
        ### tasks

        x_deflation = (SCROLL_BUTTON_WIDTH * 2) * -1
        scroll_area = self.rect.inflate(x_deflation, 0)

        if hasattr(self, "widgets"):

            delta = Vector2(scroll_area.topleft) - self.scroll_area.topleft

            self.widgets.rect.move_ip(delta)

        self.scroll_area = scroll_area

        attr_names = ("topleft", "topright")

        for attr_name, button in zip(attr_names, self.buttons):

            ## align the given coordinates of self.rect and
            ## the button's rect

            value = getattr(self.rect, attr_name)
            setattr(button.rect, attr_name, value)

    def create_scroll_buttons(self):
        """Create buttons to scroll the color widgets."""
        ### define width and height of scroll buttons

        button_width = self.rect.height
        button_height = SCROLL_BUTTON_WIDTH

        ### iterate over the buttons creation data
        ### instantiating and setting up the buttons

        self.buttons = List2D(
            Object2D.from_surface(
                render_layered_icon(
                    chars=[chr(82)],
                    dimension_name="height",
                    dimension_value=button_height - 8,
                    colors=[BLACK],
                    background_width=button_width,
                    background_height=button_height,
                    background_color=WINDOW_BG,
                    rotation_degrees=90,
                    flip_x=flip_x,
                    depth_finish_thickness=1,
                ),
                command=command,
            )
            for flip_x, command in (
                (False, self.scroll_left),
                (True, self.scroll_right),
            )
        )

        ## store buttons on their own attribute

        attr_names = (
            "left_scroll_button",
            "right_scroll_button",
        )

        for attr_name, button in zip(attr_names, self.buttons):
            setattr(self, attr_name, button)

    def scroll(self, amount):
        """Scroll color widgets according to given amount.

        Parameters
        ==========
        amount (integer)
            amount of pixels to scroll the color widgets
            left or right; the direction of the scrolling
            is given by the signal of the integer.
        """
        ### reference the widgets rect locally
        widgets_rect = self.widgets.rect

        ### rotate left
        ###
        ### that is, if amount is positive, move widgets
        ### to the right by adding to the left position
        ### of the widgets

        if amount > 0:

            ### reference the left of both the scroll area
            ### and the widget's rect locally

            current_left = widgets_rect.left
            area_left = self.scroll_area.left

            ### only rotate right if the current left
            ### position of the widget is at the left of
            ### the scroll area's left

            if current_left < area_left:

                ## even so, the value of left to be assigned
                ## mustn't surpass the left of the scroll
                ## area

                widgets_rect.left = min(current_left + amount, area_left)

        ### rotate right
        ###
        ### that is, if amount is negative, move widgets
        ### to the left by removing from the right position
        ### of the widgets

        elif amount < 0:

            ### reference the right of both the scroll area
            ### and the widget's rect locally

            current_right = widgets_rect.right
            area_right = self.scroll_area.right

            ### only rotate left if the current right
            ### position of the widget is at the right of
            ### the scroll area's right

            if current_right > area_right:

                ## even so, the value of right to be assigned
                ## mustn't never be below the value of the
                ## scroll area's right (that is, the right
                ## edge of the widgets must never be to the
                ## right of the scroll area's right edge)

                widgets_rect.right = max(current_right + amount, area_right)

    scroll_left = partialmethod(scroll, SCROLL_SPEED_PX)
    scroll_right = partialmethod(scroll, -SCROLL_SPEED_PX)

    def store_current_widget(self):
        """Store reference to the current selected widget."""
        ### reference the index of current color selected
        index = self.colors_editor.current_color_index

        ### reference the color widget which lies in that
        ### index in the list in self.widgets
        self.current_widget = self.widgets[index]

    def move_widget(self, amount):
        """Move current widget by number of given color slots.

        Parameters
        ==========
        amount (integer)
            number of color slots to jump left or right,
            depending on the signal.
        """
        ### retrieve current index
        index = self.colors_editor.current_color_index

        ### calculate and clamp new index to available
        ### indices

        new_index = index + amount

        new_index = min(max(0, new_index), len(self.widgets) - 1)

        ### if indices are the same, there's no point in
        ### moving the current widget
        if new_index == index:
            return

        ### from this point on, perform operations to move
        ### index

        ## define a slice object representing the slice
        ## of widgets affected by the change and whether
        ## we'll rotate such slice one position to the
        ## left or to the right (according to the signal
        ## of the rotation amount)

        elif index < new_index:

            slice_obj = slice(index, new_index + 1)
            rotation_amount = -1

        elif index > new_index:

            slice_obj = slice(new_index, index + 1)
            rotation_amount = 1

        ## this else clause should never be reached (at
        ## least given that both index and new_index are
        ## integer), so raise an error if such ever happens

        else:
            raise RuntimeError(
                "given the logic adopted, this block" " should never execute"
            )

        ## obtain a deque from that slice and store
        ## the positions of each widget in the slice

        slice_deque = deque(self.widgets[slice_obj])

        positions = [widget.rect.topleft for widget in slice_deque]

        ## rotate the slice in the desired direction,
        ## then update the position of each widget to
        ## the ones we stored

        slice_deque.rotate(rotation_amount)

        for widget, pos in zip(slice_deque, positions):
            widget.rect.topleft = pos

        ## then fit the widgets of the slice in their
        ## respective positions inside the widgets list
        self.widgets[slice_obj] = slice_deque

        ### finally, update the index of the current widget
        ### and store a reference to such widget

        self.colors_editor.current_color_index = new_index
        self.store_current_widget()

    widget_to_left = partialmethod(move_widget, -1)
    widget_to_right = partialmethod(move_widget, 1)

    def go_to_widget(self, steps):
        """Change current color widget to another.

        Parameters
        ==========
        steps (integer)
            number of steps from the current widget to the
            widget you want as the new current widget;
            whether the new current widget is after or
            before the actual current one is defined by
            the signal of this argument.
        """
        ### define index of new current widget by adding the
        ### index of the current widget with the given steps
        new_index = self.colors_editor.current_color_index + steps

        ### clamp the new index to the interval of existing
        ### indices
        clamped_index = max(min(new_index, len(self.widgets) - 1), 0)

        ### assign the clamped index as the current index
        self.colors_editor.current_color_index = clamped_index

        ### store a reference to the new color widget
        self.store_current_widget()

        ### set the color of the new color widget in the
        ### controls so the user can edit the fields from
        ### its actual values, if desired
        self.colors_editor.set_color_on_controls(self.current_widget.color)

        ### finally, if not already, bring color widget to
        ### visible area
        self.color_widget_to_visible_area()

    go_left = partialmethod(go_to_widget, -1)
    go_right = partialmethod(go_to_widget, 1)

    go_to_start = partialmethod(go_to_widget, -INFINITY)
    go_to_end = partialmethod(go_to_widget, INFINITY)

    def on_mouse_release(self, event):
        """Choose new color widget as current one if hovered.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event of pygame.MOUSEBUTTONUP type; its 'pos'
            attribute contains the position of the mouse
            when its left button was released, which in
            interpret here as a click (or rather, the end
            of a click).
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### reference the scroll area locally
        scroll_area = self.scroll_area

        ### return earlier if mouse isn't even inside the
        ### scroll area
        if not scroll_area.collidepoint(mouse_pos):
            return

        ### otherwise, check each color widget colliding with
        ### the scroll area, looking for the one hovered by
        ### the mouse (if there is one)

        for widget in self.widgets.get_colliding(scroll_area):

            ### if you find a color widget which collides
            ### with the mouse, make it the current color
            ### widget and break out of the "for loop"

            if widget.rect.collidepoint(mouse_pos):

                ## retrieve its index
                index = self.widgets.index(widget)

                ## define it as the index for the current
                ## color
                self.colors_editor.current_color_index = index

                ## store a reference to the
                ## new current widget (this one)
                self.store_current_widget()

                ## set the color of the new color widget in
                ## the controls so the user can edit the
                ## fields from its actual values, if desired
                self.colors_editor.set_color_on_controls(widget.color)

                break

    def update(self):
        """Check whether scroll buttons are being pressed."""
        ### if left mouse button is not pressed, exit method
        ### by returning earlier
        if not get_mouse_pressed()[0]:
            return

        ### otherwise retrieve the position of the mouse
        ### and execute the command of one of the scroll
        ### buttons in case the mouse is hovering one
        ### of them

        mouse_pos = get_mouse_pos()

        for button in self.buttons:

            if button.rect.collidepoint(mouse_pos):

                button.command()
                break

    def draw(self):
        """Draw this colors panel object."""
        ### reference relevant objects/data locally for
        ### easy and quick access

        image = self.image
        scroll_area = self.scroll_area
        offset = self.offset
        current_widget = self.current_widget

        ### clean the colors panel image
        image.blit(self.clean_bg, (0, 0))

        ### draw each color widget colliding with the
        ### scroll area in the colors panel image

        for widget in self.widgets.get_colliding(scroll_area):

            ## the widgets are drawn with an offset copy
            ## of their rects so they are draw in the
            ## right positions relative to the colors panel
            ## position

            image.blit(widget.image, widget.rect.move(offset))

        ### if the current widget collides with the scroll
        ### area, draw an outline on the colors panel image
        ### where the widget sits

        if current_widget.rect.colliderect(scroll_area):

            draw_border_on_area(
                image,
                current_widget.contrasting_color,
                current_widget.rect.move(offset),
                5,
            )

        ## draw each scroll button on the colors panel image

        for button in self.buttons:

            image.blit(button.image, button.rect.move(offset))

        ## finally, draw the colors panel image on the screen
        ## and draw a black outline around it

        super().draw()

        draw_rect(SCREEN, BLACK, self.rect.inflate(2, 2), 1)
