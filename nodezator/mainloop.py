"""Facility for application loop management."""

### third-party imports

# note: pygame is initialized in the pygameconstants.py
# module
from pygame import quit as quit_pygame

from pygame.display import update


### local imports and provisional screen filling

from .config import APP_REFS

from .userprefsman.main import TEMP_FILE_SWAP

from .pygameconstants import (
    SCREEN,
    FPS,
    maintain_fps,
)

from .colorsman.colors import WINDOW_BG

from .our3rdlibs.behaviour import watch_window_size


## before going on, fill the screen with the window
## background color; this is an usability measure,
## since issues may arise while loading the application
## and/or filepath (if given), prompting the user for
## actions and we don't want the user to solve such issues
## having a complete black screen in the background, which
## we assume may be unnerving for the user

SCREEN.fill(WINDOW_BG)
update()


from .logman.main import get_new_logger

from .our3rdlibs.behaviour import (
    are_changes_saved,
    remove_buffer,
)

from .loopman.exception import (
    ContinueLoopException,
    SwitchLoopException,
    QuitAppException,
)

from .dialog import show_dialog_from_key

from .winman.main import perform_startup_preparations


### create logger for module
logger = get_new_logger(__name__)


def run_app(filepath=None):
    """Run application by starting the loop.

    Parameters
    ==========
    filepath (string or None)
        the path to a file to be opened. May be None, though,
        in which case the application starts without a
        loaded file.
    """
    ### perform startup preparations, storing the output
    ### of this operation as a reference to the loop holder
    ### object to be used;
    ###
    ### this loop holder will be either the window manager
    ### or the splash screen
    loop_holder = perform_startup_preparations(filepath)

    ### start running the application loop

    logger.info("Entering the application loop.")

    while True:

        ### keep a constant framerate
        maintain_fps(FPS)

        ### keep an eye on the window size
        watch_window_size()

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
                method()

        ## this exception exits means the user tried closing
        ## the application, which we do so here, unless
        ## there are unsaved changes, in which case we only
        ## proceed if the user confirms

        except QuitAppException:

            logger.info("User tried closing the app.")

            ## if changes are not saved, ask user what to do

            if not are_changes_saved():

                ## ask user

                try:
                    answer = show_dialog_from_key("close_app_dialog")

                ## if a QuitAppException is raised here,
                ## it means the user tried closing the
                ## window; we assume the user really wants
                ## to leave the app, so we break out of the
                ## application loop

                except QuitAppException:

                    logger.info(
                        "User ignored the quit dialog," " trying to close the app again"
                    )

                    break

                ## if user confirmed exiting, we just log
                ## the fact, since we are inevitably going
                ## to meet
                ## the "break" statement which will throw
                ## us out of the application loop

                if answer == "quit":

                    logger.info(
                        "User confirmed closing app even"
                        " when there are unsaved changes."
                    )

                elif answer == "save_and_quit":
                    APP_REFS.window_manager.save()

                ## if user does not confirm exiting,
                ## we avoid breaking out of the loop
                ## by going back to the beggining of the
                ## "while loop" with a "continue" statement

                else:

                    logger.info(
                        "User cancelled closing app due to"
                        " existence of unsaved changes."
                    )

                    continue

            ## break out of the application loop
            break

        ## catch unexpected exceptions so we can quit pygame
        ## and log the exception before reraising

        except Exception as err:

            logger.exception(
                "While running the application an unexpected"
                " exception ocurred. Doing clean up and"
                " reraising now."
            )

            quit_pygame()

            raise err

    logger.info("Closing app under expected circumstances.")

    remove_buffer()

    APP_REFS.temp_filepaths_man.ensure_removed()

    if TEMP_FILE_SWAP.exists():
        TEMP_FILE_SWAP.unlink()

    quit_pygame()
