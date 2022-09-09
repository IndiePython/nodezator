"""Facility for character info rendering."""

### local imports

from ...classes2d.single import Object2D

from ..constants import FIRA_MONO_BOLD_FONT_HEIGHT, FIRA_MONO_BOLD_FONT_PATH

from ...textman.render import render_text

from ...surfsman.render import combine_surfaces

from ...colorsman.colors import BLACK, WHITE


SIZE_FORMATTER = "{}x{}".format


def render_char_info(char, font):

    char_surf = font.render(char, True, BLACK, WHITE)

    surfs = [
        render_text(
            text=text,
            font_height=FIRA_MONO_BOLD_FONT_HEIGHT,
            font_path=FIRA_MONO_BOLD_FONT_PATH,
            foreground_color=BLACK,
            background_color=WHITE,
        )
        for text in (str(ord(char)), hex(ord(char)), SIZE_FORMATTER(*font.size(char)))
    ]

    surfs.insert(1, char_surf)

    return combine_surfaces(
        surfs,
        retrieve_pos_from="midbottom",
        assign_pos_to="midtop",
        offset_pos_by=(0, 5),
        padding=2,
        background_color=WHITE,
    )
