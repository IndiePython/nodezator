"""Facility for text block surface creation."""

### third-party import
from pygame import Surface


### local imports

from ...surfsman.draw import draw_border

from ...syntaxman.utils import get_ready_theme

from ...textman.text import get_highlighted_lines

from ...colorsman.colors import TEXT_BLOCK_OUTLINE

from .constants import FONT_HEIGHT, FONT_PATH, PADDING, OUTLINE_THICKNESS


GENERAL_TEXT_KWARGS = {
    "font_height": FONT_HEIGHT,
    "font_path": FONT_PATH,
}

COMMENT_THEME_MAP = get_ready_theme("comment", GENERAL_TEXT_KWARGS)

TEXT_BLOCK_BG = COMMENT_THEME_MAP["background_color"]


def get_text_block_surf(text):
    """Create surface for text block from given text.

    The surface is created by rendering the lines of text
    one by one, then blitting them all into a single surface,
    one below the other.

    Parameters
    ==========

    text (string)
        text for the text block.

    Syntax-related error handling
    ===============================

    At the very beginning of the function's body we
    create the text objects representing the comment.
    Such text may have special highlighting according
    to whether special contents are present in the comment.

    In some cases, an operation to render highlighted
    text like the one in this function is guarded by
    try/exception clauses to prevent from errors when
    mapping the syntax.

    We don't do so here, because comments don't have wrong
    syntax. They either have special syntax ("todo" words)
    or no syntax at all. Thus, the probability of syntax
    related errors resulting from the contents of the
    comment doesn't exist.
    """
    ### create the text objects representing the lines
    ### (check "Syntax-related error handling" on the
    ### docstring of this function to know why we don't
    ### use a try/except clause here)

    text_objs = get_highlighted_lines(
        "comment", text, syntax_settings_map=(COMMENT_THEME_MAP["text_settings"])
    )

    ### position text objects representing lines
    ### one below the other

    text_objs.rect.snap_rects_ip(
        retrieve_pos_from="bottomleft", assign_pos_to="topleft"
    )

    ## calculate extra space in the surface for padding
    ## and border (outline);
    ##
    ## note that the measures should apply for both
    ## horizontal edges and both vertical edges, reason
    ## why we multiply the measures by 2 before summing
    ## them up

    padding_both_edges = PADDING * 2
    outline_both_edges = OUTLINE_THICKNESS * 2

    extra_space = padding_both_edges + outline_both_edges

    ## get final size

    size = (
        ## from the special list of text objects
        text_objs
        ## get a rect (a special rect which represents the
        ## union of the rects of all text objects in the list)
        .rect
        ## and produce a copy which is inflated in both
        ## dimensions by the value of extra_space
        .inflate(extra_space, extra_space)
        ## and finally get its size
        .size
    )

    ## create, fill and outline the surface

    surf = Surface(size).convert()

    surf.fill(TEXT_BLOCK_BG)

    draw_border(surf, color=TEXT_BLOCK_OUTLINE, thickness=OUTLINE_THICKNESS)

    ### finally blit text objects into surface and return
    ### the surface

    ## offset text_objs to take padding and outline into
    ## account

    offset = PADDING + OUTLINE_THICKNESS
    text_objs.rect.move_ip(offset, offset)

    ## draw and return

    text_objs.draw_on_surf(surf)
    return surf
