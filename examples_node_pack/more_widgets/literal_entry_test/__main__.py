"""Literal entry demonstration.

Can be used to provide any Python literal.
You want.
"""

def literal_entry_test(
      python_literal: {
        'widget_name': 'literal_entry',
        # note that we don't need to provide the
        # 'type' key here, since this widget can
        # edit a vast number of types (as long as
        # the value is a python literal
      } = None
    ):
    return python_literal

main_callable = literal_entry_test
