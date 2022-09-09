"""Facility for rectsman package doctests' fixtures."""

### standard library import
from re import findall

### third-party import
from pygame import Rect

### local imports
from ..main import RectsManager, rect_property


### constant
HEX_PATTERN = "0x[0-9A-Fa-f]+"


### class definitions


class ListGroup(list):
    """Group to hold multiple objects.

    It is helped by the RectsManager class and the related
    rect_property function.
    """

    def __init__(self, *args):
        """Initialize superclass and store RectsManager."""

        ### initialize superclass
        super().__init__(*args)

        ### instantiate and store the RectsManager
        self._rects_man = RectsManager(self.get_all_rects)

    ### inject the property in the "rect" attribute
    rect = rect_property

    def get_all_rects(self):
        """Return 'rect' attribute of all objects."""
        for obj in self:
            yield obj.rect


class Simple:
    """Object holding a rect."""

    def __init__(self, rect):
        """Store received rect."""
        self.rect = rect


### functions


def get_fresh_groups():
    """Return two groups ready for testing."""
    ### instantiate groups
    g1, g2 = ListGroup(), ListGroup()

    ### populate and return them

    g1.extend(
        (
            Simple(Rect(0, 0, 20, 20)),
            Simple(Rect(10, 10, 20, 20)),
            Simple(Rect(10, -10, 20, 20)),
            Simple(Rect(20, 20, 20, 20)),
        )
    )

    g2.extend(
        (
            Simple(Rect(100, 0, 20, 20)),
            Simple(Rect(110, 10, 20, 20)),
            Simple(Rect(90, 20, 20, 20)),
            Simple(Rect(130, 0, 20, 20)),
        )
    )

    return g1, g2


def check_error_raising(obj_a, obj_b, method_names, arguments):
    """Return whether errors raised were the same.

    Parameters
    ==========

    obj_a, obj_b (any Python object)
        objects whose errors type and message will be
        tested for equality.
    method_names (iterable)
        collection of names of methods to test on the rect
        attribute of the objects.
    arguments (iterable)
        collection of arguments to be used in the listed
        methods, one per call.
    """
    accumulator = []

    ### iterate over methods and arguments given

    for method_name in method_names:
        for arg in arguments:

            ### retrieve type and message for error
            ### in obj_a

            type_a, msg_a = get_error_type_and_message(obj_a, method_name, arg)

            ### retrieve type and message for error
            ### in obj_a

            type_b, msg_b = get_error_type_and_message(obj_b, method_name, arg)

            ### compare the types and messages and
            ### append the result in the accumulator

            are_equal = (type_a, msg_a) == (type_b, msg_b)
            accumulator.append(are_equal)

    ### return whether all values on the accumulator are
    ### positive
    return all(accumulator)


def get_error_type_and_message(obj, method_name, arg):
    """Return (type, message) of raised error.

    obj (any Python obj)
        obj from which to retrieve method.
    method_name (string)
        name of method to be tested.
    arg (any Python obj)
        argument to be tested on the method.
    """
    method = getattr(obj, method_name)

    try:
        method(arg)

    except Exception as err:

        error_type = type(err)
        error_msg = remove_hex(str(err))

    else:
        raise RuntimeError("Errors should have been raised, but weren't")

    return (error_type, error_msg)


def remove_hex(string):
    """Remove any hex number from string.

    This is used to remove hex numbers from the string.
    Those usually represent the address of an object in
    memory and when present make it difficult to compare
    error messages from two different objects.
    """
    hex_addresses = findall(HEX_PATTERN, string)

    for address in hex_addresses:
        string = string.replace(address, "")

    return string
