"""Loop-related tools for classes."""

### standard library imports

from functools import partial
from operator import methodcaller

### third-party import
from pygame.locals import QUIT


### local imports

from ..pygamesetup import SERVICES_NS

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
            self.draw = partial(methodcaller('update_screen'), SERVICES_NS)

        ### set self as the loop holder
        loop_holder = self

        ### create a running flag to keep the inner loop going
        self.running = True

        ### start the general loop

        while True:

            ### run app loop within a try clause

            try:

                ### run loop

                while self.running:

                    ### perform various checkups for this frame;
                    ###
                    ### stuff like maintaing a constant framerate and more
                    SERVICES_NS.frame_checkups()

                    ### perform the loop operations

                    loop_holder.handle_input()
                    loop_holder.update()
                    loop_holder.draw()

                ### when we leave the loop above, also leave the outer loop
                break

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
        for event in SERVICES_NS.get_events():
            if event.type == QUIT:
                self.quit()

    def quit(self):
        raise QuitAppException

    def update(self):
        """Do nothing."""
