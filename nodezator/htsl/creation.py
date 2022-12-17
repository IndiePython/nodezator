"""Facility for definition of HTSL classes."""

### standard library imports

from xml.dom.minidom import (
    getDOMImplementation,
    parseString as dom_from_string,
)


### third-party imports

from pygame import Rect

from pygame.draw import line as draw_line


### local imports

from ..classes2d.single import Object2D

from ..classes2d.collections import List2D

from ..textman.render import render_text

from ..textman.cache import CachedTextObject

from ..rectsman.main import RectsManager

from ..surfsman.render import render_rect, unite_surfaces

from ..colorsman.colors import (
    HTSL_CANVAS_BG,
    HTSL_MARKED_TEXT_BG,
    HTTP_ANCHOR_TEXT_FG,
    HTSL_ANCHOR_TEXT_FG,
)

from .constants import (
    ANCHOR_TEXT_SETTINGS_MINUS_FG,
    HEADING_TEXT_SETTINGS_MINUS_HEIGHT,
    HEADING_TO_FONT_HEIGHT,
    HEADING_TAGS,
    TAG_TO_TEXT_SETTINGS,
    NORMAL_TEXT_SETTINGS,
    MARKED_TEXT_SETTINGS,
)

### class definitions


class Anchor(Object2D):
    def __init__(self, surface, href):

        self.image = surface
        self.rect = surface.get_rect()

        self.href = href

    @classmethod
    def from_text(cls, text, href):

        return cls(
            render_text(
                text,
                foreground_color=(
                    HTTP_ANCHOR_TEXT_FG
                    if href.lower().startswith("http")
                    else HTSL_ANCHOR_TEXT_FG
                ),
                **ANCHOR_TEXT_SETTINGS_MINUS_FG,
            ),
            href,
        )


def get_heading(heading, max_width):

    obj_list = List2D()

    words = heading.childNodes[0].data.split()

    tag_name = heading.tagName.lower()

    text_settings = {
        "font_height": HEADING_TO_FONT_HEIGHT[tag_name],
        **HEADING_TEXT_SETTINGS_MINUS_HEIGHT,
    }

    obj_list.extend(
        Object2D.from_surface(
            surface=(
                render_text(
                    word,
                    **text_settings,
                )
            )
        )
        for word in words
    )

    obj_list.rect.snap_rects_intermittently_ip(
        dimension_name="width",
        dimension_unit="pixels",
        max_dimension_value=max_width,
        offset_pos_by=(5, 0),
    )

    heading_obj = Object2D.from_surface(
        unite_surfaces(
            [
                (
                    obj.image,
                    obj.rect,
                )
                for obj in obj_list
            ],
            background_color=(HTSL_CANVAS_BG),
        )
    )

    obj_list.clear()

    ###

    if heading.getAttribute("id"):
        heading_obj.id = heading.getAttribute("id")

    ###

    return heading_obj


