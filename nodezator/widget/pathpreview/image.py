"""Facility for widget to preview images from paths."""

### standard library imports

from pathlib import Path

from xml.etree.ElementTree import Element


### local imports

from ...config import APP_REFS

from ...ourstdlibs.path import get_new_filename

from ...imagesman.cache import (
    ORIGINAL_IMAGE_SURFS_MAP,
    IMAGE_SURFS_DB,
    update_cache_for_image,
)

from ...imagesman.viewer.main import view_images

from ...surfsman.icon import render_layered_icon

from ...colorsman.colors import (
    BLACK,
    WHITE,
    PATHPREVIEW_BG,
    THUMB_BG,
)

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


class ImagePreview(_BasePreview):

    height = 175 + 20

    button_callable_names = SP_BUTTON_CALLABLE_NAMES
    button_rects = SP_BUTTON_RECTS

    button_surfs = list(SP_BUTTON_SURFS)

    button_surfs[1] = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (38, 40, 41, 39)],
        dimension_name="height",
        dimension_value=18,
        colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
        background_width=BUTTON_WIDTH,
        background_height=BUTTON_HEIGHT,
    )
    ###

    ###

    button_svg_reprs = list(SP_BUTTON_SVG_REPRS)
    button_svg_reprs[1] = [
        (
            (
                " m2 1"
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
            (" m2 1" " m0 15" " q0 3 3 3" " l8 0" " q0 -11 -11 -11" " Z"),
            "fill:white;stroke:black;stroke-width:2;",
        ),
        (
            (" m14 19" " l3 0" " q3 0 3 -3" " l0 -4" " q-6 0 -6 7" " Z"),
            "fill:white;stroke:black;stroke-width:2;",
        ),
        (
            (" m14 3" " q3 0 3 3" " q0 3 -3 3" " q-3 0 -3 -3" " q0 -3 3 -3" " Z"),
            "fill:white;stroke:black;stroke-width:2;",
        ),
    ]

    def preview_paths(self):
        """Preview image(s) from path(s)."""
        view_images(self.value)

    def update_previews(self):
        """"""
        image_paths = (self.value,) if isinstance(self.value, str) else self.value

        for image_path in image_paths:
            update_cache_for_image(image_path)

        self.update_image()

    def blit_path_representation(self):
        """Blit representation of image in current path."""

        rect = (
            1,
            BUTTON_HEIGHT + 2,
            self.width - 2,
            self.height - ((BUTTON_HEIGHT * 2) + 2),
        )

        thumb_x, thumb_y, thumb_width, thumb_height = rect

        ###

        ### TODO 'use_alpha' should probably be defined
        ### programatically based on the extension and
        ### the presence of alpha or not; ponder; ponder
        ### specially about the check about the presence
        ### of alpha, since it may take too long to
        ### define so in real time;

        thumb_surf = IMAGE_SURFS_DB[self.current_path][
            {
                "use_alpha": True,
                "max_width": thumb_width,
                "max_height": thumb_height,
                "keep_size_ratio": True,
                "checkered_alpha": True,
                "background_width": thumb_width,
                "background_height": thumb_height,
                "background_color": THUMB_BG,
                "retrieve_pos_from": "center",
                "assign_pos_to": "center",
                "offset_pos_by": (0, 0),
                "not_found_width": thumb_width,
                "not_found_height": thumb_height,
            }
        ]

        self.image.blit(thumb_surf, (thumb_x, thumb_y))

        ###
        super().blit_path_representation()

    def svg_path_repr(self):
        """Return svg representation of path preview."""

        g = Element("g")

        ### preview bg

        rect = self.rect.move(1, BUTTON_HEIGHT + 2)

        rect.size = (self.width - 2, self.height - ((BUTTON_HEIGHT * 2) + 2))

        ###
        current_path = self.current_path

        if current_path not in ORIGINAL_IMAGE_SURFS_MAP:

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
                        "class": "thumb_bg",
                    },
                ),
            )

            ###
            x, y = rect.topleft

            for path_directives, style in [
                (
                    (
                        " m14 14"
                        " m0 21"
                        " q0 -21 21 -21"
                        " l84 0"
                        " q21 0 21 21"
                        " l0 84"
                        " q0 21 -21 21"
                        " l-84 0"
                        " q-21 0 -21 -21"
                        " l0 -84"
                        " Z"
                    ),
                    "fill:rgb(30, 130, 70);stroke:black;stroke-width:4;",
                ),
                (
                    (
                        " m14 14"
                        " m0 105"
                        " q0 21 21 21"
                        " l56 0"
                        " q0 -77 -77 -77"
                        " Z"
                    ),
                    "fill:white;stroke:black;stroke-width:4;",
                ),
                (
                    (
                        " m98 140"
                        " l21 0"
                        " q21 0 21 -21"
                        " l0 -28"
                        " q-42 0 -42 49"
                        " Z"
                    ),
                    "fill:white;stroke:black;stroke-width:4;",
                ),
                (
                    (
                        " m98 28"
                        " q21 0 21 21"
                        " q0 21 -21 21"
                        " q-21 0 -21 -21"
                        " q0 -21 21 -21"
                        " Z"
                    ),
                    "fill:white;stroke:black;stroke-width:4;",
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

                thumb_surf = IMAGE_SURFS_DB[current_path][
                    {
                        "use_alpha": True,
                        "max_width": thumb_width,
                        "max_height": thumb_height,
                        "keep_size_ratio": True,
                        "checkered_alpha": True,
                        "background_width": thumb_width,
                        "background_height": thumb_height,
                        "background_color": THUMB_BG,
                        "retrieve_pos_from": "center",
                        "assign_pos_to": "center",
                        "offset_pos_by": (0, 0),
                        "not_found_width": thumb_width,
                        "not_found_height": thumb_height,
                    }
                ]

                preview_surf_map[current_path] = thumb_surf

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
