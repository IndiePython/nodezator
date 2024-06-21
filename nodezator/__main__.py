"""Facility for launching the application.

Nodezator: A generalist Python node editor developed by
Kennedy Richard <kennedy@kennedyrichard.com>.

https://kennedyrichard.com
https://x.com/KennedyRichard

https://nodezator.com
https://github.com/IndiePython/nodezator
"""

### standard library imports

from pathlib import Path


## for temporary stdout suppression

from io import StringIO

from contextlib import redirect_stdout


### third-party import (pygame-ce)

## execute an import statement to guarantee pygame-ce is
## installed, even though we don't intend to use it here;
##
## notice we prevent the message printed when pygame-ce is
## first imported from appearing; we do so by temporarily
## redirecting stdout to a temporary file;
##
## there is no ill-meaning towards the pygame message
## here, since we display the very logo of the library
## in our splash screen, with a link to its website;
## that is, we properly credit it;
##
## we only avoid having the message printed in order to leave
## the stdout clean for when we are launching the app repeatedly
## for debugging

with StringIO() as _temp_stream:

    with redirect_stdout(_temp_stream):

        import pygame


### local imports

from .logman.main import get_new_logger

from .appinfo import TITLE, NATIVE_FILE_EXTENSION

from .config import APP_REFS



### create logger for module
logger = get_new_logger(__name__)


def main(filepath=''):
    """Launch application.

    Parameters
    ==========

    filepath (string)
        the path to a file to be opened. May an empty string,
        though, in which case the application starts without a
        loaded file.
    """
    ### load function that runs the app
    logger.info("Loading application.")

    ### try loading function to run app

    try:
        from .mainloop import run_app

    ## catch unexpected exceptions so we can log them
    ## before reraising

    except Exception as err:

        logger.exception(
            "Unexpected exception while loading application. Reraising now."
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

    ### instantiate and configure parser

    parser = ArgumentParser(description=f"{TITLE} - Python Node Editor")

    parser.add_argument(
        "filepath",
        type=str,
        nargs="?",
        default='',
        help=f"path of {NATIVE_FILE_EXTENSION} file to be loaded.",
    )

    ### parse arguments
    parsed_args = parser.parse_args()

    ### call the main function with the arguments
    main(parsed_args.filepath)


### when file is run as script...

if __name__ == "__main__":

    ### execute main() with custom-parsed arguments
    parse_args_and_execute_main()
