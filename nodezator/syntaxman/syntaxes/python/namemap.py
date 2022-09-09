"""Map grouping special words in Python syntax.

In this module we define a dict which maps special words
in Python to the name of a category for it.
"""

### standard library imports

import builtins

from itertools import chain, repeat

from keyword import kwlist as KEYWORDS


### sets of special names in Python source code

BOOLEANS = {"True", "False"}

NONE_AND_ELLIPSIS = {"None", "Ellipsis"}

# note that to build some constants below it is important
# that we use the imported "builtin" module instead of
# __builtins__ because apparently, when executing a script,
# dir(__builtins__) is equivalent to dir(dict), which isn't
# desired;

BUILTIN_EXCEPTIONS = set(
    set(builtin_name for builtin_name in dir(builtins) if builtin_name[0].isupper())
    - BOOLEANS
    - NONE_AND_ELLIPSIS
)

BUILTIN_FUNCTIONS = set(
    ### most builtins which are lowercase and don't start
    ### with an underscore are builtin functions
    set(
        builtin_name
        for builtin_name in dir(builtins)
        if builtin_name.islower()
        if not builtin_name.startswith("_")
    )
    ### except the words below, which we remove from
    ### the set of builtins functions
    - {"copyright", "credits", "license"}
)

IMPORT_AND_LOGICAL = {"and", "from", "import", "in", "is", "not", "or"}


### map associating each word with a highlight code name to
### identify the kind of content the word represents

HIGHLIGHT_NAME_MAP = {
    word: highlight_code_name
    for word, highlight_code_name in chain(
        ## builtin functions and exceptions
        zip(BUILTIN_FUNCTIONS, repeat("builtin_function")),
        zip(BUILTIN_EXCEPTIONS, repeat("builtin_exception")),
        ## keyword names
        zip(KEYWORDS, repeat("keyword")),
        ## other special names
        ##
        ## these zip objects must come after the zip object
        ## from the KEYWORDS, because their words will
        ## override some words from KEYWORDS
        zip(BOOLEANS, repeat("boolean")),
        zip(NONE_AND_ELLIPSIS, repeat("none_and_ellipsis")),
        zip(IMPORT_AND_LOGICAL, repeat("logical_and_import")),
    )
}
