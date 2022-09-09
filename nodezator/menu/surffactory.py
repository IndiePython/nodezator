"""Facility wherein to create surfaces for menu elements."""

### local imports

from ..surfsman.draw import (
    draw_depth_finish,
    blit_aligned,
)

from ..surfsman.icon import render_layered_icon

from ..surfsman.render import (
    render_rect,
    render_separator,
)

from ..textman.render import (
    render_text,
    get_text_size,
)

from ..colorsman.colors import (
    MENU_BG,
    MENU_HOVERED_BG,
    BLACK,
    WHITE,
)

from .common import (
    ## kwargs
    FONT_SIZE_KWARGS,
    NORMAL_LABEL_KWARGS,
    HOVERED_LABEL_KWARGS,
    ## arrow surfs
    RIGHT_ARROW_SURF,
    HOVERED_RIGHT_ARROW_SURF,
)

from .iconfactory import ICON_MAP


ICON_WIDTH = FONT_SIZE_KWARGS["font_height"] + (FONT_SIZE_KWARGS["padding"] * 2)

INCREMENT_MAP = {
    "children": RIGHT_ARROW_SURF.get_width(),
    "icon": ICON_WIDTH,
    "widget": ICON_WIDTH,
}


(
    UNMARKED_CHECKBUTTON,
    MARKED_CHECKBUTTON,
    UNMARKED_RADIOBUTTON,
    MARKED_RADIOBUTTON,
) = (
    render_layered_icon(
        chars=[chr(ordinal) for ordinal in ordinals],
        dimension_name="height",
        dimension_value=ICON_WIDTH - 6,
        colors=colors,
        background_width=ICON_WIDTH,
        background_height=ICON_WIDTH,
    )
    for ordinals, colors in (
        ((169, 171), (BLACK, WHITE)),
        ((169, 170, 171), (BLACK, BLACK, WHITE)),
        ((174, 176), (BLACK, WHITE)),
        ((174, 175, 176), (BLACK, BLACK, WHITE)),
    )
)


def create_top_surfaces(menu_list):
    """"""
    surf_data_list = []

    ###

    for item in menu_list:

        label = item["label"]

        ##

        surf_map = {}
        surf_data_list.append(surf_map)

        ##

        if set(label) == {"-"}:
            continue

        ##

        surf_map["normal"] = render_text(text=label, **NORMAL_LABEL_KWARGS)

        surf_map["highlighted"] = render_text(text=label, **HOVERED_LABEL_KWARGS)

    return surf_data_list


