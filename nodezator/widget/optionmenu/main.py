"""Facility for OptionMenu widget class definition."""

### standard library imports

from functools import partial
from itertools import combinations

from ast import literal_eval

from xml.etree.ElementTree import Element


### local imports

from ...pygameconstants import SCREEN_RECT

from ...ourstdlibs.behaviour import (
    empty_function,
    empty_oblivious_function,
)

from ...ourstdlibs.dictutils import settings_to_hashable_repr

from ...classes2d.single import Object2D
from ...classes2d.collections import List2D

from ...fontsman.constants import (
    ENC_SANS_BOLD_FONT_HEIGHT,
    ENC_SANS_BOLD_FONT_PATH,
)


from ...colorsman.colors import (
    OPTION_MENU_FG,
    OPTION_MENU_BG,
    OPTION_MENU_HOVERED_FG,
    OPTION_MENU_HOVERED_BG,
    OPTION_MENU_UNHOVERED_FG,
    OPTION_MENU_UNHOVERED_BG,
)

## creation operations and objects

from .creation import (
    STYLE_TO_ARROW_SURFS,
    get_arrow_surf,
    get_scroll_arrow_surfs,
    create_chosen_surfs,
    create_other_surfs,
)

## class extension
from .op import OptionMenuLifetimeOperations


### constants

## support function


def isliteral(value):

    try:
        literal_eval(repr(value))

    except Exception:
        return False

    return True


## nested dictionary that associates data in many
## different nesting levels;
##
## here's an example of its contents:
##
##
## {
##
##   ### in the top level of this dict, keys are frozensets
##   ### of the options converted to strings
##
##   frozenset({'option1', 'option2', 'option3'}) : {
##
##      ### the dict in this second level, uses tuples
##      ### with strings as keys, where each string
##      ### represents the value of a text setting;
##      ### the values are ordered by the name of
##      ### the setting they represent
##
##      (
##
##        'True',           # antialiased
##        '(38, 38, 38)',   # background_color
##        '17',             # font_height
##        ENC_SANS_BOLD_FONT_PATH,      # font_path
##        '(238, 238, 238)' # foreground_color
##
##      ) : {
##
##          ### the dict in the third level has strings
##          ### representing option names for keys, each
##          ### pointing to the respective text surface
##          ### as the value
##
##          'option1' : option1_surf,
##          'option2' : option2_surf,
##          'option3' : option3_surf
##
##      },
##
##      (
##
##        'True',            # antialiased
##        '(38, 38, 38)',    # background_color
##        '17',              # font_height
##        ENC_SANS_BOLD_FONT_PATH,       # font_path
##        '(238, 238, 238)', # foreground_color
##        '140'              # max width
##
##      ) : {
##
##          'option1' : option1_surf,
##          'option2' : option2_surf,
##          'option3' : option3_surf
##
##      }
##
##   }
##
## }
OPTIONS_TO_STYLE_DATA = {}


### class definition


