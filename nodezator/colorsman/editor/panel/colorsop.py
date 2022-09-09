"""Colors panel extension w/ colors-related operations."""

### standard library imports

from random import shuffle
from functools import partial, partialmethod


### local imports

from ....classes2d.collections import List2D

from ....ourstdlibs.color.utils import (
    get_color_sorter_by_properties,
)

from ....ourstdlibs.color.creation import (
    random_color_from_existing,
)

from ....dialog import create_and_show_dialog

from ...color2d import Color2D

from ...viewer.main import view_colors

from ...picker.main import (
    pick_html_colors,
    pick_pygame_colors,
)

from .constants import COLOR_WIDGET_SIZE


class ColorsOperations:
    """Colors-related operations for the colors panel."""

    def set_colors(self, colors):
        """(Re)build list of color widgets from given colors.

        Parameters
        ==========
        colors (list of colors)
            each color is represented by a list of integers
            in the range(256); such integers represent the
            values of the red, green and blue channels of
            the color, respectively; a fourth integer may
            also be present, representing the value of the
            alpha channel of the color.
        """
        ### create a special list containing a color widget
        ### for each given color

        self.widgets = List2D(Color2D(*COLOR_WIDGET_SIZE, color) for color in colors)

        ### align the rects of each color widget one beside
        ### the other
        self.widgets.rect.snap_rects_ip("topright", "topleft")

        ### align the topleft of the color widgets
        ### collectively to the topleft of the scroll area
        self.widgets.rect.topleft = self.scroll_area.topleft

        ### assign the first item (index 0) as the one
        ### representing the current selected color
        ### (the color whose values are displayed in the
        ### controls for edition)
        self.colors_editor.current_color_index = 0

        ### store a reference to the widget in that
        ### position, which we call the current widget
        self.store_current_widget()

        ### and finally, since we picked a widget and its
        ### color as the current one, let's display that
        ### color in the controls so it can be seen/edited
        self.colors_editor.set_color_on_controls(self.current_widget.color)

    def update_colors(self, colors):
        """Update colors on each widget to the given ones.

        Parameters
        ==========
        colors (list of colors)
            each color is represented by a list of integers
            in the range(256); such integers represent the
            values of the red, green and blue channels of
            the color, respectively; a fourth integer may
            also be present, representing the value of the
            alpha channel of the color.
        """
        ### set given colors on each widget

        for widget, color in zip(self.widgets, colors):
            widget.set_color(color)

        ### display color of current widget in the controls
        ### so it can be seen/edited
        ###
        ### this also has the side-effect of bring the
        ### current widget to the visible area if it isn't
        ### already there
        self.colors_editor.set_color_on_controls(self.current_widget.color)

    def perform_widget_quantity_setups(self):
        """Perform setups after changing number of widgets.

        Extra setups are needed after changing the number
        of existing widgets, so that the colors panel
        works properly. Such setups are performed here.
        """
        ### reference list of existing widgets locally for
        ### quicker and easier access
        widgets = self.widgets

        ### align the rects of the remaining color widgets
        ### one beside the other
        widgets.rect.snap_rects_ip("topright", "topleft")

        ### align the topleft of the color widgets
        ### collectively to the topleft of the scroll area
        widgets.rect.topleft = self.scroll_area.topleft

        ### retrieve the current index and clamp it to the
        ### available remaining indices

        current_index = self.colors_editor.current_color_index

        clamped_index = min(max(0, current_index), len(widgets) - 1)

        ### store the clamped index (which may or not be the
        ### same as the original) as the current index
        self.colors_editor.current_color_index = clamped_index

        ### store a reference to the widget in that
        ### position, which we call the current widget
        self.store_current_widget()

        ### finally, since we picked a widget and its
        ### color as the current ones, let's display that
        ### color in the controls so it can be seen/edited
        ###
        ### this also has the side-effect of moving the
        ### widgets so the current one is visible in the
        ### scroll area (though I'm not sure this side-effect
        ### is necessary here; it is ok, though)
        self.colors_editor.set_color_on_controls(self.current_widget.color)

    def set_current_color(self, color):
        """Update color on current color widget."""
        ### if not already, bring color widget to visible
        ### area
        self.color_widget_to_visible_area()

        ### if current color widget's color is equal to the
        ### given color, there's no need to update it,
        ### so we return early
        if self.current_widget.color == color:
            return

        ### otherwise set color on the widget
        self.current_widget.set_color(color)

    def get_colors(self):
        """Return tuple of colors represented by widgets."""
        return tuple(widget.color for widget in self.widgets)

    def get_current_color(self):
        """Return color of current widget."""
        return self.current_widget.color

    def shuffle_color_order(self):
        """Shuffle order of colors on widgets."""
        ### retrieve colors from widgets; colors
        ### must be inside a list so they can be
        ### shuffled
        colors = list(self.get_colors())

        ### shuffle them
        shuffle(colors)

        ### then set them back on each widget and update
        ### color values on controls for display/edition
        self.update_colors(colors)

    def reverse_color_order(self):
        """Reverse the order of color widgets."""
        ### get a reversed list out of the current colors
        colors = list(self.get_colors())[::-1]

        ### then set them back on each widget and update
        ### color values on controls for display/edition
        self.update_colors(colors)

    def sort_colors(self):
        """Sort color widgets' colors."""
        ### retrieve the names of color properties used
        ### to sort the colors
        ###
        ### the color properties used and their order as
        ### well as the available properties are listed
        ### in the properties sorting button

        property_names = self.colors_editor.color_sorting_holder.value

        ### if no property names are listed, we can't
        ### proceed, let the user know and return earlier

        if not property_names:

            create_and_show_dialog(
                "Can't sort colors because no properties are"
                " listed in the list sorting button with the"
                " property names (the one to the right of the"
                " 'Sort' button)"
            )

            return

        ### otherwise, obtain a new list with the colors
        ### sorted by the named properties

        sorter_function = get_color_sorter_by_properties(property_names)

        sorted_colors = sorted(self.get_colors(), key=sorter_function)

        ### then update the color of the widgets with such
        ### colors
        self.update_colors(sorted_colors)

    def remove_duplicated_colors(self):
        """Remove widgets so each color appears only once."""
        ### reference widget list locally, for quick and
        ### easier access
        widgets = self.widgets

        ### create two sets to keep track of colors we have
        ### already seen and widgets to be removed

        colors_already_seen = set()
        widgets_to_remove = set()

        ### iterate over color widgets, separating for
        ### removal those widgets whose colors have already
        ### been seen

        for widget in widgets:

            color_tuple = tuple(widget.color)

            if color_tuple in colors_already_seen:
                widgets_to_remove.add(widget)

            colors_already_seen.add(color_tuple)

        ### if there are widgets to be removed, try doing so

        if widgets_to_remove:
            self.remove_color_widgets(widgets_to_remove)

    def add_new_color_widget(self):
        """Create and add new color widget from current color.

        That is, the color of the current widget is used as
        a basis to generate a new one.
        """
        ### retrieve color of the current widget
        current_color = self.current_widget.color

        ### retrieve the name of a color property from
        ### the option menu

        property_ = self.colors_editor.color_add_option_menu.value

        ### obtain a new color from the current one by
        ### randomizing the property whose name we just
        ### retrieved
        new_color = random_color_from_existing(current_color, property_)

        ### instantiate and insert the new widget

        ## instantiate
        new_widget = Color2D(*COLOR_WIDGET_SIZE, new_color)

        ## insert the new widget after the current color
        ## widget

        self.widgets.insert(self.colors_editor.current_color_index + 1, new_widget)

        ### finally, perform setups needed when changing
        ### the number of existing widgets
        self.perform_widget_quantity_setups()

    def remove_color_widgets(self, widgets_to_remove=()):
        """Remove given color widgets (or the current one).

        Removal of widgets can only be done if the number
        to be remove won't leave the list of existing
        widgets empty, that is, there must always be at
        least one exiting color widget.

        Parameters
        ==========
        widgets_to_remove (iterable)
            contains references to the widgets to be removed;
            if empty, it is replaced by a list containing
            the current widget.
        """
        ### reference the existing color widgets locally
        ### for quicker and easier access
        widgets = self.widgets

        ### if the iterable with widgets to remove is empty,
        ### use a list with a reference to the current widget
        ### instead
        if not widgets_to_remove:
            widgets_to_remove = [self.current_widget]

        ### only advance if the removal of the widgets
        ### will leave at least one widget, otherwise you
        ### must leave the method early by returning
        if len(self.widgets) - len(widgets_to_remove) < 1:
            return

        ### since we didn't leave the method, then we assume
        ### it is ok to remove the given widgets, so we do
        ### so and performed extra tasks needed to keep
        ### the colors panel working suitably

        ## remove widgets
        for widget in widgets_to_remove:
            widgets.remove(widget)

        ### finally, perform setups needed when changing the
        ### number of existing widgets
        self.perform_widget_quantity_setups()

    def color_widget_to_visible_area(self):
        """Move widgets so current one is in visible area.

        The visible area is the scroll area, since all
        the widgets inside the scroll area (and not just
        touching it) are completely visible.

        We perform the movement if the current widget isn't
        already inside the visible area.
        """
        ### reference the rect of the current widget locally
        widget_rect = self.current_widget.rect

        ### obtain a copy of the current widget's rect
        ### clamped to the scroll area
        clamped_copy = widget_rect.clamp(self.scroll_area)

        ### if the original and clamped rects are the same,
        ### it means the current widget is already in the
        ### visible area, so we can return already
        if clamped_copy == widget_rect:
            return

        ### otherwise we obtain the difference between the
        ### positions of the clamped and original rects
        ### move all the widgets by that difference, so that
        ### the current widget ends up in the visible area

        offset = [a - b for a, b in zip(clamped_copy.topleft, widget_rect.topleft)]

        self.widgets.rect.move_ip(offset)

    def view_colors(self):
        """Display widgets' colors in the colors viewer."""
        ### unhighlight the colors editor
        self.colors_editor.unhighlight()

        ### call the colors viewer view_colors operation
        ### with the colors from the color widgets
        view_colors(self.get_colors())

    def pick_colors_from_collection(
        self,
        color_picking_operation,
    ):
        """Display specific colors for the user to pick.

        If the user picks one or more colors, a new color
        widget is created for each color and inserted into
        the list of existing ones.
        """
        ### unhighlight colors editor
        self.colors_editor.unhighlight()

        ### offer colors for user to pick by calling the
        ### corresponding color picker operation
        picked_colors = color_picking_operation()

        ### if no picked colors were received, we leave the
        ### method earlier by returning
        if not picked_colors:
            return

        ### otherwise we create new color widgets from the
        ### given colors, insert them and perform needed
        ### setups

        ## reference the insert operation of the list of
        ## existing widgets locally for quicker and easier
        ## access
        insert_widget = self.widgets.insert

        ## calculate the index after the current color
        ## widget
        ##
        ## we'll insert colors from that position
        index_wherein_to_insert = self.colors_editor.current_color_index + 1

        ## create and insert a color widget for each
        ## picked color in the index we defined,
        ## iterating the colors in reverse order, so they
        ## end up after the current widget in the original
        ## order (since the later ones are inserted before
        ## the first ones)

        for color in reversed(picked_colors):

            insert_widget(index_wherein_to_insert, Color2D(*COLOR_WIDGET_SIZE, color))

        ## finally, perform setups needed when changing
        ## the number of existing widgets
        self.perform_widget_quantity_setups()

    pick_html_colors = partialmethod(
        pick_colors_from_collection,
        pick_html_colors,
    )

    pick_pygame_colors = partialmethod(
        pick_colors_from_collection,
        pick_pygame_colors,
    )

    def free_up_memory(self):
        """Free memory by getting rid of widgets."""
        self.widgets.clear()
