"""Facility for viewing images from given paths."""

### standard library import
import asyncio
from functools import partialmethod


### third-party import
from pygame import Rect, Surface


### local imports

from ...config import APP_REFS

from ...pygamesetup import SERVICES_NS, SCREEN_RECT, set_modal

from ...surfsman.render import render_rect

from ...surfsman.cache import draw_cached_screen_state

from .op import ViewerOperations

from .constants import MOVE_AREA




class SurfaceViewer(ViewerOperations):
    """loop holder for viewing a surface."""

    def __init__(self):
        """Create/store useful objects."""
        ### the size will be updated to the size
        ### of the surface being displayed
        self.rect = Rect(0, 0, 100, 100)

        ###

        self.running = False

        self.should_draw_rect = False
        self.should_move_with_mouse = False

        ### store the centering method as a
        ### window resize setup
        APP_REFS.window_resize_setups.append(self.center_surface_viewer)

    def center_surface_viewer(self):

        ##
        MOVE_AREA.size = SCREEN_RECT.inflate(-100, -100).size

        ###
        center = SCREEN_RECT.center

        MOVE_AREA.center = center
        self.rect.center = center

        ### if the loop is running, ask to redraw

        if self.running:
            APP_REFS.draw_after_window_resize_setups = self.response_draw

    async def view_surface_loop(self):
        while self.running:
            await asyncio.sleep(0)        

            ### perform various checkups for this frame;
            ###
            ### stuff like maintaing a constant framerate and more
            SERVICES_NS.frame_checkups()

            self.handle_input()
            self.draw()

        del self.image
        set_modal(False)
        if self.callback is not None:
            self.callback()

    
    def view_surface(self, surface: Surface, callback = None):
        """Display given surface."""

        if not isinstance(surface, Surface):
            return TypeError("given argument must be a pygame.Surface.")

        ###
        self.callback = callback
        self.image = surface
        self.rect.size = surface.get_size()
        self.rect.center = MOVE_AREA.center

        self.response_draw()

        ###
        self.running = True

        set_modal(True)
        asyncio.get_running_loop().create_task(self.view_surface_loop())


### instantiate the surface viewer and store a reference
### to its 'view_surface' method in this module so
### it can be easily imported
view_surface = SurfaceViewer().view_surface
