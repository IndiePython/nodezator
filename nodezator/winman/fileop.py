"""File operations for the window manager class."""

### standard library import
from pathlib import Path


### local imports

from config import APP_REFS

from userprefsman.main import USER_PREFS

from appinfo import NATIVE_FILE_EXTENSION

from dialog import (
              create_and_show_dialog,
              show_dialog_from_key,
            )

from fileman.main import (
                    select_path,
                    create_path,
                  )

from ourstdlibs.path import (
                       get_swap_path,
                       get_custom_path_repr,
                       save_timestamped_backup,
                     )

from ourstdlibs.pyl import load_pyl, save_pyl

from loopman.exception import SwitchLoopException

from our3rdlibs.behaviour import (
                            are_changes_saved,
                            indicate_saved,
                            set_status_message,
                          )

from recentfile import store_recent_file


### constants

## different captions for when invoking the file manager

NEW_FILE_CAPTION = (
   "Type path wherein to save new"
  f" '{NATIVE_FILE_EXTENSION}' file"
)


# when requesting file to be opened

OPEN_FILE_CAPTION = (
  f"Select '{NATIVE_FILE_EXTENSION}' file to open"
)


# when requesting file to be opened

SAVE_AS_CAPTION = (
   "Create new path wherein to save"
  f" '{NATIVE_FILE_EXTENSION}' file"
)



### class definition

