"""Class extension for preparation of visual objects."""

### standard library import
from collections.abc import Callable


### third-party import
from pygame import Rect


### local imports

from .....ourstdlibs.collections.fldict.main import FlatListDict

from .....classes2d.single import Object2D

from .....rectsman.main import RectsManager

from ....socket.surfs import type_to_codename


## class for composition
from ....socket.output import OutputSocket


class CallableModeVisualPreparations():
    """Manages creation and setup of node visuals for callable mode."""

    ### define remaining methods

    def create_callable_mode_visual_elements(self):
        """Create visual elements for node's callable mode."""

        ### create output socket

        self.callable_output_socket = (
            OutputSocket(
                node=self,
                output_name=self.title_text,
                type_codename=(type_to_codename(Callable)),
            )
        )

        ### store it in a collection
        self.callable_output_sockets = (self.callable_output_socket,)

        ### also create and store a rects manager to
        ### control all the rects in the node

        ## create a list containing the rects to be managed
        ## and get its __iter__ method to use as a callable
        ## which returns the rects to be managed by the
        ## rects manager instance

        all_rects = [
            self.rect,
            self.top_rectsman,
            self.title_text_obj.rect,
            self.body.rect,
            self.callable_output_socket.rect,
            self.id_text_obj.rect,
            self.bottom_rectsman,
        ]

        get_all_rects = all_rects.__iter__


        ## use the callable to instantiate the rects
        ## manager and then store it
        self.cal_rectsman = RectsManager(get_all_rects)
