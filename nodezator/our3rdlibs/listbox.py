
### standard library imports

from math import inf as INFINITY

from functools import partialmethod


### third-party imports

from pygame.locals import KMOD_CTRL, KMOD_SHIFT

from pygame.draw import rect as draw_rect


### local imports

from ..pygamesetup import SERVICES_NS

from ..classes2d.single import Object2D

from ..fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)

from ..textman.render import render_text

from ..surfsman.render import render_rect

from ..surfsman.cache import RECT_SURF_MAP

from ..colorsman.colors import BLACK, WHITE



class ListBox(Object2D):
    """Holds and displays a list of items

    Has extra behaviour, some of which can be configured.
    """

    def __init__(
        self,
        items=(),
        no_of_visible_lines = 7,
        width=100,
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        padding=0,
        normal_foreground_color = BLACK,
        normal_background_color_a = (245, 245, 245),
        normal_background_color_b = (215, 215, 215),
        selected_foreground_color = WHITE,
        selected_background_color_a = (0, 0, 255),
        selected_background_color_b = (0, 0, 195),
        selectable_hint='all', # 'none', 'one' or 'all'
        ommit_direction='right',
        coordinates_name='topleft',
        coordinates_value=(0, 0),
    ):

        if width < 10:
            raise ValueError(f"'width' must be at least 10 pixels")

        item_height = self.item_height = font_height + (padding * 2)

        height = item_height * no_of_visible_lines

        self.toplefts = [(0, y) for y in range(0, height, item_height)]

        ###

        self.image = render_rect(width, height)

        self.rect = self.image.get_rect()
        setattr(self.rect, coordinates_name, coordinates_value)

        ###

        self.selectable_hint = selectable_hint
        self.no_of_visible_lines = no_of_visible_lines

        self.font_height = font_height
        self.font_path = font_path
        self.padding = padding
        self.width = width
        self.ommit_direction = ommit_direction

        self.normal_foreground_color = normal_foreground_color
        self.normal_background_color_a = normal_background_color_a
        self.normal_background_color_b = normal_background_color_b
        self.selected_foreground_color = selected_foreground_color
        self.selected_background_color_a = selected_background_color_a
        self.selected_background_color_b = selected_background_color_b

        self.item_to_surf_map = {}

        self.items = []
        self.item_objects = []
        self.selected_flags = []

        self.extend(items)

    def render_items(self):

        nfg = self.normal_foreground_color
        nbg_a = self.normal_background_color_a
        nbg_b = self.normal_background_color_b

        sfg = self.selected_foreground_color
        sbg_a = self.selected_background_color_a
        sbg_b = self.selected_background_color_b

        width = self.width
        padding = self.padding

        item_objects = self.item_objects
        item_objects.clear()
        append_item_object = item_objects.append

        item_to_surf_map = self.item_to_surf_map

        for value in self.items:

            if value not in item_to_surf_map:

                surf_map = {

                    name : (
                        render_text(
                            str(value),
                            font_height = self.font_height,
                            font_path = self.font_path,
                            padding = padding,
                            foreground_color=fg,
                            background_color=bg,
                            max_width=width,
                            ommit_direction=self.ommit_direction,
                        )
                    )

                    for name, fg, bg in (
                        ('normal_a', nfg, nbg_a),
                        ('normal_b', nfg, nbg_b),
                        ('selected_a', sfg, sbg_a),
                        ('selected_b', sfg, sbg_b),
                    )

                }

                item_to_surf_map[value] = surf_map

            else:
                surf_map = item_to_surf_map[value]

            append_item_object(
                Object2D.from_surface(
                    surf_map['normal_a'],
                    surface_map = surf_map,
                    value = value,
                )
            )

    def _clear_no_update(self):

        self.items.clear()
        self.item_objects.clear()
        self.index_of_top_visible_item = 0
        self.index_of_last_selected = None
        self.selected_flags.clear()

    def clear(self):
        self._clear_no_update()
        self.update_image()

    def update_image(self):

        image = self.image
        blit_on_image = image.blit
        toplefts = self.toplefts

        item_objects = self.item_objects
        flags = self.selected_flags

        width = self.width
        item_height = self.item_height

        nbg_a = self.normal_background_color_a
        nbg_b = self.normal_background_color_b
        sbg_a = self.selected_background_color_a
        sbg_b = self.selected_background_color_b

        index_range = range(len(item_objects))

        ils = self.index_of_last_selected

        for line_index, item_index in enumerate(

            range(
                self.index_of_top_visible_item,
                self.index_of_top_visible_item + self.no_of_visible_lines
            )

        ):

            theres_an_item = item_index in index_range
            is_even = not item_index % 2
            is_selected = flags[item_index] if theres_an_item else False

            if is_selected:
                bg_color = sbg_a if is_even else sbg_b

            else:
                bg_color = nbg_a if is_even else nbg_b

            bg = RECT_SURF_MAP[(width, item_height, bg_color)]

            topleft = toplefts[line_index]
            blit_on_image(bg, topleft)

            if theres_an_item:

                state = 'selected' if flags[item_index] else 'normal'
                state += '_a' if is_even else '_b'

                blit_on_image(
                    item_objects[item_index].surface_map[state],
                    topleft,
                )

                if item_index == ils:

                    for pos, size in (
                        (topleft, (width, item_height)),
                        (tuple(v+1 for v in topleft), (width-2, item_height-2))
                    ):
                        draw_rect(image, 'black', (pos, size), 1)

    def get(self):

        return [
            item.value
            for item, sel_state in zip(self.item_objects, self.selected_flags)
            if sel_state
        ]

    def set_items(self, item_values):

        self._clear_no_update()
        self.extend(item_values)

    def extend(self, item_values):

        self.items.extend(item_values)

        self.render_items()

        self.selected_flags.clear()
        self.selected_flags.extend(0 for _ in self.items)

        self.index_of_top_visible_item = 0
        self.index_of_last_selected = None

        self.update_image()

    def remove(self, item_value):
        self.remove_items([item_value])

    def remove_items(self, item_values):

        remove_item = self.items.remove

        for value in item_values:
            remove_item(value)

        self.render_items()

        self.selected_flags.clear()
        self.selected_flags.extend(0 for _ in self.items)

        self.index_of_top_visible_item = 0
        self.index_of_last_selected = None

        self.update_image()

    def remove_selected(self):

        selected_values = self.get()

        if selected_values:
            self.remove_items(selected_values)

    def on_mouse_release(self, event):

        if event.button == 1:
            self.mouse_select(event.pos[1])

        elif event.button == 4:
            self.scroll(-1)

        elif event.button == 5:
            self.scroll(1)

    def mouse_select(self, y):
        ### calculate distance from top of listbox to y
        dy = y - self.rect.y

        ### index of clicked line
        iocl = divmod(dy, self.item_height)[0]

        ### if clicked line has no item, clear selection and
        ### leave method by returning

        if iocl >= len(self.item_objects):

            self.clear_selection()
            return

        ### index of clicked item
        ioci = self.index_of_top_visible_item + iocl

        ### store index of last selected item as the previous one,
        ### since we are about to update such value
        previous_ils = self.index_of_last_selected

        ### update the index of last selected item so its equivalent
        ### to the index of the item under the mouse
        self.index_of_last_selected = ioci

        ### reference selectable hint locally
        selectable_hint = self.selectable_hint

        ### if items aren't selectable, update image then exit method
        ### by returning

        if selectable_hint == 'none':

            self.update_image()
            return

        ### retrieve pressed state of ctrl and shift keys

        mods_bitmask = SERVICES_NS.get_pressed_mod_keys()
        ctrl = mods_bitmask & KMOD_CTRL
        shift = mods_bitmask & KMOD_SHIFT

        ### reference selected flags locally
        flags = self.selected_flags

        ### execute the appropriate operation
        ### for the remaining scenarios depending
        ### on the pressed states of the ctrl and
        ### shift keys

        if selectable_hint == 'one':

            selected_state = flags[ioci]

            self.clear_selection()

            new_selected_state = (
                (selected_state + 1) % 2
                if ctrl
                else 1
            )

            flags[ioci] = new_selected_state

        elif selectable_hint == 'all':

            if not ctrl and not shift:
                self.clear_selection()
                flags[ioci] = 1

            elif ctrl and not shift:
                flags[ioci] = (flags[ioci] + 1) % 2

            elif shift and not ctrl:

                if previous_ils is None:
                    flags[ioci] = (flags[ioci] + 1) % 2

                else:

                    a = min(previous_ils, ioci)
                    b = max(previous_ils, ioci) + 1

                    for i in range(a, b):
                        flags[i] = 1

        ### finally update the image
        self.update_image()

    def clear_selection(self):

        sf = self.selected_flags

        sf.clear()
        sf.extend(0 for _ in self.items)

    def walk(self, steps):
        """Move the cursor/indicator."""
        ### store number of items
        length = len(self.item_objects)

        ### if there are no items or no steps to be taken,
        ### exit method by returning
        if not length or not steps:
            return

        ### reference data/objects locally

        selectable_hint = self.selectable_hint
        ils = self.index_of_last_selected
        flags = self.selected_flags

        ### define start and end of movement

        ## if there's no last selected item...

        if ils is None:

            if steps > 0:

                steps += -1

                start = 0
                end = start + steps

                if end >= length:
                    end = length - 1

            elif steps < 0:

                steps += 1

                start = length - 1
                end = start + steps

                if end < 0:
                    end = 0


        ## otherwise, if there's a last selected item...

        else:

            start = ils
            end = start + steps

            if steps > 0:

                if end >= length:
                    end = length - 1

            elif steps < 0:

                if end < 0:
                    end = 0

        ### store the end as the new index of last selected
        ### item
        self.index_of_last_selected = ils = end

        ### change selected states depending on selectable
        ### hint and whether the shift key is pressed or not

        if selectable_hint == 'one':

            self.clear_selection()
            flags[end] = 1

        elif selectable_hint == 'all':

            ### if shift is pressed...

            if SERVICES_NS.get_pressed_mod_keys() & KMOD_SHIFT:

                a = min(start, end)
                b = max(start, end) + 1

                for i in range(a, b):
                    flags[i] = 1

            ### otherwise...

            else:
                self.clear_selection()
                flags[end] = 1

        ### calculate the first and last visible items

        first_visible_index = self.index_of_top_visible_item

        last_visible_index = (
            first_visible_index
            + self.no_of_visible_lines
            - 1
        )

        ### if the last selected index is below or above the visible range,
        ### scroll it so it is in the visible range;
        ###
        ### in such case, the image is updated implicitly;

        if ils < first_visible_index:
            scroll_steps = ils - first_visible_index
            self.scroll(scroll_steps)

        elif ils > last_visible_index:
            scroll_steps = ils - last_visible_index
            self.scroll(scroll_steps)

        ### otherwise, just update the image
        else:
            self.update_image()

    go_to_top = partialmethod(walk, -INFINITY)
    go_to_bottom = partialmethod(walk, INFINITY)

    def scroll(self, steps):
        """Scroll items."""

        itvi = self.index_of_top_visible_item
        nvl = self.no_of_visible_lines
        length = len(self.item_objects)

        ### if steps == 0 or number of visible lines is equal or higher
        ### than number of items, there's no need to scroll, so we exit
        ### the method by returning
        if not steps or (nvl >= length):
            return

        ### if scrolling down (items go up), ensure last item
        ### doesn't go above last visible line

        elif steps > 0:

            ## index of bottom visible item
            ibvi = itvi + nvl

            ## index of last item
            ili = length

            ##
            if ibvi + steps > ili:
                steps = ili - ibvi

        ### if scrolling up (items go down), ensure first item
        ### doesn't go below first visible line

        elif steps < 0:

            if itvi + steps < 0:
                steps = -itvi

        ### finally, increment/decrement the index of the top visible
        ### item and update the image

        self.index_of_top_visible_item += steps
        self.update_image()

    def sort(self):

        self.items.sort()
        self.item_objects.sort(key=lambda item: item.value)

        self.selected_flags.clear()
        self.selected_flags.extend(0 for _ in self.items)

        self.index_of_top_visible_item = 0
        self.index_of_last_selected = None

        self.update_image()
