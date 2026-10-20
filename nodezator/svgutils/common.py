"""Common SVG-related utilities."""

### standard library imports

from collections.abc import Iterable

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element



def format_color(color):
    """Return color in format usable by 'fill' attribute of SVG shapes."""

    if isinstance(color, str):
        return color

    elif isinstance(color, Iterable):

        _r, _g, _b, *_ = color
        return f'rgb({_r}, {_g}, {_b})'

    elif color is None:
        return 'none'

    else:

        raise TypeError(
            "'color' must be None, string or iterable of integers with 3+ values"
        )


def yield_transformed_svgs(svg_text, id_string, transform_data):

    doc = parseString(svg_text)
    svg = doc.firstChild

    ###

    for element in doc.getElementsByTagName('*'):

        if element.hasAttribute('id'):
            element.setIdAttribute('id')

    ###
    element = doc.getElementById(id_string)

    for transform_name, *deltas in transform_data:

        _change_transform(element, transform_name, *deltas)
        yield svg.toxml()


def _change_transform(element, transform_name, value_string):

    if not value_string:
        raise ValueError("'value_string' must not be empty")

    ### if a transform attribute already exists, either:
    ###
    ### - replace the value of the specific transform function
    ###   if there's one already
    ### - add it to the existing transforms already present

    if element.hasAttribute('transform'):

        transform = element.getAttribute('transform')

        ### replace value if tranform function already present

        if transform_name in transform:

            new_transform = (

                _substitute_old_value(
                    transform_name,
                    transform,
                    value_string,
                )

            )

        ### otherwise add it

        else:

            ## build call
            transform_call_text = f'{transform_name}({value_string})'

            ## add this call to existing ones (if any) or use it
            ## as-is if there aren't others

            new_transform = (

                f'{transform} {transform_call_text}'
                if transform

                else transform_call_text

            )

    ### if otherwise a transform attribute does not exist,
    ### use call to the transform using the given value to
    ### use as the transform text
    else:
        new_transform = f'{transform_name}({value_string})'


    ### finally set the new transform text built in the attribute
    element.setAttribute('transform', new_transform)


def _substitute_old_value(
    transform_name,
    transform_text,
    value_string,
):
    """Return transform text with value replaced by given value string.

    Uses string indexing and slicing to build the new string with the value
    replaced.
    """

    ## index of transform name
    t_index = transform_text.index(transform_name)

    ## index of open parenthesis
    op_index = transform_text.index('(', t_index)

    ## index of close parenthesis
    cp_index = transform_text.index(')', op_index)

    ## return text with content between parentheses replaced

    return (

        ## everything before opening parenthesis + the open parenthesis
        ## itself
        transform_text[:op_index+1]

        ## the new value
        + value_string

        ## the close parenthesis and everything after it
        + transform_text[cp_index:]

    )


def get_mask_from_rect(rect, mask_id):
    """Return 2-tuple with mask tree and text to use to point to mask.

    Parameters
    ==========
    rect (pygame.Rect)
        Rect defining the boundaries of the mask.

    mask_id (str)
        id assigned to mask.
    """

    defs_el = Element("defs")
    mask_el = Element("mask", {"id": mask_id})

    rect_el = (
        Element(
            "rect",
            {
                "fill": "white",
                **{
                    attr_name: str(getattr(rect, attr_name))
                    for attr_name in ("x", "y", "width", "height")
                },
            },
        )
    )

    defs_el.append(mask_el)
    mask_el.append(rect_el)

    return (defs_el, f"url(#{mask_id})")

