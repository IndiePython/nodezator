"""Facility for text visualization."""

### standard library import
import asyncio
from itertools import cycle


### third-party imports

## pygame

from pygame import (

              QUIT,

              KEYUP,

              K_ESCAPE,


              K_w, K_a, K_s, K_d,
              K_UP, K_LEFT, K_DOWN, K_RIGHT,

              MOUSEBUTTONUP,
              MOUSEMOTION,

              Surface, Rect,

            )

from pygame.time import Clock
from pygame.font import Font

from pygame.display import get_surface, update
from pygame.event   import get as get_events
from pygame.draw    import rect as draw_rect

from pygame.key import get_pressed as get_pressed_keys

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

class TextViewer:
    """Manages the loop of the view_text() node."""

    def __init__(self):
        """Create support objects/flags."""

        ### create a scroll area so the text can be moved
        ### around
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

        ### instantiate background

        self.background = (
          Surface(SCREEN.get_size()).convert()
        )

        self.background.fill((128, 128, 128))

        ### instantiate and store rendering operation
        self.render_text = Font(None, 26).render

        ### create lists to hold surfaces and rects
        ### representing text lines

        self.line_surfs = []
        self.line_rects = []

    def handle_events(self):
        """Handle events from event queue."""

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.running = False

    def handle_key_state(self):
        """Handle pressed keys."""

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
                dx = 1 * X_SCROLLING_SPEED

            elif go_right and not go_left:
                dx = -1 * X_SCROLLING_SPEED

            else: dx = 0

        ## if the "moves_horizontally" flag is not set,
        ## it means the text's width is smaller than
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
                dy = 1 * Y_SCROLLING_SPEED

            elif go_down and not go_up:
                dy = -1 * Y_SCROLLING_SPEED

        else: dy = 0

        ### if there is movement in the x or y
        ### axis, move the text
        if dx or dy: self.move_text(dx, dy)

    def move_text(self, dx, dy):
        """Move text in x and/or y axis.

        It performs extra checks/movement relative to
        a scroll area to ensure the text never leaves
        the screen completely.
        """

        text_rect = Rect(
                      *self.line_rects[0].topleft,
                      self.text_width,
                      self.text_height,
                    )

        scroll_area = self.scroll_area

        ### apply x movement if != 0

        if dx < 0:

            if (
              (text_rect.right + dx)
              < scroll_area.right
            ):
                dx = scroll_area.right - text_rect.right


        elif dx > 0:

            if (
              (text_rect.left + dx)
              > scroll_area.left
            ):
                dx = scroll_area.left - text_rect.left

        ### apply y movement if != 0

        if dy < 0:

            if (
              (text_rect.bottom + dy)
              < scroll_area.bottom
            ):
                dy = scroll_area.bottom - text_rect.bottom

        elif dy > 0:

            if (
              (text_rect.top + dy)
              > scroll_area.top
            ):
                dy = scroll_area.top - text_rect.top

        for rect in self.line_rects: rect.move_ip(dx, dy)

    def watch_window_size(self):
        """Perform setups if window was resized."""

        ### if the screen and the background have the
        ### same size, then no window resizing took place,
        ### so we exit the function right away

        if SCREEN.get_size() == self.background.get_size():
            return

        ### otherwise, we keep executing the function,
        ### performing the needed setups

        ## update the screen rect's size
        SCREEN_RECT.size = SCREEN.get_size()

        ## update the moving flags

        self.moves_horizontally = (
          self.text_width > SCREEN_RECT.width - 80
        )

        self.moves_vertically = (
          self.text_height > SCREEN_RECT.height - 80
        )

        ## recreate the background

        self.background = (

          Surface(SCREEN.get_size()).convert()

        )

        self.background.fill((128, 128, 128))

        ## redraw everything
        self.draw()

        ## replace the scroll area
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

    def check_draw(self):
        """If text moved, redraw."""

        ### if the text is in the same position,
        ### do nothing by returning early

        if (
          self.last_topleft == self.line_rects[0].topleft
        ): return

        ### otherwise store the current position and
        ### redraw background and text

        self.last_topleft = self.line_rects[0].topleft
        self.draw()

    def draw(self):
        """Draw background and text on screen."""
        blit = SCREEN.blit

        blit(self.background, (0, 0))

        text_rect = Rect(
                      *self.line_rects[0].topleft,
                      self.text_width,
                      self.text_height,
                    )

        text_bg_rect = text_rect.clip(SCREEN_RECT).inflate(40, 40)

        draw_rect(
          SCREEN,
          (35, 35, 65),
          text_bg_rect,
        )

        is_on_screen = SCREEN_RECT.colliderect

        for surf, rect in zip(

          self.line_surfs,
          self.line_rects,

        ):

            if is_on_screen(rect): blit(surf, rect)

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
            self.check_draw()

            ## finally update the screen with
            ## pygame.display.update()
            update()

        ### clear surf and rect lists

        self.line_surfs.clear()
        self.line_rects.clear()

    def create_line_surfaces(self):
        """Create text surfaces from text lines."""

        self.line_surfs.clear()
        self.line_rects.clear()

        render_text = self.render_text

        self.line_surfs.extend(
          render_text(line_text, True, (235, 235, 235), (35, 35, 65)).convert()
          for line_text in self.lines
        )

        self.line_rects.extend(
          surf.get_rect()
          for surf in self.line_surfs
        )

        topleft = SCREEN_RECT.move(40, 40).topleft
        y_offset = 5

        for rect in self.line_rects:

            rect.topleft = topleft
            topleft = rect.move(0, y_offset).bottomleft


    ### the method below is the main callable we'll use
    ### for our node;
    ###
    ### that is, we'll instantiate the TextViewer class
    ### and use this method from the instance as the
    ### main callable;
    ###
    ### don't worry about the "self" parameter, Nodezator
    ### is smart enough to ignore it (actually, the smart
    ### one is inspect.signature(), the responsible for
    ### such behaviour)

    def view_text(self, text: 'text' = ''):
        """Display text on screen.

        To stop displaying the text just press <Escape>.
        This will trigger the exit of the inner loop.
        """
        ### ensure we receive a non-empty string

        if type(text) != str:

            raise TypeError(
              "'text' argument must be a string."
            )

        if not text:

            raise ValueError(
              "'text' argument must be a non-empty string."
            )

        ### obtain lines from text
        self.lines = text.splitlines()

        ### obtain surfaces for each line of text
        self.create_line_surfaces()

        ### obtain text dimensions

        self.text_width = max(
                            self.line_rects,
                            key=lambda rect: rect.width
                          ).width

        self.text_height = (

            self.line_rects[-1].bottom
          - self.line_rects[ 0].top

        )

        ### update the moving flags;
        ###
        ### such flags just indicate whether moving the
        ### text makes sense horizontally and
        ### vertically, depending on whether the text
        ### is larger than the screen or not;
        ###
        ### for instance, if the screen is wider than
        ### the text, then there is no need to move
        ### the text horizontally, so the corresponding
        ### flag is set to false

        self.moves_horizontally = (
          self.text_width > SCREEN_RECT.width - 80
        )

        self.moves_vertically = (
          self.text_height > SCREEN_RECT.height - 80
        )

        ### create attribute to track topleft position
        self.last_topleft = (0, 0)

        ### redraw everything
        self.draw()

        ### loop
        asyncio.get_running_loop().create_task(self.loop())


    ### set attribute on view_text method so the
    ### execution time tracking is dismissed for this
    ### node;
    ###
    ### we need to do this here rather than after
    ### instantiating TextViewer because after
    ### instantiating the class the view_text method
    ### doesn't allow new attributes to be set on it
    view_text.dismiss_exec_time_tracking = True


### instantiate the TextViewer and use the view_text
### method as the main callable
main_callable = TextViewer().view_text

### also make sure it can be found in this module using
### its own name, so that it can be found when the node
### layout is exported as a Python script
view_text = main_callable
