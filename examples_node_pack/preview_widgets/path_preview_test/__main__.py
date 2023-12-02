"""Facility for path preview demonstration."""



def path_preview_test(

      ### path parameter

      path : {
        "widget_name": "path_preview",
        "type": str
      } = '.'

    ):
    """Return received path."""
    return path

### callable used must always be aliased to 'main'
main_callable = path_preview_test
