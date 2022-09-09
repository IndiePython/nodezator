"""Window manager methods for 'segment_definition' state."""

### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_w,
    K_a,
    K_s,
    K_d,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events

from pygame.key import get_pressed as get_pressed_keys

from pygame.display import update


### local imports

from ...config import APP_REFS

from ...loopman.exception import QuitAppException


class BoxSelectionState:
    """Methods related to 'box_selection' state."""

    def box_selection_event_handling(self):
        """Get and respond to events."""
        for event in get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                ## confirm box selection

                if event.button == 1:
                    APP_REFS.ea.confirm_box_selection()

                ## cancel box selection

                elif event.button == 3:
                    APP_REFS.ea.cancel_box_selection()

            ### KEYUP

            elif event.type == KEYUP:

                ## cancel box selection

                if event.key == K_ESCAPE:
                    APP_REFS.ea.cancel_box_selection()

    def box_selection_keyboard_input_handling(self):
        """Handle keyboard specific input."""
        ### get input state maps
        key_input = get_pressed_keys()

        ### states related to widgets when file is loaded

        w_key = key_input[K_w]
        a_key = key_input[K_a]
        s_key = key_input[K_s]
        d_key = key_input[K_d]

        ## vertical scrolling

        if w_key and not s_key:
            APP_REFS.ea.scroll_up()

        elif s_key and not w_key:
            APP_REFS.ea.scroll_down()

        ## horizontal scrolling

        if a_key and not d_key:
            APP_REFS.ea.scroll_left()

        elif d_key and not a_key:
            APP_REFS.ea.scroll_right()

    ### update

    def box_selection_update(self):
        """Update method for 'segment_definition' state."""
        for item in self.labels_update_methods:
            item()
        for item in self.switches_update_methods:
            item()

        APP_REFS.ea.recalculate_selection_box()

    ### draw

    def box_selection_draw(self):
        """Draw method for the 'segment_definition' state."""
        self.background.draw()

        APP_REFS.ea.grid_drawing_behaviour()
        APP_REFS.ea.draw_selected()
        APP_REFS.gm.draw()
        APP_REFS.ea.draw_selection_box()

        for item in self.labels_drawing_methods:
            item()
        for item in self.switches_drawing_methods:
            item()

        self.separator.draw()
        self.menubar.draw_top_items()

        update()  # pygame.display.update
