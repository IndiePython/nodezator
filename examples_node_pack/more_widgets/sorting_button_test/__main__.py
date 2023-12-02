"""Demonstrating the sorting button widget.

Item can be used to provide sorted collections of a set
of available items.
"""

def sorting_button_test(
      sorted_tuple : {
        'widget_name': 'sorting_button',
        'widget_kwargs': {
          'available_items': {
            'red',
            'green',
            'blue',
          },
        },
        'type': tuple
      } = ('blue', 'red')
    ):
    return sorted_tuple

main_callable = sorting_button_test
