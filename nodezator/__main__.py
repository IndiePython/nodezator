"""Facility for launching the application.

Nodezator: A Python node editor developed by
Kennedy Richard <kennedy@kennedyrichard.com>.

https://kennedyrichard.com
https://twitter.com/KennedyRichard

https://nodezator.com
https://github.com/IndiePython/nodezator
"""

### standard library import
from pathlib import Path


### local imports

from .logman.main import get_new_logger

from .appinfo import TITLE, NATIVE_FILE_EXTENSION

from .config import APP_REFS



### create logger for module
logger = get_new_logger(__name__)


def main(filepath='', recording_path='', ):
    """Launch application.

    Parameters
    ==========

    filepath (string)
        the path to a file to be opened. May be None, though,
        in which case the application starts without a
        loaded file.

    recording_path (string)
        if path is given, app launches in recording mode and
        saves recording sessions in it.
    """
    ### load function that runs the app
    logger.info("Loading application.")

    ### store recording path

    ## if a path was given, turn it into a pathlib.Path object
    if recording_path:
        recording_path = Path(recording_path)

    ## store it
    APP_REFS.recording_path = recording_path

    ## try loading
    try:
        from .mainloop import run_app

    ## catch unexpected exceptions so we can log them
    ## before reraising

    except Exception as err:

        logger.exception(
            "Unexpected exception while loading application." " Reraising now."
        )

        raise err

    ### finally, run the application

    logger.info("Starting application session.")

    run_app(filepath)

    logger.info("Finished application session.")


### utility function

def parse_args_and_execute_main():
    """Execute main() with custom-parsed arguments.

    This function is used when executing the package after
    installing it from https://pypi.org.
    """
    ### standard library import
    from argparse import ArgumentParser

    ### configure parser

    parser = ArgumentParser(description=f"{TITLE} - Python Node Editor")

    parser.add_argument(
        "filepath",
        type=str,
        nargs="?",
        default='',
        help=f"path of {NATIVE_FILE_EXTENSION} file to be loaded.",
    )

    parser.add_argument(
        "-r",
        "--recording-path",
        type=str,
        default='',
        help=(
            "path wherein to save session recording data when requested;"
            " if given, the app is launched in session recording mode"
        ),
    )

    ### parse arguments
    parsed_args = parser.parse_args()

    ### call the main function with the arguments
    main(parsed_args.filepath, parsed_args.recording_path)


### when file is run as script...

if __name__ == "__main__":

    ### execute main() with custom-parsed arguments
    parse_args_and_execute_main()
