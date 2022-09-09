"""Facility w/ class for visualizing fonts (characters)."""

### standard library imports

from string import (
    ascii_uppercase,
    ascii_lowercase,
    digits,
    punctuation,
)


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_a,
    K_s,
    K_d,
    K_w,
)

from pygame.event import get as get_events

from pygame.key import get_pressed as get_pressed_keys

from pygame.display import update

from pygame.font import Font

from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygameconstants import SCREEN_RECT

from ...dialog import create_and_show_dialog

from ...logman.main import get_new_logger

from ...our3rdlibs.userlogger import USER_LOGGER

from ...loopman.main import LoopHolder

from ...classes2d.single import Object2D

from ...classes2d.collections import List2D

from ...surfsman.render import render_rect

from .render import render_char_info


CHARS = ascii_uppercase + ascii_lowercase + digits + punctuation

### create logger for module
logger = get_new_logger(__name__)


class FontsViewer(Object2D, LoopHolder):
    """Allows viewing characters from font file(s)."""

    def __init__(self):

        self.image = render_rect(800, 600, (180, 180, 180))

        self.clean_image = self.image.copy()

        # draw_border(self.image, thickness=2)

        self.rect = self.image.get_rect()

        ###
        self.font_obj_map = {}

        ### center font viewer and append centering method
        ### as a window resize setup

        self.center_font_viewer()

        APP_REFS.window_resize_setups.append(self.center_font_viewer)

    def center_font_viewer(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        self.offset = -Vector2(self.rect.topleft)

        try:
            self.char_objs
        except AttributeError:
            pass
        else:
            self.char_objs.rect.move_ip(diff)

    def view_fonts(self, font_paths, index=0):

        ###

        font_paths = [font_paths] if isinstance(font_paths, str) else font_paths

        self.font_paths = font_paths
        self.font_path = font_paths[0]

        max_index = len(font_paths) - 1
        index = max(0, min(index, max_index))

        ### check paths

        self.font_obj_map.clear()

        try:

            self.font_obj_map.update(
                (font_path, Font(font_path, 32)) for font_path in self.font_paths
            )

        except Exception as err:

            msg = str(err)

            logger.exception(msg)
            USER_LOGGER.exception(msg)

            create_and_show_dialog(
                (
                    "An error ocurred while trying to"
                    " generate visualization for one of"
                    " the fonts. Check the user log for"
                    " details (click <Ctrl+Shift+J> after"
                    " leaving this dialog)."
                ),
                level_name="error",
            )

            return

        ###
        self.prepare()

        ###
        self.loop()

    def prepare(self):

        font = self.font_obj_map[self.font_path]

        self.char_objs = List2D(
            Object2D.from_surface(render_char_info(char, font)) for char in CHARS
        )

        self.char_objs.rect.lay_rects_like_table_ip(
            dimension_name="width",
            dimension_unit="pixels",
            max_dimension_value=780,
            cell_padding=5,
        )

        self.char_objs.rect.topleft = self.rect.move(10, 10).topleft

    def handle_input(self):

        self.handle_events()
        self.handle_key_states()

    def handle_key_states(self):

        key_pressed_states = get_pressed_keys()

        if key_pressed_states[K_a]:
            self.char_objs.rect.move_ip(-20, 0)

        elif key_pressed_states[K_s]:
            self.char_objs.rect.move_ip(0, 20)

        elif key_pressed_states[K_w]:
            self.char_objs.rect.move_ip(0, -20)

        elif key_pressed_states[K_d]:
            self.char_objs.rect.move_ip(20, 0)

    def handle_events(self):

        for event in get_events():

            if event.type == QUIT:
                self.quit()

            elif event.type == KEYUP:

                if event.key in (K_RETURN, K_KP_ENTER, K_ESCAPE):
                    self.running = False

    ### TODO create methods to automatically
    ### scroll objects within an scroll area
    ### in the RectsManager class;
    ###
    ### make sure classes2d/collections.py
    ### has a suitable way to draw objects
    ### in such arrangement (within a scroll
    ### area); maybe a thourough review of
    ### classesman/collections.py is needed;

    def draw(self):

        image = self.image
        image.blit(self.clean_image, (0, 0))

        rect_touches_viewer = self.rect.colliderect

        offset = self.offset

        for obj in self.char_objs:

            if rect_touches_viewer(obj.rect):

                image.blit(obj.image, obj.rect.move(offset))

        super().draw()

        ### update screen: pygame.display.udpate()
        update()


view_fonts = FontsViewer().view_fonts
