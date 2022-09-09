"""Facility for visuals related node class extension."""

### XXX module docstring isn't accurate

### standard library import
from functools import partial


### local imports

from ...widget.utils import WIDGET_CLASS_MAP

from ..utils import update_with_widget

from ...socket.surfs import type_to_codename


## classes for composition

from ...socket.input import InputSocket

from ....widget.defaultholder import DefaultHolder

from ....rectsman.main import RectsManager


def create_parameter_objs(self, param_obj):
    """Build socket and widget for the parameter.

    The parameter in question must not be of variable
    kind.

    This function is meant to extend the
    VisualRelatedPreparations class as one of its methods.

    Parameters
    ==========
    param_obj (inspect.Parameter instance)
        an object representing a parameter from a callable
        object, containing related data.
    """
    ### retrieve the name of the parameter
    param_name = param_obj.name

    ### create list to gather rects of objects in this
    ### parameter to use in a RectsManager instance
    rectsman_rects = []

    ### let's also alias the live instances map for
    ### the input sockets using a variable of low
    ### character count, for better code layout
    isl_flmap = self.input_socket_live_flmap

    ### also retrieve the expected type of the
    ### parameter and use it to obtain a string
    ### representing a codename for the type;
    ###
    ### no type enforcement is ever performed,
    ### though

    expected_type = self.type_map[param_name]
    type_codename = type_to_codename(expected_type)

    ### define a temporary center coordinate for the
    ### input socket
    center = self.top_rectsman.left, 0

    ### instantiate socket

    input_socket = InputSocket(
        node=self, type_codename=type_codename, parameter_name=param_name, center=center
    )

    ### store the input socket instance in the
    ### live instance map for input sockets
    isl_flmap[param_name] = input_socket

    ## this dict subclass instance needs to be updated
    ## every time it is changed
    isl_flmap.update()

    ### gather the input socket's rect
    rectsman_rects.append(input_socket.rect)

    ### try retrieving the widget meta map for the
    ### parameter
    try:
        param_widget_meta = self.widget_meta[param_name]

    ### if widget metadata for the parameter doesn't
    ### exists, we just pass: no widget will be created
    except KeyError:
        pass

    ### otwerwise, we use the retrieved metadata to
    ### properly instantiate and set a widget

    else:

        ## retrieve widget class using the widget name
        ## from the parameter widget metadata

        widget_name = param_widget_meta["widget_name"]
        widget_cls = WIDGET_CLASS_MAP[widget_name]

        ## retrieve keyword arguments to use when
        ## instantiating the widget
        kwargs = param_widget_meta["widget_kwargs"]

        ## put together position data for the widget
        ## (widget topleft is positioned relative to the
        ## input socket topright)

        topleft_pos = input_socket.rect.move(8, -1).topright

        pos_data = {"coordinates_name": "topleft", "coordinates_value": topleft_pos}

        ## instantiate the widget using the keyword arguments
        ## as well as the position data

        try:
            widget = widget_cls(name=param_name, **kwargs, **pos_data)

        except Exception as err:

            raise RuntimeError(
                "Error while trying to instantiate"
                f" widget for '{param_name}' parameter"
                f" of '{self.title_text}' node"
                f" of id #{self.id} with data from"
                " the parameter widget metadata map"
            ) from err

        ## if available, set widget value as defined
        ## by the user in its last editing session

        param_widget_value_map = self.data["param_widget_value_map"]

        # check existence of value
        try:
            value = param_widget_value_map[param_name]

        # if not available, use the current value of
        # the widget to fill it (unless it is a
        # default holder widget, a special widget
        # which can't be edited, and in fact may
        # even hold non-JSON-serializable values)

        except KeyError:

            if not isinstance(widget, DefaultHolder):

                # by ensuring the value being seen
                # in the widget is the one to be
                # used, we avoid confusion, that is,
                # what you see is what you get (except
                # for the default holder widget, of
                # course, but it is a special case of
                # which the users must be made aware
                # anyway)

                (param_widget_value_map[param_name]) = widget.get()

        # otherwise, do the opposite: set the value
        # on the widget
        else:
            widget.set(value)

        ## also define a command to update the
        ## widget value in the node data and
        ## assign it to the command attribute of
        ## the widget

        command = partial(
            update_with_widget, param_widget_value_map, param_name, widget
        )

        widget.command = command

        ## store the widget instance in the live map
        ## and set for widgets
        self.widget_live_flmap[param_name] = widget

        # this dict subclass instance must be updated
        # whenever it is changed
        self.widget_live_flmap.update()

        ### gather the widget's rect
        rectsman_rects.append(widget.rect)

    ### instantiate and store a RectsManager for the
    ### gathered rects in this parameter

    rectsman = RectsManager(rectsman_rects.__iter__)
    self.param_rectsman_map[param_name] = rectsman
