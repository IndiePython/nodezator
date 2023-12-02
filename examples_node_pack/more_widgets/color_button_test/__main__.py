"""Facility for demonstrating color button widget."""

def color_button_test(

      color: {
        "widget_name" : "color_button",
        "type": tuple
      } = (255, 0, 0)
    
    ):
    """Return received color.

    The color button attached to the "color" parameter
    makes it easy to select any desired color.
    """
    return color

### functions used must always be aliased as 'main'
main_callable = color_button_test
