"""Facility for font preview demonstration."""

def font_preview_test(

      font_path: {
        "widget_name" : "font_preview",
        "type": str
      } = '.'
    
    ):
    """Return received font path.

    The font preview attached to the "font_path" parameter
    makes it easy to select any desired font.
    """
    return font_path

### the callable used must always be aliased as "main"
main_callable = font_preview_test
