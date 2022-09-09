"""TextViewer class extension with routine operations."""

### standard library import
from math import inf as INFINITY


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_a,
    K_s,
    K_d,
    K_k,
    K_h,
    K_j,
    K_l,
    K_PAGEUP,
    K_PAGEDOWN,
    K_HOME,
    K_END,
    KMOD_SHIFT,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from pygame.display import update

from pygame.event import get as get_events

from pygame.key import (
    get_pressed as get_pressed_keys,
    get_mods as get_modifier_keys,
)


### local imports

from ...pygameconstants import (
    SCREEN_RECT,
    FPS,
    blit_on_screen,
    maintain_fps,
)

from ...our3rdlibs.behaviour import watch_window_size

from ...surfsman.draw import draw_border
from ...surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ...classes2d.single import Object2D

from ...loopman.exception import QuitAppException


### constants

## keys with the same purpose

UP_KEYS = K_UP, K_w, K_k
DOWN_KEYS = K_DOWN, K_s, K_j
LEFT_KEYS = K_LEFT, K_a, K_h
RIGHT_KEYS = K_RIGHT, K_d, K_l


### utility function


def within_height(rect_a, rect_b):
    """Return whether rect_a is within height of rect_b."""
    return rect_a.top >= rect_b.top and rect_a.bottom <= rect_b.bottom


### class definition


