"""Facility for image visualization."""

### third-party imports
import asyncio

## pygame

from pygame import (

              QUIT,

              KEYUP,

              K_ESCAPE,


              K_w, K_a, K_s, K_d,
              K_UP, K_LEFT, K_DOWN, K_RIGHT,
              K_HOME,

              MOUSEBUTTONUP,
              MOUSEBUTTONDOWN,
              MOUSEMOTION,

              Surface,

            )

from pygame.display import get_surface, update
from pygame.time    import Clock
from pygame.event   import get as get_events

from pygame.key import get_pressed as get_pressed_keys


### local import
from .utils import blit_checker_pattern



### get screen reference and a rect for it

SCREEN      = get_surface()
SCREEN_RECT = SCREEN.get_rect()

### define scrolling speeds in different 2D axes

X_SCROLLING_SPEED = 20
Y_SCROLLING_SPEED = 20

### obtain fps maintaining operation
maintain_fps = Clock().tick

### define the framerate
FPS = 30


### now here comes the first big change on our script:
###
### rather than using a single function as our main
### callable, we'll create a whole class to hold
### several methods, one of which we'll be using
### as the main callable for our node;
###
### why do we do that? Simply because we'll be dealing
### with a lot state (different objects, values and
### behaviours) and classes are a great tool for such job

