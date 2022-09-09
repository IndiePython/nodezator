"""Colors viewer extension for the color list mode."""

### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_w,
    K_UP,
    K_s,
    K_DOWN,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events

from pygame.display import update

from pygame.math import Vector2

from pygame.key import get_pressed as get_pressed_keys


### local imports

from ....pygameconstants import blit_on_screen

from ....ourstdlibs.color.conversion import (
    full_rgb_to_html_name,
    full_rgb_to_hex_string,
)

from ....classes2d.single import Object2D
from ....classes2d.collections import List2D

from ....loopman.exception import QuitAppException

from ....surfsman.draw import draw_border
from ....surfsman.render import render_rect

from ....textman.render import render_text

from ....fontsman.constants import ENC_SANS_BOLD_FONT_HEIGHT

from ...colors import (
    COLOR_VIEWER_COLOR_LIST_FG,
    COLOR_VIEWER_COLOR_LIST_BG,
)

from ...color2d import Color2D


### size in pixels of the surfaces representing each color
COLOR_SIZE = (120, 84)


### class definition (class extension)


class ColorListMode:
    """Has operations to show colors in a list.

    Such list has the form of a column. In such column
    the colors area displayed one by one with the
    values of each of their channels as well as the
    hex value for the color and its html name, if it
    haso one.
    """

    def color_list_prepare_mode(self):
        """Setups to execute before starting the mode."""
        ### check the existence of a 'color_list_colors'
        ### attribute
        try:
            self.color_list_colors

        ### if such attribute doesn't exist, execute a
        ### method to create such list and the related
        ### color widgets
        except AttributeError:
            self.create_color_list()

        ### the same method should be used in case the
        ### attribute exists but it is different from the
        ### value in the 'colors' attribute, in which case
        ### the 'colors' is assigned to 'color_list_colors'
        ### and related color widgets are recreated

        else:

            if self.colors != self.color_list_colors:
                self.create_color_list()

    def create_color_list(self):
        """(Re)create widgets representing the colors."""
        ### store a reference to the list from the 'colors'
        ### attribute in the 'color_list_colors' attribute
        ### and also reference said list locally
        colors = self.color_list_colors = self.colors

        ### create a new custom list for color widgets,
        ### storing it in its own attribute but also
        ### referencing it locally
        color_list_objs = self.color_list_objs = List2D()

        ### define a topleft next to the topleft of self.rect,
        ### but way to the right and a bit lower
        topleft = self.rect.move(200, 70).topleft

        ### create widgets representing each color, always
        ### storing them in the custom list we created

        for color in colors:

            ## create and store widget which is a surface
            ## filled with the color being represented

            color_widget = Color2D(*COLOR_SIZE, color)
            color_widget.rect.topleft = topleft

            color_list_objs.append(color_widget)

            ## create and store text objects displaying
            ## different representations of the color

            # start from the a topleft defined close to
            # the topright of the color widget
            topleft = color_widget.rect.move(5, 8).topright

            # iterate over color representations

            for text in (
                # integers in range(256) representing values
                # of the RGB(A) channels
                repr(color),
                # a hex string (string starting with '#'
                # followed by substrings representing the
                # values of RGB(A) channels in range(256),
                # but representing in hexadecimal numbers;
                # for instance: #ffffff for white color)
                full_rgb_to_hex_string(color),
                # the name of the color used by HTML or
                # 'unamed' if it doesn't have a name
                full_rgb_to_html_name(color),
            ):

                # create and append the text object

                text_obj = Object2D.from_surface(
                    surface=render_text(
                        text=text,
                        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
                        foreground_color=(COLOR_VIEWER_COLOR_LIST_FG),
                        background_color=(COLOR_VIEWER_COLOR_LIST_BG),
                    ),
                    coordinates_name="topleft",
                    coordinates_value=topleft,
                )

                color_list_objs.append(text_obj)

                # the next text object should have its
                # topleft a bit bellow the current object's
                # bottomleft
                topleft = text_obj.rect.move(0, 5).bottomleft

            ## update the topleft so the next color widget
            ## have its topleft aligned with the bottomleft
            ## of the current color widget
            topleft = color_widget.rect.bottomleft

        ### create panel over which to draw the objects
        ### in the list

        ## define an area wherein to display the list
        ## of widgets; this area is obtained by deflating
        ## self.rect
        display_area = self.rect.inflate(-500, -40)

        ## also reference the 'rect' attribute of the list
        ## of widgets locally; this is a special rect-like
        ## object which we can use to control all the rects
        ## in the list
        color_list_rect = self.color_list_objs.rect

        ## align the widgets midtop with the midtop of the
        ## display area, slightly moving them down
        color_list_rect.midtop = display_area.move(0, 10).midtop

        ## redefine the height of the display area if the
        ## bottom of the widgets, if they were lowered 10
        ## pixels (for padding), would still stand above
        ## the display area's bottom

        # obtain the highest bottom between the display area
        # and widgets, considering the widgets as if they
        # were 10 pixels below the current position

        highest_bottom = min(display_area.bottom, color_list_rect.bottom + 10)

        # update the display area's height to the difference
        # between the highest bottom previously calculated
        # and its top
        display_area.height = highest_bottom - display_area.top

        ## finally create an object representing the display
        ## area defined previously and copy its surface
        ## from its 'image' attribute so we can use it to
        ## clean the surface when scroling the objects

        self.color_list_bg = Object2D.from_surface(
            surface=render_rect(
                *display_area.size,
                COLOR_VIEWER_COLOR_LIST_BG,
            ),
            coordinates_name="topleft",
            coordinates_value=display_area.topleft,
        )

        self.color_list_clean = self.color_list_bg.image.copy()

    def color_list_event_handling(self):
        """Event handling for the color list mode."""
        for event in get_events():
            ### raise specific exception if user tries to
            ### quit the application

            if event.type == QUIT:
                raise QuitAppException

            ### trigger exiting the color viewer by setting
            ### 'running' flag to False if one of following
            ### keys is released

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.running = False

            ### if a mouse button is released...

            elif event.type == MOUSEBUTTONUP:

                ## if it is the left button, execute
                ## specific mouse action method

                if event.button == 1:
                    self.color_list_on_mouse_release(event)

                ## if it is the mouse wheel being
                ## scrolled, scroll the list up or down

                elif event.button == 4:
                    self.scroll_color_list(40)

                elif event.button == 5:
                    self.scroll_color_list(-40)

    def color_list_keyboard_input_handling(self):
        """Keyboard input handling for the color list mode."""
        ### get a list of booleans representing flags for
        ### whether specific buttons are pressed or not
        pressed_keys = get_pressed_keys()

        ### calculate whether we should scroll based on the
        ### state of specific buttons

        should_scroll = (
            ## whether a key to go up was pressed
            any(pressed_keys[i] for i in (K_w, K_UP))
            ## minus whether a key to go down was pressed
            - any(pressed_keys[i] for i in (K_s, K_DOWN))
        )

        ### if should_scroll is truthy (different than 0),
        ### it will be either 1 or -1, which indicates
        ### a direction to which to scroll;
        ### if such is the case, multiply the value by 20,
        ### scrolling by the resulting amount

        if should_scroll:
            self.scroll_color_list(should_scroll * 20)

    def scroll_color_list(self, amount):
        """Scroll widgets representing the list of colors.

        The way this method works makes it so the widgets
        return the their initial position if there's no
        widget out of the boundaries of the color list
        background object.

        This way the widgets or at least part of it are
        always visible.
        """
        ### XXX rect for boundary checking below should
        ### probably be stored, instead of being created
        ### every time we scroll

        ### define rect used for boundary checking
        bg_rect = self.color_list_bg.rect.inflate(0, -20)

        ### retrieve rect used to read and control the
        ### position of widgets
        objs_rect = self.color_list_objs.rect

        ### move widgets
        objs_rect.move_ip(0, amount)

        ### if scrolling up, don't allow the top of widgets
        ### to go above the top of the background area

        if amount > 0:

            ## if the top of widgets goes above the top
            ## of the background, set the top of the widgets
            ## to the top of the background
            if objs_rect.top > bg_rect.top:
                objs_rect.top = bg_rect.top

        ### if scrolling down, don't allow the bottom of
        ### widgets to go below the bottom of the background
        ### area

        elif amount < 0:

            ## if the bottom of widgets goes below the
            ## bottom of the background, set the bottom of
            ## the widgets to the bottom of the background

            if objs_rect.bottom < bg_rect.bottom:
                objs_rect.bottom = bg_rect.bottom

    def color_list_on_mouse_release(self, event):
        """Trigger exiting colors viewer or invoke button.

        Parameters
        ==========
        event (pygame.event.Event instance)
            event of type MOUSEBUTTONUP; its 'pos' attribute
            contains a tuple with two integers and represents
            the position of the mouse on the screen;

            check the glossary entry for the "mouse action
            protocol".
        """
        ### retrieve the position of the mouse
        mouse_pos = event.pos

        ### if the mouse is out of the area occupied by
        ### the color viewer, trigger exiting the color
        ### viewer by turning the 'running' flag off and
        ### exiting the method by returning

        if not self.rect.collidepoint(event.pos):
            self.running = False
            return

        ### if we don't return in the previous block, we
        ### look for the first button which collides with
        ### the mouse

        for button in self.buttons:

            ## if a button collides, execute its mouse
            ## release action if it has one, then break out
            ## of the "for loop"

            if button.rect.collidepoint(mouse_pos):

                try:
                    method = getattr(button, "on_mouse_release")

                except AttributeError:
                    pass

                else:
                    method(event)

                break

    def color_list_draw(self):
        """Drawing operation for the color list mode."""
        ### draw the background of the colors viewer in
        ### the screen
        blit_on_screen(self.image, self.rect)

        ### draw the labels and buttons on the screen

        self.labels.draw()
        self.buttons.draw()

        ### reference useful objects locally

        ## the surface and rect of the color list background

        bg_image = self.color_list_bg.image
        bg_rect = self.color_list_bg.rect

        ## an offset equivalent to the opposite of the
        ## topleft coordinate of the background rect
        offset = -Vector2(bg_rect.topleft)

        ### clean the color list background
        bg_image.blit(self.color_list_clean, (0, 0))

        ### draw each object from the list of color objects
        ### which collide with the background rect on the
        ### background surface
        ###
        ### the objects must be drawn as though the offset
        ### were applied to their rects (by using copies
        ### of their rects obtained from pygame.Rect.move
        ### with the offset as the sole argument)

        for obj in self.color_list_objs.get_colliding(bg_rect):

            bg_image.blit(obj.image, obj.rect.move(offset))

        ### draw a border around the color list background
        draw_border(bg_image, thickness=2)

        ### now that all the color objects were drawn on
        ### the color list background, draw the background
        ### itself on the screen
        self.color_list_bg.draw()

        ### and finally update the screen
        update()  # pygame.display.update

    def color_list_free_up_memory(self):
        """Clear objects/delete references to free memory."""
        ### Clear the list of color-related objects.
        ###
        ### by default, entering the colors viewer for the
        ### first time will always land in the color list
        ### mode, which will trigger the creation of this
        ### list;
        ###
        ### however, in the case we ever decide to make
        ### another mode the default one, the list wouldn't
        ### exist when this clearing operation is attempted,
        ### so we wrap it in a try/except clause to guard
        ### against AttributeErrors

        try:
            self.color_list_objs.clear()
        except AttributeError:
            pass

        ### also delete the attribute referencing the
        ### list of colors being displayed
        ###
        ### this doesn't save much memory, but forces the
        ### color-related objects to be created again
        ### the next time the user enter the colors viewer;
        ###
        ### it is necessary to guard the statement against
        ### AttributeError here because let's suppose the
        ### user enters the colors viewer, then leaves with
        ### another mode on; the next time the user enters,
        ### the color list mode may not be visited again,
        ### which will make it so this attribute won't be
        ### created, so, when the user leaves again and
        ### we try to delete this attribute, this would
        ### raise an AttributeError since the attribute
        ### wouldn't exist

        try:
            del self.color_list_colors
        except AttributeError:
            pass
