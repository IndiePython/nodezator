"""Facility for preparing HTSL objects."""

### standard library import
from pathlib import Path


### local imports

from ..classes2d.collections import List2D

from ..surfdef import surfdef_obj_from_element

from .constants import KNOWN_TAGS

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
    get_python_codeblock,
    get_pre_textblock,
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

        self.title_label.set(f"HTSL Browser - {title}")

        self.title_cache[resource_path] = title

    def handle_body(self, body):

        self.objs = List2D()
        append_obj = self.objs.append

        max_width = self.content_area_obj.rect.inflate(-10, -10).width

        ELEMENT_NODE = body.ELEMENT_NODE

        for child in body.childNodes:

            if child.nodeType != ELEMENT_NODE:
                continue

            tag_name = child.tagName.lower()

            if tag_name not in KNOWN_TAGS:
                continue

            if tag_name in (
                "h6",
                "h5",
                "h4",
                "h3",
                "h2",
                "h1",
            ):
                append_obj(get_heading(child, max_width))

            elif tag_name == "p":
                append_obj(TextBlock(child, max_width))

            elif tag_name == "blockquote":
                append_obj(BlockQuote(child, max_width))

            elif tag_name == "python":
                append_obj(get_python_codeblock(child))

            elif tag_name == "pre":
                append_obj(get_pre_textblock(child))

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

        self.objs.rect.topleft = self.content_area_obj.rect.move(5, 5).topleft

        self.objs.rect.snap_rects_ip(
            retrieve_pos_from="bottom", assign_pos_to="top", offset_pos_by=(0, 14)
        )

    def set_htsl_objects_from_cache(self, key):

        self.objs.clear()
        self.objs.extend(self.cache[key])

        self.title_label.set(f"HTSL Browser - {self.title_cache[key]}")


def get_extension(src):
    return Path(src).suffix.lower()
