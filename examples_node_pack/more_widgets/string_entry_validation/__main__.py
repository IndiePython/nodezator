"""Demonstrating string entry widget with validation.

That is, the user will only be able to leave a value in
the entry if the validation command allows it.

The validation command option can be any callable that,
given the a string, returns True if it is valid and False
otherwise. It can also be the name of any string method
starting with 'is...'.

Below we use 'isidentifier', which means  the
str.isidentifier() method is used to validate the
content of the string entry. Now the user can only leave
a value in the string for which str.isidentifier()
returns True. For instance, identifiers in Python cannot
have spaces or start with a digit character, so if you
type such values in the entry and press <Enter> the
entry will not allow it and will instead revert to the
previous value.
"""


def string_entry_validation(

      string_with_validation : {

        'widget_name': 'string_entry',
        'widget_kwargs': {
          'validation_command': 'isidentifier'
        },
        'type': str

      } = 'string'

    ):
    return string_with_validation

main_callable = string_entry_validation
