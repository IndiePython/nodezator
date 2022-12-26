"""Loop-related tools for classes."""

### third-party imports

from pygame import QUIT


### local imports

from ..pygamesetup import (

    get_events,
    update_screen,
    frame_checkups,

)

from .exception import (
    ContinueLoopException,
    SwitchLoopException,
    QuitAppException,
)


class LoopHolder:

    def loop(self):

        ### if loop hold doesn't have a 'draw' method,
        ### assign update_screen to the attribute

        try:
            self.draw
        except AttributeError:
            self.draw = update_screen

        ### set self as the loop holder
        loop_holder = self

        ### set a running flag and start the loop

        self.running = True

        while self.running:

            ### perform various checkups for this frame;
            ###
            ### stuff like maintaing a constant framerate and more
            frame_checkups()

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
