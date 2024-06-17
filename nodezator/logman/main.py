"""Log config for main application and its modules."""

### standard library imports

from os.path import getsize

from pathlib import Path

from platform import (
    python_version,
    python_implementation,
    system as get_os_name,
    architecture as get_architecture_info,
)

from pprint import pformat

from textwrap import wrap

from datetime import datetime

from traceback import format_exception

from logging import DEBUG, Formatter, getLogger

from logging.handlers import RotatingFileHandler


### third-party imports

import pygame

from numpy.version import (
    full_version as full_numpy_version,
    release as numpy_release,
)

### local imports

from ..config import APP_REFS, WRITEABLE_PATH

from ..appinfo import TITLE, APP_VERSION

from ..ourstdlibs.datetimeutils import UTC_OFFSET

from .constants import PYGAME_CE_REQUIRED_MESSAGE

from .fixeddialog import display_dialog_and_quit



### constants

## path to log folder

APP_LOGS_DIR = WRITEABLE_PATH / 'logs'

if not APP_LOGS_DIR.exists():
    APP_LOGS_DIR.mkdir(parents=True)

## log level
LOG_LEVEL = DEBUG

## number of log files kept; they are called backups, and
## each one represents a run of the software until the
## user closes it (or when the file size nears the maximum
## size in bytes defined in the next constant);
BACKUP_COUNT = 30

## maximum size in bytes of the log files;
##
## whenever a log file gets close to this size, a new log
## file replaces it and it becomes a rotated file (called
## a backup log) and its contents are rotated (transfered)
## through a log file backup hierarchy;
##
## bear in mind, however, that we mean to keep each log
## file containing only records for a single run of the
## software whenever possible and this size limit was
## provided just for safety, to prevent the log to grow
## indefinitely large in case something goes wrong;
##
## that's why we use a value purposefully higher than what
## we expect a common session to produce in size, though we
## don't have data enough to determine such number
## accurately; thus, this value will be adjusted in the
## future when we have enough data to decide on a value
## closer to reality;
##
## however, even if a log file reaches its limit and
## rotates, thereby no longer representing a full session
## (since new records for the current session will still
## be produced and logged in the new file), it is not a
## problem per se, since the python-like format we use
## allows us to easily identify if/when a log file rotated
## before reaching the end of the session, thereby allowing
## us to easily determine to which session each record
## belongs;
MAX_BYTES = 1 * 1024 * 1024  # 1 MiB per file

### define log level and set top level logger

## top logger

top_logger = getLogger("app")
top_logger.setLevel(LOG_LEVEL)


### custom pyl formatter for log records


class PylLogFormatter(Formatter):
    """Outputs pyl logs."""

    def format(self, record):
        """Return a log record as pyl formated data."""
        ### serialize exception info if needed

        ## retrieve
        exc_info = record.exc_info

        ## serialize if not None

        if exc_info is not None:

            ### turn all the data into a list of strings
            ### representing exception information,
            ### concatenate them into a single text;
            ###
            ### such text represent the exact text that
            ### would be printed by traceback.print_exc

            exc_info = "".join(
                format_exception(
                    ### here exc_info is
                    ### exploded into its
                    ### individual pieces:
                    ### (
                    ###   exc_type,
                    ###   exc_value,
                    ###   exc_traceback,
                    ### )
                    *exc_info
                )
            )

        ### put the record data together in a dict and
        ### return it as a pretty-formatted string with
        ### a trailing comma

        ## XXX perhaps using a f-string with formatting
        ## for datetime.now() would be faster (check and
        ## implement if confirmed)

        return (
            pformat(
                {
                    "name": record.name,
                    "func_name": record.funcName,
                    "timestamp": str(datetime.now()),
                    "level": record.levelname,
                    "message": record.msg,
                    "exc_info": exc_info,
                    "lineno": record.lineno,
                },
                indent=2,
                width=300,
            )
            + ","
        )


