"""Option tray class extension with creation operations."""

### standard library imports

from itertools import accumulate

from collections import OrderedDict


### third-party import
from pygame.draw import line as draw_line


### local imports

from ...surfsman.draw import blit_aligned, draw_border
from ...surfsman.render import render_rect

from ...classes2d.single import Object2D
from ...classes2d.collections import Iterable2D

from ...textman.render import render_text

from ...colorsman.colors import OPTION_TRAY_OPTION_SEPARATOR


### class definition


class OptionTrayCreationOperations:
    """Operations to create OptionTray assets."""

    def create_surface_map(self):
        """Return dict w/ surfaces for the widget."""
        ### create ordered dictionaries containing text objs
        ### representing each possible option in both normal
        ### and selected state

        normal_obj_dict = OrderedDict(
            (value, get_option_obj(str(value), self.normal_text_settings))
            for value in self.options
        )

        selected_obj_dict = OrderedDict(
            (value, get_option_obj(str(value), self.selected_text_settings))
            for value in self.options
        )

        ### position the text objects in both dictionaries
        ### side by side and set its topleft to the origin

        for a_dict in (normal_obj_dict, selected_obj_dict):

            objs_rectsman = Iterable2D(a_dict.values().__iter__).rect

            objs_rectsman.snap_rects_ip(
                retrieve_pos_from="bottomright", assign_pos_to="bottomleft"
            )

            objs_rectsman.topleft = (0, 0)

        ### using the last rectsman created (we can use
        ### the rectsman for any of the dicts, since we
        ### are interested only in the size here, not the
        ### appearance) create a base surface to surround
        ### all text objects representing the options

        bg_color = self.normal_text_settings["background_color"]

        base_surf = render_rect(*objs_rectsman.size, bg_color)

        ### now, for each option, blit over a copy of the
        ### base surface all the options, with the selected
        ### option using the "selected" appearance while all
        ### the others use the "normal" appearance, saving
        ### each resulting surface in the surface map with
        ### the selected option as the key

        ## create the surface map
        surface_map = {}

        ## iterate over each option, considering the
        ## one being iterated as the selected one

        for selected_option in self.options:

            ## create copy of base surface
            base_copy = base_surf.copy()

            ## iterate over each option, blitting the
            ## respective surface in the appropriate
            ## state

            for option in self.options:

                ## obtain a text object with a
                ## surface for that option;
                ##
                ## note that we choose the dict based on
                ## whether the option is the selected one
                ## or not, so that we use the selected
                ## surface for the selected option and the
                ## normal surface for the options that are
                ## not selected

                text_obj = (
                    selected_obj_dict if option == selected_option else normal_obj_dict
                )[option]

                ## reference the text object's rect locally
                text_obj_rect = text_obj.rect

                ## blit the surface from the text object in
                ## the copy of the base surface, according
                ## to the position of the object's rect

                base_copy.blit(text_obj.image, text_obj_rect)

                ## blit a line at the left side of the
                ## text obj rect, to make it easier to
                ## perceive different options from each
                ## other

                draw_line(
                    base_copy,
                    OPTION_TRAY_OPTION_SEPARATOR,
                    text_obj_rect.topleft,
                    text_obj_rect.bottomleft,
                    1,
                )

            ## finally draw a black border around the base
            ## surface's copy and store it in the map

            draw_border(base_copy)

            surface_map[selected_option] = base_copy

        ### return the surface map
        return surface_map

    def create_right_coordinates(self):
        """Return tuple w/ right_coordinates."""
        ### since the right coordinate of each option
        ### equals its width, we just needed to create
        ### a tuple where each item is the width of an
        ### option plus the width of the previous options;
        ###
        ### we can do so by accumulating the values as
        ### they are given, using itertools.accumulate();
        ###
        ### we use the normal text settings here, but the
        ### selected text settings could be used as well,
        ### since we are only interested in the width of
        ### the objects, not their appearance

        return tuple(
            accumulate(
                ## create object representing an option
                ## and grab the width from its rect...
                get_option_obj(str(value), self.normal_text_settings).rect.width
                ## ...for each of the existing options
                for value in self.options
            )
        )


### utility function


def get_option_obj(text, text_settings):
    """Create and return custom text object.

    Parameters
    ==========
    text (string)
        text to be rendered.
    text_settings (dict)
        contains settings used to define how text should
        be rendered.
    """
    ### render the text according to the given settings
    surf = render_text(text, **text_settings)

    ### retrieve its width and height
    width, height = surf.get_size()

    ### create a new surface 6 pixels wider than the
    ### original one, with the same height; 6 is just
    ### an arbitrary value based on what looks good

    new_surf = render_rect(width + 6, height, text_settings["background_color"])

    ### blit the original surface over the new one,
    ### with their center coordinates aligned

    blit_aligned(
        surf,
        new_surf,
        retrieve_pos_from="center",
        assign_pos_to="center",
    )

    ### finally return an object containing the new surface
    ### as its 'image' attribute and a rect obtained from
    ### the surface as the 'rect' attribute

    return Object2D(image=new_surf, rect=new_surf.get_rect())
