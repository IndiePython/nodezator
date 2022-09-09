"""Special metaprogramming related functions."""


def has_own_init(class_):
    """Return True if class defines its own __init__ method.

    ### parameters

    class_ (python custom class)
        it is verified if this class defines its own
        __init__ method

    ### discussion

    All classes have constructors which are either:
        1) defined by themselves (regardless if it overrides
           completely or just extends the superclass
           __init__);
        2) defined by the superclass;

    This function returns True in the first scenario.

    ### docstests

    >>> class Obj: pass
    >>> has_own_init(Obj)
    False
    >>> class OtherObj:
    ...     def __init__(self): pass
    ...
    >>> has_own_init(OtherObj)
    True
    >>> has_own_init(object)
    True
    """
    class_init = class_.__init__

    ### try retrieving the superclass
    try:
        superclass = class_.__bases__[0]

    ### considering the class has an init but it doesn't
    ### have a superclass, then we assume the init is its
    ### own;
    except IndexError:
        return True

    ### if you succeed, retrieve its constructor
    else:
        superclass_init = superclass.__init__

    ### return the inequality comparison of the inits
    return class_init != superclass_init


def initialize_bases(obj):
    """Initialize base classes with own __init__ method.

    ### parameters

    obj (custom class instance)
        an instance whose class inherits from other classes
        which may have or not their own constructors.

    ### discussion

    Iterates over the bases classes of obj, initializing
    those which have their own constructor method (__init__).

    It is meant to be used inside the __init__ method of
    a class which inherits from other classes which you'll
    want to initialize (execute the __init__ method) if
    they have their own __init__ method.

    ### doctests

    >>> class A:
    ...     def __init__(self):
    ...         self.name = "a name"
    >>> class B:
    ...     def __init__(self):
    ...         self.age = 23
    >>> class C: pass
    >>> class D(A, B, C):
    ...     def __init__(self):
    ...         initialize_bases(self)
    >>> obj = D()
    >>> obj.name, obj.age
    ('a name', 23)
    """
    ### iterate over base classes (superclasses)

    for class_ in obj.__class__.__bases__:

        ## if the class has its own __init__ method,
        ## execute it passing the obj instance to it

        if has_own_init(class_):
            class_.__init__(obj)
