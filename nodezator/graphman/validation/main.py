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

        raise TypeError("return annotation must be of class 'list'")

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

    ### viewer node indication
    ###
    ### if the node is meant to be a viewer node, than
    ### it can have 01 or 02 outputs with a 'viz' key, which means
    ### those outputs will be used to retrieve visualization data;
    ###
    ### if 01, it must be 'side', and if 02, one must be 'side' and
    ### the other must be 'loop';

    viz_values = [
        a_dict['viz']
        for a_dict in return_annotation
        if 'viz' in a_dict
    ]

    if viz_values:

        count = len(viz_values)

        if count == 1 and viz_values[0] != 'side':

            raise ValueError(
                "if only one 01 output is marked to be used as"
                " visualization data, the value of 'viz' must be 'side',"
                " so the visualization data is used as the in-graph visual"
                " (beside the node)"
            )

        elif count == 2 and set(viz_values) != {'side', 'loop'}:

            raise ValueError(
                "if 02 outputs are marked to be used as visualization data,"
                " the value of 'viz' must be 'side' in one and 'loop' in the"
                " other (the order isn't important, but only those values"
                " are allowed), to indicate they provide visualization to be"
                " displayed beside the node and within a visualization loop"
            )