class OptionMenu(OptionMenuLifetimeOperations):
    """Widget similar to a tkinter.OptionMenu.

    Used to select a value among a finite set of known
    values.
    """

    def __init__(
        self,
        value="",
        options=("",),
        loop_holder=None,
        clamp_area=SCREEN_RECT,
        max_width=155,
        font_path=ENC_SANS_BOLD_FONT_PATH,
        font_height=ENC_SANS_BOLD_FONT_HEIGHT,
        antialiased=True,
        foreground_color=OPTION_MENU_FG,
        background_color=OPTION_MENU_BG,
        hovered_foreground_color=OPTION_MENU_HOVERED_FG,
        hovered_background_color=OPTION_MENU_HOVERED_BG,
        unhovered_foreground_color=(OPTION_MENU_UNHOVERED_FG),
        unhovered_background_color=(OPTION_MENU_UNHOVERED_BG),
        draw_on_window_resize=empty_function,
        name="option_menu",
        coordinates_name="topleft",
        coordinates_value=(0, 0),
        command=empty_function,
    ):
        """Store data and perform setups.

        Parameters
        ==========

        value (any python literal)
            value assumed by the widget. Must be present
            in the 'options' argument.
        options (iterable of values)
            values the widget is allowed to assume. Each
            value in the options must be a python literal.
        loop_holder
        (obj with handle_input-update-draw operations)
            The loop holder regarded as the parent of
            the object.
        clamp_area (pygame.Rect instance)
            area to which the options will be clamped when
            they are expanded.
        width (integer)
            widget width in pixels.
        font_path (string)
            a key used to define which font file to used;
            for available keys, check the FONT_PATH_MAP
            dictionary in textman/font.py.
        font_height (integer)
            font height in pixels.
        antialiased (boolean)
            indicates whether the text should be antialiased
            or not.
        foreground_color (sequence of integers)
            the integers represent the values of red, blue
            and green channels respectively, with values
            from 0 to 255, all inclusive; the color is
            used for the text.
        background_color (sequence of integers)
            same as foreground color, but used for the
            background.
        hovered_foreground_color (sequence of integers)
            same as foreground color, but used for the
            foreground of hovered surfaces.
        hovered_background_color (sequence of integers)
            same as foreground color, but used for the
            background of hovered surfaces.
        unhovered_foreground_color (sequence of integers)
            same as foreground color, but used for the
            foreground of unhovered surfaces.
        unhovered_background_color (sequence of integers)
            same as foreground color, but used for the
            background of unhovered surfaces.
        name (string)
            an optional arbitrary string which is stored
            in the 'name' attribute of the instance;
            may be used to help identify the widget.
        coordinates_name (string)
            attribute name of pygame.Rect wherein to set the
            position information from the coordinates value
            parameter.
        coordinates_value (2-tuple of integers)
            represents a position in 2d space; the values of
            x and y axes, respectively.
        command (callable)
            callable executed whenever an option is selected.
        """
        ### make sure options is a list
        options = list(options)

        ### validate value and options
        self.validate_value_and_options(value, options)

        ### store value and options

        self.value = value
        self.options = options
        self.clamp_area = clamp_area

        ### store other attributes

        self.command = command
        self.loop_holder = loop_holder
        self.name = name

        self.draw_on_window_resize = draw_on_window_resize

        ### define a max width taking the given width and
        ### arrow's width into account

        ## obtain the arrow's width

        arrow_width = get_arrow_surf(foreground_color, font_height).get_width()

        ## calculate the max text width

        max_text_width = max_width if not max_width else max_width - arrow_width

        ### gather text style data for each kind of text
        ### surfaces to be created;
        ###
        ### note that the "chosen text settings",
        ### different than the "hovered text settings",
        ### has the max width specified; this will cause
        ### both text settings to never override each
        ### other within the second nesting level of the
        ### OPTIONS_TO_STYLE_DATA dictionary;
        ###
        ### this is important, because even in cases where
        ### the "hovered" settings and the "chosen"
        ### settings are practically equal (when the max
        ### width is 0), they are subject to different
        ### treatments;
        ###
        ### for instance, chosen surfaces have an arrow
        ### blitted at their right end and have a border
        ### drawn around them;
        ###
        ### in other words, there must always be something
        ### to differentiate them, and the max width
        ### value is does the trick;

        self.chosen_text_settings = {
            "font_path": font_path,
            "font_height": font_height,
            "antialiased": antialiased,
            "max_width": max_text_width,
            "foreground_color": foreground_color,
            "background_color": background_color,
        }

        self.hovered_text_settings = {
            "font_path": font_path,
            "font_height": font_height,
            "antialiased": antialiased,
            "foreground_color": hovered_foreground_color,
            "background_color": hovered_background_color,
        }

        self.unhovered_text_settings = {
            "font_path": font_path,
            "font_height": font_height,
            "antialiased": antialiased,
            "foreground_color": unhovered_foreground_color,
            "background_color": unhovered_background_color,
        }

        ### build widgets that form the OptionMenu instance
        self.build_widget_structure()

        ### position rect

        setattr(self.rect, coordinates_name, coordinates_value)

        ### define behaviours for used protocols

        ## loop holder update operation
        self.update = empty_function

        ## method for mouse interaction protocol
        self.on_mouse_release = self.get_focus

        ## drawing behaviour
        self.draw = self.draw_collapsed

        ## input handling
        self.handle_input = self.handle_events_and_mouse_pos

    def validate_value_and_options(self, value, options):
        """Check whether value and options are valid.

        Parameters
        ==========
        value, options
            same as defined in __init__() method.
        """
        ### raise an error immediately if the value isn't
        ### within the possible values

        if value not in options:
            raise ValueError("'value' must be listed in 'options'")

        ### raise type error if values aren't python
        ### literals

        if any(not isliteral(item) for item in options):

            raise TypeError("each item in 'options' must be a" " python literal")

        ### raise value error if any value is the same/equal
        ### as any other existing value

        if any(a is b or a == b for a, b in combinations(options, 2)):

            raise ValueError(
                "'options' can't have items which are"
                " identical or equal to one another"
            )

    def build_widget_structure(self):
        """Build widgets for the OptionMenu."""
        ### create a frozenset from the options with
        ### each item converted into a string
        options_fset = frozenset(map(str, self.options))

        ### using the frozenset, try retrieving a dict
        ### which associates text styles (settings) to
        ### data about options

        try:
            styles_to_option_data = OPTIONS_TO_STYLE_DATA[options_fset]

        ### if such dict doesn't exist, create and store
        ### a new one, also referencing it locally

        except KeyError:

            styles_to_option_data = OPTIONS_TO_STYLE_DATA[options_fset] = {}

        ### obtain dictionaries which associate the option
        ### as strings to their respective text surface,
        ### storing the dictionaries inside a new one,
        ### which uses strings representing the roles of
        ### the surfaces as keys

        ## create dictionary to store the other ones
        role_to_maps = {}

        ## iterate over given data below

        for role_name, text_settings, creation_op in (
            ("chosen", self.chosen_text_settings, create_chosen_surfs),
            ("hovered", self.hovered_text_settings, create_other_surfs),
            ("unhovered", self.unhovered_text_settings, create_other_surfs),
        ):

            ## obtain a key from the given text settings

            key_chosen_style = settings_to_hashable_repr(text_settings)

            ## try retrieving the dictionary associating
            ## options converted to strings to their
            ## respective surfaces

            try:

                option_name_to_surf = styles_to_option_data[key_chosen_style]

            ## if such dictionary doesn't exist, create
            ## and store it, also referencing it locally

            except KeyError:

                option_name_to_surf = styles_to_option_data[
                    key_chosen_style
                ] = creation_op(self.options, text_settings)

            ## then store such dictionary in the other one
            ## we create specifically to store maps,
            ## using the role name as the key
            role_to_maps[role_name] = option_name_to_surf

        ### instantiate widgets;
        ###
        ### now that we have all the dictionaries with
        ### all the surfaces we need, we instantiate
        ### the option widgets inside a custom list
        ### class

        self.option_widgets = List2D(
            build_option_widget(
                option,  # option
                role_to_maps,  # surface maps
                self.set,  # method to set new value
            )
            for option in self.options
        )

        ### align the option widgets one on top of the
        ### other

        self.option_widgets.rect.snap_rects_ip("bottomleft", "topleft")

        ### get image surf
        self.update_image()

        ### also create a rect from it
        self.rect = self.image.get_rect()

        ### then perform additional creation/setup based
        ### on whether the option widgets are taller than
        ### the clamp area

        ### TODO finish implementing behaviours referenced
        ### below (in the 'op.py' sibling module); also
        ### create other dependencies as needed in order to
        ### make the options to scroll

        if self.option_widgets.rect.height > self.clamp_area.height:
            (self.upper_scroll_arrow, self.lower_scroll_arrow) = get_scroll_arrow_surfs(
                self.option_widgets.rect.width,
                (self.unhovered_text_settings["foreground_color"]),
                (self.unhovered_text_settings["background_color"]),
            )

            self.align_subobjects = self.align_options_and_scroll_arrows
            self.draw_subobjects = self.draw_options_and_scroll_arrows
            self.handle_mouse_pos = self.scroll_when_hovering_scroll_arrow

            self.on_mousewheel = self.scroll_with_mousewheel

        else:

            self.align_subobjects = self.align_options
            self.draw_subobjects = self.draw_options
            self.handle_mouse_pos = empty_oblivious_function
            self.on_mousewheel = empty_oblivious_function

    def get_expected_type(self):

        classes = set(map(type, self.options))

        return classes.pop() if len(classes) == 1 else tuple(classes)

    def svg_repr(self):

        g = Element("g", {"class": "option_menu"})

        g.append(super().svg_repr())

        path_rect = self.rect.inflate(-2, -2)
        path_rect.width = 12
        path_rect.bottomright = self.rect.inflate(-2, -2).bottomright

        path_rect.inflate_ip(-3, -3)
        path_rect.move_ip(0, -2)

        points = (
            path_rect.midleft,
            path_rect.midright,
            path_rect.midbottom,
        )

        path_directives = "M"
        for x, y in points:
            path_directives += f"{x} {y} L"
        path_directives = path_directives[:-1] + " Z"

        g.append(Element("path", {"d": path_directives}))

        (
            text_x_str,
            text_y_str,
        ) = map(str, self.rect.move(1, -4).bottomleft)

        text_element = Element(
            "text",
            {
                "x": text_x_str,
                "y": text_y_str,
                "text-anchor": "start",
            },
        )

        text_element.text = str(self.value)

        g.append(text_element)

        return g

    @staticmethod
    def free_up_memory():
        """Free unused memory by clearing up unused objects.

        Used just before loading a new file, so data
        accumulated from the edition of the previous file
        (if there was one) isn't kept around now that
        another file is being loaded.

        The previous file edited might be the one being
        loaded (that is, the file is reloaded). However,
        even if it is the case, this measure should still
        save memory, since data/objects present in
        the past session may not be needed anymore in
        the new session.
        """
        ### clear dictionary used to store surfaces and
        ### other data across multiple nested levels
        OPTIONS_TO_STYLE_DATA.clear()

        ### clear dictionary used to map text setting data
        ### to arrow surfaces
        STYLE_TO_ARROW_SURFS.clear()


