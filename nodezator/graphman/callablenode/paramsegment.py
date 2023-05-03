"""Facility for operations on subparameters via segments."""

### local imports

from ...config import APP_REFS

from ...ourstdlibs.behaviour import remove_by_identity

from ...our3rdlibs.button import Button

from ...widget.stringentry import StringEntry

from ...rectsman.main import RectsManager

from .constants import FONT_HEIGHT


class ParameterSegmentOps:
    """Segment related operations on regular parameters."""

    def perform_param_connection_setups(self, input_socket):
        ### obtain parameter name 
        ### from input socket
        param_name = input_socket.parameter_name

        ### try accessing a widget instance for the
        ### subparameter using its parameter name
        try:
            widget = self.widget_live_flmap[param_name]

        ### if accessing the widget fails, there's no need to do anything,
        ### so we must return right away
        except KeyError:
            return

        ### otherwise, we must ensure it is not visible and perform additional
        ### measures

        ## make invisible
        self.visible_widgets.remove(widget)

        ##
        rectsman_rects = (
            self.param_rectsman_map[param_name]
            ._get_all_rects.__self__
        )

        ##
        remove_by_identity(
            widget.rect,
            rectsman_rects
        )

        ## reposition all objects within the node
        self.reposition_elements()

        ## also perform extra admin tasks, related to
        ## the change in the node body's height
        self.perform_body_height_change_setups()

    def perform_param_severance_setups(self, input_socket):
        ### obtain parameter name 
        ### from input socket
        param_name = input_socket.parameter_name

        ### try accessing a widget instance for the
        ### subparameter using its parameter name
        try:
            widget = self.widget_live_flmap[param_name]

        ### if accessing the widget fails, there's no need to do anything,
        ### so we must return right away
        except KeyError:
            return

        ### otherwise, we must ensure it is visible and perform additional
        ### measures

        ## position widget
        widget.rect.topleft = input_socket.rect.move(8, -1).topright

        ## make visible
        self.visible_widgets.append(widget)

        ##
        rectsman_rects = (
            self.param_rectsman_map[param_name]
            ._get_all_rects.__self__
        )

        ##
        rectsman_rects.append(widget.rect)

        ## reposition all objects within the node
        self.reposition_elements()

        ## also perform extra admin tasks, related to
        ## the change in the node body's height
        self.perform_body_height_change_setups()
