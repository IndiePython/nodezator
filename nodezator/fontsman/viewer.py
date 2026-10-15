"""Facility w/ class for visualizing fonts (characters)."""

### standard library imports

from pathlib import Path

from string import (
    ascii_uppercase,
    ascii_lowercase,
    digits,
    punctuation,
)

from functools import partial

from operator import attrgetter


### third-party imports

from pygame import Rect, error as PygameError

from pygame.locals import (

    QUIT,

    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,

    MOUSEBUTTONDOWN,

    K_a,
    K_s,
    K_d,
    K_w,

)

from pygame.font import Font, SysFont

from pygame.math import Vector2

from pygame.transform import smoothscale


### local imports

from ..config import APP_REFS

from ..pygamesetup import SCREEN_RECT, SERVICES_NS

from ..dialog import create_and_show_dialog

from ..logman.main import get_new_logger

from ..ourstdlibs.collections.general import FactoryDict

from ..our3rdlibs.userlogger import USER_LOGGER

from ..loopman.main import LoopHolder

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..surfsman.render import render_rect, combine_surfaces
from ..surfsman.draw import draw_border

from ..widget.intfloatentry.main import IntFloatEntry

from ..textman.render import render_text, render_multiline_text

from ..rectsman.main import RectsManager

from .constants import ENC_SANS_BOLD_FONT_PATH, SAMPLE_TEXT_MAP

from .cache import UnattainableFontHeightError



CHARS = ascii_uppercase + ascii_lowercase + digits + punctuation

### create logger for module
logger = get_new_logger(__name__)


GET_TOPLEFT = attrgetter('rect.topleft')


FONT_KEY_TEXT_SETTINGS = {
    'font_key': APP_REFS.mono_font_key,
    'font_height': APP_REFS.mono_font_height,
    'foreground_color': (0, 0, 0),
    'background_color': (180, 180, 180),
    'padding': 2,
}


TRANSLATIONS_MD_MESSAGE = ' '.join(
"""
Missing a preview for your language?
Check the TRANSLATIONS.md file to learn how to add one
""".strip().splitlines()
)


