"""Facility with function for mapping Python syntax."""

### standard library imports

from collections import defaultdict

from io import BytesIO

from tokenize import (
    ## tokens to ignore
    ENCODING,
    ENDMARKER,
    NEWLINE,
    NL,
    INDENT,
    DEDENT,
    ## tokens to process
    COMMENT,
    NUMBER,
    NAME,
    STRING,
    OP,
    ## function for tokenizing source
    tokenize,
)


### local imports

from ....ourstdlibs.mathutils import get_remaining_intervals

from ....ourstdlibs.exceptionutils import new_raiser_from_existing_deco

from ...exception import SyntaxMappingError

from .namemap import HIGHLIGHT_NAME_MAP

from .utils import (
    is_triple_quotes_string,
    has_def_or_class_statement,
    interval_of_next_def_word,
    represents_applied_decorator,
    get_comment_offset_intervals,
)


### XXX implement doctest highlighting inside docstrings
### when convenient


### constant (tokens which are not processed)

TOKENS_TO_IGNORE = {ENCODING, ENDMARKER, NEWLINE, NL, INDENT, DEDENT}


### function definition


@new_raiser_from_existing_deco(
    new_exception=SyntaxMappingError,
    new_message="error while mapping syntax of Python code",
)
def get_python_syntax_map(source_text):
    """Return dict mapping portions to respective category.

    That is, we mark each portion of the text according
    to the category of that portion in the syntax.

    Python has a lot of categories like 'keyword', 'boolean',
    'builtin_function', etc.

    The dict itself contains indices of lines from the text
    mapped to another dict which contains the intervals in
    that line mapped to the category of text they contain.

    The intervals are 2-tuples of integers representing
    the [a, b) interval. Another way of seeing such
    integers is as the indices you'd use to grab the
    slice of text from the line representing the interval:
    line_text[a:b].

    For instance, if a line has the (0, 12) interval mapped
    to 'normal', it means the line text has normal text
    from the index 0 until the index 11. If you were to
    execute line_text[0, 12] you'd get a normal portion
    of text.


    Doctest
    =======

    An example in the form of a doctest can be seen below:

    >>> # XXX interesting fact I learned while testing
    >>> # this doctest: because this function was decorated,
    >>> # "python -m doctest" can't find this function
    >>> # anymore, so this test isn't performed; think
    >>> # about solutions for this

    >>> text = "condition = True"
    >>> expected_output = {
    ...   0: {
    ...        ( 0, 12) : 'normal',
    ...        (12, 16) : 'boolean'
    ...      }
    ... }
    >>> get_python_syntax_map(text) == expected_output
    True

    In other words, the output means that the text we
    provided, in its first line (index 0), has normal
    text from the index 0 until the 11 and then has
    text representing a boolean from the index 12
    until the index 15.
    """
    ### create a default dict to store highlight data for
    ### each line using its index;
    ###
    ### we set the dict to automatically create, store and
    ### return a new dict for us whenever we try to store
    ### intervals for a line index which don't exist in
    ### the dict yet
    line_index_to_data = defaultdict(dict)

    ### tokenize the string;
    ###
    ### that is, get an iterable which yields named tuples
    ### representing tokens (data from each token) when we
    ### iterate over it

    raw_tokens = tokenize(BytesIO(source_text.encode("utf-8")).readline)

    ### also list all lines in the source
    source_lines = source_text.splitlines()

    ### iterate over tokens changing them as desired;

    for (token_type, token_string, token_start, token_end, token_line) in raw_tokens:

        ### ignore tokens

        ## ignore tokens from special constant
        if token_type in TOKENS_TO_IGNORE:
            continue

        ## ignore all OP tokens, except '@'
        if token_type == OP and token_string != "@":
            continue

        ### store the line number where the token begins
        ### (STRING tokens may take multiple lines)
        line_index = token_start[0] - 1

        ### store the interval of the token
        interval = token_start[1], token_end[1]

        ### process single line token

        if len(token_string.splitlines()) == 1:

            ### mark token according to its type

            ## if token is string, define the category
            ## of this kind of text and map the interval
            ## to it

            if token_type == STRING:

                ## define category name

                string_category_name = (
                    "triple_quotes_string"
                    if is_triple_quotes_string(token_string)
                    else "string"
                )

                ## map interval to category name

                (line_index_to_data[line_index][interval]) = string_category_name

            ## if token is a number, just map the interval
            ## to the 'number' category name

            elif token_type == NUMBER:

                (line_index_to_data[line_index][interval]) = "number"

            ## comments have special treatment in which
            ## "todo" words, though part of the comment,
            ## are marked as a different category of text
            ## in order to be highlighted differently from
            ## the rest of the comment;
            ##
            ## this is why comments are further decomposed
            ## into intervals of different categories;

            elif token_type == COMMENT:

                ## decompose comments into normal comment
                ## text and "todo" words

                interval_category_pairs = get_comment_offset_intervals(
                    token_line, interval[0]
                )

                ## map the intervals to their respective
                ## category names

                for interval, comment_category_name in interval_category_pairs:

                    (line_index_to_data[line_index][interval]) = comment_category_name

            ## names (identifiers) in Python are highlighted
            ## according to several rules...

            elif token_type == NAME:

                ## if the name is present in a special map,
                ## grab the respective value as the
                ## category of that name and map the interval
                ## to that category

                try:
                    category_of_name = HIGHLIGHT_NAME_MAP[token_string]

                except KeyError:
                    pass

                else:

                    (line_index_to_data[line_index][interval]) = category_of_name

                ## additionally, if the name is a 'def' or
                ## 'class' statement, mark the word after
                ## it to be highlighted as well, so names
                ## of classes, functions and methods
                ## appear highlighted in the line where
                ## they are defined;
                ##
                ## the has_def_or_class_statement check is
                ## important because the token string
                ## being equal to 'def' or 'class' don't
                ## mean it is an statement (it could be
                ## an attribute name used after a '.'
                ## operator, for instance)

                if token_string in ("def", "class") and has_def_or_class_statement(
                    token_line
                ):

                    interval = interval_of_next_def_word(token_line)

                    (line_index_to_data[line_index][interval]) = "name_after_definition"

            ## process the '@' operator;
            ##
            ## (if token is an operator we know it is
            ## an '@' operator, since at the top of this
            ## "for loop" we ignored all other operators)

            elif token_type == OP:

                ## if the '@' represents the usage of
                ## a decorator over a class, method or
                ## function definition (regardless of
                ## whether the decorator is nested or not)
                ## mark the operator and the name of the
                ## decorator as different categories of
                ## highlighted text;

                # the represents_applied_decorator
                # returns the interval of the name
                # after the '@' operator (since we
                # already now the interval of the
                # operator itself) if it really
                # represents the usage of a decorator

                decorator_name_interval = represents_applied_decorator(
                    line_index, source_lines
                )

                # if the interval of the name after the
                # decorator really exists, it means we
                # really have the use of a decorator,
                # so we map the intervals of the operator
                # and the name after it to their respective
                # category names

                if decorator_name_interval:

                    (line_index_to_data[line_index][interval]) = "decorator_at"

                    (
                        line_index_to_data[line_index][decorator_name_interval]
                    ) = "name_after_decorator_at"

        ### otherwise process multiline string
        ###
        ### we assume we are dealing with a string
        ### because we already filtered out tokens of
        ### type NEWLINE and NL, which leaves us with
        ### a STRING token as the only remaining type
        ### containing line separator characters

        else:

            ## if the token isn't of STRING type, it means
            ## something went wrong, so we raise an error
            ## to indicate it

            if token_type != STRING:

                raise RuntimeError(
                    (
                        "a token other than STRING has reached"
                        " this 'else' block, which is unexpected"
                        "; its token string: '{}'"
                    ).format(token_string)
                )

            ## process string as a triple quotes string

            if is_triple_quotes_string(token_string):

                ## define the indices of the first and
                ## last lines containing the string

                first_line_index = line_index
                last_line_index = token_end[0] - 1

                ## iterate over the indices of each line,
                ## from the first to the last one

                for line_index in range(first_line_index, last_line_index + 1):

                    ## grab the line text
                    line_text = source_lines[line_index]

                    ## define the interval containing the
                    ## string for each line according to
                    ## whether it is the first one, the
                    ## last one or a line in-between

                    if line_index == first_line_index:

                        interval = (token_start[1], len(line_text))

                    elif line_index == last_line_index:
                        interval = (0, token_end[1])

                    else:
                        interval = (0, len(line_text))

                    ## then map that interval to the name
                    ## of the category representing triple
                    ## quotes strings

                    (line_index_to_data[line_index][interval]) = "triple_quotes_string"

            ## just cause the string spans multiple lines,
            ## it doesn't mean it is a triple quotes string,
            ## it may just be a regular string that has line
            ## separator characters in it, which is the
            ## case here, so mark the string as a regular
            ## one;

            else:

                (line_index_to_data[line_index][interval]) = "string"

    ### since we already know which intervals contains
    ### highlighted text, now we only need to do the
    ### opposite: define which intervals of each line
    ### of text contain normal text

    for line_index, line_text in enumerate(source_lines):

        ## ignore line if it is empty
        if not line_text:
            continue

        ## otherwise define the intervals of normal text

        normal_intervals = get_remaining_intervals(
            all_indices=range(len(line_text)),
            intervals_to_subtract=(line_index_to_data[line_index].keys()),
        )

        ## and store then in the highlight data as
        ## "normal" text;
        ##
        ## the try/except clause is needed for compatibility
        ## with Python 3.7+ (see PEP 479)

        try:

            for interval in normal_intervals:

                (line_index_to_data[line_index][interval]) = "normal"

        except RuntimeError:
            pass

    ### finally return the highlighting data as a regular
    ### dict since we don't need the defaultdict
    ### functionality anymore
    return dict(line_index_to_data)