class TextBlock(List2D):
    """Represents text blocks."""

    def __init__(self, text_block, max_width):

        super().__init__()

        ELEMENT_NODE = text_block.ELEMENT_NODE
        TEXT_NODE = text_block.TEXT_NODE

        substrings_data = []

        for child in text_block.childNodes:

            node_type = child.nodeType

            if node_type == TEXT_NODE:

                substrings_data.append({"text": child.data})

            elif node_type == ELEMENT_NODE:

                substrings_data.append(
                    {
                        "text": child.childNodes[0].data,
                        "href": child.getAttribute("href"),
                        "tag_name": child.tagName.lower(),
                    }
                )

        append_to_text = self.append

        anchor_groups = []
        marked_groups = []
        strikethrough_groups = []
        underline_groups = []

        for data in substrings_data:

            words = data["text"].split()

            href = data.get("href")
            tag_name = data.get("tag_name")

            if href:

                anchor_group = []

                append_to_anchor_group = anchor_group.append

                for word in words:

                    anchor = Anchor.from_text(
                        word,
                        data["href"],
                    )

                    append_to_text(anchor)
                    append_to_anchor_group(anchor)

                anchor_groups.append(anchor_group)

            elif tag_name == "mark":

                marked_group = []
                append_to_marked_group = marked_group.append

                for word in words:

                    marked_word = Object2D.from_surface(
                        render_text(
                            word,
                            **MARKED_TEXT_SETTINGS,
                        )
                    )

                    append_to_text(marked_word)
                    append_to_marked_group(marked_word)

                marked_groups.append(marked_group)

            elif tag_name in ("s", "del", "u", "ins"):

                linecut_group_list = (
                    strikethrough_groups
                    if tag_name in ("s", "del")
                    else underline_groups
                )

                linecut_group = []
                append_to_linecut_group = linecut_group.append

                for word in words:

                    linecut_word = Object2D.from_surface(
                        render_text(
                            word,
                            **NORMAL_TEXT_SETTINGS,
                        ),
                    )

                    append_to_text(linecut_word)
                    append_to_linecut_group(linecut_word)

                linecut_group_list.append(linecut_group)

            else:

                text_settings = TAG_TO_TEXT_SETTINGS.get(
                    tag_name,
                    NORMAL_TEXT_SETTINGS,
                )

                for word in words:

                    append_to_text(
                        Object2D.from_surface(
                            surface=(
                                render_text(
                                    word,
                                    **text_settings,
                                )
                            )
                        )
                    )

        self.rect.snap_rects_intermittently_ip(
            dimension_name="width",
            dimension_unit="pixels",
            max_dimension_value=max_width,
            offset_pos_by=(5, 0),
        )

        ###

        same_line_anchors = []

        for group in anchor_groups:

            last_left = -1
            same_line_anchors.clear()

            underline_color = (
                HTTP_ANCHOR_TEXT_FG
                if group[0].href.lower().startswith("http")
                else HTSL_ANCHOR_TEXT_FG
            )

            for anchor in group:

                left = anchor.rect.left

                if left > last_left:
                    same_line_anchors.append(anchor)

                else:

                    length = len(same_line_anchors)

                    if length > 1:

                        self.unite_anchors(same_line_anchors)

                    elif length == 1:

                        underline(
                            same_line_anchors[0].image,
                            underline_color,
                        )

                    same_line_anchors.clear()
                    same_line_anchors.append(anchor)

                last_left = left

            length = len(same_line_anchors)

            if length > 1:
                self.unite_anchors(same_line_anchors)

            elif length == 1:

                underline(
                    same_line_anchors[0].image,
                    underline_color,
                )

        ###

        same_line_marked = []

        for group in marked_groups:

            last_left = -1
            same_line_marked.clear()

            for marked in group:

                left = marked.rect.left

                if left > last_left:
                    same_line_marked.append(marked)

                else:

                    if len(same_line_marked) > 1:
                        self.unite_marked(same_line_marked)

                    same_line_marked.clear()

                last_left = left

            if len(same_line_marked) > 1:
                self.unite_marked(same_line_marked)

        ###

        for linecut_groups, line_operation in (
            (underline_groups, underline),
            (strikethrough_groups, strikethrough),
        ):

            same_line_linecut = []

            for group in linecut_groups:

                last_left = -1
                same_line_linecut.clear()

                for linecut in group:

                    left = linecut.rect.left

                    if left > last_left:
                        same_line_linecut.append(linecut)

                    else:

                        length = len(same_line_linecut)

                        if length > 1:

                            (
                                self.unite_linecut(
                                    same_line_linecut,
                                    line_operation,
                                )
                            )

                        elif length == 1:

                            line_operation(same_line_linecut[0].image)

                        same_line_linecut.clear()

                    last_left = left

                length = len(same_line_linecut)

                if length > 1:

                    self.unite_linecut(
                        same_line_linecut,
                        line_operation,
                    )

                elif length == 1:

                    line_operation(same_line_linecut[0].image)

        text_body = Object2D.from_surface(
            render_rect(
                *self.rect.size,
                HTSL_CANVAS_BG,
            )
        )

        all_objs = self[:]

        self.clear()
        self.append(text_body)

        image = text_body.image

        self.anchor_list = []

        for obj in all_objs:

            if isinstance(obj, Anchor):

                self.append(obj)
                self.anchor_list.append(obj)

            else:
                image.blit(obj.image, obj.rect)

    def unite_anchors(self, anchors):

        first_anchor = anchors[0]

        topleft = first_anchor.rect.topleft
        href = first_anchor.href

        for index, obj in enumerate(self):
            if obj is first_anchor:
                break

        union_surf = unite_surfaces(
            [(anchor.image, anchor.rect) for anchor in anchors],
            background_color=HTSL_CANVAS_BG,
        )

        underline(
            union_surf,
            (
                HTTP_ANCHOR_TEXT_FG
                if href.lower().startswith("http")
                else HTSL_ANCHOR_TEXT_FG
            ),
        )

        new_anchor = Anchor(union_surf, href)
        new_anchor.rect.topleft = topleft

        for anchor in anchors:
            self.remove(anchor)

        self.insert(index, new_anchor)

    def unite_marked(self, marked_objs):

        first_marked = marked_objs[0]

        topleft = first_marked.rect.topleft

        for index, obj in enumerate(self):
            if obj is first_marked:
                break

        union_surf = unite_surfaces(
            [(marked.image, marked.rect) for marked in marked_objs],
            background_color=HTSL_MARKED_TEXT_BG,
        )

        new_marked = Object2D.from_surface(union_surf)
        new_marked.rect.topleft = topleft

        for marked in marked_objs:
            self.remove(marked)

        self.insert(index, new_marked)

    def unite_linecut(self, linecut_objs, line_operation):

        first_linecut = linecut_objs[0]

        topleft = first_linecut.rect.topleft

        for index, obj in enumerate(self):
            if obj is first_linecut:
                break

        union_surf = unite_surfaces(
            [(linecut.image, linecut.rect) for linecut in linecut_objs],
            background_color=HTSL_CANVAS_BG,
        )

        line_operation(union_surf)

        new_linecut = Object2D.from_surface(union_surf)
        new_linecut.rect.topleft = topleft

        for linecut in linecut_objs:
            self.remove(linecut)

        self.insert(index, new_linecut)


