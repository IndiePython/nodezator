"""Log config for main application and its modules."""

### standard library imports

from os import environ

from os.path import getsize

from pathlib import Path

from platform import (
    python_version,
    python_implementation,
    system as get_os_name,
    architecture as get_architecture_info,
)

from pprint import pformat

from datetime import datetime, timezone

from traceback import format_exception

from logging import DEBUG, Formatter, getLogger

from logging.handlers import RotatingFileHandler


## for temporary stdout suppression

from io import StringIO

from contextlib import redirect_stdout


### local imports
from ..appinfo import TITLE, APP_VERSION, APP_DIR_NAME


### constants

## path to log folder

if "APPDATA" in environ:
    general_log_dir = Path(environ["APPDATA"])

else:
    general_log_dir = Path(environ["HOME"]) / ".local"

APP_LOGS_DIR = general_log_dir / APP_DIR_NAME / "logs"

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
### debugging; note that the developer (me) never have
### access to the logs nor are they sent anywhere
### automatically;
###
### if you ever have an issue with your software, I'll
### ask you to send them to me, either as an attachment
### in an github issue or via email;
###
### for more info on that chech the application website
### (url can be found in appinfo.py);

## OS/system name
logger.debug(f"OS/system name is {get_os_name()}")

## architecture

logger.debug(f"Architecture info is {get_architecture_info()}")

## python version
logger.debug(f"Python version is {python_version()}")

## python implementation
logger.debug(f"Python implementation is {python_implementation()}")

## pygame version

## execute an import statement to guarantee pygame is
## installed;
##
## also, notice we also prevent the message printed when
## pygame is first imported from appearing; we do so by
## temporarily redirecting stdout to a temporary file;
## there is no ill-meaning towards the pygame message
## here, since we display the very logo of the library
## in our splash screen, with a link to its website;

try:

    with StringIO() as temp_stream:

        with redirect_stdout(temp_stream):

            from pygame.version import ver

except ImportError:

    logger.exception("pygame doesn't seem to be available." " Reraising.")

    raise

else:
    logger.debug(f"pygame version is {ver}")

## app version

logger.debug(("{} version is {}.{}.{} ({})").format(TITLE, *APP_VERSION))

## timezone

UTC_OFFSET = datetime.now(timezone.utc).astimezone().strftime("%z")

logger.debug("UTC offset (timezone) is " + UTC_OFFSET)
