"""Facility for widget to preview audio from paths."""

### local imports

from ...audioplayer import play_audio

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import BLACK, WHITE

from .base import _BasePreview

from .constants import (
    BUTTON_SURFS,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_SVG_REPRS,
)


class AudioPreview(_BasePreview):

    ###

    button_surfs = list(BUTTON_SURFS)
    button_surfs[1] = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 42, 43, 39)],
        dimension_name="height",
        dimension_value=18,
        colors=[
            BLACK,
            BLACK,
            WHITE,
            (30, 130, 70),
        ],
        background_width=BUTTON_WIDTH,
        background_height=BUTTON_HEIGHT,
    )

    ###

    button_svg_reprs = list(BUTTON_SVG_REPRS)
    button_svg_reprs[1] = [
        (
            (
                "m2 1"
                " m0 3"
                " q0 -3 3 -3"
                " l12 0"
                " q3 0 3 3"
                " l0 12"
                " q0 3 -3 3"
                " l-12 0"
                " q-3 0 -3 -3"
                " l0 -12"
                " Z"
            ),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;",
        ),
        (
            (
                "m2 1"
                "m7 16"
                "q-3 0 -3 -3"
                "q0 -3 3 -3"
                "l0 -7"
                "l4 0"
                "l4 4"
                "l-4 0"
                "l0 6"
                "q0 3 -3 3"
                " Z"
            ),
            ("fill:white;" "stroke-linejoin:round;" "stroke:black;" "stroke-width:2;"),
        ),
    ]

    def preview_paths(self):
        """Trigger audio playing from audio in path(s)."""
        play_audio(self.value, index=self.path_index)
