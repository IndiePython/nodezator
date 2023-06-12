"""Operations for surface viewer."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### third-party imports

from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE,
    KMOD_SHIFT,
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
    K_r,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    MOUSEBUTTONDOWN,
)

from pygame.math import Vector2


### local imports

from ...pygamesetup import (
    SERVICES_NS,
    SCREEN,
    SCREEN_RECT,
    blit_on_screen,
)

from ...surfsman.draw import draw_border_on_area

from ...classes2d.single import Object2D

from ...loopman.exception import QuitAppException

from ...surfsman.cache import (
    UNHIGHLIGHT_SURF_MAP,
    draw_cached_screen_state,
)

from ...our3rdlibs.keyconst import KEYPAD_TO_COORDINATE_MAP

from .constants import MOVE_AREA



class ViewerOperations(Object2D):

    def handle_input(self):

        for event in SERVICES_NS.get_events():

            ### TODO this will cause cleaning/tear down to
            ### be skipped; address it, including the same
            ### behaviour occurring in other state managers

            if event.type == QUIT:
                raise QuitAppException()

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    self.running = False

                elif event.key == K_HOME:

                    if event.mod & KMOD_SHIFT:
                        self.move_to_left_edge()

                    else:
                        self.move_to_top()

                elif event.key == K_END:

                    if event.mod & KMOD_SHIFT:
                        self.move_to_right_edge()

                    else:
                        self.move_to_bottom()

                elif event.key == K_PAGEUP:

                    if event.mod & KMOD_SHIFT:
                        self.move_right_a_lot()

                    else:
                        self.move_down_a_lot()

                elif event.key == K_PAGEDOWN:

                    if event.mod & KMOD_SHIFT:
                        self.move_left_a_lot()

                    else:
                        self.move_up_a_lot()

                ###

                elif event.key in KEYPAD_TO_COORDINATE_MAP:

                    self.snap_image(KEYPAD_TO_COORDINATE_MAP[event.key])

                elif event.key == K_r:

                    self.should_draw_rect = not self.should_draw_rect

                    self.response_draw()

            elif event.type == MOUSEBUTTONDOWN:
                self.on_mouse_click(event)

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event)

            elif event.type == MOUSEBUTTONUP:
                self.on_mouse_release(event)

        ###

        keys_pressed_state = SERVICES_NS.get_pressed_keys()

        dx = dy = 0

        for keys, (x_amount, y_amount) in (
            ((K_UP, K_k, K_w), (0, 10)),
            ((K_DOWN, K_j, K_s), (0, -10)),
            ((K_LEFT, K_h, K_a), (10, 0)),
            ((K_RIGHT, K_l, K_d), (-10, 0)),
        ):

            for key in keys:

                if keys_pressed_state[key]:

                    dx += x_amount
                    dy += y_amount

                    break

        self.move_image(dx, dy)

    def move_image(self, dx, dy):
        """Move image."""
        rect = self.rect

        if rect.width <= MOVE_AREA.width:
            dx = 0

        else:

            if dx < 0:
                dx = max(dx, MOVE_AREA.right - rect.right)

            elif dx > 0:
                dx = min(dx, MOVE_AREA.left - rect.left)

        if rect.height <= MOVE_AREA.height:
            dy = 0

        else:

            if dy < 0:
                dy = max(dy, MOVE_AREA.bottom - rect.bottom)

            elif dy > 0:
                dy = min(dy, MOVE_AREA.top - rect.top)

        if dx or dy:
            rect.move_ip(dx, dy)
        else:
            return

        self.response_draw()

    move_up = partialmethod(move_image, 0, -10)
    move_down = partialmethod(move_image, 0, 10)
    move_left = partialmethod(move_image, -10, 0)
    move_right = partialmethod(move_image, 10, 0)

    move_up_a_lot = partialmethod(move_image, 0, -MOVE_AREA.height)
    move_down_a_lot = partialmethod(move_image, 0, MOVE_AREA.height)
    move_left_a_lot = partialmethod(move_image, -MOVE_AREA.width, 0)
    move_right_a_lot = partialmethod(move_image, MOVE_AREA.width, 0)

    move_to_top = partialmethod(move_image, 0, INFINITY)
    move_to_bottom = partialmethod(move_image, 0, -INFINITY)

    move_to_left_edge = partialmethod(move_image, -INFINITY, 0)

    move_to_right_edge = partialmethod(move_image, INFINITY, 0)

    def snap_image(self, coordinate_name):
        """Snap image by align it with the moving area."""
        rect = self.rect

        current_pos = getattr(rect, coordinate_name)

        pos = getattr(MOVE_AREA, coordinate_name)

        dx, dy = pos - Vector2(current_pos)

        if rect.width <= MOVE_AREA.width:
            dx = 0

        else:

            if dx < 0:
                dx = max(dx, MOVE_AREA.right - rect.right)

            elif dx > 0:
                dx = min(dx, MOVE_AREA.left - rect.left)

        if rect.height <= MOVE_AREA.height:
            dy = 0

        else:

            if dy < 0:
                dy = max(dy, MOVE_AREA.bottom - rect.bottom)

            elif dy > 0:
                dy = min(dy, MOVE_AREA.top - rect.top)

        if dx or dy:
            rect.move_ip(dx, dy)
        else:
            return

        self.response_draw()


    def attempt_image_grabbing(self, event):
        """"""
        if self.rect.collidepoint(event.pos):
            self.should_move_with_mouse = True

    on_mouse_click = attempt_image_grabbing

    def attempt_moving_image(self, event):
        """"""
        if self.should_move_with_mouse:
            self.move_image(*event.rel)

    on_mouse_motion = attempt_moving_image

    def attempt_image_release(self, event):
        """"""
        self.should_move_with_mouse = False

    on_mouse_release = attempt_image_release

    def response_draw(self):
        """Draw in response to change/movement of image."""
        draw_cached_screen_state()

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        super().draw()

        if self.should_draw_rect:
            draw_border_on_area(SCREEN, (0, 0, 0), self.rect.inflate(8, 8), 4)

    def draw(self):
        """Update screen."""
        SERVICES_NS.update_screen()
