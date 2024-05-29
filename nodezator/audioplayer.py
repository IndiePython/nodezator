### third-party imports

from pygame import Rect

from pygame.locals import (
    QUIT,
    KEYUP,
    K_SPACE,
    K_RETURN,
    K_KP_ENTER,
    K_ESCAPE,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

from pygame.draw import (
    rect as draw_rect,
    polygon as draw_polygon,
)

from pygame.math import Vector2

from pygame.mixer import music


### local imports

from .config import APP_REFS

from .pygamesetup import SERVICES_NS, SCREEN, SCREEN_RECT

from .dialog import create_and_show_dialog

from .logman.main import get_new_logger

from .ourstdlibs.behaviour import get_oblivious_callable

from .our3rdlibs.userlogger import USER_LOGGER

from .loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from .classes2d.single import Object2D

from .classes2d.surfaceswitcher import SURF_SWITCHER_CLASS_MAP

from .surfsman.draw import draw_border

from .surfsman.render import render_rect

from .surfsman.icon import render_layered_icon

from .textman.render import render_text

from .colorsman.colors import BLACK, WHITE

from .widget.intfloatentry.main import IntFloatEntry


PlayingPausedObject = SURF_SWITCHER_CLASS_MAP[frozenset(("playing", "paused"))]

PAUSED_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (81, 82)],
    dimension_name="height",
    dimension_value=18,
    colors=[BLACK, WHITE],
    rotation_degrees=-90,
    depth_finish_thickness=1,
    depth_finish_outset=True,
    background_width=24,
    background_height=24,
    background_color=(50, 50, 50),
)

PLAYING_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (75, 76)],
    dimension_name="height",
    dimension_value=18,
    colors=[BLACK, WHITE],
    depth_finish_thickness=1,
    depth_finish_outset=False,
    background_width=24,
    background_height=24,
    background_color=(50, 50, 50),
)


### create logger for module
logger = get_new_logger(__name__)


class AudioPlayer(Object2D):
    def __init__(self):
        """"""

        self.image = render_rect(420, 50, (128, 128, 128))
        draw_border(self.image, thickness=2)

        self.rect = self.image.get_rect()

        ###

        self.caption = Object2D.from_surface(
            render_text(
                text="Audio Player",
                font_height=17,
                padding=5,
                border_thickness=2,
                background_color=WHITE,
                foreground_color=BLACK,
            ),
        )

        ###

        self.toggle_play_button = PlayingPausedObject(
            {
                "playing": PLAYING_ICON,
                "paused": PAUSED_ICON,
            },
            on_mouse_release=(get_oblivious_callable(self.toggle_play)),
        )

        self.toggle_play_button.switch_to_paused_surface()

        ###

        self.audio_index_entry = IntFloatEntry(
            value=0,
            loop_holder=self,
            numeric_classes_hint="int",
            min_value=0,
            command=self.set_audio_from_entry,
            draw_on_window_resize=self.draw,
        )

        ###

        self.volume = 0.4
        music.set_volume(self.volume)

        ###

        volume_area = self.volume_area = Rect((0, 0), (100, 30))

        ###

        self.center_and_redefine_objects()

        APP_REFS.window_resize_setups.append(self.center_and_redefine_objects)

    def center_and_redefine_objects(self):

        self.rect.center = SCREEN_RECT.center

        self.caption.rect.topleft = self.rect.move(10, 10).topleft

        self.toggle_play_button.rect.midleft = self.caption.rect.move(5, 0).midright

        self.audio_index_entry.rect.midleft = self.toggle_play_button.rect.move(
            5, 0
        ).midright

        self.volume_area.midleft = self.audio_index_entry.rect.move(10, 0).midright

        self.full_volume_points = (
            self.volume_area.bottomleft,
            self.volume_area.topright,
            self.volume_area.bottomright,
        )

        self.set_current_volume_points()

    def set_current_volume_points(self):

        volume_area = self.volume_area

        start_vector = Vector2(volume_area.bottomleft)

        volume = self.volume

        self.current_volume_points = (
            start_vector,
            start_vector.lerp(volume_area.topright, volume),
            start_vector.lerp(volume_area.bottomright, volume),
        )

    def play_audio(self, audio_paths, index=0):

        self.audio_paths = (
            [audio_paths] if isinstance(audio_paths, str) else audio_paths
        )

        index = max(0, min(len(self.audio_paths) - 1, index))

        self.index = index

        self.audio_path = self.audio_paths[index]

        self.audio_index_entry.set(index, False)
        self.audio_index_entry.set_range(
            0,
            len(self.audio_paths) - 1,
        )

        self.set_current_volume_points()

        self.toggle_play()

        self.running = True

        loop_holder = self

        while True:

            try:

                while self.running:

                    ### perform various checkups for this frame;
                    ###
                    ### stuff like maintaing a constant framerate and more
                    SERVICES_NS.frame_checkups()

                    loop_holder.handle_input()
                    loop_holder.draw()

                ## if we leave the inner loop, also exit the outer one
                break

            except SwitchLoopException as err:
                loop_holder = err.loop_holder

        music.stop()

    def handle_input(self):
        """"""
        self.handle_events()
        self.handle_mouse_state()

    def handle_events(self):

        for event in SERVICES_NS.get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.running = False

                elif event.key == K_SPACE:
                    self.toggle_play()

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.on_mouse_click(event)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.on_mouse_release(event)

    def on_mouse_click(self, event):
        """"""
        mouse_pos = event.pos

        entry = self.audio_index_entry

        if entry.rect.collidepoint(mouse_pos):
            entry.on_mouse_click(event)

    def on_mouse_release(self, event):
        """"""
        mouse_pos = event.pos

        toggle_button = self.toggle_play_button

        if toggle_button.rect.collidepoint(mouse_pos):
            toggle_button.on_mouse_release(event)

    def handle_mouse_state(self):

        mouse_buttons_pressed = SERVICES_NS.get_mouse_pressed()

        mouse_x, _ = mouse_pos = SERVICES_NS.get_mouse_pos()

        volume_area = self.volume_area

        if mouse_buttons_pressed[0] and volume_area.collidepoint(mouse_pos):

            self.volume = (mouse_x - volume_area.x) / volume_area.width

            music.set_volume(self.volume)
            self.set_current_volume_points()

    def draw(self):

        super().draw()

        self.caption.draw()

        self.toggle_play_button.draw()
        self.audio_index_entry.draw()

        draw_polygon(SCREEN, BLACK, self.full_volume_points, 2)

        draw_polygon(SCREEN, BLACK, self.current_volume_points)

        ### update the screen
        SERVICES_NS.update_screen()

    def toggle_play(self):

        if music.get_busy():

            music.unload()
            music.stop()

            (self.toggle_play_button.switch_to_paused_surface())

        else:

            try:
                music.load(self.audio_path)

            except Exception as err:

                log_message = (
                    "An error ocurred while trying to"
                    " load current audio file."
                )

                logger.exception(log_message)
                USER_LOGGER.exception(log_message)

                dialog_message = log_message + (
                    " Check the user log for details (on the graph/canvas,"
                    " press <Ctrl+Shift+j> or access the \"Help > Show user"
                    " log\" option on the menubar)."
                )

                create_and_show_dialog(dialog_message, level_name='error')

            else:

                music.set_volume(self.volume)
                music.play()

                (self.toggle_play_button.switch_to_playing_surface())

    def set_audio_from_entry(self):
        """Browse audio files by number of given steps."""
        self.index = self.audio_index_entry.get()
        self.audio_path = self.audio_paths[self.index]
        music.load(self.audio_path)


play_audio = AudioPlayer().play_audio
