"""Utilities related to dictionaries."""

### standard library import
from ast import literal_eval


def flatten_keys(mutable_mapping):

    for key in list(mutable_mapping):

        value = mutable_mapping.pop(key)

        for subkey in key:
            mutable_mapping[subkey] = value


def settings_to_hashable_repr(settings_dict):
    """Return custom hashable representation of settings.

    The settings are represented by a dictionary where
    the keys are the names of each setting and the values
    are the values of that setting.

    That is, the settings received are returned as a
    hashable object representing that specific settings.

    Parameters
    ==========

    settings_dict (dict)
        contains items whose keys and values correspond
        to setting names and their respective value;

    Return value
    ============

    A tuple wherein each value is a 2-tuple representing
    the key-value pair from each item in the dictionary.
    The value from the pair is converted into a string
    representation using repr(). The pairs are also
    ordered by the keys.

    Why use the specific format returned?
    =====================================

    Sometimes we need a hashable format of the settings in
    order to store it as a key into another dictionary.

    We could turn the dict into an unique string, ensuring
    the order of the contents by using something like
    json.dumps(settings_dict, sort_keys=True). However,
    this would fail with values which are not serializable
    in json, like pygame.color.Color instances, in case
    someone decided to use them as values in the settings
    dict.

    That is why we use a tuple instead, with just the
    values. You may also want to know why we turn the
    values into repr() strings, though.

    We do so because this tuple is meant to be used as
    a key in a dictionary, so it would raise an error
    if the value used as an item in the tuple was
    unhashable, for instance, if someone uses a list
    instance to represent a color.

    By using repr(), there is also a chance that,
    if python literals are used, the return value can be
    easily turned back into its original dict format
    using ast.literal_eval on the values.
    """
    ### return a tuple...
    return tuple(
        ### ...wherein each item is a 2-tuple representing a
        ### key-value pair from the dict, with the value
        ### turned into a repr() string...
        (key, repr(settings_dict[key]))
        ### ..and such pairs are ordered by the name of the
        ### keys
        for key in sorted(settings_dict.keys())
    )


def hashable_repr_to_settings(a_tuple):
    """Return dict from given tuple.

    This function does the opposite of the
    settings_to_hashable_repr() function above.
    """
    ### return a dict...

    return {key: literal_eval(value) for key, value in a_tuple}
