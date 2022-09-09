"""Class extension for rectsman.main.RectsManager class."""


class SpecialMethods:
    """Python data model methods for the RectsManager class.

    Except for __init__ and __copy__, which are defined
    on the body of the RectsManager class itself.
    """

    ## method for returning an iterator

    def __iter__(self):
        """Yield each item from the union rect.

        Implemented for speed. Check the extensive
        documentation referenced in this class'
        docstring for more information.
        """
        yield from self.union_rect

    ## item getting/setting/deleting

    def __getitem__(self, index):
        """Return item from union rect index."""
        return self.union_rect[index]

    def __setitem__(self, index, value):
        """Set new value change corresponding property."""
        ### set item from sample rect using given index
        ### and value; this has the desired side-effect
        ### of the pygame.Rect instance performing type
        ### checking and error raising for us
        self._sample_rect[index] = value

        ### finally set new value for the property
        ### represented by the given index (note that we
        ### retrieve the value we just assigned to the
        ### sample_rect from it again; this way we take
        ### advantage of pygame.Rect type coercion)

        property_name = self._index_to_property[index]
        setattr(self, property_name, self._sample_rect[index])

    def __delitem__(self, index):
        """Set new value change corresponding property."""
        ### del item from sample rect using given index
        ### and value for the desired side-effect of type
        ### checking and error raising from pygame.Rect
        del self._sample_rect[index]

    ## different representations of the instance

    def __repr__(self):
        """Return result from repr(union_rect)."""
        return repr(self.union_rect)

    def __str__(self):
        """Return result from str(union_rect)."""
        return str(self.union_rect)

    def __bool__(self):
        """Return bool(union rect)."""
        return bool(self.union_rect)

    ## handling missing attributes/methods

    def __getattr__(self, name):
        """Return getattr(union, name)."""
        return getattr(self.union_rect, name)

    ### for an explanation as to why there's no custom
    ### __setattr__ implementation, check the
    ### "No custom attribute setting (__setattr__ method)"
    ### section in the "test04_specialmethods.py" test file
    ### in the extensive documentation referenced in this
    ### class' docstring.

    ## attribute deletion

    def __delattr__(self, name):
        """Execute delattr(union, name).

        The code in this method is bound to fail, since
        one can't delete attributes from the pygame.Rect
        instance returned by self.union_rect.

        The purpose of this method is to reproduce the
        exception raising behaviour of the pygame.Rect
        class.
        """
        delattr(self.union_rect, name)

    ## rich comparison methods

    def __eq__(self, other):
        """Return whether the union rect equals other.

        Also, since we didn't implement a custom __ne__
        (the '!=' operation), Python automatically uses the
        invert return value of this method instead when
        '!=' is used.

        Profiling tests shows that, at least in the
        machine tested, not implementing a custom __ne__
        (and thereby using the inverse of this method)
        makes calculating "!=" quicker, though the
        difference is tiny (usually 2 or 3 twentieths
        of a microsecond).
        """
        return self.union_rect == other

    def __gt__(self, other):
        """Return union rect's __gt__ return value."""
        return self.union_rect > other

    def __lt__(self, other):
        """Return union rect's __lt__ return value."""
        return self.union_rect < other

    def __ge__(self, other):
        """Return union rect's __ge__ return value."""
        return self.union_rect >= other

    def __le__(self, other):
        """Return union rect's __le__ return value."""
        return self.union_rect <= other

    ## length retrieval

    def __len__(self):
        """Return len(union rect)."""
        return len(self.union_rect)