def get_ordered_items(
    list_element,
    max_width,
    text_list=None,
    level=0,
):

    if text_list is None:

        text_list = List2D()
        text_list.anchor_list = []

    current_index = int(list_element.getAttribute("start") or "1")

    ELEMENT_NODE = list_element.ELEMENT_NODE

    for child in list_element.childNodes:

        if child.nodeType != ELEMENT_NODE:
            continue

        insert_list_item(
            child,
            max_width,
            text_list,
            level,
            icon_chars=f"{current_index}.",
        )

        current_index += 1

    return text_list


BULLET_CHARS = (
    "\N{bullet}",
    "\N{triangular bullet}",
)

NO_OF_BULLET_CHARS = len(BULLET_CHARS)


def get_unordered_items(
    list_element,
    max_width,
    text_list=None,
    level=0,
):

    if text_list is None:

        text_list = List2D()
        text_list.anchor_list = []

    ul_icon = BULLET_CHARS[level % NO_OF_BULLET_CHARS]

    ELEMENT_NODE = list_element.ELEMENT_NODE

    for child in list_element.childNodes:

        if child.nodeType != ELEMENT_NODE:
            continue

        insert_list_item(
            child,
            max_width,
            text_list,
            level,
            icon_chars=ul_icon,
        )

    return text_list