### instantiate the pyl formatter
pyl_formatter = PylLogFormatter()


### utility function for renaming log files


def custom_format_filename(name):
    """Apply custom format to filename.

    The format ensures that the backups always end with
    the '.log' extension.
    """
    ### remove '.0.log' from name (it is in the middle of
    ### the string in backup log files, the ones resulting
    ### from roll over operations), then append '.log'
    ### extension (note that the leading dots are needed,
    ### otherwise, if we used '0.log', the replace operation
    ### would also affect substrings like '10.log', for
    ### instance
    return name.replace(".0.log", "") + ".log"


### define a handler to generate a log file for each run

log_filepath = str(APP_LOGS_DIR / "session.0.log")

last_run_handler = RotatingFileHandler(
    filename=log_filepath,
    mode="a",
    encoding="utf-8",
    backupCount=BACKUP_COUNT,
    maxBytes=MAX_BYTES,
)

last_run_handler.namer = custom_format_filename

last_run_handler.setLevel(LOG_LEVEL)

### perform final setups

## set pyl formatter on handler
last_run_handler.setFormatter(pyl_formatter)

## add handler to the top level logger
top_logger.addHandler(last_run_handler)

## rotate the log file if it is not empty
if getsize(log_filepath):
    last_run_handler.doRollover()

## reference the getChild method of the top_logger
## as get_new_logger; modules throughout the package in need
## of logging will import this operation to get new loggers
## for them whenever needed
get_new_logger = top_logger.getChild

### finally get a new logger for this module
logger = get_new_logger(__name__)

### record the fact that logging was properly configured
logger.info("Configured logging.")

### log important system information which is useful for
### debugging;
###
### this data is also stored as system information in a
### special dict, which is included in system testing
### information
###
### note that the developer (me) never has access to this
### data nor is it sent anywhere;
###
### if you ever have an issue with on your end, I'll just
### ask you to send the info to me, either as an attachment
### in an github issue or via email;

## OS/system name

_os_name = get_os_name()

logger.debug(f"OS/system name is {_os_name}")
APP_REFS.system_info['os_name'] = _os_name

## architecture

_architecture_info = get_architecture_info()

logger.debug(f"Architecture info is {_architecture_info}")
APP_REFS.system_info['architecture_info'] = _architecture_info

## python version

_python_version = python_version()

logger.debug(f"Python version is {_python_version}")
APP_REFS.system_info['python_version'] = _python_version

## python implementation

_python_implementation = python_implementation()

logger.debug(f"Python implementation is {_python_implementation}")
APP_REFS.system_info['python_implementation'] = _python_implementation


## if pygame is not pygame-ce, display message saying the app cannot be
## used because pygame-ce is a requirement;
##
## the message is both printed and displayed in a dialog and the app is
## exited once user closes window or dismiss it by pressing the escape key

if not getattr(pygame, 'IS_CE', False):

    logger.info("imported pygame isn't pygame-ce; notifying user now")

    for line in PYGAME_CE_REQUIRED_MESSAGE.splitlines():
        print('\n'.join(wrap(line)))

    display_dialog_and_quit(pygame)

### log relevant info...

## pygame version

_pygame_version = pygame.version.ver

logger.debug(f"pygame version is {_pygame_version}")
APP_REFS.system_info['pygame_version'] = _pygame_version

## numpy version and whether it is a release version or not

logger.debug(f"numpy version is {full_numpy_version}")
logger.debug(f"numpy version is release: {numpy_release}")

APP_REFS.system_info['numpy_version'] = full_numpy_version
APP_REFS.system_info['numpy_release'] = numpy_release

## app version

_app_version = '{} {}.{}.{} ({})'.format(TITLE, *APP_VERSION)

logger.debug(f"app version is {_app_version}")
APP_REFS.system_info['app_version'] = _app_version

## timezone

logger.debug("UTC offset (timezone) is " + UTC_OFFSET)
APP_REFS.system_info['utc_offset'] = UTC_OFFSET