def create_equal_surfaces(menu_list):
    """"""
    surf_data_list = create_top_surfaces(menu_list)

    width = get_max_width(menu_list)

    height = FONT_SIZE_KWARGS["font_height"] + (FONT_SIZE_KWARGS["padding"] * 2)

    normal_bg_color = NORMAL_LABEL_KWARGS["background_color"]

    highlighted_bg_color = HOVERED_LABEL_KWARGS["background_color"]

    ##

    if any(set(item["label"]) == {"-"} for item in menu_list):

        separator_surf = render_separator(
            length=width,
            is_horizontal=True,
            padding=5,
            thickness=8,
            background_color=MENU_BG,
        )

    ##
    x_label_offset = 0

    for key in ("widget", "icon"):

        if any(key in item for item in menu_list):
            x_label_offset += INCREMENT_MAP[key]

    ##

    x_key_offset = (
        -INCREMENT_MAP["children"]
        if any("children" in item for item in menu_list)
        else 0
    )

    #####

    for item_data, surf_map in zip(menu_list, surf_data_list):

        ###

        if set(item_data["label"]) == {"-"}:

            surf_map["normal"] = surf_map["highlighted"] = separator_surf

            continue

        ###

        ### blit label

        ## normal

        normal_surf = render_rect(width, height, normal_bg_color)

        blit_aligned(
            target_surface=normal_surf,
            surface_to_blit=surf_map["normal"],
            retrieve_pos_from="midleft",
            assign_pos_to="midleft",
            offset_pos_by=(x_label_offset, 0),
        )

        surf_map["normal"] = normal_surf

        ## highlighted

        highlighted_surf = render_rect(
            width,
            height,
            highlighted_bg_color,
        )

        blit_aligned(
            target_surface=highlighted_surf,
            surface_to_blit=surf_map["highlighted"],
            retrieve_pos_from="midleft",
            assign_pos_to="midleft",
            offset_pos_by=(x_label_offset, 0),
        )

        surf_map["highlighted"] = highlighted_surf

        ### blit key text if present

        try:
            key_text = item_data["key_text"]

        except KeyError:
            pass

        else:

            normal_key_surf = render_text(text=key_text, **NORMAL_LABEL_KWARGS)

            highlighted_key_surf = render_text(text=key_text, **HOVERED_LABEL_KWARGS)

            for surf, key_surf in (
                (normal_surf, normal_key_surf),
                (highlighted_surf, highlighted_key_surf),
            ):

                blit_aligned(
                    target_surface=surf,
                    surface_to_blit=key_surf,
                    retrieve_pos_from="midright",
                    assign_pos_to="midright",
                    offset_pos_by=(x_key_offset, 0),
                )

        ##
        if "children" in item_data:

            for label_surf, arrow_surf in (
                (normal_surf, RIGHT_ARROW_SURF),
                (
                    highlighted_surf,
                    HOVERED_RIGHT_ARROW_SURF,
                ),
            ):

                blit_aligned(
                    target_surface=label_surf,
                    surface_to_blit=arrow_surf,
                    retrieve_pos_from="midright",
                    assign_pos_to="midright",
                )

        ##
        has_widget = "widget" in item_data

        if "icon" in item_data:

            x_icon_offset = ICON_WIDTH if has_widget else 0
            icon = ICON_MAP[item_data["icon"]]

            ##

            for surf in (normal_surf, highlighted_surf):

                blit_aligned(
                    target_surface=surf,
                    surface_to_blit=icon,
                    retrieve_pos_from="midleft",
                    assign_pos_to="midleft",
                    offset_pos_by=(x_icon_offset, 0),
                )

        if has_widget:

            ## TODO
            ## treat widgets here; will create two versions of
            ## surface map, one for unmarked widget and other
            ## for marked one, them clear surf_map and add
            ## the surf maps to it in the 'unmarked' and
            ## 'marked' keys;

            widget_surfs = (
                (UNMARKED_CHECKBUTTON, MARKED_CHECKBUTTON)
                if item_data["widget"] == "checkbutton"
                else (UNMARKED_RADIOBUTTON, MARKED_RADIOBUTTON)
            )

            surf_map.clear()
            surf_map[False] = {}
            surf_map[True] = {}

            for is_marked, key, surf in (
                (False, "normal", normal_surf),
                (True, "normal", normal_surf),
                (False, "highlighted", highlighted_surf),
                (True, "highlighted", highlighted_surf),
            ):

                new_surf = surf.copy()

                blit_aligned(
                    target_surface=new_surf,
                    surface_to_blit=widget_surfs[is_marked],
                    retrieve_pos_from="midleft",
                    assign_pos_to="midleft",
                )

                surf_map[is_marked][key] = new_surf

    return surf_data_list


def get_max_width(items):

    widths = []

    for item in items:

        label = item["label"]

        if set(label) == {"-"}:
            continue

        ##
        width = get_text_size(
            text=label,
            **FONT_SIZE_KWARGS,
        )[0]

        ##
        widths.append(width)

    ###
    max_width = max(widths)

    ###
    if any("key_text" in item for item in items):

        max_width += (
            max(
                get_text_size(
                    text=item["key_text"],
                    **FONT_SIZE_KWARGS,
                )[0]
                for item in items
                if "key_text" in item
            )
            + 30
        )  # padding before key text

    ###

    for key in ("children", "widget", "icon"):

        if any(key in item for item in items):
            max_width += INCREMENT_MAP[key]

    ###
    return max_width