class FontsViewer(Object2D, LoopHolder):
    """Allows viewing characters from font file(s)."""

    def __init__(self):

        self.caption = caption = (

            Object2D.from_surface(

                render_text(
                    text='Fonts viewer',
                    padding=5,
                    foreground_color=(0, 0, 0),
                    background_color=(180, 180, 180),
                )

            )

        )

        self.index_entry = index_entry = (

            IntFloatEntry(
                value=0,
                min_value=0,
                loop_holder=self,
                numeric_classes_hint='int',
                command=self.update_previewed_font_from_entry,
                position_reference_getter=(partial(GET_TOPLEFT, self)),
                coordinates_name='midleft',
                coordinates_value=caption.rect.move(5, 0).midright,
            )

        )

        self.font_key_text_obj = font_key_text_obj = (

            Object2D.from_surface(

                surface=FONT_NAMES_SURF_MAP[ENC_SANS_BOLD_FONT_PATH],
                coordinates_name='topleft',
                coordinates_value=caption.rect.move(0, 10).bottomleft,

            )

        )

        self.viz_area = viz_area = Rect(0, 0, 1024, 600)

        viz_area.topleft = font_key_text_obj.rect.move(0, 10).bottomleft


        ###

        _rectsman = (

            RectsManager(

                (
                    caption.rect,
                    index_entry.rect,
                    font_key_text_obj.rect,
                    viz_area,

                ).__iter__

            )
        )

        ###
        _rectsman.center = SCREEN_RECT.center

        self.rect = _rectsman.inflate(10, 10)
        self.image = render_rect(*self.rect.size, (180, 180, 180))

        ###

        self.clean_image = self.image.copy()

        self.clean_viz_area_image = (
            render_rect(*self.viz_area.size, (200, 200, 200))
        )

        self.viz_panel = self.clean_viz_area_image.copy()

        ###
        self.font_obj_map = {}

        ###
        self.sample_text_objs = List2D()

        ### center font viewer and append centering method
        ### as a window resize setup

        self.center_font_viewer()

        APP_REFS.window_resize_setups.append(self.center_font_viewer)

        ### create translations.md message in English for users willing
        ### to help translate the app

        height = 17

        self.missing_lang_message_label = (

            Object2D.from_surface(
                render_text(
                    text=TRANSLATIONS_MD_MESSAGE,
                    font_height=height,
                    font_key=ENC_SANS_BOLD_FONT_PATH,
                )

            )

        )


    def center_font_viewer(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        self.offset = -Vector2(self.rect.topleft)

        if self.sample_text_objs:
            self.sample_text_objs.rect.move_ip(diff)

        for rect in (
            self.caption.rect,
            self.index_entry.rect,
            self.viz_area,
            self.font_key_text_obj.rect,
        ):
            rect.move_ip(diff)

    def update_previewed_font_from_entry(self):
        """Update visualization based on index from entry."""

        self.font_key = self.font_keys[self.index_entry.get()]
        self.update_visualization()

    def view_fonts(self, font_keys, index=0):

        ###

        self.font_keys = font_keys = (

            font_keys
            if not isinstance(font_keys, (str, Path))

            else [font_keys]

        )

        ###

        if any(
            isinstance(item, str) and not item
            for item in font_keys
        ):

            raise ValueError(
                "We can only preview fonts from paths to font files or"
                " names of system fonts, but at least one of the provided"
                " values is an empty string."
            )

        ###

        max_index = len(font_keys) - 1
        index = max(0, min(index, max_index))

        entry = self.index_entry
        entry.set_range(0, max_index)
        entry.set(index, False)

        self.font_key = font_key = font_keys[index]

        ### check paths

        self.font_obj_map.clear()

        font_class = Font if isinstance(font_key, Path) else SysFont

        try:

            self.font_obj_map.update(

                (
                    font_key,
                    font_class(font_key, 32),
                )

                for font_key in self.font_keys

            )

        except Exception as err:

            log_message = (
                "An error ocurred while trying to instantiate a font object"
                " for one of the given keys (the class used was pygame.font."
                f"{font_class.__name__})"
            )

            logger.exception(log_message)
            USER_LOGGER.exception(log_message)

            dialog_message = log_message + (
                " Check the user log for details (on the graph/canvas"
                " press <Ctrl+Shift+j> or access the \"Help > Show user log\""
                " option on the menubar)."
            )

            create_and_show_dialog(dialog_message, level_name='error')

            return

        ###
        self.update_visualization()

        ###
        self.loop()

    def update_visualization(self):

        font = self.font_obj_map[self.font_key]

        ###

        stos = self.sample_text_objs
        stos.clear()

        ###

        self.missing_lang_message_label.rect.topleft = (
            self.viz_area.move(2, 2).topleft
        )

        stos.append(self.missing_lang_message_label)

        ###

        topleft = self.missing_lang_message_label.rect.move(0, 10).bottomleft

        for locale_code, sample_text in SAMPLE_TEXT_MAP.items():

            locale2d = (

                Object2D.from_surface(

                    render_text(
                        text=locale_code,
                        font_height = 28,
                        font_key = ENC_SANS_BOLD_FONT_PATH,
                    )

                )

            )

            sample2d = (

                Object2D.from_surface(

                    render_text(
                        text=sample_text,
                        font_height = 28,
                        font_key = self.font_key
                    )

                )

            )

            locale2d.rect.topleft = topleft
            sample2d.rect.topleft = locale2d.rect.move(20, 0).bottomleft

            stos.extend((locale2d, sample2d))

            topleft = (
                locale2d.rect.left,
                sample2d.rect.move(0, 10).bottom,
            )


        ###

        ### update font key text obj

        font_key_text_obj = self.font_key_text_obj 

        font_key_text_obj.image = FONT_NAMES_SURF_MAP[self.font_key]
        font_key_text_obj.rect.size = font_key_text_obj.image.get_size()

        font_key_text_obj.rect.topleft = self.caption.rect.move(0, 10).bottomleft

    def handle_input(self):

        self.handle_events()
        self.handle_key_states()

    def handle_key_states(self):

        key_pressed_states = SERVICES_NS.get_pressed_keys()

        if key_pressed_states[K_a]:
            self.sample_text_objs.rect.move_ip(-20, 0)

        elif key_pressed_states[K_s]:
            self.sample_text_objs.rect.move_ip(0, 20)

        elif key_pressed_states[K_w]:
            self.sample_text_objs.rect.move_ip(0, -20)

        elif key_pressed_states[K_d]:
            self.sample_text_objs.rect.move_ip(20, 0)

    def handle_events(self):

        for event in SERVICES_NS.get_events():


            if event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.on_mouse_click(event)

            elif event.type == KEYUP:

                if event.key in (K_RETURN, K_KP_ENTER, K_ESCAPE):
                    self.running = False

            elif event.type == QUIT:
                self.quit()

    def on_mouse_click(self, event):
        """Delegete mouse click to entry if touches it."""

        if self.index_entry.rect.collidepoint(event.pos):
            self.index_entry.on_mouse_click(event)

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

        offset = self.offset

        image.blit(
            self.caption.image, 
            self.caption.rect.move(self.offset),
        )

        if len(self.font_keys) > 1:

            image.blit(
                self.index_entry.image, 
                self.index_entry.rect.move(self.offset),
            )

        ###

        viz_panel = self.viz_panel
        viz_panel.blit(self.clean_viz_area_image, (0, 0))

        rect_touches_viewer = self.viz_area.colliderect

        viz_offset = -Vector2(self.viz_area.topleft)

        for obj in self.sample_text_objs:

            if rect_touches_viewer(obj.rect):
                viz_panel.blit(obj.image, obj.rect.move(viz_offset))

        ###
        image.blit(viz_panel, self.viz_area.move(offset))

        ###

        image.blit(
            self.font_key_text_obj.image, 
            self.font_key_text_obj.rect.move(self.offset),
        )

        ###
        draw_border(image)
        ###
        super().draw()

        ### update screen
        SERVICES_NS.update_screen()



def _get_font_names_surf(font_key):

    text = font_key if isinstance(font_key, str) else font_key.name

    height = 22

    default_surf = render_text(
        text=text,
        font_height=height,
        font_key=ENC_SANS_BOLD_FONT_PATH,
    )

    custom_surf = _get_custom_font_text_surf(

        text,
        font_key,
        height,
        default_surf,

    )

    return (

        combine_surfaces(

            (default_surf, custom_surf),
            retrieve_pos_from='bottomright',
            assign_pos_to='topright',
            offset_pos_by=(0, 2),
            padding=2,
            background_color=(255, 255, 255),

        )

    )

FONT_NAMES_SURF_MAP = FactoryDict(_get_font_names_surf)


def _get_custom_font_text_surf(text, font_key, height, default_surf):

    try:

        current_font_text_surf = (

            render_text(
                text=text,
                font_height=height,
                font_key=font_key,
            )

        )

    except UnattainableFontHeightError as err:

        print(f"Suppressed error for {font_key!r}: {err}")

        final_surf = default_surf.copy()
        final_surf.fill('white')

        font_class = Font if isinstance(font_key, str) else SysFont

        try:

            surf = (
                font_class(font_key, height)
                .render(text, True, 'black', 'white')
                .convert()
            )

        except (PygameError, Exception) as err:

            print(
                "Another suppressed error for"
                f" {font_key!r}: {err}"
            )

            final_surf.fill('red')

        else:

            smoothscale(
                surf,
                default_surf.get_size(),
                final_surf,
            )

        current_font_text_surf = final_surf

    return current_font_text_surf


###
view_fonts = FontsViewer().view_fonts
