"""Class extension w/ colors editor widget operations."""

### standard library import
from functools import partialmethod


### local imports

from ...ourstdlibs.color.largemaps import (
    HTML_COLOR_MAP,
    PYGAME_COLOR_MAP,
)

from ...ourstdlibs.color.conversion import (
    COLOR_CONVERSION_MAP,
    hex_string_to_full_rgb,
    full_rgb_to_html_name,
    full_rgb_to_pygame_name,
    full_rgb_to_hex_string,
)


class WidgetOperations:
    """Operations related to ColorsEditor's widgets."""

    def set_color_on_controls(self, color):
        """Set current color to given one."""
        ### reference the rgb entries
        entries = self.entry_map["rgb"]

        ### check whether an alpha value was provided
        try:
            color[3]

        ### if it was not, set an 'include_alpha'
        ### variable to False
        except IndexError:
            include_alpha = False

        ### otherwise, update the entry references to
        ### include the alpha entry and set an
        ### 'include_alpha' variable to True

        else:

            include_alpha = True
            entries = entries + [self.entry_map["alpha"]]

        ### set each entry with its respective value

        for entry, value in zip(entries, color):
            entry.set(value, False)

        ### set alpha checkbutton to value on the
        ### 'include_alpha' variable
        self.alpha_checkbutton.set(include_alpha, False)

        ### set alpha scale according to absence/presence
        ### of an alpha value

        ## retrieve/define the alpha value
        alpha_value = value if include_alpha else 255

        ## set the scale widget to the converted alpha value
        self.scale_map["alpha"].set(alpha_value, False)

        ### finally update the resulting color value
        ### and perform additional tasks
        self.update_from_rgb_entry()

    def update_from_scale(self, group_name, update_group_entry=True):
        """Update color value from scales and store it.

        This method grabs the color values from an specific
        scale group (from a color space) and uses it to
        update the other scales, the entries and also to
        store the rgb color.

        Parameters
        ==========

        group_name (string)
            used as key to retrieve the group of scales
            from which to update the other scales;
            represents a color model/space name.
        update_group_entry (bool)
            if True, the entries which are referenced by
            the same key as group_name will be updated too.
        """
        ### retrieve values and names from widgets in group

        retrieved_values, retrieved_names = [], []

        for scale in self.scale_map[group_name]:

            retrieved_values.append(scale.get())
            retrieved_names.append(scale.name)

        ### if requested, update corresponding entry group

        if update_group_entry:

            for entry, value in zip(self.entry_map[group_name], retrieved_values):

                entry.set(value, False)

        ### update remaining scale and entry groups

        for key, conversion_operation in COLOR_CONVERSION_MAP[group_name].items():

            ## convert retrieved values
            converted_values = conversion_operation(retrieved_values)

            ## update widget groups

            # note that only widgets which don't belong
            # in the group used to retrieve values are
            # updated (we check if the names are present
            # in the retrieved_names list)

            for scale, entry, value in zip(
                self.scale_map[key], self.entry_map[key], converted_values
            ):

                # if the scale name isn't among the ones
                # from which we retrieve the values, we
                # update its value;
                #
                # there's no need to check the entry's
                # name, cause the scale and entry have
                # the same name

                if scale.name not in retrieved_names:

                    scale.set(value, False)
                    entry.set(value, False)

        ### update the hex and name entries

        ## get color as a tuple of rgb values

        rgb_color = tuple(entry.get() for entry in self.entry_map["rgb"])

        if self.alpha_checkbutton.get():
            rgb_color += (self.entry_map["alpha"].get(),)

        ## update hex entry

        hex_string = full_rgb_to_hex_string(rgb_color)
        self.hex_entry.set(hex_string, False)

        ## update name entries

        html_name = full_rgb_to_html_name(rgb_color)
        pygame_name = full_rgb_to_pygame_name(rgb_color)

        self.html_name_entry.set(html_name, False)
        self.pygame_name_entry.set(pygame_name, False)

        ### finally update the resulting color value
        ### and perform additional tasks
        self.update_color_value()

    update_from_hls = partialmethod(update_from_scale, "hls")
    update_from_hsv = partialmethod(update_from_scale, "hsv")
    update_from_rgb = partialmethod(update_from_scale, "rgb")

    def update_from_entry(self, group_name):
        """Update color value from entry group.

        This method grabs the color values from an specific
        entry group (from a color space) and then uses them
        to update the corresponding scales, then triggers
        to self.update_from_scale method which in turn
        updates the rest of the widgets and stores the rgb
        color values.

        group_name
            String use as key to retrieve the entries from
            which to grab and convert the color values.
            It represents a color space name.
        """
        ### iterate over corresponding scale group updating
        ### each scale with value of respective entry

        for scale, entry in zip(self.scale_map[group_name], self.entry_map[group_name]):
            scale.set(entry.get(), False)

        ### then update remaining scales and entries
        ### by delegating to update_from_scale() method;
        ###
        ### this also has the desired side effect of
        ### updating the color unit surface
        self.update_from_scale(group_name, False)

    update_from_hls_entry = partialmethod(update_from_entry, "hls")

    update_from_hsv_entry = partialmethod(update_from_entry, "hsv")

    update_from_rgb_entry = partialmethod(update_from_entry, "rgb")

    def update_from_hex_entry(self):
        """Update color value from hex entry."""
        ### get value from hex entry
        hex_string = self.hex_entry.get()

        ### convert to list of RGB(A) integers so that
        ### each value is so that 0 <= value <= 255
        color = hex_string_to_full_rgb(hex_string)

        ### finally, set the color on the controls
        self.set_color_on_controls(color)

    def update_from_name_entry(
        self,
        entry_attr_name,
        color_map,
    ):
        """Update color value from name entry.

        Or, if the name in the entry is 'unamed', set
        back the actual name of the color, if it has one.
        """
        ### reference entry locally
        entry = getattr(self, entry_attr_name)

        ### get name from entry
        color_name = entry.get()

        ### if color name is 'unamed', we return earlier,
        ### since it doesn't point to any known color;
        ###
        ### however, before doing so, we also check whether
        ### the current color actually has a name, in which
        ### case we change the name in the entry to that
        ### name, since it wouldn't be right to leave
        ### 'unamed' in the entry when the current color
        ### actually has a name

        if color_name == "unamed":

            ## obtain a tuple with the 3 first values of
            ## the current color

            current_color = tuple(self.colors_panel.get_current_color()[:3])

            ## iterate over each item of the color map

            for name, color in color_map.items():

                ## if the current color has the same value
                ## as one of the color from the map, then
                ## the color actually has a name, which is
                ## the one store in the 'name' variable,
                ## so set such name as the text of the
                ## entry and break out of the "for loop"

                if current_color == color:

                    ## we use False as the second argument
                    ## so the change doesn't unnecessarily
                    ## triggers the update command of the
                    ## entry
                    entry.set(name, False)

                    break

            ## finally return
            return

        ### otherwise, retrieve the color from the
        ### corresponding map using the color name as the
        ### key, converting it to a new list
        color = list(color_map[color_name])

        ### if the alpha is supposed to be used, retrieve
        ### it from the entry and append it to the color
        if self.alpha_checkbutton.get():
            color.append(self.entry_map["alpha"].get())

        ### finally, set the color on the controls
        self.set_color_on_controls(color)

    update_from_html_name_entry = partialmethod(
        update_from_name_entry,
        "html_name_entry",
        HTML_COLOR_MAP,
    )

    update_from_pygame_name_entry = partialmethod(
        update_from_name_entry,
        "pygame_name_entry",
        PYGAME_COLOR_MAP,
    )

    def update_from_alpha(self):
        """Update the alpha value for entry and attribute."""

        ### update entry with scale value

        ## get alpha value from scale
        alpha_value = self.scale_map["alpha"].get()

        ## update the alpha entry with the alpha value we
        ## just retrieved
        self.entry_map["alpha"].set(alpha_value, False)

        ### set the alpha checkbutton to True (that is,
        ### since the user is editing the alpha, we assume
        ### it wants the alpha to be used; this also makes
        ### it so the alpha is updated in the preview rect
        ### in real time, which is useful)

        self.alpha_checkbutton.set(True, execute_command=False)

        ### finally update the color value from the
        ### rgb entry (also has side-effects of interest)
        self.update_from_rgb_entry()

    def update_from_alpha_entry(self):
        """Update alpha scale value from entry."""
        ### update scale with the alpha value from
        ### entry

        alpha = self.entry_map["alpha"].get()
        self.scale_map["alpha"].set(alpha, False)

        ### then update the color using the value on
        ### the scale
        self.update_from_alpha()

    def update_color_value(self):
        """Update RGB(A) color value and perform setups.

        Also:
            - checks whether to include alpha;
            - updates the color in current color widget
              from the colors panel;
        """
        ### store the rgb color

        color = tuple(scale.get() for scale in self.scale_map["rgb"])

        ### include alpha value in the stored color if
        ### the alpha checkbutton is checked

        if self.alpha_checkbutton.get():
            color += (self.scale_map["alpha"].get(),)

        ### set color in current color widget from the
        ### colors panel
        self.colors_panel.set_current_color(color)
