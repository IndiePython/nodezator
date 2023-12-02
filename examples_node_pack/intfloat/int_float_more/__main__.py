"""Facility for int float entry widget advanced tests."""


### function definition

def int_float_more(

    ### param 01

    int_from_0_to_100 : {
      "widget_name"  : "int_float_entry",
      "widget_kwargs": {
        "min_value": 0,
        "max_value": 100
      },
      "type": int
    } = 0,

    ### param 02

    int_float_none_def_int : {
      "widget_name": "int_float_entry",
      "type": (int, float, type(None))
    } = 0

    ):
    """Return the arguments given.

    Just a simple node to test advanced options for
    usage of the int float entry widget.

    Parameters:

      - int_from_0_to_100 (int)
        this int float entry only accepts ints from 0 to 100.

      - int_float_none_def_int (int, float or None)
        this int float accepts int, float or None, but the
        default value isn't None.
    """
    return (
      int_from_0_to_100,
      int_float_none_def_int
    )

### the callable used must also be aliased as 'main'
main_callable = int_float_more
