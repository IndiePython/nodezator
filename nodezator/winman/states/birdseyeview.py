"""Window manager event handling for 'birdseye_view' state."""

### third-party imports

from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    KMOD_CTRL,
    K_F1,
    K_ESCAPE,
    K_b,
    K_w,
    K_q,
    MOUSEBUTTONDOWN,
)


### local imports

from ...pygamesetup import SERVICES_NS

from ...config import APP_REFS

from ...loopman.exception import QuitAppException, ContinueLoopException

from ...htsl.main import open_htsl_link



### constant
EXIT_KEYS = frozenset({K_ESCAPE, K_b})


### main class

class BirdsEyeViewState:
    """Methods related to 'birdseye_view' state."""

    def birdseye_view_event_handling(self):
        """Get and respond to events."""
        for event in SERVICES_NS.get_events():

            ### KEYDOWN

            if event.type == KEYDOWN:

                ## quit application

                if event.key == K_q and event.mod & KMOD_CTRL:
                    raise QuitAppException

                ## close file

                elif event.key == K_w and event.mod & KMOD_CTRL:

                    if hasattr(APP_REFS, 'source_path'):
                        raise CloseFileException


            ### KEYUP

            elif event.type == KEYUP:

                ## leave bird's eye view mode

                if event.key in EXIT_KEYS:

                    ## set state loaded_file state
                    self.set_state('loaded_file')

                    ## restart the loop
                    raise ContinueLoopException

                ## show help text

                elif event.key == K_F1:
                    open_htsl_link("nodezator://help.nodezator.pysite")

            ### MOUSEBUTTONDOWN

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    ## trigger the mouse click method
                    self.birdseye_view_on_mouse_click(event)


            ### QUIT

            elif event.type == QUIT:
                raise QuitAppException


    def birdseye_view_on_mouse_click(self, event):
        """Act on mouse left button pressing.

        Act based on mouse position.
        """
        ### retrieve the mouse position
        mouse_pos = event.pos

        ### if mouse is clicked outside graph area, leave state

        if not APP_REFS.ea.birdseye_graph.rect.collidepoint(mouse_pos):

            ## set state loaded_file state
            self.set_state('loaded_file')

            ## restart the loop
            raise ContinueLoopException


    ### update

    def birdseye_view_update(self):
        """Move whole graph respective spot in graph representation is shown.

        That is, if the mouse is pressed and within the graph representation,
        move the whole graph so that the equivalent spot in the whole graph
        can be seen in the center of the screen.

        We only move if we are not already in that spot, though.
        """

        ### only proceed if mouse button 1 is pressed

        if SERVICES_NS.get_mouse_pressed()[0]:

            ## get mouse position and reference the editing assistant

            mouse_pos = SERVICES_NS.get_mouse_pos()

            ea = APP_REFS.ea

            ## only proceed if the mouse position is within the graph
            ## representation...

            if ea.birdseye_graph.rect.collidepoint(mouse_pos):

                ## only proceed if we aren't in that spot already...

                if mouse_pos != ea.birdseye_view_last_mouse_pos:

                    ## scroll whole graph so the respective spot
                    ## is centered on the screen
                    ea.scroll_from_birdseye_view(mouse_pos)

                    ## update labels
                    for item in self.labels_update_methods:
                        item()

                    ## redraw objects once
                    self.birdseye_view_draw_once()

    ### draw

    def birdseye_view_draw_once(self):
        """Draw relevant objects on the screen.

        This method is prefixed "draw_once" because it is meant
        to be used just once for each time the graphical elements
        change, to avoid unnecessary work.
        """

        self.background.draw()

        ea = APP_REFS.ea

        ea.draw_selected()
        APP_REFS.gm.draw()

        ea.birdseye_graph.draw()
        ea.birdseye_caption_label.draw()
        ea.birdseye_instruction_label.draw()

        for item in self.labels_drawing_methods:
            item()

    def birdseye_view_draw(self):
        """Update the screen.

        No actual drawing needs to take place because it is handled
        in another method that is called just once whenever needed,
        rather than once per loop.
        """
        SERVICES_NS.update_screen()
