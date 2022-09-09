"""Facility for execution related functions.

Definitions for doctests:

>>> from functools   import partial
>>> from collections import deque
"""
### standard library imports

from functools import partial, reduce, wraps

from collections import deque
from collections.abc import Mapping

from contextlib import suppress


def empty_function():
    """Do nothing. An empty function.

    Replaces 'lambda:None' solution.

    Some respected members in the pygame community don't
    recommend the usage of lambda functions for the sake
    of clarity. I'm still divided about it, but for such
    simple function declaration there's no cost at all
    to declare and keep it and when it is imported it has
    the advantage of communicating that some behaviour in
    the module has a 'switched off' state.

    Profiling have shown a very tiny and practically
    insignificant speed gain (less than fractions of
    microseconds) over the lambda solution, though not
    consistent through many tests.

    Try yourself on your command line:

    python -m timeit --setup "f = lambda:None" "f()"
    python -m timeit --setup "def f():pass"    "f()"

    Doctest of my life

    >>> empty_function()
    >>>

    Disclaimer: for a function which does nothing, I know
    it has quite the docstring (including its doctest),
    but the discussion and design considerations are always
    important; you don't need to be as detailed as I am,
    but reviewing your design decisions and documenting them
    is a very constructive habit and helps to develop your
    analytical thinking.
    """


def empty_oblivious_function(*args, **kwargs):
    """Ignore arguments and do nothing.

    A function just like empty_function(), but which
    accepts arguments, even though nothing is done with
    them.
    """


def return_untouched(arg):
    """Return the received argument.

    Simple identity function (in the mathematical sense,
    that is, an operation which doesn't change the operand)
    to fulfill use cases where a processing behaviour is
    required but we want it to have no effect at all.

    arg (any Python object)
    """
    return arg


## nesting related utilities


def get_nested_value(d, *strings):
    """Return inner value from nested dict.

    d (dict)
        Dictionary containing other nested dictionaries.
    strings (string arguments)
        Strings used to retrieve innermost item.

    >>> d = {
    ...   "john" : {
    ...     "id" : 22,
    ...     "school" : {
    ...       "id" : 1043,
    ...       "name" : "St. Lewis"
    ...     }
    ...   }
    ... }
    >>> get_nested_value(d, "john", "school", "id")
    1043

    ### curiosity

    A higher level version, could work with any nested
    objects with a __getitem__ method,
    and instead of strings could receive any arbitrary
    value, as long as it could be used by __getitem__ to
    retrieve the next one

    get_nested_value(obj, values):
        for item in values: obj = obj[item]
        return obj

    this would allows us to retrieve deep nested values
    within dicts, lists, tuples, etc.

    Maybe I should profile this with the higher level version
    to see if it is worth to use the more general approach
    of the higher level version.
    """
    return reduce(dict.__getitem__, strings, d)


def flatten_mapping_values(mapping_obj):
    """Return all values from map, including nested ones.

    The values are return in the form of a generator
    object.

    The mapping_obj parameter receives any python obj for
    which isinstance(obj, collections.abc.Mapping)
    returns True. It's "values" method is used to return
    its values.

    Since the order of the returned values in the
    generator depends on the specific mapping
    implementation there's no way to predict the order in
    which the values are returned.

    Even more so considering the execution flow goes
    through many different mappings in different nesting
    levels. Thus, such mappings may or not have different
    implementations.

    >>> phone_numbers = {
    ...   "Kelly": 5128,
    ...   "Amanda": {
    ...     "home": 8222,
    ...     "work": 4560
    ...   }
    ... }
    >>> actual = flatten_mapping_values(phone_numbers)
    >>> expected = (5128, 8222, 4560)
    >>> sorted(actual) == sorted(expected)
    True
    """
    ### iterate over all values in the mapping obj

    for value in mapping_obj.values():

        ## if the value isn't a mapping just yield it
        if not isinstance(value, Mapping):
            yield value

        ## otherwise, pass the value through this function
        ## again recursively, yielding each nested item
        ## resulting from the call

        # XXX use 'yield from' statement here

        else:

            for nested_value in flatten_mapping_values(value):
                yield nested_value


## attribute utilities


def get_attrs(obj, attr_names):
    """Yield attributes from given object.

    Parameters
    ==========
    obj (any Python object)
        obj from which we'll retrieve the attributes.
    attr_names (iterable of strings)
        provide the names of the attributes to be retrieved.
    """
    return (getattr(obj, attr_name) for attr_name in attr_names)


# toggling utilities


def get_attribute_rotator(obj, attr_name, values):
    """Return a function to rotate obj attribute values.

    Creates a partial from the provided arguments and the
    rotate_attribute function.

    obj (any object which can have attributes set on it)
        object whose attribute is used to hold the value.
    attr_name (string)
        name of the attribute where to store a value.
    values (iterable containing any python objects/values)
        values between which to toggle.

    Also sets the first value on the obj attribute.

    >>> values = [12, 32, 45, 26]
    >>> rotate = get_attribute_rotator
    """
    values_deque = deque(values)

    setattr(obj, attr_name, values_deque[0])

    return partial(rotate_attribute, obj, attr_name, values_deque)


