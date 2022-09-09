"""Facility for widget to preview fonts from paths."""

### standard library imports

from pathlib import Path

from string import (
    ascii_uppercase,
    ascii_lowercase,
    digits,
    punctuation,
)

from xml.etree.ElementTree import Element


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ...config import APP_REFS

from ...ourstdlibs.path import get_new_filename

from ...fontsman.preview.cache import (
    FONT_PREVIEWS_DB,
    update_cache_for_font_preview,
)

from ...fontsman.viewer.main import view_fonts

from ...surfsman.cache import NOT_FOUND_SURF_MAP

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    BLACK,
    WHITE,
    PATHPREVIEW_BG,
)

from .base import _BasePreview

from .constants import (
    SP_BUTTON_SURFS,
    SP_BUTTON_RECTS,
    SP_BUTTON_CALLABLE_NAMES,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    SP_BUTTON_SVG_REPRS,
    get_missing_path_repr,
)

### constant

PREVIEW_CHARS = (
    digits
    + "".join(
        sorted(ascii_uppercase + ascii_lowercase, key=str.lower)[
            : 2 * 9
        ]  # only first 9 pairs
    )
    + punctuation
)


### class definition


class FontPreview(_BasePreview):

    height = 150 + 20

    button_callable_names = SP_BUTTON_CALLABLE_NAMES
    button_rects = SP_BUTTON_RECTS

    button_surfs = list(SP_BUTTON_SURFS)

    button_surfs[1] = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 46, 47, 39)],
        dimension_name="height",
        dimension_value=18,
        colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
        background_width=BUTTON_WIDTH,
        background_height=BUTTON_HEIGHT,
    )

    ###

    button_svg_reprs = list(SP_BUTTON_SVG_REPRS)
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
                "m7 16"
                "q-2 0 -2 -2"
                "l4 -9"
                "q 2 -2 4 0"
                "l4 9"
                "q0 2 -2 2"
                "l-1 0"
                "q-2 0 -2 -2"
                "q-1 -2 -3 0"
                "q0 2 -2 2"
                " Z"
            ),
            ("fill:white;" "stroke:black;" "stroke-width:2;"),
        ),
    ]

    def preview_paths(self):
        """Preview font(s) from path(s)."""
        try:
            view_fonts(self.value)
        except FileNotFoundError:
            print("Font file wasn't found.")

    def update_previews(self):
        """"""
        font_paths = (self.value,) if isinstance(self.value, str) else self.value

        for font_path in font_paths:
            update_cache_for_font_preview(font_path)

        self.update_image()

    def blit_path_representation(self):
        """Blit representation of video in current path."""
        image = self.image

        rect = (
            1,
            BUTTON_HEIGHT + 2,
            self.width - 2,
            self.height - ((BUTTON_HEIGHT * 2) + 2),
        )

        draw_rect(image, PATHPREVIEW_BG, rect)

        ###

        if self.current_path == ".":

            preview_surf = NOT_FOUND_SURF_MAP[(rect[2], rect[3])]

        ###

        else:

            preview_surf = FONT_PREVIEWS_DB[self.current_path][
                {
                    "font_size": 20,
                    "chars": PREVIEW_CHARS,
                    "width": rect[2],
                    "height": rect[3],
                    "not_found_width": rect[2],
                    "not_found_height": rect[3],
                }
            ]

        image.blit(preview_surf, rect)

        super().blit_path_representation()

    def svg_path_repr(self):
        """Blit representation of image in current path."""
        g = Element("g")

        ###

        rect = self.rect.move(1, BUTTON_HEIGHT + 2)

        rect.size = (self.width - 2, self.height - ((BUTTON_HEIGHT * 2) + 2))

        ###
        current_path = self.current_path

        ###

        if not Path(current_path).exists() or Path(current_path).is_dir():

            g.append(get_missing_path_repr(rect))
            g.append(super().svg_path_repr())
            return g

        try:

            (
                preview_surf_map,
                preview_name_map,
                parent_dirname,
            ) = APP_REFS.preview_handling_kit

        except AttributeError:

            g.append(
                Element(
                    "rect",
                    {
                        **{
                            attr_name: str(getattr(rect, attr_name))
                            for attr_name in ("x", "y", "width", "height")
                        },
                        **{"class": "thumb_bg"},
                    },
                ),
            )

            ###

            x, y = rect.topleft

            for path_directives, style in [
                (
                    (
                        "m14 10"
                        " m0 18"
                        " q0 -18 21 -18"
                        " l84 0"
                        " q21 0 21 18"
                        " l0 72"
                        " q0 18 -21 18"
                        " l-84 0"
                        " q-21 0 -21 -18"
                        " l0 -72"
                        " Z"
                    ),
                    "fill:rgb(30, 130, 70);stroke:black;stroke-width:4;",
                ),
                (
                    (
                        "m49 100"
                        "q-14 0 -14 -12"
                        "l28 -54"
                        "q 14 -12 28 0"
                        "l28 54"
                        "q0 12 -14 12"
                        "l-7 0"
                        "q-14 0 -14 -12"
                        "q-7 -12 -21 0"
                        "q0 12 -14 12"
                        " Z"
                    ),
                    ("fill:white;" "stroke:black;" "stroke-width:4;"),
                ),
            ]:

                g.append(
                    Element(
                        "path",
                        {
                            "d": f"M{x} {y}" + path_directives,
                            "style": style,
                        },
                    )
                )

        else:

            thumb_width, thumb_height = rect.size

            if current_path not in preview_surf_map:

                ### create thumb

                preview_surf = FONT_PREVIEWS_DB[self.current_path][
                    {
                        "font_size": 20,
                        "chars": PREVIEW_CHARS,
                        "width": rect[2],
                        "height": rect[3],
                        "not_found_width": rect[2],
                        "not_found_height": rect[3],
                    }
                ]

                ###

                preview_surf_map[current_path] = preview_surf

            name = Path(current_path).with_suffix(".png").name

            if name in preview_name_map.values():

                for key, value in preview_name_map.items():

                    if value == name and key != current_path:

                        ## change value of name variable
                        ## so the name is different

                        name = get_new_filename(name, preview_name_map.values())

                        break

            if current_path not in preview_name_map:
                preview_name_map[current_path] = name

            href = str(Path(parent_dirname) / name)

            g.append(
                Element(
                    "image",
                    {
                        "href": href,
                        "xlink:href": href,
                        **{
                            attr_name: str(getattr(rect, attr_name))
                            for attr_name in ("x", "y", "width", "height")
                        },
                    },
                )
            )

        ###
        g.append(super().svg_path_repr())

        ###
        return g
