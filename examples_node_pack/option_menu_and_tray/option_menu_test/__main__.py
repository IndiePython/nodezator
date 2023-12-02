"""Facility for option menu widget testing."""

from itertools import combinations


def option_menu_test(

    costant_name: {
      'widget_name' : 'option_menu',
      'widget_kwargs': {
        'options' : ['e', 'inf', 'nan', 'pi']
      },
      'type': str
    } = 'pi',
    
    chosen_combination: {
      'widget_name' : 'option_menu',
      'widget_kwargs': {
        'options': [''.join(tup) for tup in combinations('abcdefgh', 5)]
      },
      'type': str
    } = 'abcde'

    ):
    """Return math constant specified by name."""
    from math import pi, e, inf, nan

    constant_value = {
      "e"   : e,
      "inf" : inf,
      "nan" : nan,
      "pi"  : pi
    }[constant_name]

    return constant_value, chosen_combination

main_callable = option_menu_test
