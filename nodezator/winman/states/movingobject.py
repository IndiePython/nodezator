"""Window manager event handling for 'moving_object' state."""

### third-party imports

from pygame import (
    QUIT,
    KEYDOWN,
    KEYUP,
    KMOD_CTRL,
    K_ESCAPE,
    K_x,
    K_y,
    K_RETURN,
    K_KP_ENTER,
    K_KP0,
    K_RSHIFT,
    K_LSHIFT,
    K_w,
    K_a,
    K_s,
    K_d,
    K_o,
    K_UP,
    K_LEFT,
    K_DOWN,
    K_RIGHT,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events
from pygame.display import update

from pygame.key import (
    get_mods as get_mods_bitmask,
    get_pressed as get_pressed_keys,
)


### local imports

from ...config import APP_REFS

from ...loopman.exception import QuitAppException


class MovingObjectState:
    """Methods related to 'moving_object' state."""

    def moving_object_event_handling(self):
        """Get and respond to events."""
        for event in get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:

                ## XXX if/elif blocks below could be better
                ## commented

                if event.button == 1:
                    APP_REFS.ea.confirm_moving()

                elif event.button == 3:

                    ## cancel operation
                    APP_REFS.ea.cancel_moving()

            ### KEYDOWN

            elif event.type == KEYDOWN:

                ## set translation factor to 10

                if event.key in (K_RSHIFT, K_LSHIFT):
                    APP_REFS.ea.translation_factor = 10

            ### KEYUP

            elif event.type == KEYUP:

                ## toggle grid
                if event.key == K_KP0:
                    APP_REFS.ea.toggle_grid()

                ## positioning related

                elif event.key == K_ESCAPE:
                    APP_REFS.ea.cancel_moving()

                elif event.key in (K_RETURN, K_KP_ENTER):
                    APP_REFS.ea.confirm_moving()

                elif event.key == K_x:
                    APP_REFS.ea.constrain_to_x()

                elif event.key == K_y:
                    APP_REFS.ea.constrain_to_y()

                elif event.key in (K_RSHIFT, K_LSHIFT):
                    APP_REFS.ea.translation_factor = 1

    def moving_object_keyboard_input_handling(self):
        """Handle keyboard specific input."""
        ### get input state maps
        key_input, mods_bitmask = get_pressed_keys(), get_mods_bitmask()

        ### state of keys related to scrolling

        up = key_input[K_w] or key_input[K_UP]
        left = key_input[K_a] or key_input[K_LEFT]
        down = key_input[K_s] or key_input[K_DOWN]
        right = key_input[K_d] or key_input[K_RIGHT]

        ### perform scrolling or not, according to state
        ### of keys

        ## vertical scrolling

        if up and not down:
            APP_REFS.ea.scroll_up()

        elif down and not up:
            APP_REFS.ea.scroll_down()

        ## horizontal scrolling

        if left and not right:
            APP_REFS.ea.scroll_left()

        elif right and not left:

            ### the state of control is used to know when
            ### not to consider the D key for scrolling
            ### (when the key is pressed because the user
            ### pressed Ctrl-D to duplicate the selected
            ### nodes in the 'loaded_file' state and didn't
            ### release the button yet)

            if not (mods_bitmask & KMOD_CTRL):

                APP_REFS.ea.scroll_right()

    ### update

    def moving_object_update(self):
        """Update method for the 'moving_object' state."""
        for item in self.labels_update_methods:
            item()
        for item in self.switches_update_methods:
            item()

        APP_REFS.ea.track_mouse()

    ### draw

    def moving_object_draw(self):
        """Draw method for the 'moving_object' state."""
        self.background.draw()

        APP_REFS.ea.grid_drawing_behaviour()
        APP_REFS.ea.check_axis_line()
        APP_REFS.gm.draw()

        for item in self.labels_drawing_methods:
            item()
        for item in self.switches_drawing_methods:
            item()

        self.separator.draw()
        self.menubar.draw_top_items()

        update()  # pygame.display.update
