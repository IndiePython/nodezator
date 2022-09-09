"""Facility for user logger's log syntax mapping."""

### constants


## log level words
LOG_LEVELS = "INFO", "WARNING", "ERROR", "CRITICAL"


## map associating level names to category names

# utility function


def level_name_to_category_name(level_name):
    """Return level name turned into a category name.

    Does so by applying a custom arbitrary format.
    """
    return "{}_header".format(level_name.lower())


# map

CATEGORY_NAME_MAP = {
    level_name: level_name_to_category_name(level_name) for level_name in LOG_LEVELS
}


## substrings surrounding the log header
HEADER_START, HEADER_END = "--- [", "] ---"


### main function definition

## Check the "No syntax errors" section in the docstring
## of the function below to know why it isn't expected
## to raise SyntaxMappingError


def get_user_log_syntax_map(log_text):
    """Return dict mapping portions to respective categories.

    That is, we map each portion of the text to the name
    of the category that portion represents in the syntax.

    By the way, a user log is just the content of a special
    logger called user logger.

    A user log has 05 categories, which are normal
    text ('normal') and log headers of different levels
    ('info_header', 'warning_header', 'error_header' and
    'critical_header').

    The dict itself contains indices of lines from the text
    mapped to another dict which contains the intervals in
    that line mapped to the category of text each interval
    contain.

    The intervals are 2-tuples of integers representing
    the [a, b) interval. Another way of seeing such
    integers is as the indices you'd use to grab the
    slice of text from the line representing the interval:
    line_text[a:b].

    For instance, if a line has the (0, 4) interval mapped
    to 'normal', it means the line text has normal text
    from the index 0 until the index 3. If you were to
    execute line_text[0, 4] you'd get a normal portion
    of text.


    Doctest
    =======

    An example in the form of a doctest can be seen below:

    >>> # TODO remember to check whether the "new line
    >>> # problem" below has already been reported as bug

    >>> # for some reason, using the new line character
    >>> # directly was causing the text to raise an error,
    >>> # so we obtain it here indirectly
    >>> NEW_LINE = chr(10)

    >>> line0 = "--- [INFO message logged at 15:22:03] ---"
    >>> line1 = "A log message"
    >>> text = NEW_LINE.join((line0, line1))
    >>> expected_output = {
    ...   0: {
    ...        (0, 41) : 'info_header'
    ...      },
    ...   1: {
    ...        (0, 13) : 'normal'
    ...      }
    ... }
    >>> get_user_log_syntax_map(text) == expected_output
    True

    In other words, the output means that the text we
    provided, in its first line (index 0), has info log
    header text from the index 0 until the 33 (the entire
    line), and the following line (index 1) has normal text
    from the character at the index 0 until the index 8
    (again, the whole line).


    No Syntax Errors
    ================

    This function wasn't set to raise SyntaxMappingError
    as was the case for the equivalent function which maps
    syntax for Python source code, for instance.

    This is so because logs don't have wrong syntax.
    They either have special syntax (header text) or no
    syntax at all, but we don't expect any syntax-related
    errors to be raised while mapping syntax for logs from
    the user logger.
    """
    ### return dict

    return {
        ### each item in such dict is composed by the index of
        ### a line to which a dict is mapped
        line_index: {
            ## this other dict associates the interval
            ## representing the whole line to the category
            ## to which its content belongs
            (0, len(line_text)): get_log_category(line_text)
        }
        ### we grab pairs of line index/ line text from lines
        ### which are not empty
        for line_index, line_text in enumerate(log_text.splitlines())
        if line_text
    }


### utility functions


def get_log_category(line_text):
    """Return category name of content the line text holds."""
    ### remove specific substrings if they exist, otherwise,
    ### consider the text as normal text by returning 'normal'

    ## substring at the beginning of the string

    if line_text.startswith(HEADER_START):
        line_text = line_text[len(HEADER_START) :]

    else:
        return "normal"

    ## substring at the end of the string

    if line_text.endswith(HEADER_END):
        line_text = line_text[: -len(HEADER_END)]

    else:
        return "normal"

    ### try separating the text into a head and tail
    ### portions using a known excerpt of text used in
    ### headers
    level_name, sep, time_str = line_text.partition(" message logged at ")

    ### the line text can't be a header in the following
    ### cases, so return 'normal'...

    if (
        ## if there is not separator, it means the separation
        ## didn't succeed, so the text can't be a user log
        ## header...
        not sep
        ## or if the level name captured isn't allowed
        or level_name not in LOG_LEVELS
        ## or yet if the time string captured doesn't validate
        or not validate_time_str(time_str)
    ):
        return "normal"

    ### otherwise we have a header, so we return its
    ### respective category name according to its level
    ### name
    else:
        return CATEGORY_NAME_MAP[level_name]


def validate_time_str(time_str):
    """Return True if time string is valid."""
    ### try splitting the time string into substrings
    ### representing the hour, minutes and seconds
    try:
        hour, minutes, seconds = time_str.split(":")

    ### if the splitting fails, it means we don't have
    ### a valid time string, so we return False
    except ValueError:
        return False

    ### otherwise, all substring retrieved must be entirely
    ### numeric, otherwise the time string isn't valid

    if not all(str.isnumeric(string) for string in (hour, minutes, seconds)):
        return False

    ### and each substring must represent an integer
    ### within a specific range according to the substring
    ### meaning, otherwise the time string isn't valid

    if (
        int(hour) in range(24)
        and int(minutes) in range(60)
        and int(seconds) in range(60)
    ):
        return True

    else:
        return False
