"""Facility for text input fixture."""

def get_text(

    text: {
      'widget_name' : 'text_display',
      'type' : str
    } = \
    """
    I'd like to make myself believe
    the Planet Earth turns slowly

    It's hard to say that I'd rather stay away when I'm
    asleep, cause everything is never as it seems.
    """
    
    ) -> str:
    """Return received string.

    The text button attached to the "text" parameter
    makes it easy to view/edit the text.
    """
    return text

### functions used must always be aliased as 'main'
main_callable = get_text
