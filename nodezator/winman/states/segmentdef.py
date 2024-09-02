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

from pygame.mouse import get_rel as get_relative_mouse_pos


### local imports

from ...pygamesetup import SERVICES_NS

from ...config import APP_REFS

from ...loopman.exception import QuitAppException



class SegmentDefinitionState:
    """Methods related to 'segment_definition' state."""

    def segment_definition_event_handling(self):
        """Get and respond to events."""
        for event in SERVICES_NS.get_events():

            ### MOUSEBUTTONUP

            if event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    APP_REFS.gm.check_nearby_socket_for_segment_definition()

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    APP_REFS.gm.cancel_defining_segment()

            ### QUIT
            elif event.type == QUIT:
                raise QuitAppException

    def segment_definition_keyboard_input_handling(self):
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

        ## if nodes or mouse moved, look for nearby socket for connecting

        if x_direction or y_direction or any(get_relative_mouse_pos()):

            APP_REFS.gm.look_for_nearby_compatible_socket(
                SERVICES_NS.get_mouse_pos()
            )

    ### update

    def segment_definition_update(self):
        """Update method for 'segment_definition' state."""

        ### update labels and switches

        for item in self.labels_update_methods:
            item()
        for item in self.switches_update_methods:
            item()

    ### draw

    def segment_definition_draw(self):
        """Draw method for the 'segment_definition' state."""
        self.background.draw()

        APP_REFS.ea.grid_drawing_behaviour()
        APP_REFS.ea.draw_selected()
        APP_REFS.gm.draw()
        APP_REFS.gm.draw_temp_segment()

        for item in self.labels_drawing_methods:
            item()
        for item in self.switches_drawing_methods:
            item()

        self.separator.draw()
        self.menubar.draw_top_items()

        SERVICES_NS.update_screen()
