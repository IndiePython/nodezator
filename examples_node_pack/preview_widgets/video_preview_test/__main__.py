"""Facility for video preview demonstration."""

def video_preview_test(

      video_path: {
        "widget_name" : "video_preview",
        "type": str
      } = '.'
    
    ):
    """Return received video path.

    The video preview attached to the "video_path"
    parameter makes it easy to select any desired video
    file.
    """
    return video_path

### the callable used must always be aliased as "main"
main_callable = video_preview_test
