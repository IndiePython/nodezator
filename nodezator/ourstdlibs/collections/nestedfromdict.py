"""Facility with custom dict class with dot notation."""


from collections.abc import Mapping


class NestedObjectFromDict:
    """Nested object created from dicts/dict arguments."""

    def __init__(self, *args, **kwargs):

        ###
        d = dict(*args, **kwargs)

        ###

        to_change = [
            (key, value) for key, value in d.items() if isinstance(value, Mapping)
        ]

        ###

        cls = self.__class__
        for key, value in to_change:
            d[key] = cls(value)

        ###

        for key, value in d.items():

            if (key, value) in to_change:
                continue

            setattr(self, key, value)

    def __repr__(self):

        middle = ""
        for key, value in self.__dict__.items():
            middle += f"{key!r}={value!r}, "

        return f"{self.__class__.__name__}({middle[:-1]})"
