"""Facility for widget to preview videos from paths."""

### standard library imports

from pathlib import Path

from xml.etree.ElementTree import Element


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ...config import APP_REFS, FFMPEG_AVAILABLE

from ...dialog import create_and_show_dialog

from ...ourstdlibs.path import get_new_filename

from ...videopreview.previewer import preview_videos

from ...videopreview.cache import (
    VIDEO_METADATA_MAP,
    VIDEO_DATA_DB,
    update_video_metadata_and_previews,
)

from ...surfsman.draw import blit_aligned

from ...surfsman.icon import render_layered_icon

from ...textman.render import render_multiline_text

from ...colorsman.colors import BLACK, PATHPREVIEW_BG

from .base import _BasePreview

from .constants import (
    SP_BUTTON_SURFS,
    SP_BUTTON_RECTS,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    SP_BUTTON_SVG_REPRS,
    SP_BUTTON_CALLABLE_NAMES,
    get_missing_path_repr,
)

NO_FFMPEG_TEXT = """
MUST INSTALL
FFMPEG TO HAVE
ACCESS TO VIDEO
PREVIEWS
""".strip()


class VideoPreview(_BasePreview):

    height = BUTTON_HEIGHT + 154 + 20

    button_callable_names = SP_BUTTON_CALLABLE_NAMES
    button_rects = SP_BUTTON_RECTS

    button_surfs = list(SP_BUTTON_SURFS)
    button_surfs[1] = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (44, 45)],
        dimension_name="height",
        dimension_value=18,
        colors=[BLACK, (30, 130, 70)],
        background_width=BUTTON_WIDTH,
        background_height=BUTTON_HEIGHT,
    )

    ###

    button_svg_reprs = list(SP_BUTTON_SVG_REPRS)
    button_svg_reprs[1] = [
        (
            ("m1 4" "q0 -3 3 -3" "q3 0 3 3" "q0 3 -3 3" "q-3 0 -3 -3" " Z"),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;",
        ),
        (
            ("m9 4" "q0 -3 3 -3" "q3 0 3 3" "q0 3 -3 3" "q-3 0 -3 -3" " Z"),
            "fill:rgb(30, 130, 70);stroke:black;stroke-width:2;",
        ),
        (
            (
                "m2 7"
                "l13 0"
                "l0 5"
                "l5 -4"
                "l0 8"
                "l-5 -4"
                "l0 5"
                "l-4 0"
                "l0  2"
                "l-5 0"
                "l0 -2"
                "l-4 0"
                " Z"
            ),
            ("fill:rgb(30, 130, 70);" "stroke:black;" "stroke-width:2;"),
        ),
    ]

    def preview_paths(self):
        """Preview video(s) from path(s)."""
        if FFMPEG_AVAILABLE:
            preview_videos(self.value, index=self.path_index)

        else:
            create_and_show_dialog(
                "Can't preview videos without FFMPEG",
                level_name="info",
            )

    def update_previews(self):

        if not FFMPEG_AVAILABLE:

            create_and_show_dialog(
                (
                    "Can't preview videos without FFMPEG,"
                    " so the reload preview button doesn't"
                    " work either."
                ),
                level_name="info",
            )

            return

        video_paths = (self.value,) if isinstance(self.value, str) else self.value

        for video_path in video_paths:
            update_video_metadata_and_previews(video_path)

        self.update_image()

    def blit_path_representation(self):
        """Blit representation of video in current path."""
        rect = (
            1,
            BUTTON_HEIGHT + 2,
            self.width - 2,
            self.height - ((BUTTON_HEIGHT * 2) + 2),
        )

        ###
        try:
            subsurf = self.path_repr_subsurf

        except AttributeError:

            subsurf = self.path_repr_subsurf = self.image.subsurface(rect)

        subsurf.fill(PATHPREVIEW_BG)

        ###

        if FFMPEG_AVAILABLE:

            preview_surf = VIDEO_DATA_DB[self.current_path][
                {
                    "max_width": 153,
                    "max_height": 153,
                    "not_found_width": 153,
                    "not_found_height": 153,
                }
            ][0]

        else:

            preview_surf = render_multiline_text(
                text=NO_FFMPEG_TEXT,
                retrieve_pos_from="bottomleft",
                assign_pos_to="topleft",
            )

        blit_aligned(
            preview_surf,
            target_surface=subsurf,
            retrieve_pos_from="center",
            assign_pos_to="center",
        )

        super().blit_path_representation()

    def svg_path_repr(self):
        """Blit representation of image in current path."""
        g = Element("g")

        ###

        rect = self.rect.move(1, BUTTON_HEIGHT + 2)

        rect.size = (self.width - 2, self.height - ((BUTTON_HEIGHT * 2) + 2))

        current_path = self.current_path

        if current_path not in VIDEO_METADATA_MAP:

            g.append(get_missing_path_repr(rect))
            g.append(super().svg_path_repr())
            return g

        ###

        try:

            (
                preview_surf_map,
                preview_name_map,
                parent_dirname,
            ) = APP_REFS.preview_handling_kit

        except AttributeError:

            ##
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
                        "m7 32"
                        "q0 -24 24 -24"
                        "q24 0 24 24"
                        "q0 24 -24 24"
                        "q-24 0 -24 -24"
                        " Z"
                    ),
                    "fill:rgb(30, 130, 70);stroke:black;stroke-width:4;",
                ),
                (
                    (
                        "m61 32"
                        "q0 -24 24 -24"
                        "q24 0 24 24"
                        "q0 24 -24 24"
                        "q-24 0 -24 -24"
                        " Z"
                    ),
                    "fill:rgb(30, 130, 70);stroke:black;stroke-width:4;",
                ),
                (
                    (
                        "m14 55"
                        "l91 0"
                        "l0 35"
                        "l35 -28"
                        "l0 56"
                        "l-35 -28"
                        "l0 35"
                        "l-28 0"
                        "l0  14"
                        "l-35 0"
                        "l0 -14"
                        "l-28 0"
                        " Z"
                    ),
                    ("fill:rgb(30, 130, 70);" "stroke:black;" "stroke-width:4;"),
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

                ###
                preview_surf_map[current_path] = self.path_repr_subsurf

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
