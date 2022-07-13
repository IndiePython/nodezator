"""Facility for launching the application.

Nodezator: A Python node editor developed by
Kennedy Richard <kennedy@kennedyrichard.com>.

https://kennedyrichard.com
https://twitter.com/KennedyRichard

https://nodezator.com
"""
### standard library imports

import asyncio

from pathlib import Path

from sys import path

### XXX temporary 'brain surgery'###################
str_app_dir = str(Path(__file__).parent.resolve())
if str_app_dir not in path: path.insert(0, str_app_dir)
####################################################


### local imports

from logman.main import get_new_logger

from appinfo import TITLE, NATIVE_FILE_EXTENSION

from config import APP_REFS


### store reference to application directory
APP_REFS.app_dir = Path(__file__).parent.resolve()


### create logger for module
logger = get_new_logger(__name__)


async def main(filepath=None):
    """Launch application.

    Parameters
    ==========
    filepath (string or None)
        the path to a file to be opened. May be None, though,
        in which case the application starts without a
        loaded file.
    """
    ### load function that runs the app
    logger.info("Loading application.")

    ## try loading
    try: from mainloop import run_app

    ## catch unexpected exceptions so we can log them
    ## before reraising

    except Exception as err:

        logger.exception(
          "Unexpected exception while loading application."
          " Reraising now."
        )

        raise err

    ### finally, run the application

    logger.info("Starting application session.")

    await run_app(filepath)

    logger.info("Finished application session.")


if __name__ == "__main__":

    ### parse arguments received, looking for a filepath
    ### (or using None instead, a filepath wasn't provided)

    ## import argument parser
    from argparse import ArgumentParser

    ## instantiate and configure it

    parser = ArgumentParser(
               description = TITLE + " - Python Node Editor"
             )

    parser.add_argument(

             'filepath',

             type    = str,
             nargs   = '?',
             default = None,

             help    = (
               "path of "
               + NATIVE_FILE_EXTENSION
               + " file to be loaded."
             )
           )

    ## parse arguments
    args = parser.parse_args()


    ### finally call the main function, passing along
    ### the filepath argument received (which might be the
    ### default, None)
    asyncio.run( main(args.filepath) )
