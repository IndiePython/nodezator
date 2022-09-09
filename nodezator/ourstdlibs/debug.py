"""Facility for debugging tools."""

### standard library import
from itertools import cycle


### scaffolding tools


def print_and_return(obj):
    """Return any given object after printing it.

    - obj (any Python object)
    """
    print(obj)
    return obj


def get_cyclic_countdown(steps, true_index=-1):
    """Get a countdown for delayed execution in if blocks.

    Useful to perform certain actions after a given number
    of iterations. For instance, you can use it in
    "while loops" to make something execute at each "n"
    iterations.

    Parameters
    ==========
    steps (integer)
        number of steps until the cycle starts over.
    true_index (integer)
        the index at which the cycle returns True; naturally,
        negative integers are allowed; for instance, -1
        (the default value), makes it so the last item of
        the cycle is True.

    Doctests
    ========

    >>> # the if block below will execute one time for each
    >>> # 10 iterations, in the last of each 10 iterations
    >>> countdown = get_cyclic_countdown(10)
    >>> for i in range(20):
    ...     if countdown(): print(i, "hello")
    ...
    9 hello
    19 hello

    >>> # the if block below will also execute once for each
    >>> # 10 iterations, but it will execute in the first
    >>> # iteration of each 10 iterations
    >>> countdown = get_cyclic_countdown(10, 0)
    >>> for i in range(20):
    ...     # the if block bellow will execute after 10
    ...     # loops/frames (in the 11th loop)
    ...     if countdown(): print(i, "hello")
    ...
    0 hello
    10 hello
    """
    ### create a list filled with False for each step
    items = [False for _ in range(steps)]

    ### assign True to the requested index
    items[true_index] = True

    ### create a cycle with the list, returning its
    ### __next__ method as the countdown

    cycle_obj = cycle(items)
    countdown = cycle_obj.__next__

    return countdown
