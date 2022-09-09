"""Facility for custom dictionary class definition."""

from copy import deepcopy
from collections.abc import Mapping

### local import
from ...behaviour import flatten_mapping_values


### XXX development note: in the future, the list class
### may be replaced by view-like, custom subclasses of
### those builtin classes, for added protection against
### misuse in the poka-yoke style; however, this is not
### urgent since there's activities of higher priority to
### be executed


class FlatListDict(dict):
    """Dictionary w/ a list of all values, nested or not.

    The list in question is found in the "flat_values"
    read-only attribute.

    Check the full docstring along with doctests in
    the fltests.py module.
    """

    ### list names of the builtin list methods so you can
    ### reference them later

    builtin_list_method_names = ("extend", "append", "remove", "clear")

    ### define names for custom attributes wherein to store
    ### bound methods of the builtin list instance

    bound_method_names = (
        "_bound_extend",
        "_bound_append",
        "_bound_remove",
        "_bound_clear",
    )

    ### constructor

    def __init__(self, *args, **kwargs):
        """Initialize superclass and perform setups.

        The setups are the creation of the flat_values
        list and the aliasing of its bound methods into
        this class instance attributes (so they can be
        directly accessed).

        Parameters:

        *args, **kwargs (positional and keyword variable
        parameters to be used by the dict constructor)

        Extends dict.__init__ method.
        """
        ### initialize the superclass
        super().__init__(*args, **kwargs)

        ### instantiate and store the flat values list
        ### using the values from this dict

        ## get generator expression which returns all values
        flat_values = flatten_mapping_values(self)

        ## feed generator into the list constructor and
        ## store the resulting instance
        self._flat_values = list(flat_values)

        ### assign and perform operations to prep the flat
        ### values list

        ## pair up the list builtin method names with the
        ## names define for their bound version

        paired_up_items = zip(self.builtin_list_method_names, self.bound_method_names)

        ## we will now iterate over the paired up items,
        ## assigning the bound methods of the flat_values
        ## list to the attribute names provided

        for builtin_name, name_for_bound in paired_up_items:

            ## retrieve the bound method using its name
            bound_method = getattr(self._flat_values, builtin_name)

            ## store the bound method in the
            ## instance attribute using the name define
            ## for the bound method
            setattr(self, name_for_bound, bound_method)

    ### turn _flat_values into a property as a poka-yoke
    ### mechanism against unintentional reassignment of
    ### the attribute

    @property
    def flat_values(self):
        """Return _flat_values attribute."""
        return self._flat_values

    ### methods inherited from dict builtin which alter
    ### its contents must be extended so they also
    ### update the values in the "flat_values" list

    def __setitem__(self, key, value):
        """Set value on key and update the flat values set.

        key (any hashable python object)
            object used as dictionary key.
        value (any python object)
            object to be mapped to the key object.

        Extends dict.__setitem__.

        ### Alternative implementation

        As can be seen in the method body, the method is
        divided into three operations:

        1) delete item corresponding to key if existent
        2) use dict.__setitem__ to set the new value for
           the key
        3) store the new value(s) in the flat_value list

        Such operations can alternatively be reduced to two
        operations, if so desired:

        1) use dict.__setitem__ to set the new value for
           the key (same as number (2) above)
        2) clearing and repopulating the flat values, which
           can be done by simply executing the "update"
           method without arguments (it happens as a
           side-effect).

        But we decide against it because depending on the
        size of both this class instance and the new value
        being set just removing items from current value
        (current step (1)) and storing items from new value
        (current step (3)) may be quicker.
        """
        ### delete the current item on the key, if existent;
        ### this is done because by deleting it we ensure
        ### the value (or nested values within it) are all
        ### properly removed from the flat values list
        ### before assigning the new value(s) to the list
        ### in a further step;

        try:
            del self[key]
        except KeyError:
            pass

        ### use the builtin dict.__setitem__ method
        super().__setitem__(key, value)

        ### finally store the new value(s) on the
        ### flat values list depending on whether it
        ### is a mapping or not

        ## store the new value in the flat_values list
        ## if it is not a mapping

        if not isinstance(value, Mapping):
            self._bound_append(value)

        ## otherwise store its nested values instead

        else:
            nested_values = flatten_mapping_values(value)
            self._bound_extend(nested_values)

    def __delitem__(self, key):
        """Delete self[key].

        It also removes the corresponding value(s) from
        the flat_values list. Also raises KeyError if key
        doesn't exist.

        key (any python hashable object)
            object used as dictionary key.

        Extends __delitem__ method.

        ### Alternative implementation

        You could also just delete the item and call the
        "update" method without arguments, since it has
        the side-effect of clearing and repopulating the
        flat_values dict. See "Alternative implementation"
        section on the __setitem__ method docstring.
        """
        ### retrieve the value from the key; this also has
        ### the desired side effect of raising a KeyError
        ### if the key doesn't exist
        value = self[key]

        ### use the builtin dict.__delitem__ method
        super().__delitem__(key)

        ### then finally remove the value(s) from the
        ### removed item from the flat values list
        ### depending on whether it is a mapping or not

        ## if it is not a mapping, remove the value from
        ## the list

        if not isinstance(value, Mapping):
            self._bound_remove(value)

        ## if it is a mapping, though, remove all its
        ## nested values from the list

        else:

            ## get generator with all nested values
            nested_values = flatten_mapping_values(value)

            ## remove one by one from the flat_values list
            for nested_value in nested_values:
                self._bound_remove(nested_value)

    def update(self, *args, **kwargs):
        """Update items on the dictionary.

        Items on the flat_values list are updated
        accordingly.

        Parameters:

        *args, **kwargs (positional and keyword variable
        parameters to be used by the dict.update method)

        Extends dict.update.
        """
        ### execute the builtin dict.update method with
        ### the received arguments; parameters used
        ### ensure that the signature works exactly like
        ### dict.update, raising errors when errors need
        ### to be raised;
        super().update(*args, **kwargs)

        ### then clear and refill the flat values list
        ### with the current nested values

        ## clear
        self._bound_clear()

        ## retrieve nested values generator
        updated_nested_values = flatten_mapping_values(self)

        ## update list using it (this is list.extend bound
        ## method, but aliased)
        self._bound_extend(updated_nested_values)

    def pop(self, *args):
        """Remove specified key, return corresponding value.

        Receives one or two arguments.

        If one it must be a key:

            i) If key exists, remove key/value item and
            return value (value is also removed from the
            flat values list);
            ii) If key doesn't exist raises KeyError;

        If there are two arguments, one is the key and the
        other is a default value:

            iii) If key exists, same as (i);
            iv) If key doesn't exist, the default value is
            returned;

        Extends dict.pop.
        """
        ### retrieve key from first argument
        key = args[0]

        ### store boolean indicating whether the key
        ### exists in the dictionary
        key_exists = key in self

        ### execute the builtin dict.pop method with
        ### the received arguments; the parameters used
        ### ensure that the signature works exactly like
        ### dict.pop, raising errors when errors need to
        ### be raised;
        value = super().pop(*args)

        ### if the key exists, remove corresponding
        ### value(s) depending on whether the value is
        ### a mapping or not

        if key_exists:

            ## remove the value from the flat_values
            ## list if it is not a mapping
            if not isinstance(value, Mapping):
                self._bound_remove(value)

            ## or remove all its nested values from the
            ## list if the value is a mapping

            else:

                # get generator with all nested values
                nested_values = flatten_mapping_values(value)

                # remove one by one from the flat_values
                # list
                for nested_value in nested_values:
                    self._bound_remove(nested_value)

        ### finally return the value
        return value

    def popitem(self):
        """Remove and return (key, value) pair.

        Raises KeyError if dict is empty. If not empty it
        also removes corresponding value(s) from the
        flat_values list accordingly.

        Extends dict.popitem.
        """
        ### execute the builtin dict.popitem method
        popped_item = super().popitem()

        ### remove value(s)

        ## retrieve value
        value = popped_item[1]

        ## remove the value(s) from the flat_values list
        ## depending on whether the value from the
        ## popped item is a mapping or not

        # if value is not a mapping, just remove it

        if not isinstance(value, Mapping):
            self._bound_remove(value)

        ## if otherwise it is a mapping, retrieve the
        ## nested values and remove one by one

        else:

            # get generator with all nested values
            nested_values = flatten_mapping_values(value)

            # remove one by one from the flat_values
            # list
            for nested_value in nested_values:
                self._bound_remove(nested_value)

        ### finally return the popped item
        return popped_item

    def clear(self):
        """Remove all items from dict and flat values list.

        Extends dict.clear.
        """
        ### execute the builtin dict.clear method
        super().clear()

        ### clear the flat values list
        self._bound_clear()

    def setdefault(self, *args):
        """Return value associated with given key.

        If the key doesn't exist, set the default value
        in the key and return the value. The flat_values
        list is updated accordingly. The default value
        mentioned is defined as explained below.

        The method receives one or two arguments:

        If one it must be a key:

            i) If key exists, return corresponding value;
            ii) If key doesn't exist, assign None as the
            value for the key and it

        If there are two arguments, one is the key and the
        other is a default value.

            iii) If key exists, same as (i);
            iv) If key doesn't exist, the default value is
                assigned to the key and returned

        Extends dict.setdefault.
        """
        ### retrieve key from first argument
        key = args[0]

        ### store boolean indicating whether the key
        ### exists in the dictionary
        key_exists = key in self

        ### execute the builtin dict.setdefault method with
        ### the received arguments; the parameters used
        ### ensure that the signature works exactly like
        ### dict.setdefault, raising errors when errors
        ### need to be raised;
        value = super().setdefault(*args)

        ### if the key doesn't exist, since the default
        ### value will be added, add the value(s) to the
        ### flat_values too, depending on whether the
        ### default value is a mapping or not

        if not key_exists:

            ## store the value in the flat value list
            ## if it is not a mapping

            if not isinstance(value, Mapping):
                self._bound_append(value)

            ## otherwise store all nested values if the
            ## value is a mapping

            else:

                nested_values = flatten_mapping_values(value)
                self._bound_extend(nested_values)

        ### finally return the value
        return value

    @classmethod
    def fromkeys(cls, *args):
        """Return a new instance of this class.

        Has two positional-only parameters, the second
        being optional.

        If one argument is received, it must be an
        iterable, and its items are used as keys in a
        new instance of this class and the default value
        is assign to all the keys. The default value is
        None.

        If two arguments are received, the second must
        be the default value to assign to all the keys
        from the iterable in the new instance of this class.

        In either case the new instance of this class is
        then returned.

        Extends dict.fromkeys.
        """
        ### execute the builtin dict.fromkeys method with
        ### the received arguments; the parameters used
        ### ensure that the signature works exactly like
        ### dict.fromkeys, raising errors when errors
        ### need to be raised;
        new_dict = super().fromkeys(*args)

        ### now use the new dict to build an instance of
        ### this class and then return it
        new_flat_list_dict = cls(new_dict)

        return new_flat_list_dict

    ### custom copy operations

    def __copy__(self):
        """Return a regular copy of this flat list dict."""
        ### retrieve class object
        cls = self.__class__

        ### instantiate a new object from this one
        ### and return it

        new_copy = cls(self)
        return new_copy

    def copy(self):
        """Return a regular copy of this flat list dict.

        Overrides dict.copy.
        """
        return self.__copy__()

    def __deepcopy__(self, memo):
        """Return a deep copy of this flat list dict.

        Works by simply creating a dictionary from this
        instance, making a deep copy of such dictionary
        and creating another instance of this class from
        the deep copy of the dictionary.

        This method is executed automatically by the
        copy.deepcopy function.

        memo (dict)
            provided automatically by the copy.deepcopy
            function. Used by copy.deepcopy to keep track
            of objects which were already deepcopied, thus
            avoiding deepcopying the same object more than
            once. It isn't used in this method, since
            there's no circular references between the
            instance components, but it is kept in order to
            comply with the python official documentation
            for the "copy" module.
        """
        ### create a normal dict out of this instance
        dict_obj = dict(self)

        ### get a deep copy of that dict
        dict_deep_copy = deepcopy(dict_obj)

        ### then finally turn it into an instance of this
        ### class and return it

        ## retrieve class object
        cls = self.__class__

        ## use the class object and the dict deep copy to
        ## instantiate a new flat list dict
        new_flat_list_dict = cls(dict_deep_copy)

        ## finally return it
        return new_flat_list_dict