class Operations(Object2D):
    """Provides common methods to control and display text.

    This class is meant to be used as an extension of the
    TextViewer class.
    """

    def run(self):
        """Define and enter text viewer loop."""
        ### blit a semitransparent surface to in the canvas
        ### to increase constrast between the dialog and
        ### whatever is behind it

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ### loop until self.running is changed

        self.running = True

        while self.running:

            maintain_fps(FPS)

            watch_window_size()

            self.handle_input()

            self.draw()

        ### blit semitransparent obj

        ## over self.rect

        blit_on_screen(
            UNHIGHLIGHT_SURF_MAP[self.rect.size],
            self.rect.topleft,
        )

        ## over lineno panel if line numbers were shown

        if self.draw_lines == self.draw_lines_and_lineno:

            panel_rect = self.lineno_panel.rect

            blit_on_screen(
                UNHIGHLIGHT_SURF_MAP[panel_rect.size],
                panel_rect.topleft,
            )

        ### free memory from objects you won't use anymore
        self.free_up_memory()

    def handle_events(self):
        """Retrieve and respond to events."""
        for event in get_events():

            ### exit app by clicking the close button
            ### in the window
            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                ## exit the text viewer by releasing
                ## any of the following keys

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.running = False

                ## jump large amounts of pixels up or down
                ## (or scroll to top or bottom edge, when
                ## shift key is pressed)

                elif event.key == K_PAGEUP:

                    if event.mod & KMOD_SHIFT:
                        self.scroll(0, INFINITY)

                    else:
                        self.scroll(0, self.page_height)

                elif event.key == K_PAGEDOWN:

                    if event.mod & KMOD_SHIFT:
                        self.scroll(0, -INFINITY)

                    else:
                        self.scroll(0, -self.page_height)

                ## scroll to different edges of the text

                elif event.key == K_HOME:

                    if event.mod & KMOD_SHIFT:
                        self.scroll(0, INFINITY)

                    else:
                        self.scroll(INFINITY, 0)

                elif event.key == K_END:

                    if event.mod & KMOD_SHIFT:
                        self.scroll(0, -INFINITY)

                    else:
                        self.scroll(-INFINITY, 0)

            ### mouse button release/mousewheel

            elif event.type == MOUSEBUTTONUP:

                ## exiting the text viewer by clicking out
                ## of boundaries

                if event.button in (1, 3):

                    if not (self.scroll_area.collidepoint(event.pos)):
                        self.running = False

                ## scrolling with mousewheel

                elif event.button == 4:

                    if get_modifier_keys() & KMOD_SHIFT:
                        self.scroll(self.line_height, 0)

                    else:
                        self.scroll(0, self.line_height)

                elif event.button == 5:

                    if get_modifier_keys() & KMOD_SHIFT:
                        self.scroll(-self.line_height, 0)

                    else:
                        self.scroll(0, -self.line_height)

            ## mouse movement

            elif event.type == MOUSEMOTION:

                self.hovering_help_icon = self.help_icon.rect.collidepoint(event.pos)

    def handle_key_input(self):
        """Respond to inputs from keys."""
        ### retrieve input list
        input_list = get_pressed_keys()

        ### define actions based on state of specific keys

        scroll_up = any(map(input_list.__getitem__, UP_KEYS))

        scroll_down = any(map(input_list.__getitem__, DOWN_KEYS))

        scroll_left = any(map(input_list.__getitem__, LEFT_KEYS))

        scroll_right = any(map(input_list.__getitem__, RIGHT_KEYS))

        ### act according to the states of the actions

        if scroll_up and not scroll_down:
            self.scroll(0, self.line_height)

        elif scroll_down and not scroll_up:
            self.scroll(0, -self.line_height)

        if scroll_left and not scroll_right:
            self.scroll(self.line_height, 0)

        elif scroll_right and not scroll_left:
            self.scroll(-self.line_height, 0)

    def draw(self):
        """Draw on self.image, then draw it on screen."""
        ### reference image attribute in local variables
        image = self.image

        ### clean self.image
        image.blit(self.background, (0, 0))

        ### draw lines
        self.draw_lines()

        ### draw a border around self.image, then draw
        ### self.image on the screen

        draw_border(image, thickness=2)
        super().draw()

        ### execute drawing routine for caption and header

        self.caption_drawing_routine()
        self.header_drawing_routine()

        ### draw the help icon and, if it is hovered,
        ### the help text

        self.help_icon.draw()

        if self.hovering_help_icon:
            self.help_text_obj.draw()

        ### finally update the screen with
        ### pygame.display.update
        update()

    def draw_lines_only(self):
        """Draw the lines, without the line number."""
        ### reference attributes in local variables

        image = self.image
        offset = self.offset
        scroll_area = self.scroll_area

        ### for lines colliding with the scroll area,
        ### draw them on self.image

        for line in self.lines.get_colliding(scroll_area):

            image.blit(line.image, line.rect.topleft + offset)

    def draw_lines_and_lineno(self):
        """Draw lines on scroll area with line numbers."""
        ### draw lineno panel
        self.lineno_panel.draw()

        ### reference attributes in local variables

        image = self.image
        offset = self.offset
        scroll_area = self.scroll_area

        ### iterate over each line and its respective line
        ### number

        for lineno, line in enumerate(self.lines, start=1):

            ## reference the line's rect locally
            line_rect = line.rect

            ## if the line is along the height of the
            ## scroll area draw the line and then its
            ## line number;
            ##
            ## regarding collisions we cannot use
            ## pygame.Rect.colliderect here, because empty
            ## lines have a rect without width (even though
            ## they have height), making it so the rect
            ## has area 0 (zero) and rects with area 0 never
            ## collide;
            ##
            ## we also cannot use pygame.Rect.contains here,
            ## cause when the user scrolls further to
            ## the right because of a large line, smaller
            ## lines may be pulled outside the boundaries
            ## of the scroll area to the left, and since
            ## they would not be contained in the scrolling
            ## area, their line numbers would not be drawn
            ##
            ## this is why we use this special within_height
            ## function

            if within_height(line_rect, scroll_area):

                ## draw line with offset topleft
                image.blit(line.image, line.rect.topleft + offset)

                ## draw line number
                self.draw_lineno(str(lineno), line_rect.y)

    def draw_lineno(self, lineno, line_y):
        """Draw line number at the given y coordinate.

        Parameters
        ==========
        lineno (string)
            represents the line number.
        line_y (integer)
            y coordinate of the line; used as the y
            coordinate wherein to blit the line number.
        """
        ### use the right coordinate from where to blit line
        ### numbers from the last to the first character,
        ### from right to left, as the x coordinate
        line_x = self.lineno_right

        ### reference the width of a digit's surface locally
        digit_width = self.digit_surf_width

        ### reference the digit surf map locally
        surf_map = self.digits_surf_map

        ### iterate over digits, blitting each of them
        ### while updating the x coordinate so they
        ### are blitted one beside the other

        for digit in lineno[::-1]:

            blit_on_screen(surf_map[digit], (line_x, line_y))
            line_x -= digit_width

    def scroll(self, dx, dy):
        """Scroll lines, if possible.

        Parameters
        ==========

        dx, dy (integers)
            indicates amounts (deltas) of pixels to scroll
            in x and y axes; accepts negative integers to
            scroll in the opposite direction.

        How it works
        ============

        Scrolling can be seen as moving text inside
        the scrolling area in the opposite direction
        of that which we want to peek.

        So, for instance, if I want to see more of the
        bottom of the text, that is, if I want to
        scroll down, it means I need to move the text
        up. However, additional checks must be performed.

        First, we must check whether there is more text
        beyond the scrolling area in the direction we
        want to peek (the opposite we want to scroll).

        This is important because if there isn't, we
        shouldn't scroll at all, so we set the delta to
        0.

        Second, we must check whether the text in the
        direction we want to peek will end up too much
        inside the scroll area (instead of being just
        inside it).

        We perform such check and, if it is the case,
        instead of scrolling the full delta, we just
        scroll the amount of pixels enough to align the
        text with the scroll area in that side.
        """
        ### retrieve a union rect of all lines,
        ### representing the text
        text_rect = self.lines.rect.union_rect

        ### perform check depending on the direction the
        ### text will scroll

        ## text will go left, so we check the right side

        if dx < 0:

            if text_rect.right < self.scroll_area.right:
                dx = 0

            elif text_rect.right + dx < self.scroll_area.right:

                dx = self.scroll_area.right - text_rect.right

        ## text will go right, so we check the left side

        elif dx > 0:

            if text_rect.left > self.scroll_area.left:
                dx = 0

            elif text_rect.left + dx > self.scroll_area.left:
                dx = self.scroll_area.left - text_rect.left

        ## text will go up, so we check the bottom

        if dy < 0:

            if text_rect.bottom < self.scroll_area.bottom:
                dy = 0

            elif text_rect.bottom + dy < self.scroll_area.bottom:

                dy = self.scroll_area.bottom - text_rect.bottom

        ## text will go down, so we check the top

        elif dy > 0:

            if text_rect.top > self.scroll_area.top:
                dy = 0

            elif text_rect.top + dy > self.scroll_area.top:
                dy = self.scroll_area.top - text_rect.top

        ### move lines (moves the rect of each line)
        self.lines.rect.move_ip(dx, dy)

    def free_up_memory(self):
        """Free up memory by removing unused text objects."""
        ### clear self.lines to free the memory taken by
        ### the line objects (specially their surfaces)
        self.lines.clear()
