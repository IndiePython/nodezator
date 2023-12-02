"""Default holder demonstration.

If you just put a default value in a parameter, a default
holder widget will be used. This widget doesn't have the
ability to edit the value and serves only to display
the default value of the parameter.
"""


# function with three parameters, all with default values
# but they don't define widgets, so the values appear
# in the node as default holder widgets, which is just
# greyed out text in the default app theme

def default_holder_test(
      a_string = 'a string',
      an_integer = 100,
      none_value = None,
    ):

    return (
      a_string,
      an_integer,
      none_value,
    )

main_callable = default_holder_test