def rotate_attribute(obj, attr_name, values_deque):
    """Rotate attribute value between those provided.

    This function is meant to be turned into partials
    by the get_attribute_rotator function for more efficient
    usage.

    Tip: passing a deque with two values creates a simple
    very useful toggle.

    obj (any object which can have attributes set on it)
        object whose attribute is used to hold the value.
    attr_name (string)
        name of the attribute where to store the value.
    values_deque (deque containing any python object/values)
        values between which to toggle.

    >>> class Obj: pass
    ...
    >>> obj = Obj()
    >>> d = deque(["a", "b", "c"])
    >>> rotate = partial(rotate_attribute, obj, "char", d)

    >>> rotate()
    >>> obj.char
    'b'
    >>> rotate()
    >>> obj.char
    'c'

    >>> obj.char = "b"
    >>> rotate()
    >>> obj.char
    'a'

    Notice in the last doctest section that even when we
    set the char attribute to "b" the next value of char
    after rotating is "a". This is because the assignement
    follows the rotation of the deque, without taking into
    consideration the current value.

    If you need a function that takes into account the
    current value before assigning a new one you should use
    the get attribute toggler function.
    """
    values_deque.rotate(-1)
    setattr(obj, attr_name, values_deque[0])


def get_attribute_toggler(
    obj, attr_name, starting_value, mapping_or_value, default=None
):
    """Return function to toggle obj atribute values.

    Creates a partial from the provided arguments using
    the toggle_attribute function.

    obj (any object which can have attributes set on it)
        object whose attribute is used to hold the value.
    attr_name (string)
        name of the attribute where to store a value.
    starting_value (any hashable obj/value),
        starting value to be assigned to the attribute.

    mapping_or_value (a dict or any hashable obj/value)
        The type of mapping_or_value may be different depending
        on two scenarios:

        1) If you have more than two values between which
           you desired to toggle though, you must then
           provide a mapping which associates the current
           value of the attribute with the desired value to
           be assigned when toggling.


        2) value to which we should toggle when executing
           the partial returned. Executing the partial
           returned again should set the previous value
           in the attribute again and so on.

        Either way the arguments are stored in a mapping
        so they fit the first scenario, thus complying with
        the underlying toggle_attribute function.

        The first scenario is just a simplification, since
        having two values to toggle would mean you want to
        toggle between them in this context. There's no
        absolute need to make each value reference each other,
        though. The work of the toggle is just to set a
        value for the attribute based on the current value
        stored there. If no value is found in the dict which
        is associated with the current value, the toggler
        (partial) will do nothing.
    default (any python value/object)
        Value to use only in case no key is found.

    >>> class Obj: pass
    ...
    >>> obj = Obj()
    >>> toggle_char = get_attribute_toggler(
    ...                   obj, 'char', 'a', 'b')
    >>> obj.char
    'a'
    >>> toggle_char()
    >>> obj.char
    'b'
    >>> obj.char = 'c'
    >>> toggle_char()
    >>> obj.char # without default it returns None
    >>>

    >>> obj.char = 'a'
    >>> toggle_char()
    >>> obj.char
    'b'
    >>> d = {1:5, 5:22, 22:13, 13:1}
    >>> toggle_number = get_attribute_toggler(
    ...                     obj, 'number', 22, d, 100)
    >>> obj.number
    22
    >>> toggle_number()
    >>> obj.number
    13
    >>> toggle_number()
    >>> obj.number
    1
    >>> obj.number = 342
    >>> toggle_number()
    >>> obj.number # 342 isn't a key, so returns default
    100

    """
    ### set the starting value of the attribute
    setattr(obj, attr_name, starting_value)

    ### now check the type of the arguments so you can
    ### create or reference the cross_mapped_values dict

    ## if mapping_or_value is a dict, reference it
    if isinstance(mapping_or_value, dict):
        cross_mapped_values = mapping_or_value

    ## otherwise, mapping_or_value is actually a value,
    ## so just use it to build a new dict
    else:
        another_value = mapping_or_value

        cross_mapped_values = {
            starting_value: another_value,
            another_value: starting_value,
        }

    ### return function
    return partial(toggle_attribute, obj, attr_name, cross_mapped_values, default)


