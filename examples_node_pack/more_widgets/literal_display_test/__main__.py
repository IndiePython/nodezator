"""Demonstration of the literal display widget.

The literal display widget does the same as the literal
entry. It is just that it has more space to see the value.
"""

def literal_display_test(
      python_literal: {
        'widget_name': 'literal_display'
      } = ('this', 'is', 'a', 'tuple', 'of', 'values')
    ):
    return python_literal

main_callable = literal_display_test
