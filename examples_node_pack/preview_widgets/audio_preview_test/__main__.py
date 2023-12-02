"""Facility for audio preview demonstration."""

def audio_preview_test(

      audio_path: {
        "widget_name" : "audio_preview",
        "type": str
      } = '.'
    
    ):
    """Return received audio path.

    The audio preview attached to the "audio_path" parameter
    makes it easy to select any desired audio file.
    """
    return audio_path

### the callable used must always be aliased as "main"
main_callable = audio_preview_test
