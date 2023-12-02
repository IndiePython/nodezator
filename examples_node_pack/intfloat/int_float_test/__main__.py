"""Facility for int float entry testing."""


def int_float_test(

    ### int float entry accepts only integers
    int_default_int : int = 0,

    ### int float entry accepts only integers and None
    int_default_none : int = None,

    ### int float entry accepts only floats
    float_default_float : float = 0.0,

    ### int float entry accepts only floats and None
    float_default_None : float = None,

    ### int float entries accepts ints and floats (only
    ### the default value is different.

    int_float_default_int   : (int, float) = 0, 
    int_float_default_float : (int, float) = 0.0,

    ### int float entries accepts ints, floats and None
    int_float_default_none  : (int, float) = None,

    ### reversing the order of the classes in the tuple
    ### also works, though it makes no difference (this
    ### exists so that the user don't bother remembering
    ### the order)
    float_int_default_int   : (float, int) = 0

    ):
    """Return received values."""
    return (
      int_default_int,
      int_default_none,
      float_default_float,
      float_default_None,
      int_float_default_int,
      int_float_default_float,
      int_float_default_none,
      float_int_default_int
    )

### callable used must always be aliased to 'main'
main_callable = int_float_test
