"""File operations for the window manager class."""

### standard library import
from pathlib import Path


### local imports

from ..config import APP_REFS

from ..userprefsman.main import USER_PREFS, TEMP_FILE_SWAP

from ..appinfo import NATIVE_FILE_EXTENSION

from ..dialog import (
    create_and_show_dialog,
    show_dialog_from_key,
)

from ..fileman.main import select_paths

from ..ourstdlibs.path import (
    get_swap_path,
    get_custom_path_repr,
    save_timestamped_backup,
)

from ..ourstdlibs.pyl import load_pyl, save_pyl

from ..our3rdlibs.userlogger import USER_LOGGER

from ..our3rdlibs.behaviour import (
    are_changes_saved,
    indicate_saved,
    indicate_unsaved,
    set_status_message,
)

from ..loopman.exception import SwitchLoopException

from ..logman.main import get_new_logger

from ..recentfile import store_recent_file


### create logger for module
logger = get_new_logger(__name__)


### constants

## different captions for when invoking the file manager

# when opening file
OPEN_FILE_CAPTION = f"Select '{NATIVE_FILE_EXTENSION}' file to open"

# when saving regular file as a new one
# or temporary file as a regular one
SAVE_AS_CAPTION = "Select/create new file wherein to save"


### class definition


class FileOperations:
    """Contains methods related to files."""
    def __init__(self):
        self.filepath = None
        self.swap_path  = None
        self.is_temp_file = None
        
    def do_new(self):
        ### generate new temporary filepath
        filepath = APP_REFS.temp_filepaths_man.get_new_temp_filepath()

        ### save file
        save_pyl({}, filepath)

        ### finally, load (open) the file
        self.open(filepath)

    def new_actions_callback(self, answer):
        ## XXX review comments in this block
        if answer == "open_new":
            ### make it appear as if there are no
            ### unsaved changes; this will cause the
            ### current changes to be ignored and
            ### thereby lost when the newly created
            ### file is opened
            indicate_saved()

            ### delete swap path contents
            APP_REFS.swap_path.unlink()

        elif answer == "save_first":
            self.save()

        else:
            return
            
        self.do_new()
        
    def discard_changes_callback(self, answer):
        if answer:
            ### make it appear as if there are no
            ### unsaved changes; this will cause the
            ### current changes to be ignored and
            ### thereby lost when the newly created
            ### file is opened
            indicate_saved()
            self.do_new()
    
    def new(self):
        """Create a new file."""
        if are_changes_saved():
            ### if there are not and there's a file loaded, it means it
            ### is a regular file, so delete its swap file
            try:
                APP_REFS.source_path
            except AttributeError:
                pass
            else:
                APP_REFS.swap_path.unlink()
            self.do_new()
            return
            
        ### prompt user for action if there are unsaved
        ### changes in the loaded file

        ### whether loaded file is temporary

        if (
            APP_REFS.temp_filepaths_man.is_temp_path(
                APP_REFS.source_path
            )
        ):

            create_and_show_dialog(

                (
                    "There's a temporary new file already"
                    " being edited. Should we discard the"
                    " contents and create a new one?"
                ),

                buttons=(

                    ("Yes", True),
                    ("Abort", False),

                ),
                level_name="warning",
                dismissable=True,
                callback = self.discard_changes_callback,
            )

        else:

            show_dialog_from_key(
                "create_new_while_unsaved_dialog",
                callback = self.new_actions_callback,
            )

    def load_file(self):
        ### try loading the file, storing its data
        try:
            loaded_data = load_pyl(self.filepath)

        ### if loading fails abort opening the file by
        ### leaving this method after notifying the
        ### user of the problem

        except Exception as err:

            message = "An error occurred while trying to" " open a file."

            logger.exception(message)

            USER_LOGGER.exception(message)

            create_and_show_dialog(
                (
                    "An error ocurred while trying to"
                    f" open {self.filepath}. Check the user"
                    " log (<Ctrl+Shift+j>) for details."
                ),
                level_name="error",
            )

            return

        ### if the given filepath is temporary or the swap path
        ### for the regular file does not exist, we copy the
        ### source contents into it

        if self.is_temp_file or not self.swap_path.is_file():

            source_contents = self.filepath.read_text(encoding="utf-8")

            self.swap_path.write_text(
                source_contents,
                encoding="utf-8",
            )

        ### store both paths for access throughout the
        ### system

        ## store source path
        APP_REFS.source_path = self.filepath

        ## store swap path

        # admin task for regular files: remove existing swap
        # if present and different from the one being loaded
        # (this will happen when loading a file when there is
        # another one already loaded)

        if not self.is_temp_file:

            try:
                current_swap = APP_REFS.swap_path

            except AttributeError:
                pass

            else:

                if not current_swap.samefile(self.swap_path):
                    current_swap.unlink()

        APP_REFS.swap_path = self.swap_path

        ### clean up native format data that may
        ### exist from previous session
        APP_REFS.data.clear()

        ### replace such data with new native format
        ### data loaded from the file to be opened
        APP_REFS.data = loaded_data

        ### if filepath is not temporary, store it as a recently
        ### open file, so it is available in the menubar under
        ### the "File > Open recent" submenu
        if not self.is_temp_file:
            store_recent_file(APP_REFS.source_path)

        ### finally,
        ### - prepare the application for a new session
        ### - indicate file as unsaved if it is temporary
        ### - draw the window manager
        ### - restart the loop making the window manager
        ###   the loop holder
        ###
        ### drawing is important here cause the user
        ### may accidentally keep the mouse over the
        ### menubar when the file finishes loading,
        ### which would make it so the menu would
        ### be the loop holder, thus the graph
        ### objects would not be initially drawn
        ### on the screen

        self.prepare_for_new_session()

        if self.is_temp_file:
            indicate_unsaved()

        self.draw()

        raise SwitchLoopException

    def swap_file_callback(self, answer):
        # load original file (ignore swap)
        if answer == "load_original":
            self.swap_path.unlink()
            source_contents = (
                self.filepath.read_text(encoding="utf-8")
            )

            self.swap_path.write_text(
                source_contents,
                encoding="utf-8",
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
                self.filepath,
                USER_PREFS["NUMBER_OF_BACKUPS"],
            )

            # copy swap file contents into
            # source file

            swap_contents = self.swap_path.read_text(encoding="utf-8")

            self.filepath.write_text(
                swap_contents,
                encoding="utf-8",
            )

        else:
            return
            
        self.load_file()
        
    def verify_temp_file(self):
        ### store boolean indicating whether or not the given path
        ### is of a temporary file
        self.is_temp_file = (
            APP_REFS.temp_filepaths_man.is_temp_path(self.filepath)
        )

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
            self.filepath.is_file()
            and self.filepath.suffix.lower() == NATIVE_FILE_EXTENSION
        ):

            ### perform actions depending on whether filepath is a
            ### temporary file or not

            if self.is_temp_file:
                self.swap_path = TEMP_FILE_SWAP

            else:

                ### before loading the file, let's check the
                ### preexistence of a swap file in the
                ### swap path attribute, since it might change
                ### how we'll approach the file loading

                ## generate swap path
                self.swap_path = get_swap_path(self.filepath)

                ## if swap file exists there might have been a
                ## crash which forced the program to exit,
                ## leaving the recent changes in the swap file
                ## before the user could save them; thus, we
                ## prompt the user to decide which action to
                ## perform:

                if self.swap_path.is_file():

                    show_dialog_from_key(
                        "swap_exists_dialog",
                        callback = self.swap_file_callback,
                    )
                    return

            self.load_file()

    def do_open_callback(self, answer):
        if answer == "open new":
            pass
        elif answer == "save first":
            self.save()
        else:
            return
        self.verify_temp_file()
    
    def do_open(self):
        ### prompt user for action in case a file is provided
        ### but there are unsaved changes in the current one
        if self.filepath and not are_changes_saved():
            show_dialog_from_key(
                "open_new_while_unsaved_dialog",
                callback = self.do_open_callback,
            )
        else:
            self.verify_temp_file()
            
    def open_callback(self, paths):
        ## respond according to number of paths given
        length = len(paths)

        if length == 1:
            filepath = paths[0]

        elif length > 1:

            show_dialog_from_key(
                "expected_single_path_dialog"
            )
            return

        else:
            filepath = None

        ### if even so the user didn't provide a filepath,
        ### return earlier
        if not filepath:
            return
            
        self.filepath = filepath
        self.do_open()
    
    
    def open(self, filepath=None):
        """Open a new file.
        filepath (pathlib.Path instance)
            Path to the file to be opened.
        """
        ### if no filepath is provided, prompt user to
        ### pick one from the file manager
        if not filepath:
            ## pick path
            select_paths(caption=OPEN_FILE_CAPTION, callback = self.open_callback)
        else:
            self.filepath = filepath
            self.do_open()
        
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
        filepath (string)
            if empty, it means no file must be loaded;
            otherwise, it is a string representing the
            path for a file to be loaded.

        Future implementation
        =====================

        in the future, the splash screen should be shown
        first, while the window prepares for a new session,
        and only then we will decide whether it will be
        kept on the screen or not.
        """
        ### clean loaded file data, if any
        clean_loaded_file_data()

        ### if a filepath is received, try opening it,
        ### taking additional steps depending on the outcome

        if filepath:

            ### try opening the filepath
            try:
                self.open(Path(filepath))

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
            except SwitchLoopException:
                return self

        ### if the filepath was an empty string, or the operation
        ### to load it fails, the execution flow of this method
        ### reaches this spot;
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
        ### the saving mechanism is different if a temporary file
        ### is loaded;
        ###
        ### if it is the case, we delegate the saving an appropriate
        ### method and exit this one by returning

        if (
            APP_REFS.temp_filepaths_man.is_temp_path(
                APP_REFS.source_path
            )
        ):

            self.save_as()
            return

        ### if all changes are already saved, we notify
        ### the user via the status bar and cancel saving
        ### the file by returning earlier

        if are_changes_saved():

            message = "Didn't save because changes are already saved."

            set_status_message(message)

            return

        ### pass content from source to backup file

        save_timestamped_backup(APP_REFS.source_path, USER_PREFS["NUMBER_OF_BACKUPS"])

        ### save changes on source path
        self.save_data()

        ### store changes from source on the swap file

        APP_REFS.swap_path.write_text(
            APP_REFS.source_path.read_text(encoding="utf-8"), encoding="utf-8"
        )

        ### perform other administrative tasks

        # XXX to be updated and uncommented once
        # the undo/redo feature is implemented

        ## clear undo/redo buffers
        # APP_REFS.ea.clear_buffers()

        ## indicate that changes were saved
        indicate_saved()

        ### notify success via statusbar

        set_status_message("Changes were successfully saved.")

    def perform_save_overwrite(self):        
        ### backup the current source path
        original_source = APP_REFS.source_path

        ### assign the new file as the source the be used
        ### instead
        APP_REFS.source_path = self.filepath

        ### try saving current data on the new path
        try:
            self.save_data()

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

        swap_path = get_swap_path(self.filepath)
        APP_REFS.swap_path = swap_path

        ### save contents of source in the swap path

        source_contents = self.filepath.read_text(encoding="utf-8")

        swap_path.write_text(source_contents, encoding="utf-8")

        ### store new path as a recently open file, so it is
        ### available in the menubar under the "File > Open recent"
        ### submenu
        store_recent_file(APP_REFS.source_path)

        ### get a custom string representation for the source
        path_str = get_custom_path_repr(self.filepath)

        ### update caption to show the new loaded path
        self.put_path_on_caption(path_str)

        ### notify user by displaying message in the
        ### statusbar
        set_status_message(f"Using new file from now on {path_str}")

    def save_overwrite_callback(self, answer):        
        ### if the answer is False, then we shouldn't
        ### override, so we cancel the operation by
        ### returning
        if not answer:
            return
        self.perform_save_overwrite()
        
    def do_save_as(self):
        if not self.filepath.exists():
            self.perform_save_overwrite()
            return
            
        ### if path already exists, prompt user to confirm
        ### whether we should override it

        ## build custom message

        message = (
            f"The path provided ({self.filepath}) already exists."
            " Should we override it?"
        )

        ## each button is represented by a pair
        ## consisting of the text of the button and
        ## the value the dialog returns when we
        ## click it

        buttons = [("Ok", True), ("Cancel", False)]

        ## display the dialog and store the answer
        ## provided by the user when clicking
        create_and_show_dialog(
            message, 
            buttons,
            callback = self.save_overwrite_callback,
            )
    
    def add_extension_callback(self, answer):
        ## if the answer is False, then cancel operation
        if not answer:
            return
        ## otherwise apply the correct extension
        self.filepath = self.filepath.with_suffix(NATIVE_FILE_EXTENSION)
        self.do_save_as()
    
    def save_as_callback(self, paths):
        ### respond according to whether paths were given

        ## if paths were given, it is a single one, we
        ## should assign it to 'filepath' variable
        if paths:
            self.filepath = paths[0]

        ## if the user didn't provide paths, though,
        ## return earlier
        else:
            return


        ### perform tasks to save current file in the
        ### provided path, using it from now on

        if self.filepath.suffix == NATIVE_FILE_EXTENSION:
            self.do_save_as()
            return

        ### if the path doesn't have the right extension,
        ### ask user if we should add it ourselves or
        ### cancel the operation (in which case we just return)

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

        buttons = [("Yes", True), ("No, cancel saving new file", False)]

        ## display the dialog and store the answer
        ## provided by the user when clicking
        create_and_show_dialog(
            message, 
            buttons,
            callback = self.add_extension_callback,
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

        select_paths(
            caption=SAVE_AS_CAPTION,
            path_name="new_file_name.ndz",
            callback = self.save_as_callback,
        )

    def save_data(self):
        """Save data on filepath.

        Support method for the save methods self.save() and
        self.save_as().
        """
        save_pyl(APP_REFS.data, APP_REFS.source_path)

    def reload_callback(self, answer):
        if answer == "reload":

            ### make it appear as if there are no
            ### unsaved changes; this will cause the
            ### current changes to be ignored and
            ### thereby lost when the file is reloaded
            ### (opened again)
            indicate_saved()
            
            ### remove swap file
            APP_REFS.swap_path.unlink()
            
            ### finally reopen the current file
            self.open(APP_REFS.source_path)

    
    def reload(self):
        """Reload current file."""
        ### the reloading mechanism doesn't apply to temporary files;
        ###
        ### if it is the case, we notify the user and exit this method

        if APP_REFS.temp_filepaths_man.is_temp_path(APP_REFS.source_path):

            create_and_show_dialog(
                "Cannot reload temporary files.",
                level_name="warning",
            )
            return

        ### prompt user for action in case there are unsaved
        ### changes

        if are_changes_saved():
            ### remove swap file
            APP_REFS.swap_path.unlink()

            ### finally reopen the current file
            self.open(APP_REFS.source_path)
        else:
            show_dialog_from_key(
                "reload_unsaved_dialog",
                callback = self.reload_callback,
            )


### utility

def clean_loaded_file_data():
    """Perform setups to cancel loading file.

    Works by deleting attributes from the APP_REFS
    whose existence trigger file loading operations.

    Also cleans up data which won't be needed anymore.
    """
    ### delete the swap path if the attribute exists

    try:
        swap_path = APP_REFS.swap_path
    except AttributeError:
        pass
    else:
        swap_path.unlink()

    ### delete attributes holding paths whose existence
    ### indicate the need to load a file, if such attributes
    ### exisst

    for attr_name in ("source_path", "swap_path"):

        try:
            delattr(APP_REFS, attr_name)
        except AttributeError:
            pass

    ### also clean up data from a possible previous
    ### session thay may still exist
    APP_REFS.data.clear()
