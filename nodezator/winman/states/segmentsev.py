"""Window manager methods for 'segment_severance' state."""

### third-party imports

from pygame import QUIT, KEYUP, K_ESCAPE, MOUSEBUTTONUP

from pygame.event import get as get_events

from pygame.display import update


### local imports

from ...config import APP_REFS

from ...loopman.exception import QuitAppException


class SegmentSeveranceState:
    """Methods related to 'segment_severance' state."""

    def segment_severance_event_handling(self):
        """Get and respond to events."""
        for event in get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    (APP_REFS.gm.resume_severing_segments(event.pos))

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    APP_REFS.gm.cancel_severing_segments()

    ### update

    def segment_severance_update(self):
        """Update method for 'segment_severance' state."""
        for item in self.labels_update_methods:
            item()
        for item in self.switches_update_methods:
            item()

    ### draw

    def segment_severance_draw(self):
        """Draw method for the 'segment_severance' state."""
        self.background.draw()

        APP_REFS.ea.grid_drawing_behaviour()
        APP_REFS.ea.draw_selected()
        APP_REFS.gm.draw()
        APP_REFS.gm.draw_temp_cutting_segment()

        for item in self.labels_drawing_methods:
            item()
        for item in self.switches_drawing_methods:
            item()

        self.separator.draw()
        self.menubar.draw_top_items()

        update()  # pygame.display.update
