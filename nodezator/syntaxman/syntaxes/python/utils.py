"""Utilities for Python syntax mapping."""

### standard library import
from itertools import count


### local import
from ..comment import get_comment_syntax_map


MULTI_LINE_STR_QUOTES = '"""', "'''"


def is_triple_quotes_string(string):
    """Return whether the string has triple quotes or not.

    Parameters
    ==========
    string (string)
        string which we check whether it is triple quotes
        string or not.
    """

    return (
        ## True if string starts with either '"""' or "'''"
        any(string.startswith(quote_str) for quote_str in MULTI_LINE_STR_QUOTES)
        and
        ## True if string ends with either '"""' or "'''"
        any(string.startswith(quote_str) for quote_str in MULTI_LINE_STR_QUOTES)
    )


def has_def_or_class_statement(line_text):
    """Return whether line starts w/ 'def ' or 'class '.

    Parameters
    ==========
    line_text (string)
        represents contents of a line of Python source.
    """
    ### get the startswith method of the line text after
    ### stripping its beginning from any existing
    ### whitespace
    startswith = line_text.lstrip().startswith

    ### return whether the text starts with either 'def '
    ### or 'class ' substrings or not; the space at the end
    ### of each substring is important, since it means the
    ### 'def' or 'class' portion appears isolated in the
    ### line, not as part of a longer word;

    return any(startswith(substring) for substring in ("def ", "class "))


def interval_of_next_def_word(line_text):
    """Return interval of word after 'def'/'class' statement.

    Parameters
    ==========
    line_text (string)
        A line containing a 'def' or 'class' statement.
    """
    ### get words from line text

    words = (
        ## get the line text
        line_text
        ## next strip any whitespace at beginning
        .lstrip()
        ## then replace any '(' character for a ' ' character
        ## so it doesn't get attached to the word before it
        ## when we split the string into words
        .replace("(", " ")
        ## finally split the line into words
        .split()
    )

    ## now check whether any of the words representing
    ## definition statements ('def' and 'class') are
    ## present

    for word in ("def", "class"):

        ## check whether the word is present by grabbing
        ## its index in the list of words
        try:
            index = words.index(word)

        ## if it isn't just pass
        except ValueError:
            pass

        ## if it is present however, then the word we
        ## look for should be just after it, that is,
        ## in the word from the next index

        else:

            ## grab the word in the next index
            next_word = words[index + 1]

            ## calculate an return the interval of the
            ## next word

            including_start = line_text.index(next_word)
            excluding_end = including_start + len(next_word)

            return (including_start, excluding_end)

    ## if none of the iterations in the "for loop" above
    ## causes the function to return and thus it reaches
    ## this point in the function, then we assume something
    ## is wrong and raise an error to notify this

    raise RuntimeError(
        "logic went wrong somewhere since this raise statement"
        " wasn't supposed to execute"
    )


