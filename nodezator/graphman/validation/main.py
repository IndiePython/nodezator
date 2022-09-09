"""Facility with operation to validate callable metadata.

Check the sibling module doctests.py for more documentation
and tests.
"""


def check_return_annotation_mini_lang(return_annotation):
    """Check whether return annotation adopts mini-language.

    Return annotations from Python callables are optional.
    When present, they may have any content.

    However, users may optionally want to use a
    mini-language defined to specify different output
    names for a function.

    Here we check whether such convention is followed.
    This return_annotation will undergo additional
    processing.

    Parameters
    ==========

    return_annotation (list)
        A list whose contents must be checked for
        compliance with pre-defined rules.
    """
    ### return annotation must be a list

    if not isinstance(return_annotation, list):

        raise TypeError("return annotation must be of class" " 'list' or 'tuple'")

    ### items must all be dictionaries

    if not all(isinstance(item, dict) for item in return_annotation):

        raise TypeError("items in 'return_annotation' must all" " be of class 'dict'")

    ### items must all have a 'name' field

    if not all("name" in item for item in return_annotation):

        raise ValueError("items in 'return_annotation' must all" " have a 'name' field")

    ### value of 'name' fields must all be strings

    if not all(isinstance(item["name"], str) for item in return_annotation):

        raise TypeError(
            "value of 'name' fields in"
            " 'return_annotation' items must all"
            " be of class 'str'"
        )

    ### items must all be valid Python identifiers
    ### this is important to avoid issues when combining
    ### the name of outputs with the id of the nodes
    ### to which they belong; additionally, it prevents
    ### the user to use whitespace in the output name,
    ### which may decrease the readability of the
    ### output name in the node

    if not all(str.isidentifier(item["name"]) for item in return_annotation):

        raise ValueError(
            "the value of 'name' fields in each item"
            " of the 'return_annotation' must pass the"
            " str.isidentifier test"
        )

    ### names must not be equal to each other

    ## list names

    names = [item["name"] for item in return_annotation]

    ## if there are equal names, set(names) will have less
    ## items and this will result in an exception being
    ## raised

    if len(set(names)) < len(names):

        raise ValueError(
            "items of 'return_annotation' must not have"
            " 'name' fields with the same value"
        )