def insert_list_item(
    item_element,
    max_width,
    text_list,
    level,
    icon_chars,
):

    indent = (level + 1) * 30

    max_width += -indent

    icon = CachedTextObject(
        icon_chars,
        text_settings=NORMAL_TEXT_SETTINGS,
    )

    icon.rect.right = indent

    if text_list:
        icon.rect.top = text_list.rect.bottom

    text_list.append(icon)

    ###

    ELEMENT_NODE = item_element.ELEMENT_NODE
    TEXT_NODE = item_element.TEXT_NODE

    ### if item has a sublist...

    if any(
        item.tagName.lower() in ("ol", "ul")
        for item in item_element.childNodes
        if item.nodeType == ELEMENT_NODE
    ):

        children_before_list = []

        for child in item_element.childNodes:

            node_type = child.nodeType

            if node_type == TEXT_NODE:

                if child.data.strip():
                    children_before_list.append(child)

                else:
                    continue

            elif node_type == ELEMENT_NODE:

                if child.tagName in ("ol", "ul"):
                    break

                else:
                    children_before_list.append(child)

        ### if item has text before the sublist,
        ### render it...

        if children_before_list:

            new_li = (
                getDOMImplementation().createDocument(None, "li", None).documentElement
            )

            for child in children_before_list:
                new_li.appendChild(child)

            text_block = TextBlock(
                new_li,
                max_width,
            )

            text_block.rect.topleft = icon.rect.move(5, 0).topright

            text_list.extend(text_block)
            text_list.anchor_list.extend(text_block.anchor_list)

        ###

        sublist_element = next(
            item
            for item in item_element.childNodes
            if (item.nodeType == ELEMENT_NODE and item.tagName.lower() in ("ol", "ul"))
        )

        sublist_tag_name = sublist_element.tagName.lower()

        ###

        if sublist_tag_name == "ol":

            ordered_list = get_ordered_items(
                sublist_element,
                max_width,
                text_list,
                level=level + 1,
            )

            ordered_list.rect.top = text_list.rect.bottom

        elif sublist_tag_name == "ul":

            unordered_list = get_unordered_items(
                sublist_element,
                max_width,
                text_list,
                level=level + 1,
            )

            unordered_list.rect.top = text_list.rect.bottom

    else:

        text_block = TextBlock(item_element, max_width)

        text_block.rect.topleft = icon.rect.move(5, 0).topright

        text_list.extend(text_block)
        text_list.anchor_list.extend(text_block.anchor_list)


### utility functions


def underline(
    surface,
    color=NORMAL_TEXT_SETTINGS["foreground_color"],
):

    rect = surface.get_rect().move(0, -3)

    draw_line(
        surface,
        color,
        rect.bottomleft,
        rect.bottomright,
        1,
    )


def strikethrough(surface):

    rect = surface.get_rect().move(0, 2)

    draw_line(
        surface,
        NORMAL_TEXT_SETTINGS["foreground_color"],
        rect.midleft,
        rect.midright,
        1,
    )


class BlockQuote(List2D):
    def __init__(self, blockquote, max_width):

        super().__init__()

        ###

        text_max_width = round(max_width * 0.8)

        paragraphs = blockquote.getElementsByTagName("p")

        top = 0

        for paragraph in paragraphs:

            text_block = TextBlock(paragraph, text_max_width)

            text_block.rect.top = top

            self.extend(text_block)

            top = text_block.rect.move(0, 14).bottom

        ###

        try:
            footer = blockquote.getElementsByTagName("footer")[0]

        except IndexError:
            has_footer = False
        else:
            has_footer = True

        if has_footer:

            footer_max_width = round(max_width * 0.7)

            footer_block = TextBlock(footer, footer_max_width)

            footer_block.rect.topleft = self.rect.move(0, 15).bottomleft

            line_starting_x = footer_block.rect.x

            footer_block.rect.move_ip(25, 0)

            self.extend(footer_block)

        ###

        blockquote_body = Object2D.from_surface(
            render_rect(
                *self.rect.size,
                HTSL_CANVAS_BG,
            )
        )

        image = blockquote_body.image

        all_objs = self[:]

        self.clear()

        self.append(blockquote_body)
        self.anchor_list = []

        for obj in all_objs:

            if isinstance(obj, Anchor):

                self.append(obj)
                self.anchor_list.append(obj)

            else:
                image.blit(obj.image, obj.rect)

        ###

        if has_footer:

            x1 = line_starting_x
            x2 = x1 + 20

            y = footer_block.rect.move(0, 13).top

            draw_line(
                image,
                (40, 40, 40),
                (x1, y),
                (x2, y),
                1,
            )

        ###

        x_offset = round(max_width * 0.1)
        self.rect.move_ip(x_offset, 0)


