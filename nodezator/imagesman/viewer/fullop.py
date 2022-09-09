"""Operations for images viewer full mode."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### third-party imports

from pygame import (
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
    K_f,
    K_r,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    MOUSEBUTTONDOWN,
)

from pygame.display import update

from pygame.event import get as get_events

from pygame.key import get_pressed as get_pressed_keys

from pygame.math import Vector2


### local imports

from ...pygameconstants import (
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

from ...colorsman.colors import IMAGES_VIEWER_BORDER

from ..cache import IMAGE_SURFS_DB

from .constants import VIEWER_BORDER_THICKNESS, LARGE_THUMB, PATH_LABEL


MOVE_AREA = SCREEN_RECT.inflate(-100, -100)


class FullModeOperations(Object2D):
    def full_prepare(self):
        """Redraw viewer in response to user action."""
        image_path = self.image_paths[self.thumb_index]

        self.full_image = IMAGE_SURFS_DB[image_path][{"use_alpha": True}]

        self.full_rect = self.full_image.get_rect()
        self.full_rect.center = MOVE_AREA.center

        self.full_response_draw()

    def full_handle_input(self):

        for event in get_events():

            ### TODO this will cause cleaning/tear down to
            ### skipped; address it, including the same
            ### behaviour occurring in other state managers

            if event.type == QUIT:
                raise QuitAppException()

            elif event.type == KEYDOWN:

                if event.key in (K_ESCAPE, K_f):
                    self.enable_normal_mode()

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

                    self.should_draw_full_rect = not self.should_draw_full_rect

                    self.full_response_draw()

            elif event.type == MOUSEBUTTONDOWN:
                self.full_on_mouse_click(event)

            elif event.type == MOUSEMOTION:
                self.full_on_mouse_motion(event)

            elif event.type == MOUSEBUTTONUP:
                self.full_on_mouse_release(event)

        ###

        keys_pressed_state = get_pressed_keys()

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
        rect = self.full_rect

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

        self.full_response_draw()

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
        rect = self.full_rect

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

        self.full_response_draw()

    ### TODO implement behaviours below

    def attempt_image_grabbing(self, event):
        """"""
        if self.full_rect.collidepoint(event.pos):
            self.should_move_with_mouse = True

    full_on_mouse_click = attempt_image_grabbing

    def attempt_moving_image(self, event):
        """"""
        if self.should_move_with_mouse:
            self.move_image(*event.rel)

    full_on_mouse_motion = attempt_moving_image

    def attempt_image_release(self, event):
        """"""
        self.should_move_with_mouse = False

    full_on_mouse_release = attempt_image_release

    def full_response_draw(self):
        """Draw in response to change/movement of image."""
        draw_cached_screen_state()

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        blit_on_screen(self.full_image, self.full_rect)

        if self.should_draw_full_rect:

            draw_border_on_area(SCREEN, (0, 0, 0), self.full_rect.inflate(8, 8), 4)

    def full_draw(self):
        """Update screen."""
        ### pygame.display.update()
        update()
