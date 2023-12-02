"""Text display with Python syntax highlighting."""

def text_display_python(

    text: {
      'widget_name' : 'text_display',
      'widget_kwargs': {
        'font_path': 'mono_bold',
        'syntax_highlighting': 'python'
      },
      'type': str
    } = \
"""
def hello_world(param1:str) -> str:
    '''Docstring'''
    print(param1)
    a = 3 + 3
    print(a)
    return 100
"""
    
    ) -> str:
    """Return received string.

    The text button attached to the "text" parameter
    makes it easy to view/edit the text.
    """
    return text

### functions used must always be aliased as 'main'
main_callable = text_display_python