class Table(List2D):
    """Represents <table> element.

    Uses a grid system inspired in the one used on
    Bootstrap 4.

    For now at least, do not support cells that expands
    more than a row or column.
    """

    def __init__(self, table, max_width):

        unit_width = max_width // 12

        super().__init__()

        rows = table.getElementsByTagName("tr")

        no_of_columns = len(rows[0].getElementsByTagName("th"))

        default_units = 12 // no_of_columns

        ELEMENT_NODE = table.ELEMENT_NODE

        column_widths = [
            get_column_size(child, unit_width, default_units)
            for child in rows[0].childNodes
            if child.nodeType == ELEMENT_NODE
        ]

        column_rects = [Rect(0, 0, width, 1) for width in column_widths]

        columns_rectsman = RectsManager(column_rects.__iter__)

        columns_rectsman.snap_rects_ip(
            retrieve_pos_from="topright",
            assign_pos_to="topleft",
        )

        row_rect = Rect(0, 0, columns_rectsman.width, 1)

        row_rects = []
        rows_rectsman = RectsManager(row_rects.__iter__)

        horizontal_lines = []

        text_blocks = []

        for row in rows:

            cells = row.getElementsByTagName("th")

            if cells:

                row_is_heading = True

            else:

                cells = row.getElementsByTagName("td")
                row_is_heading = False

            for column_rect, cell in zip(column_rects, cells):

                if cell.tagName.lower() == "th":

                    cell_text = cell.childNodes[0].data

                    cell = dom_from_string(
                        f"<th><b>{cell_text}</b></th>"
                    ).getElementsByTagName("th")[0]

                text_block = TextBlock(
                    cell,
                    # "- 10" is for horizontal
                    # padding,
                    column_rect.width - 10,
                )

                text_blocks.append(text_block)

            row_rect.height = (
                max(text_block.rect.height for text_block in text_blocks) + 20
            )  # vertical padding

            for column_rect, text_block in zip(column_rects, text_blocks):

                text_block.rect.midleft = (
                    column_rect.x,
                    row_rect.centery,
                )

            horizontal_lines.append(
                (
                    row_rect.topleft,
                    row_rect.topright,
                    1,
                )
            )

            if row_is_heading:

                horizontal_lines.append(
                    (
                        row_rect.bottomleft,
                        row_rect.bottomright,
                        2,
                    )
                )

            row_rects.append(row_rect.copy())

            row_rect.top = row_rect.bottom

            row_rect.height = 1

            ###

            for text_block in text_blocks:
                self.extend(text_block)

            ###
            text_blocks.clear()

        table_body = Object2D.from_surface(
            render_rect(
                *rows_rectsman.size,
                HTSL_CANVAS_BG,
            )
        )

        image = table_body.image

        all_objs = self[:]

        self.clear()

        self.append(table_body)
        self.anchor_list = []

        for obj in all_objs:

            if isinstance(obj, Anchor):

                self.append(obj)
                self.anchor_list.append(obj)

            else:
                image.blit(obj.image, obj.rect)

        ###

        for start, end, thickness in horizontal_lines:

            draw_line(
                image,
                (70, 70, 70),
                start,
                end,
                thickness,
            )

        ###


def get_column_size(child, unit_width, default_units):

    try:
        column_units = int(child.getAttribute("class")[4])

    except Exception:
        column_units = default_units

    return (column_units * unit_width) - 10  # for padding


def get_defined_items(dl, max_width):

    term_width = max_width

    definition_x_offset = 30
    definition_width = max_width - definition_x_offset

    elements = list(
        zip(
            dl.getElementsByTagName("dt"),
            dl.getElementsByTagName("dd"),
        )
    )

    elements.reverse()

    x = y = 0

    text_blocks = List2D()

    ELEMENT_NODE = dl.ELEMENT_NODE

    while elements:

        term, definition = elements.pop()

        ## if term text is not styled, we make it bold

        if not any(
            child for child in term.childNodes if child.nodeType == ELEMENT_NODE
        ):

            term_text = term.childNodes[0].data

            term = dom_from_string(f"<dt><b>{term_text}</b></dt>").getElementsByTagName(
                "dt"
            )[0]

        ##

        term_block = TextBlock(term, term_width)

        definition_block = TextBlock(
            definition,
            definition_width,
        )

        definition_block.rect.move_ip(
            definition_x_offset,
            0,
        )

        text_blocks.append(term_block)
        text_blocks.append(definition_block)

    text_blocks.rect.snap_rects_ip(
        retrieve_pos_from="bottom",
        assign_pos_to="top",
        offset_pos_by=(0, 2),
    )

    all_text_blocks = text_blocks[:]

    text_blocks.clear()

    text_blocks.anchor_list = []

    for text_block in all_text_blocks:

        text_blocks.extend(text_block)
        text_blocks.anchor_list.extend(text_block.anchor_list)

    return text_blocks