class ImageViewer:
    """Manages the loop of the view_surface() node."""

    def __init__(self):
        """Create support objects/flags."""

        ### create a scroll area so the image can be moved
        ### around
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

        ### instantiate background

        self.background = (
          Surface(SCREEN.get_size()).convert()
        )

        ### create flag to indicate whether the checker
        ### pattern must be drawn on the background;
        ###
        ### the first time the node is executed the
        ### checker pattern is draw on the background
        ### and then this flag is set to False; it will
        ### remain False for the lifetime of the node,
        ### that is, it is used only that time;
        ###
        ### it is actually optional: we could draw the
        ### checker pattern right away if we wanted; we
        ### just avoid doing so because though it happens
        ### practically in an instant, there's no telling
        ### whether other nodes will also perform setups
        ### that take time when the node pack is loaded
        ### and the sum of the time taken by all nodes
        ### might end up resulting in a non-trivial amount
        ### of time to load the node pack;
        ###
        ### maybe we are just being overly cautious,
        ### though;
        self.must_draw_checker_pattern = True

    def keyboard_mode_event_handling(self):
        """Event handling for the keyboard mode."""

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.enable_mouse_mode()

            elif event.type == KEYUP:

                if event.key == K_HOME:

                    self.image_rect.center = (
                      SCREEN_RECT.center
                    )

                elif event.key == K_ESCAPE:
                    self.running = False

    def keyboard_mode_key_state_handling(self):
        """Handle pressed keys for keyboard mode."""

        key_input = get_pressed_keys()

        ### calculate x movement

        ## calculate x movement if the "moves_horizontally"
        ## flag is set

        if self.moves_horizontally:

            ## check whether "go left" and "go right"
            ## buttons were pressed

            go_left = any(
              key_input[key] for key in (K_a, K_LEFT)
            )

            go_right = any(
              key_input[key] for key in (K_d, K_RIGHT)
            )

            ## assign amount of movement on x axis
            ## depending on whether "go left" and "go right"
            ## buttons were pressed

            if go_left and not go_right:
                dx = -1 * X_SCROLLING_SPEED

            elif go_right and not go_left:
                dx = 1 * X_SCROLLING_SPEED

            else: dx = 0

        ## if the "moves_horizontally" flag is not set,
        ## it means the image's width is smaller than
        ## the screen's width, so there's no need to
        ## move/scroll horizontally anyway, so the
        ## movement is 0
        else: dx = 0

        ### perform the same checks/calculations for
        ### the y axis

        if self.moves_vertically:

            go_up = any(
              key_input[key] for key in (K_w, K_UP)
            )

            go_down = any(
              key_input[key] for key in (K_s, K_DOWN)
            )

            if (

                 (go_up and go_down)
              or (not go_up and not go_down)

            ):
                dy = 0

            elif go_up and not go_down:
                dy = -1 * Y_SCROLLING_SPEED

            elif go_down and not go_up:
                dy = 1 * Y_SCROLLING_SPEED

        else: dy = 0

        ### if there is movement in the x or y
        ### axis, move the image
        if dx or dy: self.move_image(dx, dy)

    def move_image(self, dx, dy):
        """Move image in x and/or y axis.

        It performs extra checks/movement relative to
        a scroll area to ensure the image never leaves
        the screen completely.
        """

        image_rect  = self.image_rect
        scroll_area = self.scroll_area

        ### apply x movement if != 0

        if dx < 0:

            if (
              (image_rect.right + dx)
              < scroll_area.right
            ):
                image_rect.right = scroll_area.right

            else: image_rect.x += dx

        elif dx > 0:

            if (
              (image_rect.left + dx)
              > scroll_area.left
            ):
                image_rect.left = scroll_area.left

            else: image_rect.x += dx

        ### apply y movement if != 0

        if dy < 0:

            if (
              (image_rect.bottom + dy)
              < scroll_area.bottom
            ):
                image_rect.bottom = scroll_area.bottom

            else: image_rect.y += dy

        elif dy > 0:

            if (
              (image_rect.top + dy)
              > scroll_area.top
            ):
                image_rect.top = scroll_area.top

            else: image_rect.y += dy

    def mouse_mode_event_handling(self):
        """Event handling for the mouse mode."""

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == MOUSEMOTION:
                self.move_according_to_mouse(*event.rel)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.enable_keyboard_mode()

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.running = False

    def move_according_to_mouse(self, dx, dy):
        """Support method for the mouse mode."""

        if not self.moves_horizontally:
            dx = 0

        if not self.moves_vertically:
            dy = 0

        self.move_image(dx, dy)

    def mouse_mode_key_state_handling(self):
        """Mouse mode doesn't handle key pressed state.

        So this method does nothing.
        """

    def watch_window_size(self):
        """Perform setups if window was resized."""

        ### if the screen and the background have the
        ### same size, then no window resizing took place,
        ### so we exit the function right away

        if SCREEN.get_size() == self.background.get_size():
            return

        ### otherwise, we keep executing the function,
        ### performing the needed setups

        ## reference image surf and rect locally

        image_surf = self.image_surf
        image_rect = self.image_rect

        ## update the screen rect's size
        SCREEN_RECT.size = SCREEN.get_size()

        ## center the image on the screen
        image_rect.center = SCREEN_RECT.center

        ## update the moving flags

        self.moves_horizontally = (
          image_rect.width > SCREEN_RECT.width
        )

        self.moves_vertically = (
          image_rect.height > SCREEN_RECT.height
        )

        ## recreate the background and redraw the checker
        ## pattern on it

        self.background = (

          Surface(SCREEN.get_size()).convert()

        )

        blit_checker_pattern(self.background)

        ## draw the background on the screen
        SCREEN.blit(self.background, (0, 0))

        ## blit image on the screen using its rect
        SCREEN.blit(image_surf, image_rect)

        ## replace the scroll area
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

    def enable_keyboard_mode(self):
        """Set behaviours to move image with keyboard."""

        self.handle_events = (
          self.keyboard_mode_event_handling
        )

        self.handle_key_state = (
          self.keyboard_mode_key_state_handling
        )

    def enable_mouse_mode(self):
        """Set behaviours to move image with the mouse.

        That is, by dragging.
        """

        self.handle_events = (
          self.mouse_mode_event_handling
        )

        self.handle_key_state = (
          self.mouse_mode_key_state_handling
        )

    def draw(self):
        """If image moved, redraw."""

        ### if the image is in the same position,
        ### do nothing by returning early

        if (
          self.last_topleft == self.image_rect.topleft
        ): return

        ### otherwise store the current position and
        ### redraw background and image

        self.last_topleft = self.image_rect.topleft

        SCREEN.blit(self.background, (0, 0))

        SCREEN.blit(
                 self.image_surf, self.image_rect
               )

    async def loop(self):
        """Start and keep a loop.

        The loop is only exited when the running flag
        is set to False.
        """

        self.running = True

        while self.running:
            await asyncio.sleep(0)        

            ## maintain a constant fps
            maintain_fps(FPS)

            ## watch out for change in the window size,
            ## performing needed setups if such change
            ## happened
            self.watch_window_size()

            ## execute main operation of the loop,
            ## that is, input handling and drawing

            self.handle_events()
            self.handle_key_state()
            self.draw()

            ## finally update the screen with
            ## pygame.display.update()
            update()
            
        ### remove image surf and rect references

        del self.image_surf
        del self.image_rect

    ### the method below is the main callable we'll use
    ### for our node;
    ###
    ### that is, we'll instantiate the ImageViewer class
    ### and use this method from the instance as the
    ### main callable;
    ###
    ### don't worry about the "self" parameter, Nodezator
    ### is smart enough to ignore it (actually, the smart
    ### one is inspect.signature(), the responsible for
    ### such behaviour)

    def view_surface(self, surface: Surface):
        """Display surface on screen.

        To stop displaying the image just press <Escape>.
        This will trigger the exit of the inner loop.
        """
        ### enable keyboard mode
        self.enable_keyboard_mode()

        ### draw the checker pattern on the background if
        ### needed; this flag is only used once for the
        ### lifetime of this node (check the comment on
        ### the __init__ method about this flag)

        if self.must_draw_checker_pattern:

            ### draw the checker pattern on the background
            blit_checker_pattern(self.background)

            ### set flag to false
            self.must_draw_checker_pattern = False


        ### draw the background on the screen
        SCREEN.blit(self.background, (0, 0))

        ### get rect for image and center it on the screen

        rect = surface.get_rect()

        rect.center = SCREEN_RECT.center

        ### update the moving flags;
        ###
        ### such flags just indicate whether moving the
        ### image makes sense horizontally and
        ### vertically, depending on whether the image
        ### is larger than the screen or not;
        ###
        ### for instance, if the screen is wider than
        ### the image, then there is no need to move
        ### the image horizontally, so the corresponding
        ### flag is set to false

        self.moves_horizontally = (
          rect.width > SCREEN_RECT.width
        )

        self.moves_vertically = (
          rect.height > SCREEN_RECT.height
        )

        ### store image surface and rect

        self.image_surf = surface
        self.image_rect = rect

        ### blit image on the screen using its rect
        SCREEN.blit(surface, rect)

        ### create attribute to track topleft position
        self.last_topleft = rect.topleft

        ### loop
        asyncio.get_running_loop().create_task(self.loop())

    ### set attribute on view_surface method so the
    ### execution time tracking is dismissed for this
    ### node;
    ###
    ### we need to do this here rather than after
    ### instantiating ImageViewer because after
    ### instantiating the class the view_surface method
    ### doesn't allow new attributes to be set on it
    view_surface.dismiss_exec_time_tracking = True


### now, instantiate the ImageViewer and use the view_surface
### method as the main callable
main_callable = ImageViewer().view_surface

### to make it so the callable can be found in this module when
### the node layout is exported as a python script, make sure
### it can be found using its own name
view_surface = main_callable