class FileOperations:
    """Contains methods related to files."""

    def new(self):
        """Create a new file."""
        ### prompt user to pick filepath from file manager
        paths = create_path(caption=NEW_FILE_CAPTION)

        ### respond according to whether paths were given

        ## if paths were given, it is a single one, we
        ## should assign it to 'filepath' variable
        if paths: filepath = paths[0]

        ## if the user didn't provide paths, though,
        ## return earlier
        else: return

        ### if the path don't have the right extension,
        ### ask user if we should add it ourselves or
        ### cancel the operation (in which case we return)

        if filepath.suffix != NATIVE_FILE_EXTENSION:
            
            message = (
               "Path provided must have a "
              f"{NATIVE_FILE_EXTENSION} extension."
               " Want us to add it for you?"
            )

            buttons = [
              ("Yes", True),
              ("No, cancel creating new file", False)
            ]

            answer = create_and_show_dialog(message, buttons)

            if not answer: return

            else: filepath = (
                    filepath
                    .with_suffix
                    (NATIVE_FILE_EXTENSION)
                  )

        ### if filepath already exists, prompt user about
        ### what to do

        if filepath.is_file():

            answer = show_dialog_from_key(
                       'replace_existing_file_dialog'
                     )

            if   answer == 'replace': pass
            elif answer ==   'abort': return

        ### prompt user for action in case the data for a
        ### new file is provided but there are unsaved
        ### changes in the current one being edited

        if not are_changes_saved():

            ## XXX review comments inside this
            ## "if not are_changes_saved():" block

            answer = show_dialog_from_key(
                       'create_new_while_unsaved_dialog'
                     )

            if answer == 'open_new':

                ### make it appear as if there are no
                ### unsaved changes; this will cause the
                ### current changes to be ignored and
                ### thereby lost when the newly created
                ### file is opened
                indicate_saved()

            elif answer == 'save_first': self.save()

            elif answer == 'abort': return

        ## if a swap file exists, remove it

        swap_path = get_swap_path(filepath)

        try: swap_path.unlink()
        except FileNotFoundError: pass

        ### save file
        save_pyl({}, filepath)

        ### finally, load (open) the file
        self.open(filepath)

    def open(self, filepath=None):
        """Open a new file.

        filepath (pathlib.Path instance)
            Path to the file to be opened.
        """
        ### if no filepath is provided, prompt user to
        ### pick one from the file manager

        if not filepath:

            ## pick path

            paths = select_path(
                      caption=OPEN_FILE_CAPTION
                    )

            ## respond according to number of paths given

            length = len(paths)

            if length == 1:
                filepath = paths[0]

            elif length > 1:

                show_dialog_from_key(
                  'expected_single_path_dialog'
                )

                return

            else: filepath = None

        ### if even so the user didn't provide a filepath,
        ### return earlier
        if not filepath: return

        ### prompt user for action in case a file is provided
        ### but there are unsaved changes in the current one

        if filepath and not are_changes_saved():

            answer = show_dialog_from_key(
                            'open_new_while_unsaved_dialog')

            if   answer == "open new": pass
            elif answer == "save first": self.save()
            elif answer == "abort": return


        ### TODO checks below should be made before the
        ### beginning of the "if" block, so that you
        ### can notify the user in case they don't work,
        ### instead of just reaching the end of the method
        ### silently (for instance, it would be good to
        ### notify user that the file is of the wrong
        ### extension if the corresponding condition
        ### indicates so);
        ###
        ### also, review this method to guarantee we deal
        ### properly with all possible use-cases of its
        ### usage; a simple flowchart on paper should
        ### probably enough to see all possible routes
        ### the execution flow may go;

        ### but if the user provided one existing regular
        ### file with the right extension, we start
        ### processing it for usage

        if (
               filepath.is_file()
           and filepath.suffix == NATIVE_FILE_EXTENSION
        ):

            ### before loading the file, let's check the
            ### preexistence of a swap file in the
            ### swap path attribute, since it might change
            ### how we'll approach the file loading

            ## generate swap path
            swap_path = get_swap_path(filepath)

            ## if swap file exists there might have been a
            ## crash which forced the program to exit,
            ## leaving the recent changes in the swap file
            ## before the user could save them; thus, we
            ## prompt the user to decide which action to
            ## perform:

            if swap_path.is_file():

                answer = show_dialog_from_key(
                           "swap_exists_dialog"
                         )

                # load original file (ignore swap)

                if answer == "load_original":

                    swap_path.unlink()

                    source_contents = (
                      filepath.read_text(encoding='utf-8')
                    )

                    swap_path.write_text(
                                source_contents,
                                encoding='utf-8',
                              )

                # load swap file (ignore original)

                elif answer == "load_swap":

                    ### XXX review this block

                    ### TODO also prevent people from
                    ### - accidentaly - clicking the button
                    ### that leads here when the dialog
                    ### comes up;

                    # save backup for the filepath

                    save_timestamped_backup(
                      filepath,
                      USER_PREFS['NUMBER_OF_BACKUPS']
                    )

                    # copy swap file contents into
                    # source file

                    swap_contents = \
                    swap_path.read_text(encoding="utf-8")

                    filepath.write_text(swap_contents,
                                        encoding="utf-8")

                else: return

            ## otherwise we just copy the source
            ## contents into it

            else:

                # copy source file text to swap file

                source_contents = \
                        filepath.read_text(encoding='utf-8')

                swap_path.write_text(
                          source_contents, encoding='utf-8')

            ### store both paths for access throughout the
            ### system

            ## store source path
            APP_REFS.source_path = filepath

            ## store swap path

            # admin task: remove existing swap if present
            # and different from the one being loaded
            # (this will happen when loading a file when
            # there is another one already loaded)

            try: current_swap = APP_REFS.swap_path

            except AttributeError: pass

            else:

                if not current_swap.samefile(swap_path):
                    current_swap.unlink()

            APP_REFS.swap_path = swap_path

            ### clean up native format json data that may
            ### exist from previous session
            APP_REFS.data.clear()

            ### replace such data with new native format
            ### json data loaded from the file to be opened
            APP_REFS.data = load_pyl(APP_REFS.source_path)

            ### store filepath as a recently open file, so
            ### it is available in the "File > Open recent"
            ### command in the menubar
            store_recent_file(APP_REFS.source_path)

            ### finally prepare the application for a new
            ### session, draw the window manager and
            ### restart the loop making the window manager
            ### the loop holder
            ###
            ### drawing is important here cause the user
            ### may accidentally keep the mouse over the
            ### menubar when the file finishes loading,
            ### which would make it so the menu would
            ### be the loop holder, thus the graph
            ### objects would not be initially drawn
            ### on the screen

            self.prepare_for_new_session()

            self.draw()

            raise SwitchLoopException

    def perform_startup_preparations(self, filepath):
        """Perform tasks for startup and return loop holder.

        Depending on whether or not the "filepath" argument
        is a valid path to be loaded, we perform specific
        tasks and return a reference to the loop holder to
        be used.

        This loop holder will be either this window manager
        itself or the splash screen. The splash screen is
        only used if there wasn't a valid path to be
        loaded.

        Parameters
        ==========
        filepath (string or None)
            if None, it means no file must be loaded;
            otherwise, it is a string representing the
            path for a file to be loaded.

        Future implementation
        =====================

        in the future, the splash screen should be shown
        first, while the window prepares for a new session,
        and only then we will decide whether it will be
        kept on the screen or not.
        """

        ### if the filepath receive is not None, try
        ### opening the filepath, taking additional steps
        ### depending on the outcome

        if filepath is not None:

            ### try opening the filepath
            try: self.open(filepath)

            ### when the operation succeeds, a manager
            ### switch exception is raised to indicate
            ### the window manager should take control
            ### of the app;
            ###
            ### we prevent the exception to bubble up,
            ### though, since there would be no "except"
            ### clause to catch this exception at the
            ### spot where this method is executed;
            ###
            ### instead, we return a reference to this
            ### window manager, which will be used as
            ### the loop holder
            except SwitchLoopException: return self

        ### if the filepath is None, or the operation to
        ### load it fails, the execution flow of this
        ### method reaches this spot;
        ###
        ### in such case, we prepare the window
        ### manager for a new session (this call would
        ### not be necessary if we had loaded a file,
        ### because it would have already been called
        ### inside self.open());
        self.prepare_for_new_session()

        ### finally, return a reference to the splash
        ### screen, after calling the drawing operation
        ### of this window manager, so its objects appear
        ### behind the splash screen

        self.draw()
        return self.splash_screen

    def save(self):
        """Trigger pos handler to save position data."""

        ### if all changes are already saved, we notify
        ### the user via the status bar and cancel saving
        ### the file by returning earlier

        if are_changes_saved():

            message = (
              "Didn't save because changes are already saved."
            )

            set_status_message(message)

            return

        ### pass content from source to backup file

        save_timestamped_backup(
          APP_REFS.source_path,
          USER_PREFS['NUMBER_OF_BACKUPS']
        )

        ### save changes on source path
        self.save_data()

        ### store changes from source on the swap file

        APP_REFS.swap_path.write_text(
          APP_REFS.source_path.read_text(encoding='utf-8'),
          encoding='utf-8'
        )

        ### perform other administrative tasks

        # XXX to be updated and uncommented once
        # the undo/redo feature is implemented

        ## clear undo/redo buffers
        #APP_REFS.ea.clear_buffers()

        ## indicate that changes were saved
        indicate_saved()

        ### notify success via statusbar

        set_status_message(
          "Changes were successfully saved."
        )

    def save_as(self):
        """Save data in new file and keep using new file.

        Works by saving the data in the new location
        provided by the user via the file manager
        session we start and using that new location from
        then on.
        
        Other admin taks are also performed like deleting
        the swap file for the original file.
        """
        ### prompt user to pick filepath from file manager
        paths = create_path(caption=SAVE_AS_CAPTION)

        ### respond according to whether paths were given

        ## if paths were given, it is a single one, we
        ## should assign it to 'filepath' variable
        if paths:
            filepath = paths[0]

        ## if the user didn't provide paths, though,
        ## return earlier
        else: return

        ### perform tasks to save current file in the
        ### provided path, using it from now on

        ### if the path don't have the right extension,
        ### ask user if we should add it ourselves or
        ### cancel the operation (in which case we return)

        if filepath.suffix != NATIVE_FILE_EXTENSION:
            
            ## build custom message

            message = (
               "Path provided must have a"
              f" {NATIVE_FILE_EXTENSION} extension."
               " Want us to add it for you?"
            )

            ## each button is represented by a pair
            ## consisting of the text of the button and
            ## the value the dialog returns when we
            ## click it

            buttons = [
              ("Yes", True),
              ("No, cancel saving new file", False)
            ]

            ## display the dialog and store the answer
            ## provided by the user when clicking
            answer = create_and_show_dialog(message, buttons)

            ## if the answer is False, then cancel operation
            if not answer: return

            ## otherwise apply the correct extension

            else: filepath = \
                  filepath.with_suffix(NATIVE_FILE_EXTENSION)

        ### if path already exists, prompt user to confirm
        ### whether we should override it

        if filepath.exists():

            ## build custom message

            message = (
              f"The path provided ({filepath}) already exists."
               " Should we override it?"
            )

            ## each button is represented by a pair
            ## consisting of the text of the button and
            ## the value the dialog returns when we
            ## click it

            buttons = [
              ('Ok', True),
              ('Cancel', False)
            ]

            ## display the dialog and store the answer
            ## provided by the user when clicking
            answer = create_and_show_dialog(message, buttons)

            ### if the answer is False, then we shouldn't
            ### override, so we cancel the operation by
            ### returning
            if not answer: return

        ### otherwise we proceed

        ### backup the current source path
        original_source = APP_REFS.source_path

        ### assign the new file as the source the be used
        ### instead
        APP_REFS.source_path = filepath

        ### try saving current data on the new path
        try: self.save_data()

        ### if something goes wrong, restore the original
        ### source, notify user and cancel the operation
        ### by returning

        except Exception as err:
            
            ## restore source
            APP_REFS.source_path = original_source
            
            ## build and display error message

            error_message = (
               "Something went wrong while trying to save"
              f" the new file. The error message: {err}"
            )

            create_and_show_dialog(error_message)

            ## cancel by returning
            return

        ### otherwise, again, we proceed

        ### delete the contents of the current swap path
        APP_REFS.swap_path.unlink()

        ### create a swap path for the new source and store
        ### it

        swap_path          = get_swap_path(filepath)
        APP_REFS.swap_path = swap_path

        ### save contents of source in the swap path

        source_contents = \
                filepath.read_text(encoding='utf-8')

        swap_path.write_text(
                  source_contents, encoding='utf-8')

        ### get a custom string representation for the source
        path_str = get_custom_path_repr(filepath)

        ### update caption to show the new loaded path
        self.update_caption(path_str)

        ### notify user by displaying message in the
        ### statusbar

        set_status_message(
          f"Using new file from now on {path_str}"
        )

    def save_data(self):
        """Save json data on filepath.

        Support method for the save methods self.save() and
        self.save_as().
        """
        save_pyl(APP_REFS.data, APP_REFS.source_path)

    def reload(self):
        """Reload current file."""
        ### prompt user for action in case there are unsaved
        ### changes

        if not are_changes_saved():

            answer = show_dialog_from_key(
                       "reload_unsaved_dialog"
                     )

            if answer == "reload":

                ### make it appear as if there are no
                ### unsaved changes; this will cause the
                ### current changes to be ignored and
                ### thereby lost when the file is reloaded
                ### (opened again)
                indicate_saved()

            elif answer == "abort": return

        ### remove swap file
        APP_REFS.swap_path.unlink()

        ### finally reopen the current file
        self.open(APP_REFS.source_path)
