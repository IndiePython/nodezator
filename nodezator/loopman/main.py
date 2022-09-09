"""Loop-related tools for classes."""

### third-party imports

from pygame import QUIT

from pygame.event import get as get_events

from pygame.display import update


### local imports

from ..pygameconstants import FPS, maintain_fps

from ..our3rdlibs.behaviour import watch_window_size

from .exception import (
    ContinueLoopException,
    SwitchLoopException,
    QuitAppException,
)


class LoopHolder:
    def loop(self):

        ### if loop hold doesn't have a 'draw' method,
        ### assign pygame.display.update to the
        ### attribute

        try:
            self.draw
        except AttributeError:
            self.draw = update  # pygame.display.update

        ### set self as the loop holder
        loop_holder = self

        ### set a running flag and start the loop

        self.running = True

        while self.running:

            maintain_fps(FPS)

            watch_window_size()

            try:

                loop_holder.handle_input()
                loop_holder.update()
                loop_holder.draw()

            ## the sole purpose of this exception is to
            ## stop the execution flow of the try block and
            ## restart again at the top of the 'while' block,
            ## so we just pass, since this is exactly what
            ## happens
            except ContinueLoopException:
                pass

            except SwitchLoopException as err:

                ## set new loop holder
                loop_holder = err.loop_holder

                ## if loop holder has an enter method,
                ## execute it

                try:
                    method = loop_holder.enter
                except AttributeError:
                    pass
                else:
                    method()

    def exit_loop(self):
        self.running = False

    def handle_input(self):
        """Quit if 'x' on window is clicked."""
        for event in get_events():
            if event.type == QUIT:
                self.quit()

    def quit(self):
        raise QuitAppException

    def update(self):
        """Do nothing."""
