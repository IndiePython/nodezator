"""Facility for preparing HTSL objects."""

### standard library import
from pathlib import Path


### third-party import verification

try:
    from pygame.scrap import put_text
except ImportError:
    PUT_TEXT_AVAILABLE = False
else:
    PUT_TEXT_AVAILABLE = True


### local imports

from ..classes2d.single import Object2D

from ..classes2d.collections import List2D

from ..surfdef import surfdef_obj_from_element

from .constants import (
    BROWSER_TITLE,
    KNOWN_TAGS,
    HEADING_TAGS,
    PRE_PYTHON_TAGS,
)

from .creation import (
    TextBlock,
    BlockQuote,
    Table,
    get_heading,
    get_unordered_items,
    get_ordered_items,
    get_defined_items,
)

from .image import get_image_obj

from .codeblock import (
    COPY_TO_CLIPBOARD_SURF,
    get_python_codeblock,
    get_pre_textblock,
    get_copy_button,
    get_save_button,
)

from ..colorsman.colors import HTSL_CANVAS_BG



class Preparation:

    def __init__(self):
        self.cache = {}

    def create_and_set_htsl_objects(
        self,
        htsl_dom,
        resource_path,
    ):
        """Create and set htsl objects."""

        ###
        self.handle_body(htsl_dom.getElementsByTagName("body")[0])

        ###
        self.cache[resource_path] = List2D(self.objs)

        ### remember to process title as well

        try:
            title = htsl_dom.getElementsByTagName("title")[0].childNodes[0].data

        except IndexError:
            title = "Untitled document"

        self.title_label.set(f"{title} - {BROWSER_TITLE}")

        self.title_cache[resource_path] = title

    def handle_body(self, body):

        self.objs = List2D()
        append_obj = self.objs.append

        pre_or_python_tags = 0

        max_width = self.scroll_area.width

        ELEMENT_NODE = body.ELEMENT_NODE

        for child in body.childNodes:

            if child.nodeType != ELEMENT_NODE:
                continue

            tag_name = child.tagName.lower()

            if tag_name not in KNOWN_TAGS:
                continue

            elif tag_name in HEADING_TAGS:
                append_obj(get_heading(child, max_width))

            elif tag_name == "p":
                append_obj(TextBlock(child, max_width))

            elif tag_name == "blockquote":
                append_obj(BlockQuote(child, max_width))

            elif tag_name == "python":
                append_obj(get_python_codeblock(child))
                pre_or_python_tags += 1

            elif tag_name == "pre":
                append_obj(get_pre_textblock(child))
                pre_or_python_tags += 1

            elif tag_name == "ol":
                append_obj(get_ordered_items(child, max_width))

            elif tag_name == "ul":
                append_obj(get_unordered_items(child, max_width))

            elif tag_name == "dl":
                append_obj(get_defined_items(child, max_width))

            elif tag_name == "surfdef":
                append_obj(surfdef_obj_from_element(child, HTSL_CANVAS_BG))

            elif tag_name == "img":

                resource_path = self.resolve_htsl_path(child.getAttribute("src"))

                extension = get_extension(resource_path)

                if extension == ".surfdef":

                    append(
                        surfdef_obj_from_path(
                            resource_path,
                            HTSL_CANVAS_BG,
                        )
                    )

                else:

                    append_obj(
                        get_image_obj(
                            resource_path,
                            extension,
                        )
                    )

            elif (
                tag_name == "a"
                and len(child.childNodes) == 1
                and (child.childNodes[0].tagName.lower()) == "img"
            ):

                resource_path = self.resolve_htsl_path(
                    (child.childNodes[0].getAttribute("src"))
                )

                extension = get_extension(resource_path)

                img = get_image_obj(resource_path, extension)

                img.href = child.getAttribute("href")

                append_obj(img)

            elif tag_name == "table":
                append_obj(Table(child, max_width))


        ### position objects relative to each other

        rect = self.objs.rect

        rect.snap_rects_ip(
            retrieve_pos_from="bottom", assign_pos_to="top", offset_pos_by=(0, 14)
        )

        ### if there are pre/python tags in the page...


        if pre_or_python_tags:

            ### request buttons to be added to each pre/python tag

            buttons_to_add = ['save_on_disk']

            ### if clipboard functionality is available, request
            ### "copy to clipboard" buttons to be added as well

            if PUT_TEXT_AVAILABLE:
                buttons_to_add.append('copy_to_clipboard')

            ### add button/buttons

            index_button_pairs = []

            y_offset = 0
            offset_increment = COPY_TO_CLIPBOARD_SURF.get_height()

            buttons = []

            for index, obj in enumerate(self.objs):

                tag_name = getattr(obj, 'tag_name', '').lower()

                if tag_name in PRE_PYTHON_TAGS:

                    y_offset += offset_increment

                    obj.rect.y += y_offset

                    bottomright = obj.rect.topright

                    for button_name in buttons_to_add:

                        if button_name == 'save_on_disk':

                            extension = '.py' if tag_name == 'python' else '.txt'
                            button = get_save_button(obj.text, extension, bottomright)

                        elif button_name == 'copy_to_clipboard':
                            button = get_copy_button(obj.text, bottomright)

                        buttons.append(button)

                        bottomright = button.rect.bottomleft

                        index_button_pairs.append((index, button))

                    left_diff =  obj.rect.left - buttons[-1].rect.left

                    if left_diff > 0:

                        for button in buttons:
                            button.rect.x += left_diff

                    buttons.clear()

                else:
                    obj.rect.y += y_offset

            ##
            insert_obj = self.objs.insert

            for index, button in reversed(index_button_pairs):
                insert_obj(index, button)

        ### add top padding to all headings

        y_offset = 0
        offset_increment = 40

        for obj in self.objs:

            if getattr(obj, 'tag_name', '') in HEADING_TAGS:
                y_offset += offset_increment

            obj.rect.y += y_offset

        ### position objects on the topleft of the scroll area
        rect.topleft = self.scroll_area.topleft

    def set_htsl_objects_from_cache(self, key):

        self.objs.clear()
        self.objs.extend(self.cache[key])

        self.title_label.set(f"{self.title_cache[key]} - {BROWSER_TITLE}")


def get_extension(src):
    return Path(src).suffix.lower()
