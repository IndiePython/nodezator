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


def main(
    filepath='',
    input_path='',
    recording_path='',
    recording_size=(1280, 720),
    recording_title="Untitled session",
    ):
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

    input_path (string)
        if path is given, app launches in playing mode and
        play the given input data.
    """
    ### load function that runs the app
    logger.info("Loading application.")

    ### treat extra arguments received


    ## cannot receive both a recording_path and input_path

    if recording_path and input_path:

        raise ValueError(
            "The app cannot receive both a 'recording_path' and"
            " 'input_path'"
        )

    ## if a recording or input path was given, turn it into a pathlib.Path
    ## object and store it, along with additional options if relevant

    elif recording_path:

        recording_path = Path(recording_path)
        APP_REFS.recording_path = recording_path

        ## also store the recording size and title

        APP_REFS.recording_size = recording_size
        APP_REFS.recording_title = recording_title

    elif input_path:
        input_path = Path(input_path)
        APP_REFS.input_path = input_path

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

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-r",
        "--recording-path",
        type=str,
        default='',
        help=(
            "path wherein to save session recording data when requested;"
            " if given, the app is launched in session recording mode"
        ),
    )

    group.add_argument(
        "-i",
        "--input-path",
        type=str,
        default='',
        help=(
            "file containing input data to be played in the app;"
            " if given, the app is launched in input playing mode"
        ),
    )

    parser.add_argument(
        "-s",
        "--recording-size",
        type=str,
        nargs="?",
        default='1280x720',
        help=(
            "fixed window size for recording (default is '1280x720');"
            " only used if recording path is given."
        )
    )

    parser.add_argument(
        "-t",
        "--recording-title",
        type=str,
        nargs="?",
        default='Untitled session',
        help=(
            "title for recording session (default is 'Untitled session');"
            " only used if recording path is given."
        )
    )

    ### parse arguments
    parsed_args = parser.parse_args()

    ### process recording size

    try:
        recording_size = tuple(
            map(int, parsed_args.recording_size.split('x'))
        )

    except Exception as err:

        raise ValueError(
            "If given, recording size must be a string in the 'WIDTHxHEIGHT'"
            " format; for instance: 1280x720"
        ) from err


    else:

        w, h = recording_size

        if w == 0 or h == 0:

            raise ValueError(
                "Neither width nor height for recording size can be 0"
            )

    ### call the main function with the arguments

    main(
        parsed_args.filepath,
        parsed_args.input_path,
        parsed_args.recording_path,
        recording_size,
        parsed_args.recording_title,
    )


### when file is run as script...

if __name__ == "__main__":

    ### execute main() with custom-parsed arguments
    parse_args_and_execute_main()
