"""Facility for vim comment syntax mapping."""

### standard library imports
from string import punctuation, whitespace


### local import
from ...ourstdlibs.mathutils import get_remaining_intervals


### constants

## words to highlight in the text of comments
TODO_WORDS = "TODO", "XXX", "FIXME"

## chars allowed to surround todo words
ALLOWED_SURROUNDING_CHARS = punctuation + whitespace


### main function definition

## Check the "No syntax errors" section in the docstring
## of the function below to know why it isn't expected
## to raise SyntaxMappingError


def get_comment_syntax_map(comment_text):
    """Return dict mapping portions to respective categories.

    That is, we map each portion of the text to the name
    of the category that portion represents in the syntax.

    Comments only have two categories, which are normal
    text ('normal') and todo words ('todo_words').

    How we map the text is based on the behaviour observed
    in the vim editor, which highlights todo words within
    comments. Such todo words are the words TODO, XXX and
    FIXME.

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

    >>> text = "### TODO hello world"
    >>> expected_output = {
    ...   0: {
    ...        (0, 4)  : 'normal',
    ...        (4, 8)  : 'todo_word',
    ...        (8, 20) : 'normal',
    ...      }
    ... }
    >>> get_comment_syntax_map(text) == expected_output
    True

    In other words, the output means that the text we
    provided, in its first line (index 0), has normal
    text from the index 0 until the 3 and then has
    text representing a todo word from the index 4
    until the index 7, then normal text again from
    index 8 until the index 19.


    No Syntax Errors
    ================

    This function wasn't set to raise SyntaxMappingError
    as was the case for the equivalent function which maps
    syntax for Python source code, for instance.

    This is so because comments don't have wrong syntax.
    They either have special syntax ("todo" words) or no
    syntax at all, but we don't expect any syntax-related
    errors to be raised while mapping syntax for comments.
    """
    ### return dict

    return {
        ### each item in such dict is composed by the index of
        ### a line to which a dict is mapped
        line_index: {
            ## this other dict associates intervals of the line
            ## to the name of the syntax category the text in
            ## that interval represents
            interval: syntax_category_name
            ## we get the intervals and respective categories
            ## from passing the line text through a special
            ## function
            for interval, syntax_category_name in get_line_syntax_intervals(line_text)
        }
        ### we grab pairs of line index/ line text from lines
        ### which are not empty
        for line_index, line_text in enumerate(comment_text.splitlines())
        if line_text
    }


### utility functions


def get_line_syntax_intervals(comment_text):
    """Return list containing interval/syntax name pairs.

    For the defintion of interval and syntax (category)
    name, check the docstring of the get_comment_syntax_map
    function in this module.
    """
    ### create list to gather todo intervals, that is,
    ### 2-tuples representing the boundaries of slices
    ### of the comment_text string which contain todo words
    ### (when they do)
    todo_intervals = []

    ### iterate over the todo words storing the intervals
    ### where they can be found in the comment_text string
    ### (if there are such words)

    for word in TODO_WORDS:

        ## store the length of the word
        length = len(word)

        ## store the index from where we should look
        ## for the word in the comment_text string
        start_search_index = 0

        ## now we repeat the block below as many times as
        ## there are substrings of the todo word in the
        ## comment_text string

        for _ in range(comment_text.count(word)):

            ## define the boundaries of the interval
            ## containing the todo word in the string

            # pick the first index where the todo substring
            # can be found in the comment_text searching
            # from the start search index on
            including_start = comment_text.index(word, start_search_index)

            # then calculate the end by adding the length
            # to it
            excluding_end = including_start + length

            ## now calculate the index of the characters
            ## before and after the substring;
            ##
            ## (note the index of the character after the
            ## substring is the same value as the end
            ## index of the substring; this is so because
            ## the "end" calculated above is an excluding
            ## end point, not making part of the substring
            ## interval, just being used to define the
            ## right boundary of the interval)

            index_char_before = including_start - 1
            index_char_after = excluding_end

            ## here we check whether the substring really
            ## represents a proper todo word or not: by
            ## checking whether both the character before
            ## and after the todo substring are both valid
            ## characters according to rules defined on a
            ## specific function;
            ##
            ## if the todo substring is indeed a valid todo
            ## word, its interval is stored

            if all(
                is_char_allowed(comment_text, index)
                for index in (index_char_before, index_char_after)
            ):

                todo_intervals.append((including_start, excluding_end))

            ## we then update the start search index, so
            ## the next search is performed from such index
            start_search_index = excluding_end

    ### now that we know which intervals contains todo words
    ### (if we did find substrings which really qualify as
    ### todo words), we do the opposite here: we define
    ### which intervals of the comment_text string contain
    ### normal text by removing the todo word intervals

    normal_intervals = get_remaining_intervals(
        all_indices=range(len(comment_text)), intervals_to_subtract=todo_intervals
    )

    ### now that we have the intervals for each kind of
    ### text, we pair the intervals with the corresponding
    ### color setting for them in new lists

    ## normal pairs;
    ##
    ## the try/except clause is needed for compatibility
    ## with Python 3.7+ (see PEP 479)

    try:
        normal_pairs = [(item, "normal") for item in normal_intervals]

    except RuntimeError:
        normal_pairs = []

    ## todo pairs

    todo_pairs = [(item, "todo_word") for item in todo_intervals]

    ### then we concatenate all the pairs together into a
    ### a new list then return it

    interval_name_pairs = normal_pairs + todo_pairs

    return interval_name_pairs


def is_char_allowed(line_string, index):
    """Return True if char in index is allowed or don't exist.

    Parameters
    ==========
    line_string (string)
        represents a line of text.
    index (integer)
        the index of a character in the line string.

    Purpose
    =======

    Used to check whether a "todo" substring (a string
    from the TODO_WORDS constant) from line_string is
    a proper todo word.

    Such check is made indirectly, by checking the
    characters which reside in the adjacent indices
    of the substring. The following rules apply:

    A character sitting on an adjacent index is valid
    if either...

    a) it doesn't exist (not having an adjacent character
       is a valid condition for a todo word)
    b) it exists and is considered an allowed character
       (it must be in the ALLOWED_SURROUNDING_CHARACTERS
       string)

    For the substring to be considered valid, both the
    adjacent indices must be checked, which is why this
    function is called twice: one call per index.
    """
    ### in this context, if the index is negative, it means
    ### it doesn't exist, which is a valid condition, so
    ### we return True
    if index < 0:
        return True

    ### check whether the index points to a character in
    ### the line string
    try:
        char = line_string[index]

    ### if it doesn't, since this is a valid condition we
    ### pass in order to meet the 'return True' statement
    ### at the end of the function
    except IndexError:
        pass

    ### if there is such character, we check whether it
    ### is not allowed, in which case we return False

    else:

        if char not in ALLOWED_SURROUNDING_CHARS:
            return False

    ### if we reach this point, it means we didn't meet an
    ### invalidating condition, so we can return True
    return True
