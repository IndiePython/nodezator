"""Facility for text preview demonstration."""

def text_preview_test(

      text_path: {
        "widget_name" : "text_preview",
        "type": str
      } = '.'
    
    ):
    """Return received text path.

    The text preview attached to the "text_path" parameter
    makes it easy to select any desired text file.
    """
    return text_path

### the callable used must always be aliased as "main"
main_callable = text_preview_test
