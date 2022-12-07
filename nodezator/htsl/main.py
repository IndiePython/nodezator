"""Facility for about dialog."""

### standard library imports

from xml.dom.minidom import parse as dom_from_filepath

from operator import truediv

from functools import reduce, partialmethod

from webbrowser import open as open_url


### third-party imports

from pygame import (
    QUIT,
    KEYUP,
    K_ESCAPE,
    K_RETURN,
    K_KP_ENTER,
    K_w,
    K_a,
    K_s,
    K_d,
    K_k,
    K_h,
    K_j,
    K_l,
    K_UP,
    K_LEFT,
    K_DOWN,
    K_RIGHT,
    K_PAGEUP,
    K_PAGEDOWN,
    K_HOME,
    K_END,
    MOUSEBUTTONUP,
)

from pygame.event import get as get_events

from pygame.key import get_pressed as get_pressed_keys

from pygame.display import update

from pygame.math import Vector2


### local imports

from ..config import APP_REFS, APP_WIDE_WEB_DIR

from ..pygameconstants import SCREEN_RECT, blit_on_screen

from ..ourstdlibs.meta import initialize_bases

from ..classes2d.single import Object2D

from ..fontsman.constants import ENC_SANS_BOLD_FONT_PATH

from ..textman.label.main import Label

from ..surfsman.icon import render_layered_icon

from ..loopman.main import LoopHolder

from ..surfsman.render import render_rect

from ..surfsman.cache import UNHIGHLIGHT_SURF_MAP

from ..colorsman.colors import (
    HTSL_BROWSER_BG,
    HTSL_CANVAS_BG,
    HTSL_DOCUMENT_TITLE_TEXT_FG,
    BLACK,
)

## extension class
from .prep import Preparation


### constants

UP_KEYS = (K_w, K_k, K_UP)
LEFT_KEYS = (K_a, K_h, K_LEFT)
DOWN_KEYS = (K_s, K_j, K_DOWN)
RIGHT_KEYS = (K_d, K_l, K_RIGHT)


AWW_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (90, 91)],
    dimension_name="height",
    dimension_value=22,
    colors=[BLACK, (30, 150, 80)],
    background_width=24,
    background_height=24,
)


