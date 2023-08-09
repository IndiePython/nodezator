"""Facility for monospaced text visualization."""



### main callable

def view_as_monotext(

    obj_or_text,
    max_preview_lines: 'natural_number' = 10,
    placeholder_text: str = "---",

) -> [

    {'name': 'obj_or_text'},
    {'name': 'preview_text', 'type': dict, 'viz': 'side'},
    {'name': 'full_text', 'type': dict, 'viz': 'loop'},

]:
    """Return dict with data representing full view and preview as text.

    Parameters
    ==========
    obj_or_text
        Any object. It will be turned into a string with str() and this
        string will be used as the text for full view/preview.
    max_preview_lines
        Maximum number of lines to use for preview. If 0, all lines are used.
    placeholder_text
        Fallback text to use if 'str(obj_or_text)' returns an empty string.
    """
    ### cast given obj as text or use placeholder
    text = str(obj_or_text) or placeholder_text

    ### ensure max_preview_lines is >= 0

    if max_preview_lines < 0:
        raise ValueError("'max_preview_lines' must be >= 0")

    ### obtain lines from text
    lines = text.splitlines()

    ### use the full text as the preview text if any of the
    ### conditions below applies...

    if (

        ## if a maximum number of lines for the preview was not
        ## specified, that is, it is 0
        not max_preview_lines

        ## if the maximum number of allowed lines in the preview
        ## is >= the number of lines
        or max_preview_lines >= len(lines)

    ):
        preview_text = text


    ### otherwise, use only a portion of the full text as the preview

    else:
        preview_text = '\n'.join(lines[:max_preview_lines])


    ### finally return the data

    return {
        'obj_or_text': obj_or_text,
        'preview_text': {'hint': 'monospaced_text', 'data': preview_text},
        'full_text': {'hint': 'monospaced_text', 'data': text},
    }