def represents_applied_decorator(line_index, source_lines):
    """Check whether line has a decorator declaration."""
    ### grab line text from its index
    line_text = source_lines[line_index]

    ### if the quantity of '@' characters in the line
    ### isn't 1, we assume it isn't a decorator being
    ### applied, so we return an empty tuple
    if line_text.count("@") != 1:
        return ()

    ### XXX note that, in the 'if block' above, even though
    ### we assume that a line which doesn't have only one
    ### '@' character is't a decorator, there is still a
    ### possibility, however rare, in which we could still
    ### have a decorator being applied with more than one
    ### '@' character in the same line:
    ###
    ### the other(s) character(s) could be inside strings
    ### in arguments of a call, in case the decorator is
    ### returned by a callable;
    ###
    ### this kind of edge case should be dealt with in
    ### future redesigns, probably by using the tokenize
    ### module so we analize the substrings in the line
    ### by their meanings as Python source code units,
    ### not as raw strings (we'd probably eliminate NL
    ### tokens to simplify the analysys; we'd probably
    ### also use OP to found the quantity of actual
    ### '@' operators in the line, instead of using the
    ### character as a string);
    ###
    ### for now, the string analysis we use here isn't
    ### perfect, but covers common cases satisfactorily;

    ### define the index of the '@' character and the
    ### slice of the text before it, which we'll call
    ### "the indent of 'at'"

    index_of_at = line_text.index("@")
    indent_of_at = line_text[0:index_of_at]

    ### calculate the interval of the word after '@'

    ## grab index after '@'
    index_after_at = index_of_at + 1

    ## grab word after '@'

    word = (
        ## grab slice of line after the '@'
        line_text[index_after_at:]
        ## next replace any '(' character for a ' ' character
        ## so it doesn't get attached to the word before it
        ## when we split the string into words
        .replace("(", " ")
        ## then split the string into words
        .split()
        ## and finally grab the first word
        [0]
    )

    ## having found the word, now calculate its interval

    including_start = line_text.index(word, index_after_at)
    excluding_end = including_start + len(word)

    next_word_interval = including_start, excluding_end

    ### now let's check whether the next lines comply with
    ### the decorator declaration by iterating over which
    ### subsequent line;
    ###
    ### we iterate until we find a definition statement
    ### (a 'def' or 'class' statement), which confirms that
    ### we have a decorator being applied (since they are
    ### applied before definition statements);
    ###
    ### or until we hit a condition which means that our
    ### line containing '@' doesn't actually represents
    ### a decorator being applied (since the character is
    ### used for other purposes in Python as well, like
    ### matrix multiplication)

    ## grab index of next line
    next_line_index = line_index + 1

    ## iterate over each subsequent line

    for index in count(start=next_line_index):

        ## grab the text of the line
        line_text = source_lines[index]

        ## check whether same indent as the one in
        ## our first line is used in this line;
        ##
        ## if indents are different, we abort the
        ## highlighting by returning an empty tuple,
        ## since we assume it isn't the application
        ## of a decorator

        current_indent = line_text[0:index_of_at]

        if current_indent != indent_of_at:
            return ()

        ## XXX the "if block" above is another instance
        ## where what we assume could not actually be
        ## True, since different indents could be caused,
        ## for instance, by the situation shown below:
        ##
        ## @deco_func(
        ##    arg1, arg2)
        ## @deco2
        ## def func():
        ##
        ## that is, by a nested decorator with arguments
        ## being nested irregularly;
        ##
        ## once again this justifies a future redesign of
        ## this function using the tokenize module as
        ## discussed previously

        ## if current line has an '@' character at the
        ## same position that there's an '@' character in
        ## the first line, we must perform specific checks...

        if line_text[index_of_at] == "@":

            ## if quantity of '@' characters in the line
            ## isn't 1, we abort highlighting by returning
            ## an empty tuple
            if line_text.count("@") != 1:
                return ()

            ## otherwise we assume this is ok and go on to
            ## check the next line (it may be that the
            ## decorators are nested, and this is why we
            ## found a '@' before hitting a 'def' or 'class'
            ## statement)
            else:
                continue

        ## if at the beginning of the substring from the
        ## index of '@' you find a def or class statement,
        ## then we consider that we truly have a decorator
        ## declaration in our hands, so we return the
        ## interval of the word after the '@' in the
        ## first line

        startswith = line_text[index_of_at:].startswith

        if any(startswith(substring) for substring in ("def ", "class ")):
            return next_word_interval

        ## otherwise we abort highlighting by returning
        ## an empty tuple
        else:
            return ()


def get_comment_offset_intervals(line_text, comment_start):
    """Return intervals for comment syntax with offset.

    Such syntax separates normal comment text from special
    "todo" words (TODO, XXX and FIXME). The offset is
    need because the comment doesn't always start from
    the first index of the line text.

    Parameters
    ==========
    line_text (string)
        line which contains the comment (comment may
        be entire line or part of it).
    comment_start (integer)
        represent index from which comment starts in
        the line.
    """
    ### get slice of line where lies the comment
    comment = line_text[comment_start:]

    ### retrieve intervals from the comment mapped to
    ### names of categories according to an specific
    ### comment syntax (one which separates normal
    ### comment text from "todo" words)
    data = get_comment_syntax_map(comment)

    ### the data we just grab is a dict; it has another
    ### dict in its 0 (zero) key; we'll use the items
    ### from that dict in the 0 key as our source of data;
    ###
    ### such items consists of pairs in which the first
    ### element are intervals and the second elements
    ### are the name of the category of content that
    ### interval contains which is either 'normal' for
    ### normal comment text or 'todo_word' for special
    ### todo words (todo, xxx and fixme, when all letters
    ### are in uppercase)
    interval_category_pairs = data[0].items()

    ### finally return a list of pairs where the first
    ### element is an offset interval and the second pair
    ### is the name of the category to which the content
    ### in that interval belogs

    return [
        ## 2-tuple (pair)
        (
            ## 1st item:
            ## the interval, but offset by the comment start
            (including_start + comment_start, excluding_end + comment_start),
            ## 2nd item:
            ## custom category name based on the original value
            ## of the category name from the data source
            ("comment" if category_name == "normal" else "todo_word"),
        )
        ## note that the key from the data source is further
        ## decomposed into the interval boundaries called
        ## "including_start" and "excluding_end" and the
        ## value, called category_name, is used as-is
        for (including_start, excluding_end), category_name in interval_category_pairs
    ]