### utility function


def build_option_widget(option, role_to_maps, set_method):
    """Build a option widget from given arguments.

    Parameters
    ==========
    option (string, integer, float, bool or None)
        the value of one of the options available to the
        user.
    role_to_maps (dict)
        its keys are strings representing roles of surfaces
        and its values are other dictionaries; this other
        dictionaries contain strings representing option
        text as keys and the values are the respective
        text surfaces for those strings.
    set_method (callable)
        set() method of the option menu instance; used to
        set the option as the new value of the option menu
        instance when the user clicks the option widget
        (actually, when the mouse is released over it).
    """
    ### instantiate object
    obj = Object2D()

    ### reference surfaces locally according to their
    ### roles/purposes and the text of the option

    option_text = str(option)

    chosen_surf = role_to_maps["chosen"][option_text]
    hovered_surf = role_to_maps["hovered"][option_text]
    unhovered_surf = role_to_maps["unhovered"][option_text]

    ### define surface switching behaviours

    obj.unhighlight = partial(setattr, obj, "image", unhovered_surf)

    obj.highlight = partial(setattr, obj, "image", hovered_surf)

    ### define image and rect attributes for the object

    obj.image = unhovered_surf
    obj.rect = unhovered_surf.get_rect()

    ### reference the chosen_surf in the instance attribute
    ### of the obj using the same name as the variable
    obj.chosen_surf = chosen_surf

    ### store a partial on the 'select' attribute of the
    ### widget that causes it to be selected
    obj.select = partial(set_method, option)

    ### define function complying with the mouse interaction
    ### protocol making it so it executes the command

    def on_mouse_release(event):
        """Set option as the new value of the option menu.

        Parameters
        ==========

        event
            pygame.event.Event of pygame.MOUSEBUTTONUP type;

            although not used, it is required in order to
            comply with protocol used;

            check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        set_method(option)

    ### assign the function we just defined to the obj
    ### attribute with the same name
    obj.on_mouse_release = on_mouse_release

    ### store the option in the 'value' attribute of the obj
    obj.value = option

    ### finally return the obj
    return obj