def toggle_attribute(obj, attr_name, cross_mapped_values, default=None):
    """Toggle attribute between values a and b.

    This function is meant to be turned into partials
    by the get_attribute_toggler function for more efficient
    usage.

    It is slightly different from the toggler achievable with
    the get_attribute_rotator function because it checks the
    value of the attribute before toggling, so there is no
    intrinsic order. The value set depends solely on the
    current value.

    obj (any object which can have attributes set on it)
        object whose attribute is used to hold the value.
    attr_name (string)
        name of the attribute where to store the value.
    cross_mapped_values (dict)
        its keys reference each other. Such keys represent
        values from which and to which to toggle.
    default (any python value/object)
        Value to use only in case no key is found.

    >>> class Obj: pass
    ...
    >>> obj = Obj()
    >>> d = {"a":"b", "b":"a"}
    >>> toggler = partial(toggle_attribute, obj, "char", d)

    >>> obj.char = "a"
    >>> toggler()
    >>> obj.char
    'b'
    >>> toggler()
    >>> obj.char
    'a'
    """
    ### retrieve current attribute value to use as key
    key = getattr(obj, attr_name)

    ### retrieve value using key, also defining a default
    ### to be returned if needed
    value = cross_mapped_values.get(key, default)

    ### assign value to the attribute
    setattr(obj, attr_name, value)


## other utilities


def remove_by_identity(item_for_removal, a_list):
    """Remove item from list using an identity check.

    A ValueError is raised if the item isn't present.

    Parameters
    ==========
    item_for_removal (any value)
        item to be removed.
    a_list (list)
        list from where the item will be removed.
    """
    ### iterate over the list, keep tracking of the
    ### current index of the current item

    for index, item in enumerate(a_list):

        ## if the current item - is - the item for removal,
        ## pop it from the list using its index, then break
        ## out of the loop

        if item is item_for_removal:

            # changing the list while looping
            # it won't have adverse effects
            # because we break out of the loop
            # immediately after changing the list
            a_list.pop(index)
            break

    ### if the loop resumes normally, without we breaking
    ### out of it though, it means we didn't find the item
    ### for removal, so raise a ValueError to indicate it
    else:
        raise ValueError("'item_for_removal' not in list")


def had_to_set_new_value(obj, attr_name, new_value):
    """Return whether had to set new value for attr.

    That is, if the given value is different than the
    one stored on the

    If the attribute didn't previously exist, we also
    consider this case as a case where the value changed.
    We also set the attribute to the new value, if it
    changed.
    """
    ### check whether the attribute existed previously,
    ### considering the value as the current one
    try:
        current_value = getattr(obj, attr_name)

    ### if there's no current value, we just pass, since
    ### we'll be creating the attribute in the next step
    except AttributeError:
        pass

    ### if there is a current value, though, we check
    ### whether such value is equal to the new one,
    ### in which case we just return False to indicate
    ### we didn't need to set the attribute ourselves

    else:
        if current_value == new_value:
            return False

    ### if we get to this point in the function, than
    ### the attribute either didn't exist or it's value
    ### is different than the new one provided, meaning
    ### we need to set it to the new value
    setattr(obj, attr_name, new_value)

    ### we finally return True to indicate we had to set
    ### the value
    return True


## wrapping utilities


def get_decorator_from_wrapper(wrapper_func):
    """Return decorator function from a wrapper function.

    That is, this function allows a function A which is
    used to wrap a function B with extra behaviour to be
    used as a decorator with arguments.

    In other words, it turns the pattern below:
    # func_c = func_a(func_b, *args, **kwargs)

    Into the pattern below
    # @func_a(*args, **kwargs)
    # def func_b(...):
    # ...
    """

    def get_decorator(*args, **kwargs):
        """Return decorator function.

        Used to collect positional and keyword arguments.
        So they can be used by the decorator which it
        returns.
        """

        def get_wrapped_func(func):
            """Wrap function w/ args and return it."""
            wrapped_func = wrapper_func(func, *args, **kwargs)
            return wrapped_func

        return get_wrapped_func

    return get_decorator


def get_oblivious_callable(func):
    """Return callable which executes func ignoring args.

    Parameters
    ==========
    func (callable object)
        callable to be wrapped in the function which
        ignores arguments when called.

    Original use-case
    =================

    We had a function that didn't need any arguments, but
    had to use it in a scenario where it was required to
    conform to an arbitrary protocol (it had to receive a
    single argument).

    We didn't want to add a parameter to it just for that
    specific scenario and risk turning it unnecessarily
    confusing for people analysing from the point of view
    of the other scenarios where no argument is needed at
    all.

    So, instead of changing the functions, it is much more
    convenient to wrap the function with this wrapper,
    just before providing it wherever it needs to be used.
    """

    @wraps(func)
    def execute(*args, **kwargs):
        """Execute func ignoring arguments; return value."""
        return func()

    return execute


def get_suppressing_callable(func, *exceptions):
    """Return callable which suppresses given exceptions.

    Parameters
    ==========
    func (callable object)
        callable to be wrapped in the function which
        ignores arguments when called.
    exceptions (instance(s) of Exception to be suppressed)
        exceptions to be suppressed.
    """

    @wraps(func)
    def execute(*args, **kwargs):
        """Execute func supressing exceptions."""
        with suppress(*exceptions):
            return func(*args, **kwargs)

    return execute
