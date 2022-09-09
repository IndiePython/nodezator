### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    MOUSEBUTTONDOWN,
)

from pygame.event import get as get_events

from pygame.display import update

from pygame.draw import rect as draw_rect


### local imports

from ..config import APP_REFS, FFMPEG_AVAILABLE

from ..pygameconstants import (
    SCREEN,
    SCREEN_RECT,
    maintain_fps,
)

from ..ourstdlibs.behaviour import get_oblivious_callable

from ..our3rdlibs.behaviour import watch_window_size

from ..loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ..classes2d.single import Object2D

from ..surfsman.render import render_rect
from ..surfsman.draw import draw_border

from ..textman.render import render_text

from ..colorsman.colors import BLACK, WHITE

from ..widget.intfloatentry.main import IntFloatEntry

from .cache import (
    VIDEO_METADATA_MAP,
    CachedVideoObject,
)


class VideoPreviewer(Object2D):
    def __init__(self):
        """"""

        self.image = render_rect(330, 330, (128, 128, 128))

        draw_border(self.image, thickness=2)

        self.rect = self.image.get_rect()

        self.videopreview = CachedVideoObject(
            ".",
            {
                "max_width": 250,
                "max_height": 250,
                "not_found_width": 250,
                "not_found_height": 250,
            },
            width=250,
            height=250,
        )

        ###

        self.caption = Object2D.from_surface(
            render_text(
                text="Video Previewer",
                font_height=17,
                padding=5,
                border_thickness=2,
                background_color=WHITE,
                foreground_color=BLACK,
            ),
        )
        ###

        self.video_index_entry = IntFloatEntry(
            value=0,
            loop_holder=self,
            numeric_classes_hint="int",
            min_value=0,
            command=self.update_preview_from_entry,
            draw_on_window_resize=self.draw,
        )

        ###

        self.not_available_message_obj = Object2D.from_surface(
            render_text(
                text="ffmpeg is not available",
                font_height=17,
                foreground_color=BLACK,
                background_color=WHITE,
            ),
        )

        ###

        self.draw_video_representation = (
            self.draw_next_video_frame
            if FFMPEG_AVAILABLE
            else self.not_available_message_obj.draw
        )

        ###
        self.center_video_previewer()

        APP_REFS.window_resize_setups.append(self.center_video_previewer)

        ###
        outline = self.videopreview.rect.inflate(2, 2)

        outline.topleft = tuple(
            a - b for a, b in zip(outline.topleft, self.rect.topleft)
        )

        draw_rect(self.image, (0, 0, 0), outline, 1)

    def center_video_previewer(self):

        self.rect.center = SCREEN_RECT.center

        self.videopreview.rect.center = self.rect.center

        self.caption.rect.topleft = self.rect.move(10, 10).topleft

        self.video_index_entry.rect.midtop = self.videopreview.rect.move(0, 5).midbottom

        if not FFMPEG_AVAILABLE:

            self.not_available_message_obj.rect.center = SCREEN_RECT.center

    def preview_videos(self, video_paths, index=0):

        self.video_paths = (
            [video_paths] if isinstance(video_paths, str) else video_paths
        )

        index = max(0, min(len(self.video_paths) - 1, index))

        self.index = index

        self.video_path = self.video_paths[index]

        self.video_index_entry.set(index, False)
        self.video_index_entry.set_range(0, len(self.video_paths) - 1)

        self.set_preview()

        self.running = True

        loop_holder = self

        while self.running:

            maintain_fps(self.fps)

            watch_window_size()

            try:

                loop_holder.handle_input()
                loop_holder.update()
                loop_holder.draw()

            except SwitchLoopException as err:
                loop_holder = err.loop_holder

    def handle_input(self):
        """"""
        self.handle_events()

    def handle_events(self):

        for event in get_events():

            if event.type == QUIT:
                raise QuitAppException

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.running = False

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.on_mouse_click(event)

    def on_mouse_click(self, event):
        """"""
        mouse_pos = event.pos

        entry = self.video_index_entry

        if entry.rect.collidepoint(mouse_pos):
            entry.on_mouse_click(event)

    def update(self):
        self.videopreview.update()

    def draw(self):

        super().draw()

        self.caption.draw()
        self.video_index_entry.draw()

        self.draw_video_representation()

        ### update the screen (pygame.display.update)
        update()

    def draw_next_video_frame(self):
        """"""
        self.videopreview.draw()

    def set_preview(self):

        self.videopreview.change_video_path(self.video_path)

        try:
            metadata = VIDEO_METADATA_MAP[self.video_path]
        except KeyError:
            self.fps = 24
        else:
            self.fps = metadata.get("fps", 24)

    def update_preview_from_entry(self):
        """Browse audio files by number of given steps."""

        self.index = self.video_index_entry.get()
        self.video_path = self.video_paths[self.index]
        self.set_preview()


preview_videos = VideoPreviewer().preview_videos
