"""Facility for image preview demosntration."""

def image_preview_test(

      image_path: {
        "widget_name" : "image_preview",
        "type": str
      } = '.'
    
    ):
    """Return received image path.

    The image preview attached to the "image" parameter
    makes it easy to select any desired image.
    """
    return image_path

### the callable used must always be aliased as "main"
main_callable = image_preview_test
