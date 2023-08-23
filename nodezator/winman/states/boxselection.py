"""Window manager methods for 'segment_definition' state."""

### third-party imports

from pygame.locals import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_w,
    K_a,
    K_s,
    K_d,
    K_UP,
    K_LEFT,
    K_DOWN,
    K_RIGHT,
    MOUSEBUTTONUP,
)


### local imports

from ...pygamesetup import SERVICES_NS

from ...config import APP_REFS

from ...loopman.exception import QuitAppException


class BoxSelectionState:
    """Methods related to 'box_selection' state."""

    def box_selection_event_handling(self):
        """Get and respond to events."""
        for event in SERVICES_NS.get_events():

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
        key_input = SERVICES_NS.get_pressed_keys()

        ### state of keys related to scrolling

        up = key_input[K_w] or key_input[K_UP]
        left = key_input[K_a] or key_input[K_LEFT]
        down = key_input[K_s] or key_input[K_DOWN]
        right = key_input[K_d] or key_input[K_RIGHT]

        ### perform scrolling or not, according to state
        ### of keys

        x_direction = y_direction = 0

        ## horizontal

        if left and not right:
            x_direction = 1

        elif right and not left:
            x_direction = -1

        ## vertical

        if up and not down:
            y_direction = 1

        elif down and not up:
            y_direction = -1

        ## scroll

        if x_direction or y_direction:
            APP_REFS.ea.scroll_on_direction(x_direction, y_direction)

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

        SERVICES_NS.update_screen()
