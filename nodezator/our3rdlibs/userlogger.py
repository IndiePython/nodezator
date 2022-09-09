"""Facility for simple user-related logging."""

### standard library imports

from os import linesep

from functools import partialmethod

from traceback import format_exc


### local import
from ..ourstdlibs.timeutils import get_friendly_time


### constants

### log level words
LOG_LEVELS = "INFO", "WARNING", "ERROR", "CRITICAL"

### log level error message
LEVEL_ERROR_MESSAGE = "'level' argument must be one of {}".format(LOG_LEVELS)

### custom formatter for the header of logged messages
HEADER_FORMATTER = "--- [{} message logged at {}] ---".format

### formatter for message with a single line

ONE_LINE = linesep
TWO_LINES = linesep * 2

SINGLE_LINE_FORMATTER = ("{}" + TWO_LINES + "{}" + TWO_LINES).format

MULTILINE_FORMATTER = ("{}" + ONE_LINE + "{}" + TWO_LINES).format


### class definition


class UserLogger:
    """Log to communicate with user in the application.

    Simple logger to log events relevant to the user,
    rather than the usual all-purpose logging performed
    with the "logging" standard library module.

    This is logger is meant to gather info of interest to
    the user, for displaying in the application, rather than
    being collected in files.

    The contents of this logger are stored in a string.
    We limit the maximum number of lines such string may
    contain. The such limit can be adjusted at the
    config.py module.
    """

    def __init__(self):
        """Create relevant attributes."""
        ### string to hold log contents
        self.contents = ""

        ### maximum number of lines to be kept;
        ###
        ### this default value is replaced by a user
        ### defined one if the user decides to change
        ### it in the user preferences editing form
        self.max_lines = 1000

    def log(self, level, message):
        """Log given message.

        Parameters
        ==========
        level (string)
            indicates level of the message.
        message (string)
            text to be logged; can have multiple lines.
        """
        ### raise error if level isn't among allowed ones
        if level not in LOG_LEVELS:
            raise ValueError(LEVEL_ERROR_MESSAGE)

        ### create a header with a friendly representation
        ### of the current time

        header = HEADER_FORMATTER(level, get_friendly_time())

        ### choose a message formatter depending on whether
        ### or not the message has more than one line
        ### and create a full message by passing the
        ### header and message through it

        ## measure line count
        message_line_count = len(message.splitlines())

        ## choose formatter

        message_formatter = (
            MULTILINE_FORMATTER if message_line_count > 1 else SINGLE_LINE_FORMATTER
        )

        ## obtain full message by formatting
        ## header and message
        full_message = message_formatter(header, message)

        ### finally, extend the lines of the log with
        ### the ones we put together and limit the number
        ### of lines to the value in the 'max_lines'
        ### attribute

        self.contents += full_message + TWO_LINES

        self.contents = linesep.join(self.contents.splitlines()[-self.max_lines :])

    ### partial implementation of the log method

    info = partialmethod(log, "INFO")
    warning = partialmethod(log, "WARNING")
    error = partialmethod(log, "ERROR")
    critical = partialmethod(log, "CRITICAL")

    def exception(self, message):
        """Log given message plus traceback w/ level 'ERROR'.

        Parameters
        ==========

        message (string)
            text to be logged; can have multiple lines.
        """

        ### create a header with a friendly representation
        ### of the current time

        header = HEADER_FORMATTER("ERROR", get_friendly_time())

        ### obtain full message by formatting
        ### header and message
        full_message = MULTILINE_FORMATTER(header, message)

        ### obtain the text of the exception's traceback
        ### and increment the full message with it

        traceback_text = format_exc()

        full_message += ONE_LINE + traceback_text

        ### finally, extend the lines of the log with
        ### the ones we put together and limit the number
        ### of lines to the value in the 'max_lines'
        ### attribute

        self.contents += full_message + TWO_LINES

        self.contents = "\n".join(self.contents.splitlines()[-self.max_lines :])


### instantiate the user logger, referencing it as a
### module variable so it can be imported anywhere else
### in the package;
USER_LOGGER = UserLogger()
