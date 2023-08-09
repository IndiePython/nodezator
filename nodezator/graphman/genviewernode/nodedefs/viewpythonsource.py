"""Facility for python source visualization."""


### main callable

def view_python_source(

    python_source: 'python_source' = '"""Python source"""',
    max_preview_lines: 'natural_number' = 10,
    placeholder_source: str = "# empty source",

) -> [

    {'name': 'python_source', 'type': str},
    {'name': 'source_preview_data', 'type': dict, 'viz': 'side'},
    {'name': 'full_source_data', 'type': dict, 'viz': 'loop'},

]:
    """Return dict with data representing full view and preview from source.

    Parameters
    ==========
    python_source
        Python source text for full view/preview.
    max_preview_lines
        Maximum number of lines to use for preview. If 0, all lines
        are used.
    placeholder_source
        Fallback text to use if 'python_source' is an empty string.
        If 'placeholder_source' itself is empty, we use '# empty source'
        instead.
    """
    ### ensure 'text' is a string

    if type(python_source) != str:
        raise TypeError("'python_source' argument must be a string.")

    ### if an empty python_source is received, set source_full_text to
    ### 'placeholder_source' (unless it is empty as well)

    if not python_source:

        source_full_text = (
            placeholder_source
            if placeholder_source
            else '# empty source'
        )

        ### if we end up using the placeholder, and it is not the default,
        ### ensure it is a string as well

        if (
            placeholder_source != '# empty source'
            and not isinstance(placeholder_source, str)
        ):
            raise TypeError("'placeholder_source' argument must be a string.")

    ### otherwise set python_source as source_full_text
    else:
        source_full_text = python_source

    ### ensure max_preview_lines is >= 0

    if max_preview_lines < 0:
        raise ValueError("'max_preview_lines' must be >= 0")


    ### obtain lines from source
    lines = source_full_text.splitlines()

    ### use the full source as the source preview text if any of the
    ### conditions below applies...

    if (

        ## if a maximum number of lines for the preview was not
        ## specified, that is, it is 0
        not max_preview_lines

        ## if the maximum number of allowed lines in the preview
        ## is >= the number of lines
        or max_preview_lines >= len(lines)

    ):
        source_preview_text = source_full_text


    ### otherwise, use only a portion of the full source as the preview

    else:
        source_preview_text = '\n'.join(lines[:max_preview_lines])


    ### finally return the source data

    return {

        'python_source': python_source,

        'source_preview_data': {
            'hint': 'python_source', 'data': source_preview_text
        },

        'full_source_data': {
            'hint': 'python_source', 'data': source_full_text
        },

    }
