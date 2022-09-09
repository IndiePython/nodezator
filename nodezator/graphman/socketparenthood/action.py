"""Facility with class extension with user actions."""

### local imports

from ...config import APP_REFS

from ...loopman.exception import ContinueLoopException
from ...our3rdlibs.behaviour import indicate_unsaved

from ..socket.output import OutputSocket


class UserActions:
    """Behaviours related to user actions."""

    def trigger_defining_segment(self, socket_a):
        """Prep to define new line segment.

        Parameters
        ==========
        socket_a (reference to socket instance)
            reference of socket from where line is being
            defined.
        """
        ### store socket reference
        self.socket_a = socket_a

        ### change window manager state to draw temp line
        ### between socket and
        APP_REFS.window_manager.set_state("segment_definition")

        ### restart the loop
        raise ContinueLoopException

    def resume_defining_segment(self, socket_b):
        """Resume definition of new line segment.

        Parameters
        ==========
        socket_b (reference to socket instance)
            reference of socket to where line is being
            defined.
        """
        ### retrieve the socket_a reference and delete the
        ### attribute

        socket_a = self.socket_a
        del self.socket_a

        ### the output socket must be the socket at the
        ### left (socket_a), so swap places if needed
        ### (this is ok even if both sockets are output
        ### sockets)

        if isinstance(socket_b, OutputSocket):
            socket_a, socket_b = socket_b, socket_a

        ### establish segment line segment if it validates

        try:
            self.validate_line_segment(socket_a, socket_b)

        except (TypeError, ValueError) as err:
            print(err)

        else:

            ## if socket_b has a parent, sever the segment
            ## between them since after this we're about to
            ## establish a new one

            try:
                parent = socket_b.parent

            except AttributeError:
                pass

            else:

                self.sever_segment_between_sockets(
                    parent,
                    socket_b,
                    store_for_signaling=False,
                )

            ## check whether socket_b has a
            ## 'get_input_socket' method
            try:
                get_input_socket = socket_b.get_input_socket

            ## if it doesn't have one, just pass
            except AttributeError:
                pass

            ## if it has, though, it is a placeholder
            ## socket, so use the retrieved method to
            ## obtain an input socket to replace it
            else:
                socket_b = get_input_socket()

            ### you can now safely establish a new line
            ### segment between the two sockets
            self.establish_segment(socket_a, socket_b)

            ### also, indicate that changes were made
            ### to the data
            indicate_unsaved()

        ### change window manager state to the loaded
        ### file state
        APP_REFS.window_manager.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException

    def cancel_defining_segment(self):
        """Cancel definition of a new line segment."""
        ### delete attribute holding socket reference
        ### from where to define a line
        del self.socket_a

        ### change window manager state to the loaded
        ### file state
        APP_REFS.window_manager.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException

    def trigger_segments_severance(self, pos):
        """Prep to cut existing line segments.

        Parameters
        ==========
        pos (2-tuple of integers)
            start point of "cut" line segment used to define
            which segments must be severed.
        """
        ### store cut start position
        self.cut_start_pos = pos

        ### change window manager state to draw temporary
        ### "cut" line between provided cut start position
        ### and mouse
        APP_REFS.window_manager.set_state("segment_severance")

        ### restart the loop
        raise ContinueLoopException

    def resume_severing_segments(self, cut_end_pos):
        """Resume severance of existing line segments.

        Parameters
        ==========
        cut_end_pos (2-tuple of integers)
            end point of "cut" line segment used to define
            which segments must be severed.
        """
        ### retrieve the start cut position and delete the
        ### attribute

        cut_start_pos = self.cut_start_pos
        del self.cut_start_pos

        ### perform severance of segments which are crossed
        ### by the line defined by the points
        self.cut_crossing_segments(cut_start_pos, cut_end_pos)

        ### change window manager state to the loaded
        ### file state
        APP_REFS.window_manager.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException

    def cancel_severing_segments(self):
        """Cancel severance of line segments."""
        ### delete attribute holding start point for
        ### "cutting" line segment
        del self.cut_start_pos

        ### change window manager state to the loaded
        ### file state
        APP_REFS.window_manager.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException
