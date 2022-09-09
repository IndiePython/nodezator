"""Function to validate text of text block."""

### local imports

from ...ourstdlibs.stringutils import check_contains_non_whitespace

from ...ourstdlibs.exceptionutils import new_raiser_from_existing


### utility function to validate text for text block

check_text_block_text = (
    ## get new function with custom exception raising
    ## behaviour
    new_raiser_from_existing(
        ## use check_contains_non_whitespace as original
        ## function to raise exception
        raiser_func=check_contains_non_whitespace,
        ## but format the message of the original exception
        ## with the given str.format function
        message_formatter=(
            "Text for text block must adhere to following" " requirement: {}"
        ).format,
        ## also leave the message as-is (that is, don't
        ## include the name of the exception class in the
        ## original message before passing it to the formatter
        ## we gave as the 'message_formatter' argument above
        include_exception_name=False,
    )
)
