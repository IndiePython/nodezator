"""Facility for visuals related node class extension."""

# XXX module's docstring isn't accurate

### standard library import
from functools import partial


### local imports

from ....config import APP_REFS

from ....classes2d.single import Object2D

from ...widget.utils import WIDGET_CLASS_MAP

from ...socket.surfs import type_to_codename

from ..utils import update_with_widget

## classes for composition

from ....our3rdlibs.button import Button

from ...socket.input import InputSocket
from ...socket.placeholder import PlaceholderSocket

from ....widget.stringentry import StringEntry

from ....rectsman.main import RectsManager

from ..surfs import (
    ADD_BUTTON_SURF,
    REMOVE_BUTTON_SURF,
    SUBP_UP_BUTTON_SURF,
    SUBP_DOWN_BUTTON_SURF,
    UNPACKING_ICON_SURFS_MAP,
)

from ..constants import FONT_HEIGHT


def create_var_parameter_objs(self, param_obj):
    """Create socket(s) and widget(s) for the parameter.

    The parameter in question must not be of non-variable
    kind.

    This function is meant to extend the
    VisualRelatedPreparations class as one of its methods.

    Parameters
    ==========
    param_obj (inspect.Parameter instance)
        an object representing a parameter from a callable,
        containing related data.
    """
    ### retrieve the name of the parameter
    param_name = param_obj.name

    ### create list to gather rects of objects in this
    ### parameter to use in a RectsManager instance
    rectsman_rects = []

    ### since we'll use their information, let's
    ### retrieve subparameter-related maps

    subparam_map = self.data["subparam_map"]

    subparam_widget_map = self.data["subparam_widget_map"]

    subparam_unpacking_map = self.data["subparam_unpacking_map"]

    ### let's also alias live instances maps using
    ### variables of low character count, for better
    ### code layout

    isl_flmap = self.input_socket_live_flmap
    sub_flmap = self.subparam_up_button_flmap
    sdb_flmap = self.subparam_down_button_flmap
    wl_flmap = self.widget_live_flmap
    sui_flmap = self.subparam_unpacking_icon_flmap
    skl_map = self.subparam_keyword_entry_live_map
    wab_flmap = self.widget_add_button_flmap
    wrb_flmap = self.widget_remove_button_flmap
    srm_map = self.subparam_rectsman_map
    pab_map = self.placeholder_add_button_map
    psl_map = self.placeholder_socket_live_map

    ### create dicts to store instances of objects
    ### related to subparameters, using the parameter
    ### name as key

    isl_flmap[param_name] = {}
    sub_flmap[param_name] = {}
    sdb_flmap[param_name] = {}
    wl_flmap[param_name] = {}
    sui_flmap[param_name] = {}
    wab_flmap[param_name] = {}
    wrb_flmap[param_name] = {}
    srm_map[param_name] = {}

    ### retrieve the subparameter indices list,
    ### creating it in case it doesn't previously
    ### exist
    subparams = subparam_map.setdefault(param_name, [])

    ### retrieve the subparameter widget data for the
    ### current parameter, creating it in case it
    ### doesn't exist
    subwidgets_data = subparam_widget_map.setdefault(param_name, {})

    ### retrieve the list of subparameters to be unpacked
    ### when the graph is executed, creating such list in
    ### case it doesn't exist
    subparams_for_unpacking = subparam_unpacking_map.setdefault(param_name, [])

    ### instantiate socket for each subparameter if
    ### there's any subparameter (also instantiate
    ### related widgets if any)

    ## define specific kind of this variable parameter
    kind = self.var_kind_map[param_name]

    ### also retrieve the expected type of the
    ### parameter and use it to obtain a string
    ### representing a codename for the type;
    ###
    ### no type enforcement is ever performed,
    ### though

    expected_type = self.type_map[param_name]
    type_codename = type_to_codename(expected_type)

    ## define an initial center coordinate; it will be
    ## used by the first subparameter, if it exists
    center = self.top_rectsman.left, 0

    ## iterate over each subparameter listed on the
    ## subparameter sockets' data (if there's any)
    ## using the keys to sort the iteration order;
    ##
    ## in each iteration, we create the input socket,
    ## buttons and widget related to the subparameter
    ## (also a keyword entry if applicable);

    for subparam_index in sorted(subparams):

        ## create list to gather rects of objects in
        ## this subparameter to use in a RectsManager
        ## instance
        subrectsman_rects = []

        ## instantiate socket

        input_socket = InputSocket(
            node=self,
            type_codename=type_codename,
            parameter_name=param_name,
            subparameter_index=subparam_index,
            center=center,
        )

        ## store the input socket instance in
        ## the live instance map for input sockets

        (isl_flmap[param_name][subparam_index]) = input_socket

        # this dict subclass instance must be updated
        # every time it is changed
        isl_flmap.update()

        ## store reference to input socket's rect
        subrectsman_rects.append(input_socket.rect)

        ## instantiate subparam moving buttons

        bottomleft = input_socket.rect.move(2, 0).midright

        move_subparam_up = partial(self.move_subparam_up, input_socket)

        subp_up_button = Button(
            surface=SUBP_UP_BUTTON_SURF,
            command=move_subparam_up,
            coordinates_name="bottomleft",
            coordinates_value=bottomleft,
        )

        (sub_flmap[param_name][subparam_index]) = subp_up_button

        # this dict subclass instance must be updated
        # every time it is changed
        sub_flmap.update()

        # store reference to button's rect
        subrectsman_rects.append(subp_up_button.rect)

        topleft = bottomleft

        move_subparam_down = partial(self.move_subparam_down, input_socket)

        subp_down_button = Button(
            surface=SUBP_DOWN_BUTTON_SURF,
            command=move_subparam_down,
            coordinates_name="topleft",
            coordinates_value=topleft,
        )

        (sdb_flmap[param_name][subparam_index]) = subp_down_button

        # this dict subclass instance must be updated
        # every time it is changed
        sdb_flmap.update()

        # store reference to button's rect
        subrectsman_rects.append(subp_down_button.rect)

        ## check if subparameter has a content widget
        ## (by checking whether the respective data is
        ## present)

        try:
            widget_data = subwidgets_data[subparam_index]

        ## if the data isn't present (KeyError is
        ## raised), then create an "add button"
        ## so the user can add a widget if desired

        except KeyError:

            midleft = input_socket.rect.move(15, 0).midright

            command = partial(
                (APP_REFS.ea.widget_creation_popup_menu.trigger_simple_widget_picking),
                self,
                param_name,
                input_socket,
            )

            button = Button(
                surface=ADD_BUTTON_SURF,
                command=command,
                coordinates_name="midleft",
                coordinates_value=midleft,
            )

            wab_flmap[param_name][subparam_index] = button

            # this dict subclass need to be updated
            # whenever it is changed
            wab_flmap.update()

            # store reference to button's rect
            subrectsman_rects.append(button.rect)

        ## otherwise instantiate widget and also a
        ## 'remove widget' button in case the user
        ## decides to remove the widget and take any
        ## additional needed measures

        else:

            ## retrieve widget class using the widget
            ## name from the widget data

            widget_name = widget_data["widget_name"]
            widget_cls = WIDGET_CLASS_MAP[widget_name]

            ## retrieve keyword arguments to use when
            ## instantiating the widget
            kwargs = widget_data["widget_kwargs"]

            ## put together position data for the widget
            ## (widget topleft is positioned relative to the
            ## input socket topright)

            topleft_pos = input_socket.rect.move(15, -1).topright

            pos_data = {"coordinates_name": "topleft", "coordinates_value": topleft_pos}

            ## instantiate the widget using the keyword
            ## arguments as well as the position data;

            widget = widget_cls(name=param_name, **kwargs, **pos_data)

            ## store the widget instance in the live
            ## map and set for widgets
            (wl_flmap[param_name][subparam_index]) = widget

            # this dict subclass instance must be
            # updated whenever it is changed
            wl_flmap.update()

            ## store reference to widget's rect
            subrectsman_rects.append(widget.rect)

            ### create "remove widget" button

            ## define midleft coordinates for the button

            x = widget.rect.right

            midleft = x, input_socket.rect.centery

            ## define command

            command = partial(self.remove_subparameter_widget, widget)

            ## instantiate and store

            button = Button(
                surface=REMOVE_BUTTON_SURF,
                command=command,
                coordinates_name="midleft",
                coordinates_value=midleft,
            )

            wrb_flmap[param_name][subparam_index] = button

            # this dict subclass needs to be update
            # whenever it is changed
            wrb_flmap.update()

            ## store reference to remove button's rect
            subrectsman_rects.append(button.rect)

            ### also define a command to update the
            ### widget value in the node data and
            ### the position of the remove button
            ### (because the widget may change its width
            ### when edited, depending on the kind of
            ### widget), then assign such command to the
            ### 'command' attribute of the widget

            command = partial(update_with_widget, kwargs, "value", widget, button)

            widget.command = command

        ## at this point we already need the
        ## rects manager for this subparameter,
        ## even though we might yet need to add other
        ## objects in following steps;
        ##
        ## instantiate and store a RectsManager
        ## for the gathered rects in this subparameter

        subrectsman = RectsManager(subrectsman_rects.__iter__)

        srm_map[param_name][subparam_index] = subrectsman

        ### store reference to the subrectsman, so it is
        ### part of the rectsman instance controlling the
        ### entire parameter
        rectsman_rects.append(subrectsman)

        ## if the subparameter is marked to be unpacked,
        ## add an unpacking icon to it

        if subparam_index in subparams_for_unpacking:

            # put together a bottomleft coordinate for the
            # unpacking icon;
            #
            # for the bottom use the top of the subrectsman
            # (3 pixels higher, by subtracting the amount)

            bottomleft = (input_socket.rect.right + 15, subrectsman.top - 3)

            icon_surf = UNPACKING_ICON_SURFS_MAP[
                (
                    kind,
                    self.data.get("commented_out", False),
                )
            ]

            unpacking_icon = Object2D.from_surface(
                surface=icon_surf,
                coordinates_name="bottomleft",
                coordinates_value=bottomleft,
            )

            # store the subparam keyword entry
            sui_flmap[param_name][subparam_index] = unpacking_icon

            # this dict subclass instance must be updated
            # every time it is changed
            sui_flmap.update()

            # store reference to unpacking icon's rect
            subrectsman_rects.append(unpacking_icon.rect)

        ## if otherwise, the parameter is of
        ## keyword-variable kind, we need to instantiate
        ## a keyword entry widget for the subparameter

        elif kind == "var_key":

            # put together a bottomleft coordinate for the
            # keyword entry widget;
            #
            # for the bottom use the top of the subrectsman
            # (3 pixels higher, by subtracting the amount)

            bottomleft = (input_socket.rect.right + 15, subrectsman.top - 3)

            keyword_name = self.data["subparam_keyword_map"][subparam_index]

            command = partial(self.update_keyword, input_socket)

            subparam_keyword_entry = StringEntry(
                value=keyword_name,
                font_height=FONT_HEIGHT,
                width=155,
                command=command,
                coordinates_name="bottomleft",
                coordinates_value=bottomleft,
            )

            # store the subparam keyword entry
            skl_map[subparam_index] = subparam_keyword_entry

            # store reference to keyword entry's rect
            subrectsman_rects.append(subparam_keyword_entry.rect)

        ### assign a new center to be used by
        ### the next subparameter;
        ###
        ### if there isn't one, the placeholder socket
        ### defined after this loop uses such center
        center = self.top_rectsman.left, 0

    ### instantiate a placeholder socket
    ### (a socket which generates a new subparameter
    ### when an inlink is stablished with it)

    ## instantiate socket (notice we used the "center"
    ## variable defined either in the end of the
    ## previous "for" loop or before it)

    placeholder_socket = PlaceholderSocket(self, param_name, center)

    ## store the placeholder socket instance in the
    ## live instance map for placeholder sockets
    psl_map[param_name] = placeholder_socket

    ### store reference to placeholder socket rect
    rectsman_rects.append(placeholder_socket.rect)

    ### now, add a button to create new sockets
    ### by instantiating widgets to provide input

    midleft = placeholder_socket.rect.move(5, 0).midright

    command = partial(
        (APP_REFS.ea.widget_creation_popup_menu.trigger_simple_widget_picking),
        self,
        param_name,
    )

    button = Button(
        surface=ADD_BUTTON_SURF,
        command=command,
        coordinates_name="midleft",
        coordinates_value=midleft,
    )

    pab_map[param_name] = button

    ### store reference to button rect
    rectsman_rects.append(button.rect)

    ### instantiate and store a RectsManager for the
    ### entire parameter, using the gathered rects

    rectsman = RectsManager(rectsman_rects.__iter__)
    self.param_rectsman_map[param_name] = rectsman
