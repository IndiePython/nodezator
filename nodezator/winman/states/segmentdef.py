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


### local import

from ...config import APP_REFS

from ...loopman.exception import QuitAppException


class SegmentDefinitionState:
    """Methods related to 'segment_definition' state."""

    def segment_definition_event_handling(self):
        """Get and respond to events."""
        for event in get_events():

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
        ### loop, so there's the execution flow of this
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

        update()  # pygame.display.update
