"""Window manager behaviour for 'no_file' state."""

### third-party imports

from pygame.locals import (
    QUIT,
    KEYDOWN,
    KMOD_CTRL,
    KMOD_SHIFT,
    K_w,
    K_n,
    K_o,
    K_j,
    KEYUP,
    K_F1,
    MOUSEMOTION,
    MOUSEBUTTONUP,
)


### local imports

from ...pygamesetup import SERVICES_NS

from ...pygamesetup.constants import to_virtual_point

from ...config import APP_REFS

from ...loopman.exception import (
    QuitAppException,
    SwitchLoopException,
)

from ...htsl.main import open_htsl_link


class NoFileState:
    """Methods for the no-file state."""

    def no_file_event_handling(self):
        """Get and respond to events."""
        for event in SERVICES_NS.get_events():

            ### QUIT
            if event.type == QUIT:
                raise QuitAppException

            ### MOUSEMOTION

            elif event.type == MOUSEMOTION:
                self.no_file_on_mouse_motion(event)

            ### MOUSEBUTTONUP

            elif event.type == MOUSEBUTTONUP:
                self.no_file_on_mouse_release(event)

            ### KEYUP

            elif event.type == KEYUP:

                if event.key == K_F1:

                    open_htsl_link("nodezator://help.nodezator.pysite")

                elif (
                    event.key == K_j
                    and event.mod & KMOD_CTRL
                    and event.mod & KMOD_SHIFT
                ):

                    (APP_REFS.ea.show_user_log_contents())

            ### KEYDOWN

            elif event.type == KEYDOWN:

                ## Application related operations

                # quit
                if event.key == K_w and event.mod & KMOD_CTRL:
                    raise QuitAppException

                # create new file
                elif event.key == K_n and event.mod & KMOD_CTRL:
                    self.new()

                # open file
                elif event.key == K_o and event.mod & KMOD_CTRL:
                    self.open()

    def no_file_on_mouse_motion(self, event):
        """Act based on mouse motion event.

        event
            pygame.event.Event object of type pygame.MOUSEMOTION
            or similar object.
        """
        mouse_pos = to_virtual_point(event.pos)
        if self.menubar.get_hovered_menu(mouse_pos):
            raise SwitchLoopException(self.menubar)

    def no_file_on_mouse_release(self, event):
        """Act on mouse left button release.

        Act based on mouse position.
        """
        mouse_pos = to_virtual_point(event.pos)
        if self.menubar.get_hovered_menu(mouse_pos):
            raise SwitchLoopException(self.menubar)

    ### draw

    def no_file_draw(self):
        """Draw method for the 'no_file' state."""
        self.background.draw()

        self.separator.draw()
        self.menubar.draw_top_items()

        SERVICES_NS.update_screen()
