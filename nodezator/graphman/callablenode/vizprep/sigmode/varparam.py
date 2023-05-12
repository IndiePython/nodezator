"""Facility for visuals related node class extension."""

# XXX module's docstring isn't accurate

### standard library import
from functools import partial


### local imports

from .....config import APP_REFS

from .....classes2d.single import Object2D

from ....widget.utils import WIDGET_CLASS_MAP

from ....socket.surfs import type_to_codename

from ...utils import update_with_widget

## classes for composition

from .....our3rdlibs.button import Button

from ....socket.input import InputSocket
from ....socket.placeholder import PlaceholderSocket

from .....widget.stringentry import StringEntry

from .....rectsman.main import RectsManager

from ...surfs import (
    ADD_BUTTON_SURF,
    REMOVE_BUTTON_SURF,
    SUBP_UP_BUTTON_SURF,
    SUBP_DOWN_BUTTON_SURF,
    UNPACKING_ICON_SURFS_MAP,
)

from ...constants import FONT_HEIGHT, SUBPARAM_KEYWORD_ENTRY_WIDTH



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


    ### since we'll use their information, let's
    ### reference subparameter-related maps, locally

    subparam_map = self.data["subparam_map"]

    subparam_widget_map = self.data["subparam_widget_map"]

    subparam_unpacking_map = self.data["subparam_unpacking_map"]

    ### let's also reference maps of live instances locally using
    ### variables of low character count, for better code layout

    isl_flmap = self.input_socket_live_flmap
    sub_flmap = self.subparam_up_button_flmap
    sdb_flmap = self.subparam_down_button_flmap
    wl_flmap = self.widget_live_flmap
    sui_flmap = self.subparam_unpacking_icon_flmap
    skl_map = self.subparam_keyword_entry_live_map
    wrb_flmap = self.widget_remove_button_flmap
    pab_map = self.placeholder_add_button_map
    psl_map = self.placeholder_socket_live_map
    srm_map = self.subparam_rectsman_map

    ### create dicts to store instances of objects
    ### related to subparameters, using the parameter
    ### name as key

    isl_flmap[param_name] = {}
    sub_flmap[param_name] = {}
    sdb_flmap[param_name] = {}
    wl_flmap[param_name] = {}
    sui_flmap[param_name] = {}
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

    ## iterate over each subparameter listed on the
    ## subparameter sockets' data (if there's any)
    ## using the keys to sort the iteration order;
    ##
    ## in each iteration, we create the input socket,
    ## buttons and widget related to the subparameter
    ## (also a keyword entry if applicable);

    for subparam_index in sorted(subparams):

        ## instantiate socket

        input_socket = InputSocket(
            node=self,
            type_codename=type_codename,
            parameter_name=param_name,
            subparameter_index=subparam_index,
        )

        ## store the input socket instance in
        ## the live instance map for input sockets

        (isl_flmap[param_name][subparam_index]) = input_socket

        # this dict subclass instance must be updated
        # every time it is changed
        isl_flmap.update()

        ## instantiate subparam moving buttons

        move_subparam_up = partial(self.move_subparam_up, input_socket)

        subp_up_button = Button(
            surface=SUBP_UP_BUTTON_SURF,
            command=move_subparam_up,
        )

        (sub_flmap[param_name][subparam_index]) = subp_up_button

        # this dict subclass instance must be updated
        # every time it is changed
        sub_flmap.update()

        #
        move_subparam_down = partial(self.move_subparam_down, input_socket)

        subp_down_button = Button(
            surface=SUBP_DOWN_BUTTON_SURF,
            command=move_subparam_down,
        )

        (sdb_flmap[param_name][subparam_index]) = subp_down_button

        # this dict subclass instance must be updated
        # every time it is changed
        sdb_flmap.update()

        ## check if subparameter has a content widget
        ## (by checking whether the respective data is
        ## present)

        try:
            widget_data = subwidgets_data[subparam_index]

        ## if the data isn't present (KeyError is
        ## raised), just pass

        except KeyError:
            pass

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

            ## instantiate the widget using the keyword
            ## arguments
            widget = widget_cls(name=param_name, **kwargs)

            ## store the widget instance in the live
            ## map and set for widgets
            (wl_flmap[param_name][subparam_index]) = widget

            # this dict subclass instance must be
            # updated whenever it is changed
            wl_flmap.update()

            ### create "remove widget" button

            ## define command

            command = partial(self.remove_subparameter_widget, widget)

            ## instantiate and store

            button = Button(
                surface=REMOVE_BUTTON_SURF,
                command=command,
            )

            wrb_flmap[param_name][subparam_index] = button

            # this dict subclass needs to be update
            # whenever it is changed
            wrb_flmap.update()

            ### also define a command to update the
            ### widget value in the node data and
            ### the position of the remove button
            ### (because the widget may change its width
            ### when edited, depending on the kind of
            ### widget), then assign such command to the
            ### 'command' attribute of the widget

            command = partial(update_with_widget, kwargs, "value", widget, button)

            widget.command = command


        ## if the subparameter is marked to be unpacked,
        ## add an unpacking icon to it

        if subparam_index in subparams_for_unpacking:

            icon_surf = UNPACKING_ICON_SURFS_MAP[
                (
                    kind,
                    self.data.get("commented_out", False),
                )
            ]

            unpacking_icon = Object2D.from_surface(surface=icon_surf)

            # store the unpacking icon
            sui_flmap[param_name][subparam_index] = unpacking_icon

            # this dict subclass instance must be updated
            # every time it is changed
            sui_flmap.update()

        ## if otherwise, the parameter is of
        ## keyword-variable kind, we need to instantiate
        ## a keyword entry widget for the subparameter

        elif kind == "var_key":

            # put together a bottomleft coordinate for the
            # keyword entry widget;
            #
            # for the bottom use the top of the subrectsman
            # (3 pixels higher, by subtracting the amount)

            #bottomleft = (input_socket.rect.right + 15, subrectsman.top - 3)

            keyword_name = self.data["subparam_keyword_map"][subparam_index]

            command = partial(self.update_keyword, input_socket)

            subparam_keyword_entry = StringEntry(
                value=keyword_name,
                font_height=FONT_HEIGHT,
                width=SUBPARAM_KEYWORD_ENTRY_WIDTH,
                command=command,
            )

            # store the subparam keyword entry
            skl_map[subparam_index] = subparam_keyword_entry

        ## instantiate and store a RectsManager for the rects in this
        ## subparameter
        srm_map[param_name][subparam_index] = RectsManager([].__iter__)


    ### instantiate a placeholder socket
    ### (a socket which generates a new subparameter
    ### when a new connection is stablished with it)

    ## instantiate socket (notice we used the "center"
    ## variable defined either in the end of the
    ## previous "for" loop or before it)
    placeholder_socket = PlaceholderSocket(self, param_name)

    ## store the placeholder socket instance in the
    ## live instance map for placeholder sockets
    psl_map[param_name] = placeholder_socket

    ### now, add a button to create new sockets
    ### by instantiating widgets to provide input

    #midleft = placeholder_socket.rect.move(5, 0).midright

    command = partial(
        (APP_REFS.ea.widget_creation_popup_menu.trigger_simple_widget_picking),
        self,
        param_name,
    )

    button = Button(surface=ADD_BUTTON_SURF, command=command,)

    pab_map[param_name] = button
