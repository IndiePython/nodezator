### standard library import
from os import linesep


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ..classes2d.single import Object2D

from ..surfsman.render import render_rect

from ..surfsman.draw import draw_border

from ..textman.render import render_text, get_text_size

from ..textman.text import (
    get_normal_lines,
    get_highlighted_lines,
)

from ..syntaxman.exception import SyntaxMappingError

from ..syntaxman.utils import get_ready_theme

from .constants import (
    GENERAL_CODE_TEXT_SETTINGS,
    PRE_TEXT_SETTINGS,
    PRE_TEXT_BORDER,
)

###

THEME_MAP = get_ready_theme(
    "python",
    GENERAL_CODE_TEXT_SETTINGS,
)

DIGIT_WIDTH, _ = get_text_size(
    "0",
    font_height=(GENERAL_CODE_TEXT_SETTINGS["font_height"]),
    font_path=GENERAL_CODE_TEXT_SETTINGS["font_path"],
)

### TODO ponder: should the code block surfaces be cached
### accross different .htsl pages? they probably should.


def get_python_codeblock(python_code_element):

    ### TODO include <python> tag attributes:
    ###
    ### 1) hidelineno: to hide line numbers
    ### 2) includefirst: to include first line,
    ###    which is otherwise stripped by default;

    text = python_code_element.childNodes[0].data

    ### by default, first line is stripped
    text = linesep.join(text.splitlines()[1:])

    ###

    try:

        lines = get_highlighted_lines(
            "python", text, syntax_settings_map=(THEME_MAP["text_settings"])
        )

    ## if a syntax mapping error occurs...
    except SyntaxMappingError:

        background_color = GENERAL_CODE_TEXT_SETTINGS["background_color"]

        lines = get_normal_lines(
            text,
            GENERAL_CODE_TEXT_SETTINGS,
        )

        lineno_settings = GENERAL_CODE_TEXT_SETTINGS

    else:

        background_color = THEME_MAP["background_color"]

        ##

        text_settings = THEME_MAP["text_settings"]

        try:
            lineno_settings = text_settings["line_number"]

        except KeyError:
            lineno_settings = text_settings["normal"]

    ### position text objects representing lines one
    ### below the other

    lines.rect.snap_rects_ip(retrieve_pos_from="bottomleft", assign_pos_to="topleft")

    ### lineno

    first_lineno = int(python_code_element.getAttribute("linenofrom") or "1")

    ## calculate the number of digits needed to
    ## display the number of the last line
    max_chars = len(str((first_lineno - 1) + len(lines)))

    ## width of panel is total width occupied
    ## by max_chars plus 2 additional characters
    ## used as padding
    lineno_width = (max_chars + 2) * DIGIT_WIDTH

    ### areas

    code_area = lines.rect.copy()
    code_area.width += 15
    code_area.height += 10

    lineno_area = lines.rect.copy()
    lineno_area.width = lineno_width
    lineno_area.height += 10

    code_area.topleft = lineno_area.topright

    total_area = lineno_area.union(code_area)

    surf = render_rect(*total_area.size)

    for bg_color, area in (
        (
            lineno_settings["background_color"],
            lineno_area,
        ),
        (
            background_color,
            code_area,
        ),
    ):

        draw_rect(surf, bg_color, area)

    ###

    lines.rect.topleft = lineno_area.topright
    lines.rect.move_ip(5, 5)

    for lineno, line in enumerate(lines, first_lineno):

        surf.blit(line.image, line.rect)

        lineno_surf = render_text(
            str(lineno).rjust(max_chars, "0"),
            **lineno_settings,
        )

        surf.blit(lineno_surf, (DIGIT_WIDTH, line.rect.top))

    ###

    return Object2D.from_surface(surf)

def get_pre_textblock(pre_element):

    text = pre_element.childNodes[0].data

    ### by default, first line is stripped
    text = linesep.join(text.splitlines()[1:])

    ###
    background_color = PRE_TEXT_SETTINGS["background_color"]

    lines = get_normal_lines(
        text,
        PRE_TEXT_SETTINGS,
    )

    lineno_settings = PRE_TEXT_SETTINGS

    ### position text objects representing lines one
    ### below the other
    lines.rect.snap_rects_ip(retrieve_pos_from="bottomleft", assign_pos_to="topleft")

    ### lineno

    use_lineno = pre_element.getAttribute("use_lineno") or "false"

    if use_lineno != "false":

        first_lineno = int(pre_element.getAttribute("linenofrom") or "1")

        ## calculate the number of digits needed to
        ## display the number of the last line
        max_chars = len(str((first_lineno - 1) + len(lines)))

        ## width of panel is total width occupied
        ## by max_chars plus 2 additional characters
        ## used as padding
        lineno_width = (max_chars + 2) * DIGIT_WIDTH

        ### areas

        text_area = lines.rect.copy()
        text_area.width += 15
        text_area.height += 10

        lineno_area = lines.rect.copy()
        lineno_area.width = lineno_width
        lineno_area.height += 10

        text_area.topleft = lineno_area.topright

        total_area = lineno_area.union(text_area)

        surf = render_rect(*total_area.size)

        for bg_color, area in (
            (
                lineno_settings["background_color"],
                lineno_area,
            ),
            (
                background_color,
                text_area,
            ),
        ):

            draw_rect(surf, bg_color, area)

        ###

        lines.rect.topleft = lineno_area.topright
        lines.rect.move_ip(5, 5)

        for lineno, line in enumerate(lines, first_lineno):

            surf.blit(line.image, line.rect)

            lineno_surf = render_text(
                str(lineno).rjust(max_chars, "0"),
                **lineno_settings,
            )

            surf.blit(lineno_surf, (DIGIT_WIDTH, line.rect.top))

    ###
    else:

        ### text area

        text_area = lines.rect.copy()
        text_area.width += 15
        text_area.height += 10

        surf = render_rect(*text_area.size)

        draw_rect(surf, background_color, text_area)

        ###

        lines.rect.move_ip(5, 5)

        for line in lines:
            surf.blit(line.image, line.rect)


    draw_border(surf, PRE_TEXT_BORDER)
    ###
    return Object2D.from_surface(surf)
