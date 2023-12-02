#import pygbag.aio as asyncio
import asyncio
import sys
import fractions
import statistics
from pygame import base 
from pygame import quit as quit_pygame
from pygame.display import update
import numpy
from nodezator.config import APP_REFS
from nodezator.pygamesetup import (
    SERVICES_NS,
    SCREEN,
    switch_mode,
    clean_temp_files,
    is_modal,
)
from nodezator.pygamesetup.constants import GENERAL_NS
from nodezator.colorsman.colors import WINDOW_BG
from nodezator.logman.main import get_new_logger
from nodezator.our3rdlibs.behaviour import are_changes_saved
from nodezator.loopman.exception import (
    ContinueLoopException,
    SwitchLoopException,
    QuitAppException,
    ResetAppException,
)
from nodezator.dialog import show_dialog_from_key
from nodezator.winman.main import perform_startup_preparations


### create logger for module
logger = get_new_logger(__name__)


STOPPED = False

def is_stopped():
    return STOPPED

def stop_running():
    global STOPPED
    STOPPED = True

def quit_callback(answer):
    print("*** answer:", answer)
    if answer == "quit":
        logger.info("User confirmed closing app even when there are unsaved changes.")
        stop_running()
    elif answer == "save_and_quit":
        APP_REFS.window_manager.save()
        stop_running()
    else:
        logger.info("User cancelled closing app due to existence of unsaved changes.")
    
async def main(filepath=None):
    filepath = "/data/data/app/assets/samples/test2.ndz"
    #print("filepath:", filepath)
    
    #SCREEN.fill(WINDOW_BG)
    #update()
    
    loop_holder = perform_startup_preparations(filepath)
    logger.info("Entering the application loop now.")
    
    while True:
        await asyncio.sleep(0)
        if is_modal():
            continue
        if is_stopped():
            break
            
        ### perform various checkups for this frame;
        ###
        ### stuff like maintaing a constant framerate and more
        SERVICES_NS.frame_checkups()
        ### run the GUD methods (check glossary for
        ### loop holder/methods/loop)
        try:
            loop_holder.handle_input()
            loop_holder.update()
            loop_holder.draw()
        ### catch exceptions as they happen
        ## the sole purpose of this exception is to stop
        ## the execution flow of the try block and restart
        ## again at the top of the 'while' block, so we
        ## just pass, since this is exactly what happens
        except ContinueLoopException:
            pass
        ## this exceptions sets a new object to become the
        ## loop holder; the new object is obtained from
        ## the 'loop_holder' attribute of the exception
        ## instance
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
                try:
                    method()
                except Exception as e:
                    print("*** MAIN", e)
                #
            #

        ## this exception exits means the user tried closing
        ## the application, which we do so here, unless
        ## there are unsaved changes, in which case we only
        ## proceed if the user confirms
        except QuitAppException:
            logger.info("User tried closing the app.")
            ## if we are on normal mode and changes are not saved,
            ## ask user what to do
            if GENERAL_NS.mode_name == 'normal' and not are_changes_saved():
                ## ask user
                show_dialog_from_key(
                    "close_app_dialog",
                    callback = quit_callback,
                )
                continue

            ### if we get to the point, we just perform extra admin
            ### tasks to exit the app and its loop

            logger.info("Closing app under expected circumstances.")

            clean_temp_files()

            quit_pygame()

            ## break out of the application loop
            break

        ## this exception serves to reset the app to an
        ## initial state, that is, when it is just launched,
        ## either with or without a file to be loaded

        except ResetAppException as obj:

            ### switch mode according to exception info
            switch_mode(obj)

            ### perform startup preparations, retrieving the chosen
            ### loop holder, just like we did before starting the
            ### mainloop at the beginning of this function
            loop_holder = perform_startup_preparations(obj.filepath)


        ## catch unexpected exceptions so we can quit pygame
        ## and log the exception before reraising

        except Exception as err:

            logger.exception("While running the application an unexpected exception ocurred. Doing clean up and reraising now.")

            quit_pygame()

            raise err
    print("*** STOPPED")
    quit_pygame()
    exit()

# This is the program entry point:
if __name__ == '__main__':
    asyncio.run(main())
    #filepath = None
    #if len(sys.argv) > 0:
    #    filepath = sys.argv[1]
    #asyncio.run(main(filepath))

# Do not add anything from here, especially sys.exit/pygame.quit
# asyncio.run is non-blocking on pygame-wasm and code would be executed
# right before program start main()
