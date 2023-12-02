"""Loop-related tools for classes."""

### standard library imports
import asyncio
from functools import partial
from operator import methodcaller

### third-party import
from pygame.locals import QUIT


### local imports

from ..pygamesetup import SERVICES_NS, set_modal

from .exception import (
    ContinueLoopException,
    SwitchLoopException,
    QuitAppException,
)


class LoopHolder:

    async def async_loop(self, callback):
        ### set self as the loop holder
        loop_holder = self

        ### set a running flag and start the loop

        self.running = True

        while self.running:
            await asyncio.sleep(0)            
            ### perform various checkups for this frame;
            ###
            ### stuff like maintaing a constant framerate and more
            SERVICES_NS.frame_checkups()

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
        set_modal(False)
        try:
            if callback is not None:
                callback()
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
                print("method: ", method)
                method()
                print("method: executed")
        except Exception as e:
            raise e
    
    def loop(self, callback = None):

        ### if loop hold doesn't have a 'draw' method,
        ### assign update_screen to the attribute

        try:
            self.draw
        except AttributeError:
            self.draw = partial(methodcaller('update_screen'), SERVICES_NS)

        set_modal(True)
        asyncio.get_running_loop().create_task(self.async_loop(callback))


    def exit_loop(self):
        self.running = False

    def handle_input(self):
        """Quit if 'x' on window is clicked."""
        for event in SERVICES_NS.get_events():
            if event.type == QUIT:
                self.quit()

    def quit(self):
        set_modal(False)
        #raise QuitAppException

    def update(self):
        """Do nothing."""
