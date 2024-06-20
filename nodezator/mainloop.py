"""Facility for application loop management."""

### third-party imports

# note: pygame is initialized in the pygameconstants.py
# module
from pygame import quit as quit_pygame

from pygame.display import update


### local imports and provisional screen filling

from .config import APP_REFS

from .pygamesetup import (
    SERVICES_NS,
    SCREEN,
    switch_mode,
    clean_temp_files,
)

from .pygamesetup.constants import GENERAL_NS

from .colorsman.colors import WINDOW_BG


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

from .our3rdlibs.behaviour import are_changes_saved, indicate_saved

from .loopman.exception import (
    ContinueLoopException,
    SwitchLoopException,
    QuitAppException,
    CloseFileException,
    ResetAppException,
)

from .dialog import create_and_show_dialog, show_dialog_from_key

from .winman.main import perform_startup_preparations

from .systemtesting import report_viewer

from .userprefsman.utils import save_test_settings_if_needed



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

        try:

            while True:

                ### perform various checkups for this frame;
                ###
                ### stuff like maintaing a constant framerate and more
                SERVICES_NS.frame_checkups()

                ### run the GUD methods (check glossary for
                ### loop holder/methods/loop)

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

        ## this exception means the user tried closing the application,
        ## which we do so here, unless there are unsaved changes,
        ## in which case we only proceed if the user confirms

        except QuitAppException:

            logger.info("User tried quitting the app.")

            ### if we are not in normal mode, ignore rest of the block by
            ### restarting loop

            if GENERAL_NS.mode_name != 'normal':
                continue

            ### if changes are saved, quit app right away

            if are_changes_saved():
                clean_and_quit_app()

            ### if changes are not saved, ask user what to do

            else:

                ## ask user

                try:
                    answer = show_dialog_from_key("quit_app_dialog")

                ## if a QuitAppException is raised here,
                ## it means the user tried closing the
                ## window; we assume the user really wants
                ## to leave the app, so we do it immediatelly

                except QuitAppException:

                    logger.info(
                        "User attempted closing window while the"
                        " quit dialog was on screen. Quitting now."
                    )

                    clean_and_quit_app()

                ## if user confirmed exiting, we just log the fact,
                ## perform extra admin tasks and quit the app

                if answer == "quit":

                    logger.info(
                        "User confirmed closing app even"
                        " when there are unsaved changes."
                    )

                    clean_and_quit_app()

                ## if user does not confirm quitting, we just
                ## log the fact and carry on with normal execution
                ## of the app

                else:

                    logger.info(
                        "User cancelled quitting app (there are"
                        " unsaved changes, so it may be the cause)."
                    )


        ## this exception means the user tried closing the loaded file,
        ## which we do so here, unless there are unsaved changes,
        ## in which case we only proceed if the user confirms

        except CloseFileException:

            logger.info("User tried closing the loaded file.")

            ### conditions when it is pointless to close a file and thus
            ### we ignore the rest of the block by restarting the loop

            ## this one should notify user
            if APP_REFS.wm.state_name == 'no_file':
                create_and_show_dialog("There's no loaded file to be closed.")

            ## this one should pass silently

            if GENERAL_NS.mode_name != 'normal':
                continue

            ### if changes are saved, close file right away

            if are_changes_saved():

                ### perform startup preparations, retrieving the chosen
                ### loop holder

                loop_holder = (

                    perform_startup_preparations(
                        filepath='',
                        after_closing_file=True,
                    )

                )

            ### if changes are not saved, ask user what to do

            else:

                ## ask user

                try:
                    answer = show_dialog_from_key("close_file_dialog")

                ## if a QuitAppException is raised here,
                ## it means the user tried closing the
                ## window; we assume the user actually wants
                ## to leave the app, ignoring unsaved changes so
                ## we do it

                except QuitAppException:

                    logger.info(
                        "User ignored the close file dialog, trying to"
                        " quit the app this time. Quitting now."
                    )

                    clean_and_quit_app()

                ## if user confirmed closing, we perform the needed
                ## setups

                if answer == "close":

                    logger.info(
                        "User confirmed closing file even"
                        " when there are unsaved changes."
                    )

                    ## ensure app indicates that there are no unsaved changes
                    indicate_saved()

                    ### perform startup preparations, retrieving the chosen
                    ### loop holder

                    loop_holder = (

                        perform_startup_preparations(
                            filepath='',
                            after_closing_file=True,
                        )

                    )

                elif answer == "save_and_close":

                    APP_REFS.wm.save()

                    ### perform startup preparations, retrieving the chosen
                    ### loop holder

                    loop_holder = (

                        perform_startup_preparations(
                            filepath='',
                            after_closing_file=True,
                        )

                    )

                ## if user does not confirm exiting,
                ## we avoid breaking out of the loop
                ## by going back to the beggining of the
                ## "while loop" with a "continue" statement

                else:

                    logger.info(
                        "User cancelled closing file (since there are"
                        " unsaved changes, it may be the cause)"
                    )


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

            ### use report viewer as loop holder instead if there's
            ### a system testing report

            if hasattr(obj, 'tests_report_data'):

                save_test_settings_if_needed(obj.tests_report_data)

                report_viewer.prepare_report(obj.tests_report_data)

                report_viewer.loop_holder = loop_holder
                loop_holder = report_viewer

            ### if user left a system testing session midway, notify
            ### via dialog

            elif hasattr(obj, 'left_system_testing_midway'):

                create_and_show_dialog(
                    (
                        "You left the system testing session midway,"
                        " which is fine. However, in case you want"
                        " system testing data to be properly gathered and"
                        " show/update the system testing report, you must"
                        " execute a system testing session until the end,"
                        " that is, until it finishes by itself."
                    ),
                    level_name='info',
                )

        ## catch unexpected exceptions so we can quit pygame
        ## and log the exception before reraising

        except Exception as err:

            logger.exception(
                "While running the application an unexpected"
                " exception ocurred. Doing clean up and"
                " reraising now."
            )

            logger.error(
                "The previously logged error ocurred during"
                f" {GENERAL_NS.mode_name!r} mode."
            )

            quit_pygame()

            raise err


## small utility

def clean_and_quit_app():

    quit_pygame()
    logger.info("Quitting under expected circumstances.")
    clean_temp_files()
    quit()
