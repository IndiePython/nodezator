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


class SegmentDefinitionState:
    """Methods related to 'segment_definition' state."""

    def segment_definition_event_handling(self):
        """Get and respond to events."""
        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    (self.segment_definition_on_mouse_release(event))

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    APP_REFS.gm.cancel_defining_segment()

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

    def segment_definition_on_mouse_release(self, event):
        """Act on mouse left button release.

        Act based on mouse position.
        """
        mouse_pos = event.pos

        ### iterator over each node on screen, checking if
        ### any collides, if so, break out of the loop

        for node in APP_REFS.gm.nodes.get_on_screen():

            if node.rect.collidepoint(mouse_pos):
                break

        ### if you don't break out of the loop, cancel
        ### the segment definition behaviour, this
        ### automatically triggers the restart of the
        ### loop, so that the execution flow of this
        ### method won't go past this point
        else:
            APP_REFS.gm.cancel_defining_segment()

        ### otherwise, it means there's a colliding node
        ### in the 'node' variable; trigger its operation
        ### to check whether sockets are picked for
        ### segment definition
        node.check_sockets_for_segment_definition(event)

    ### update

    def segment_definition_update(self):
        """Update method for 'segment_definition' state."""
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
