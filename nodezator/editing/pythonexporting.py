"""Functions for visualizing and saving exported python code."""

### local imports

from ..config import APP_REFS

from ..translation import TRANSLATION_HOLDER as t

from ..logman.main import get_new_logger

from ..dialog import create_and_show_dialog

from ..fileman.main import select_paths

from ..our3rdlibs.userlogger import USER_LOGGER

from ..our3rdlibs.behaviour import set_status_message

from ..textman.viewer.main import view_text



### create logger for module
logger = get_new_logger(__name__)


### constants

DEFAULT_FILENAME = (t.editing.python_exporting.default_filename) + ".py"

NEW_PYTHON_FILEPATH_CAPTION = (t.editing.python_exporting.pick_new_path) + " (.py)"


### main functions

def export_as_python():

    exported_python_code = get_exported_python_code()

    if exported_python_code:

        ### grab filepath

        paths = select_paths(
            caption=NEW_PYTHON_FILEPATH_CAPTION,
            path_name=DEFAULT_FILENAME,
        )

        ### act according to whether paths were given

        ## if paths were given, there can only be one,
        ## it should be used as the new filepath

        if paths:
            filepath = paths[0]

        ## if no path is given, we return earlier, since
        ## it means the user cancelled setting a new
        ## path
        else:
            return

        ### if the extension is not allowed, notify the
        ### user and cancel the operation by returning

        if filepath.suffix.lower() != ".py":

            create_and_show_dialog("File extension must be '.py'")
            return

        ### otherwise, save the exported code in the given path

        with open(filepath, mode="w", encoding="utf-8") as f:
            f.write(exported_python_code)

        ### set status message informing user

        message = f"File succesfully exported as python script in {filepath}"
        set_status_message(message)


def view_as_python():

    exported_python_code = get_exported_python_code()

    if exported_python_code:

        view_text(
            exported_python_code,
            syntax_highlighting='python',
            show_line_number=True,
        )


### assisting function

def get_exported_python_code():

    ### try returning exported python code

    try:
        return APP_REFS.gm.python_repr()

    ### if it fails, notify the user and return False

    except Exception as err:

        ### log traceback in regular log and and user log

        msg = (
            "An unexpected error ocurred"
            " while trying to export node"
            " layout as python code."
        )

        logger.exception(msg)
        USER_LOGGER.exception(msg)

        error_str = f'{err.__class__.__name__}({str(err)})'

        ### if there was an error message (an error
        ### occured), show it to the user via a dialog

        dialog_message = (
            "An error ocurred while trying to"
            " export the layout. Check the user log"
            " for more info (click <Ctrl+Shift+J> after"
            " leaving the dialog). Here's the error"
            f" message: {error_str}"
        )

        create_and_show_dialog(
            dialog_message,
            level_name="error",
        )

        ### return False
        return False
