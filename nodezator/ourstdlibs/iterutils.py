"""Tools related to iterables, iterators, iterations."""

### standard library import
from collections.abc import Iterable


def get_type_yielder(
    types_to_yield,
    types_not_to_iterate=(),
    types_to_ignore=(),
):
    """Return custom type-related filter generator function.

    That is, returns a generator function that

    Parameters
    ==========
    types_to_yield (tuple)
        must contain the type of the items you want to yield.
    types_not_to_iterate (tuple)
        default is an empty tuple; if not empty, must contain
        iterable types over which you don't want to iterate.
    types_to_ignore (tuple)
        types that must be ignored; used, for instance,
        to prevent subtypes to be yielded.

    Doctests
    ========

    Case 1
    ------

    For instance, we want strings.

    >>> str_yielder = get_type_yielder(types_to_yield=(str))
    >>> l1 = ['str0', ('str1', 'str2'), ['str3'], 'str4']
    >>> list(str_yielder(l1))
    ['str0', 'str1', 'str2', 'str3', 'str4']

    Case 2
    ------

    We want integers, but there's no point in iterating
    strings in search of integers, so we don't iterate them.

    >>> int_yielder = get_type_yielder(
    ...                types_to_yield=(int),
    ...                types_not_to_iterate=(str)
    ...              )
    >>> l2 = [1, (2, 3), 'no integers here', [4, 5], True]
    >>> list(int_yielder(l2))
    [1, 2, 3, 4, 5, True]

    The usage of the 'types_not_to_iterate' in the example
    above is done to prevent useless work, since even if we
    didn't define strings as a type not to be iterated, the
    return value would be the same as can be seen below:

    >>> new_int_yielder = get_type_yielder(
    ...                     types_to_yield=(int)
    ...                   )
    >>> l3 = [1, (2, 3), 'no integers here', [4, 5], True]
    >>> list(new_int_yielder(l3))
    [1, 2, 3, 4, 5, True]

    Case 3
    ------

    We want integers, but strictly integers, no subtypes
    allowed.

    >>> strict_int_yielder = get_type_yielder(
    ...                       types_to_yield=(int),
    ...                       types_not_to_iterate=(str),
    ...                       types_to_ignore=(bool)
    ...                     )
    >>> l4 = [1, (2, 3), 'I have no integers', [4, 5], True]
    >>> list(strict_int_yielder(l4))
    [1, 2, 3, 4, 5]
    """

    def yield_type(iterable_obj):
        """Yield items of specific types.

        If the iterable object contains iterable items,
        we may further iterate over those as well,
        depending on whether they meet specific conditions.

        That is, this generator may iterate recursively.

        Parameters
        ==========
        iterable_obj (any iterable instance)
            object over which to iterate.
        """
        ### iterate over the items in the given iterable,
        ### yielding the wanted items and further iterating
        ### the item's contents when appropriate

        for item in iterable_obj:

            ### if the item is of one of the desired types
            ### and not of one of the undesired ones,
            ### yield it

            if isinstance(item, types_to_yield) and not isinstance(
                item, types_to_ignore
            ):
                yield item

            ### otherwise, if the item can be subject to
            ### iteration without incurring in recursion
            ### and its type is not listed among those
            ### not to be iterated, we must try to yield
            ### from it

            elif (
                ## item must be iterable
                isinstance(item, Iterable)
                ## and its type must not be listed among
                ## those not to be iterated
                and not isinstance(item, types_not_to_iterate)
                ## also, to prevent recursion in iterable
                ## classes whose items are also iterables,
                ## like strings, the item must also be
                ## different from the iterable itself
                and item != iterable_obj
            ):
                yield from yield_type(item)

            ### since the two conditional branches above
            ### (the "if block" and "elif block") are the
            ### only scenarios of interest, no "else clause"
            ### is needed;

    ### return the yielder function
    return yield_type


def separate_by_condition(items, bool_func=bool):
    """Return two lists of items separated by a condition.

    That is, we iterate over the items, evaluating them
    according to a condition given in the form of a
    boolean function.

    The items who don't pass are stored in the first list
    (the "false list") and those who do are stored in the
    second one (the "true list").

    Doctests
    ========

    >>> separate_by_condition([2, 4, 0, 22, 0, 11])
    ([0, 0], [2, 4, 22, 11])
    >>> separate_by_condition('AbcDefGhI', str.isupper)
    (['b', 'c', 'e', 'f', 'h'], ['A', 'D', 'G', 'I'])
    """
    ### create the false and true lists
    false_list, true_list = [], []

    ### reference their append method locally for easier
    ### and quicker access

    append_false = false_list.append
    append_true = true_list.append

    ### iterate over items, storing each of them in one of
    ### the lists, depending on whether they condition is
    ### evaluated to True or False

    for item in items:

        ## append item in "true list" if condition
        ## passes

        if bool_func(item):
            append_true(item)

        ## otherwise, append it in the "false list"
        else:
            append_false(item)

    ### finally return both lists
    return false_list, true_list
