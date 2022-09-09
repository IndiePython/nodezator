"""Facility for text-related utilities.

By text we mean strings with multiple line separators.
"""
### third-party imports
from pygame import Rect, Surface


### local imports

from ..classes2d.single import Object2D
from ..classes2d.collections import List2D

from ..surfsman.cache import EMPTY_SURF

from .render import render_text

from ..syntaxman.utils import SYNTAX_TO_MAPPING_FUNCTION


### functions


def get_normal_lines(text, text_settings):
    """Return list of text objs as lines of text.

    By 'normal' we mean text which is not rendered with
    syntax highlighting.

    Parameters
    ==========
    text (string)
        text to be turned into objects for blitting.
    text_settings (dict)
        keyword arguments for rendering text.
    """
    ### retrieve list of lines
    text_lines = text.splitlines() or [""]

    ### get height of text surfaces from text settings
    height = text_settings["font_height"]

    ### create and return special list of text objects
    ### representing lines

    return List2D(
        ## a text object is either an empty line or
        ## a text object rendered with the text settings
        (
            Object2D.from_surface(render_text(text=line_string, **text_settings))
            if line_string
            else Object2D(image=EMPTY_SURF, rect=Rect(0, 0, 0, height))
        )
        ## iterate over each line of text
        for line_string in text_lines
    )


def get_highlighted_lines(syntax_name, text, syntax_settings_map):
    """Return list of text objs as lines of python source.

    Parameters
    ==========
    syntax_name (string)
        represents name of syntax used to map the received
        text; we use it to retrieve the suitable mapping
        function to map the syntax of the text.
    text (string)
        Text to be mapped, generating mapped syntax data
        used to highlighted text objects.
    syntax_settings_map (dict)
        maps strings to dicts; the strings indicate the
        kind of highlighted data (including 'normal' for
        text which isn't highlighted at all); the dicts
        are keyword arguments for each kind of highlighted
        data.
    """
    ### retrieve syntax mapping function
    syntax_mapping_func = SYNTAX_TO_MAPPING_FUNCTION[syntax_name]

    ### get mapped syntax
    mapped_syntax_data = syntax_mapping_func(text)

    ### retrieve list of lines
    text_lines = text.splitlines() or [""]

    ### get height of text surfaces from text settings
    height = syntax_settings_map["normal"]["font_height"]

    ### create and return special list of text objects
    ### representing lines

    return List2D(
        ## a text object is either an empty line or
        ## a text object rendered with the text settings
        (
            render_highlighted_line(
                line_text=line_string,
                mapped_syntax_data=mapped_syntax_data[line_index],
                syntax_settings_map=syntax_settings_map,
                join_objects=True,
            )
            if line_string
            else Object2D(image=EMPTY_SURF, rect=Rect(0, 0, 0, height))
        )
        ## iterate over each line index and line content
        for line_index, line_string in enumerate(text_lines)
    )


def render_highlighted_line(
    line_text, mapped_syntax_data, syntax_settings_map, join_objects=False
):
    """Return highlighted text object(s) from the line.

    Parameters
    ==========
    line_text (string)
        text to be turned into syntax highlighted text
        objects.
    mapped_syntax_data (dict)
        maps 2-tuples to strings; the 2-tuples represent
        intervals of highlighted text in the line text;
        the strings indicate the kind of highlighted data
        (comments, keywords, etc.)
    syntax_settings_map (dict)
        maps strings to dicts; the strings indicate the kind
        of highlighted data (including 'normal' for text
        which isn't highlighted at all); the dicts are
        keyword arguments for rendering each kind of
        highlighted data.
    join_objects (boolean)
        whether to join text objects into a single one
        or not.
    """
    string_kwargs_pairs = (
        ### grab a pair containing the slice of the line text
        ### and the text settings corresponding to the kind
        ### of highlight to be applied
        (line_text[including_start:excluding_end], syntax_settings_map[kind])
        ### from each interval/kind pair in
        ### mapped_syntax_data sorted by the interval,
        ###
        ### the interval is further decomposed into its
        ### first and second elements, including_start and
        ### excluding_end, respectively
        for (including_start, excluding_end), kind in sorted(
            mapped_syntax_data.items(), key=lambda item: item[0]
        )
    )

    ### create a special list containing text objects
    ### instantiated from each item in the pairs
    ### from the string_kwargs_pairs iterator

    text_objs = List2D(
        Object2D.from_surface(
            surface=render_text(
                text=string,
                ### text settings
                **text_settings
            )
        )
        for string, text_settings in string_kwargs_pairs
    )

    ### align objects in the list one beside the other
    ### from left to right
    text_objs.rect.snap_rects_ip()

    ### return text objects (or single one) depending on
    ### quantity of text objects and special argument

    ## if there's more than one text object...

    if len(text_objs) > 1:

        ### if requested, join objects into a single one
        ### and return the object

        if join_objects:

            image = Surface(text_objs.rect.size).convert()

            image.fill(syntax_settings_map["normal"]["background_color"])

            text_objs.draw_on_surf(image)

            rect = image.get_rect()

            return Object2D(image=image, rect=rect)

        else:
            return text_objs

    ### otherwise we assume there's only a single
    ### text object, so we return it
    else:
        return text_objs.pop()
