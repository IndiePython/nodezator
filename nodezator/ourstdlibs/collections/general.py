"""Special collections for general use."""


class CallList(list):
    """A list of callable objects to be executed in order."""

    def __init__(self, *args, **kwargs):
        """Check callable state of items.

        Extends list.__init__
        """
        super().__init__(*args, **kwargs)

        if not all(map(callable, self)):
            raise ValueError("All items must be callable")

    def __call__(self):
        """Call all items."""
        for item in self:
            item()

    def append(self, item):
        """Append item if callable. Extends list.append."""
        if not callable(item):
            raise ValueError("All items must be callable")

        else:
            super().append(item)

    def insert(self, index, item):
        """Insert item if callable. Extends list.insert."""
        if not callable(item):
            raise ValueError("All items must be callable")

        else:
            super().insert(index, item)

    def extend(self, iterable):
        """Extend call list if all in iterable are callable.

        Extends list.extend.
        """
        if not all(map(callable, iterable)):
            raise ValueError("All items must be callable")

        else:
            super().extend(iterable)


class FactoryDict(dict):
    """Produces value in function of missing key."""

    def __init__(self, callable_obj):
        """Store callable used to create missing values.

        Whenever someone tries to access a missing key,
        this dict instance executes the callable with the
        missing key and uses the return value as the
        new value, which is stored in the dict and
        returned.
        """
        self.callable_obj = callable_obj

    def __missing__(self, key):
        value = self[key] = self.callable_obj(key)
        return value