class HTSLBrowser(
    Object2D,
    Preparation,
    LoopHolder,
):
    """Allows browsing web-like pages.

    HTSL means "HyperText as Surfaces" markup Language,
    which is just a xml file used to describe web-like
    pages to be rendered as pygame surfaces.

    This class is instantiated only once in the end of the
    module and its main method is aliased to be used
    wherever needed in the entire package.
    """

    def __init__(self):
        """Initialize base classes as needed."""
        ### execute __init__ method of bases classes, if
        ### they have
        initialize_bases(self)

        ### create dicts to serve as caches

        self.cache = {}
        self.title_cache = {}

        ### create image and rect

        self.image = render_rect(960, 680, HTSL_BROWSER_BG)

        self.image.blit(AWW_ICON, (5, 5))

        self.rect = self.image.get_rect()

        content_area = self.rect.inflate(-20, -50)

        content_area.bottomleft = self.rect.move(5, -15).bottomleft

        content_canvas = render_rect(
            *content_area.size,
            HTSL_CANVAS_BG,
        )
        self.canvas_copy = content_canvas.copy()

        self.content_area_obj = Object2D(
            image=content_canvas,
            rect=content_area,
        )

        ### XXX
        ### also probably create a scroll area by
        ### slightly smaller than the content area to
        ### be used for scrolling

        ### set initial pysite attribute (default pysite
        ### opened in the htsl browser)
        self.pysite = "nodezator.pysite"

        ### set vertical page movement amount
        self.v_page_amount = content_area.height - 140

        ### create label for document titles

        label_max_width = self.rect.inflate(-40, 0).width

        self.title_label = Label(
            "HTSL Browser - Untitled document",
            font_height=20,
            font_path=ENC_SANS_BOLD_FONT_PATH,
            foreground_color=HTSL_DOCUMENT_TITLE_TEXT_FG,
            background_color=HTSL_BROWSER_BG,
            padding=0,
            max_width=label_max_width,
        )

        ### center htsl browser and append the centering
        ### method as a window resize setup

        self.center_htsl_browser()

        APP_REFS.window_resize_setups.append(self.center_htsl_browser)

    def center_htsl_browser(self):

        diff = Vector2(SCREEN_RECT.center) - self.rect.center

        self.rect.center = SCREEN_RECT.center

        ###
        self.content_area_obj.rect.move_ip(diff)

        ###

        self.title_label.rect.midleft = (
            self.rect.move(35, 0).left,
            self.rect.move(0, 17).top,
        )

        ###

        for obj_list in self.cache.values():
            obj_list.rect.move_ip(diff)

        ### if htsl browser loop is running, request it
        ### to be drawn

        if hasattr(self, "running") and self.running:

            APP_REFS.draw_after_window_resize_setups = self.draw_once

    def open_htsl_link(self, link):
        """Create a htsl page from existing htsl file.

        The file is found with the given file name.

        Parameters
        ==========
        link (string)
            used to retrieve the file from which to obtain
            the htsl data to generate the page.
        """
        resource_path = self.resolve_htsl_path(link)

        address, _, optional_id = resource_path.partition("#")

        if address in self.cache:
            self.set_htsl_objects_from_cache(address)

        else:

            htsl_dom = dom_from_filepath(address)

            self.create_and_set_htsl_objects(
                htsl_dom,
                address,
            )

        ### show htsl page
        self.show_htsl_page(optional_id)

    def create_and_show_htsl_page(self, htsl_element):

        self.create_and_set_htsl_objects(htsl_element)
        self.show_htsl_page()

    def show_htsl_page(self, optional_id=""):

        ### define whether horizontal and vertical
        ### scrolling are enabled

        available_width, available_height = self.content_area_obj.rect.size

        page_width, page_height = self.objs.rect.size

        self.horizontal_scrolling_enabled = (
            True if page_width > available_width else False
        )

        self.vertical_scrolling_enabled = (
            True if page_height > available_height else False
        )

        ### blit a semitransparent surface in the canvas
        ### to increase constrast between the dialog
        ### and whatever is behind it (making what's behind
        ### appear unhighlighted)

        blit_on_screen(UNHIGHLIGHT_SURF_MAP[SCREEN_RECT.size], (0, 0))

        ###

        if optional_id:

            for obj in self.objs:

                obj_id = getattr(obj, "id", "")

                if optional_id == obj_id:

                    self.ensure_obj_on_screen(obj)
                    break

        ###
        self.draw_once()

        ### loop
        self.loop()

        ### free up memory from rendered objects
        self.free_up_memory()

    def open_link(self, link_string):

        if link_string.startswith("http"):
            open_url(link_string)

        else:
            self.open_htsl_link(link_string)

    def resolve_htsl_path(self, path_string):

        for string in (
            "htap://aww.",
            "htap://",
            "aww.",
        ):

            if path_string.startswith(string):

                path_string = path_string[len(string) :]
                break

        start = path_string.find(".pysite")

        if start != -1:

            pysite = self.pysite = path_string[: start + 7]

            path_string = path_string[start + 8 :] or "index.htsl"

        else:
            pysite = self.pysite

        return str(
            reduce(
                truediv,
                path_string.split("/"),
                APP_WIDE_WEB_DIR / pysite,
            )
        )

    def ensure_obj_on_screen(self, obj):

        content_area = self.content_area_obj.rect

        area_top = content_area.top
        obj_top = obj.rect.top

        dy = area_top - obj_top

        self.move_objs(0, dy)

    def handle_input(self):

        self.handle_events()
        self.handle_keyboard_input()

    def handle_events(self):
        """Retrieve and handle events."""
        for event in get_events():

            if event.type == QUIT:
                self.quit()

            elif event.type == KEYUP:

                if event.key in (K_ESCAPE, K_RETURN, K_KP_ENTER):
                    self.exit_loop()

                elif event.key == K_PAGEUP:

                    self.move_objs(0, self.v_page_amount)
                    self.draw_once()

                elif event.key == K_PAGEDOWN:

                    self.move_objs(0, -self.v_page_amount)
                    self.draw_once()

                elif event.key == K_HOME:

                    self.move_objs(0, self.objs.rect.height)
                    self.draw_once()

                elif event.key == K_END:

                    self.move_objs(0, -self.objs.rect.height)
                    self.draw_once()

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.on_mouse_release(event)

                elif event.button == 4:

                    self.go_up()
                    self.draw_once()

                elif event.button == 5:

                    self.go_down()
                    self.draw_once()

    def on_mouse_release(self, event):
        """Open link if collides.

        Parameters
        ==========
        event (pygame.event.Event instance)

            represents data about a button of the mouse
            being pressed/released;

            we use the value of its "pos" attribute which
            represents the position of the mouse when the
            event happened to check whether an object from
            the page collided with the mouse.
        """
        ### retrieve the position of the mouse
        mouse_pos = event.pos

        ### iterate over objects

        for obj in self.objs:

            if obj.rect.collidepoint(mouse_pos):

                try:
                    href = self.href

                except AttributeError:
                    pass

                else:

                    self.open_link(href)
                    break

                try:
                    anchors = obj.anchor_list

                except AttributeError:
                    pass

                else:

                    for anchor in anchors:

                        if anchor.rect.collidepoint(mouse_pos):

                            self.open_link(anchor.href)
                            break

                break

    def handle_keyboard_input(self):
        """Handle pressed state of keys from keyboard."""
        key_input = get_pressed_keys()

        up = any(key_input[item] for item in UP_KEYS)
        left = any(key_input[item] for item in LEFT_KEYS)
        down = any(key_input[item] for item in DOWN_KEYS)
        right = any(key_input[item] for item in RIGHT_KEYS)

        if up and not down:

            self.go_up()
            self.draw_once()

        elif down and not up:

            self.go_down()
            self.draw_once()

        if left and not right:

            self.go_left()
            self.draw_once()

        elif right and not left:

            self.go_right()
            self.draw_once()

    def move_objs(self, x, y):

        objs_rect = self.objs.rect.copy()
        content_area = self.content_area_obj.rect

        if x and self.horizontal_scrolling_enabled:

            if x > 0:

                max_left = content_area.left
                resulting_left = objs_rect.move(x, 0).left

                if resulting_left > max_left:
                    x += max_left - resulting_left

            else:

                min_right = content_area.right
                resulting_right = objs_rect.move(x, 0).right

                if resulting_right < min_right:
                    x += min_right - resulting_right

        else:
            x = 0

        if y and self.vertical_scrolling_enabled:

            if y > 0:

                max_top = content_area.top
                resulting_top = objs_rect.move(0, y).top

                if resulting_top > max_top:
                    y += max_top - resulting_top

            else:

                min_bottom = content_area.bottom
                resulting_bottom = objs_rect.move(0, y).bottom

                if resulting_bottom < min_bottom:
                    y += min_bottom - resulting_bottom

        else:
            y = 0

        self.objs.rect.move_ip(x, y)

    go_up = partialmethod(move_objs, 0, 20)
    go_left = partialmethod(move_objs, -20, 0)
    go_down = partialmethod(move_objs, 0, -20)
    go_right = partialmethod(move_objs, 20, 0)

    def draw_once(self):
        """"""
        ###
        super().draw()

        ###
        self.title_label.draw()

        ###
        content_area_obj = self.content_area_obj

        content_canvas = content_area_obj.image
        content_area = content_area_obj.rect

        ###
        content_canvas.blit(self.canvas_copy, (0, 0))

        ###

        for obj in self.objs:

            if obj.rect.colliderect(content_area):

                obj.draw_relative(content_area_obj)

        ###
        self.content_area_obj.draw()

    def free_up_memory(self):
        """Free memory by clearing collections."""
        self.objs.clear()

    def draw(self):
        """Update screen."""
        ### pygame.display.update
        update()


### instantiate htsl browser and reference its relevant
### methods in the module level, so they can be easily
### imported from anywhere else in the package

_ = HTSLBrowser()

open_htsl_link = _.open_htsl_link
create_and_show_htsl_page = _.create_and_show_htsl_page
