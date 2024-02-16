"""Operations for images viewer normal mode."""

### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### third-party imports

from pygame.locals import (
    QUIT,
    KEYDOWN,
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
    K_f,
    K_PAGEUP,
    K_PAGEDOWN,
    K_HOME,
    K_END,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from pygame.math import Vector2

from pygame.draw import rect as draw_rect


### local imports

from ...pygamesetup import SERVICES_NS

from ...dialog import create_and_show_dialog

from ...surfsman.draw import (
    draw_border,
    draw_border_on_area,
)

from ...surfsman.cache import draw_cached_screen_state

from ...surfsman.viewer.main import view_surface

from ...classes2d.single import Object2D

from ...loopman.exception import QuitAppException

from ...colorsman.colors import IMAGES_PREVIEWER_BORDER

from ..cache import IMAGE_SURFS_DB

from .constants import PREVIEWER_BORDER_THICKNESS, LARGE_THUMB, PATH_LABEL



class PreviewerOperations(Object2D):

    def prepare(self):
        """"""
        draw_cached_screen_state()
        self.response_draw()

    def handle_input(self):

        for event in SERVICES_NS.get_events():

            if event.type == QUIT:
                raise QuitAppException()

            elif event.type == KEYDOWN:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.running = False

                elif event.key in (K_UP, K_LEFT, K_h, K_k, K_w, K_a):
                    self.go_left()

                elif event.key in (K_DOWN, K_RIGHT, K_j, K_l, K_s, K_d):
                    self.go_right()

                elif event.key == K_PAGEUP:
                    self.go_many_left()

                elif event.key == K_PAGEDOWN:
                    self.go_many_right()

                elif event.key == K_HOME:
                    self.go_to_first()

                elif event.key == K_END:
                    self.go_to_last()

                elif event.key == K_f:
                    self.try_visualizing_full_image()

            elif event.type == MOUSEBUTTONUP:
                self.on_mouse_release(event)

            elif event.type == MOUSEMOTION:
                self.on_mouse_motion(event)

    def browse_thumbs(self, steps):
        """"""
        last_index = len(self.image_paths) - 1

        self.thumb_index = min(max(0, self.thumb_index + steps), last_index)

        ###
        thumb_rect = self.thumb_objects[self.thumb_index].rect

        clamped_rect = thumb_rect.clamp(self.rect)

        if clamped_rect != thumb_rect:

            x_difference = clamped_rect.x - thumb_rect.x
            self.thumb_objects.rect.move_ip(x_difference, 0)

        ###
        self.response_draw()

    go_right = partialmethod(browse_thumbs, 1)
    go_left = partialmethod(browse_thumbs, -1)

    go_many_right = partialmethod(browse_thumbs, 4)
    go_many_left = partialmethod(browse_thumbs, -4)

    go_to_last = partialmethod(browse_thumbs, INFINITY)
    go_to_first = partialmethod(browse_thumbs, -INFINITY)

    def try_visualizing_full_image(self):

        image_path = self.image_paths[self.thumb_index]

        try:
            full_image_surface = (
                IMAGE_SURFS_DB[image_path]
                [{
                    "use_alpha": True,
                    "checkered_alpha": True,
                    "not_found_width": 300,
                    "not_found_height": 300,
                }]
            )

        except FileNotFoundError:

            create_and_show_dialog(
                "Couldn't find the image",
                level_name='info',
            )

        else:
            view_surface(full_image_surface)
            self.response_draw()

    def on_mouse_release(self, event):
        """"""
        mouse_pos = event.pos
        rect = self.rect

        if not rect.collidepoint(mouse_pos):
            self.running = False
            return

        for index, obj in enumerate(self.thumb_objects):

            thumb_rect = obj.rect

            if not (
                thumb_rect.colliderect(rect) and thumb_rect.collidepoint(mouse_pos)
            ):
                continue

            clamped_rect = thumb_rect.clamp(rect)
            x_difference = clamped_rect.x - thumb_rect.x
            self.thumb_objects.rect.move_ip(x_difference, 0)
            self.thumb_index = index
            self.response_draw()

            break

    def on_mouse_motion(self, event):
        """"""
        mouse_pos = event.pos
        rect = self.rect

        current_hovered_index = self.hovered_index

        for index, obj in enumerate(self.thumb_objects):

            thumb_rect = obj.rect

            if not (
                thumb_rect.colliderect(rect) and thumb_rect.collidepoint(mouse_pos)
            ):
                continue

            new_hovered_index = index

            break

        else:
            new_hovered_index = None

        if new_hovered_index != current_hovered_index:

            self.hovered_index = new_hovered_index
            self.response_draw()

    def response_draw(self):
        """Redraw viewer in response to user action."""
        ###
        draw_cached_screen_state()

        ###
        image = self.image
        rect = self.rect

        image_path = self.image_paths[self.thumb_index]
        ###

        image.blit(self.background, (0, 0))

        ###

        LARGE_THUMB.change_image_path(image_path)
        LARGE_THUMB.draw_relative(self)

        ###

        negative_topleft = -Vector2(rect.topleft)

        thumb_index = self.thumb_index
        hovered_index = self.hovered_index

        for (index, thumb_obj) in enumerate(self.thumb_objects):

            thumb_rect = thumb_obj.rect

            if thumb_rect.colliderect(rect):

                offset_rect = thumb_rect.move(negative_topleft)

                image.blit(thumb_obj.image, offset_rect)

                if index == hovered_index:

                    draw_border_on_area(image, (0, 0, 0), offset_rect, 5)

                if index == thumb_index:

                    draw_border_on_area(image, (145, 145, 255), offset_rect, 5)

        ###

        PATH_LABEL.set(image_path)
        PATH_LABEL.draw_relative(self)

        ###

        draw_border(
            image, color=IMAGES_PREVIEWER_BORDER, thickness=PREVIEWER_BORDER_THICKNESS
        )

        super().draw()

    def draw(self):
        """Update screen."""
        SERVICES_NS.update_screen()
