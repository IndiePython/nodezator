"""Facility with class extension with user actions."""

### standard library imports

from itertools import chain

from operator import attrgetter


### third-party import
from pygame.math import Vector2


### local imports

from ...config import APP_REFS

from ...pygamesetup import SERVICES_NS

from ...loopman.exception import ContinueLoopException

from ...our3rdlibs.behaviour import indicate_unsaved

from ...userprefsman.main import USER_PREFS

from ..socket.output import OutputSocket



class UserActions:
    """Behaviours related to user actions."""

    def __init__(self):
        """Create support object."""

        ### when defining a new connection, the temporary line segment
        ### must go from socket_a to the mouse cursor, and if there's a
        ### compatible socket nearby, we also draw a line from the cursor
        ### to that socket
        ###
        ### (a compatible socket is one that can connect with the one from
        ### where the line segment is coming, that is, if one socket is an
        ### output socket, the other must be an input socket and vice-versa)
        ###
        ### this point is used to assist in this, by temporarily storing the
        ### position of the mouse
        self.magnet_point = Vector2()

        ### store percentage of distance from a candidate socket to the mouse
        ###
        ### a candidate socket is one that is almost near enough the mouse to
        ### be picked as a nearby socket but not near enough yet;
        ###
        ### this percentage represents how much the distance must decrease in
        ### order for the socket to be picked
        self.percentage_to_mouse = 0

        ### list to temporily store references to nodes for which the mouse
        ### is close but not over them
        self.nodes_near_mouse = []

    def trigger_defining_segment(self, socket_a, mouse_pos=None):
        """Prep to define new line segment.

        Parameters
        ==========
        socket_a (reference to socket instance)
            reference of socket from where line is being
            defined.
        mouse_pos (2-tuple of integers or None)
            if not None, represents position of mouse on screen.
        """
        ### store socket reference
        self.socket_a = socket_a

        ### snap the magnet point to the mouse (if the mouse position is not
        ### available, we use socket a, cause in this circumnstance we assume
        ### they should be almost at the same position)

        self.magnet_point.update(

            mouse_pos
            if mouse_pos

            else socket_a.rect.center

        )

        ### placeholder attributes to hold socket to which we'd like to
        ### connect socket a

        self.socket_b = None
        self.socket_b_candidate = None

        ### assing function to retrieve compatible sockets
        ### (i. e., if socket_a is an output socket, must retrieve
        ### input sockets and vice-versa)

        self.get_compatible_sockets = (

            get_connectable_input_sockets
            if isinstance(socket_a, OutputSocket)

            else get_output_sockets

        )

        ### change window manager state to draw temp line
        ### between socket and
        APP_REFS.wm.set_state("segment_definition")

        ### depending on the socket detection graphics, make it so the
        ### mouse isn't visible

        if USER_PREFS['SOCKET_DETECTION_GRAPHICS'] != 'assisting_line':
            SERVICES_NS.set_mouse_visibility(False)

        ### restart the loop
        raise ContinueLoopException

    def start_defining_segment_if_close_to_socket(self, mouse_pos):
        """Trigger segment definition if a socket from given node is nearby."""

        ### reference nodes near the mouse in a dedicated list

        nodes_near_mouse = self.nodes_near_mouse

        nodes_near_mouse.extend(
            node
            for node in self.nodes_on_screen
            if node.rect.inflate(120, 120).collidepoint(mouse_pos)
        )

        ### clear the collection of nodes on screen
        self.nodes_on_screen.clear()

        ### if no collision was detected, we can leave the method right away,
        ### since there's no point searching for a nearby socket if there
        ### isn't even a nearby node
        if not nodes_near_mouse: return

        ### otherwise, it means the periphery of one or more nodes collided
        ### (we know that cause this method only executes when the mouse moves
        ### while clicked outside objects in the graph);
        ###
        ### we assume the user may want to start defining a segment from the
        ### nearest socket, but only if there's one close enough to the mouse,
        ### which is what we'll check next

        ## reference magnet point locally and set it to the mouse position

        mp = self.magnet_point
        mp.update(mouse_pos)

        ## get iterator of all connectable sockets

        sockets = chain.from_iterable(

            get_all_connectable_sockets(node)
            for node in nodes_near_mouse

        )

        ## try grabing the closest socket

        key_func = lambda item: mp.distance_to(item.rect.center)

        try:
            closest_socket = min(sockets, key=key_func)

        ### if none is found, indicate it by assigning None to the
        ### corresponding variable

        except ValueError:
            closest_socket = None

        ### before we continue, let's make sure the list of nodes
        ### near the mouse is cleared

        finally:
            nodes_near_mouse.clear()

        ### now, if there is indeed a socket near the mouse, we can
        ### trigger segment definition from that socket

        if closest_socket and mp.distance_to(closest_socket.rect.center) < 60:
            self.trigger_defining_segment(closest_socket, mouse_pos)

    def look_for_nearby_compatible_socket(self, mouse_pos):
        """Reference nearby compatible socket, if any."""
        ### reference magnet point locally and set it to the mouse position

        mp = self.magnet_point
        mp.update(mouse_pos)

        ### reference socket detection values locally for easier/quicker
        ### access

        detection_distance = USER_PREFS['DETECTION_DISTANCE']
        grasping_distance = USER_PREFS['GRASPING_DISTANCE']

        ### define how much to inflate a node to obtain an area used to
        ### detect whether the mouse is close enough to a node
        node_inflation = detection_distance * 2

        ### assume there's no compatible socket nearby
        self.socket_b = self.socket_b_candidate = None

        ### grab reference to our node
        our_node = self.socket_a.node

        ### grab compatible socket from nearby nodes (if any)

        retrieve_sockets = self.get_compatible_sockets

        sockets = chain.from_iterable(

            retrieve_sockets(node)
            for node in self.nodes.get_on_screen()

            if (

                (
                    node.rect
                    .inflate(node_inflation, node_inflation)
                    .collidepoint(mouse_pos)
                )

                and node is not our_node

            )

        )

        ### try grabing the closest socket

        key_func = lambda item: mp.distance_to(item.rect.center)

        try:
            closest_socket = min(sockets, key=key_func)

        ### if none is found, just pass

        except ValueError:
            pass

        ### if one is found though, store a reference to it
        ### and other values depending on how close it is

        else:

            distance = mp.distance_to(closest_socket.rect.center)

            if distance < grasping_distance:
                self.socket_b = closest_socket

            elif distance < detection_distance:

                self.socket_b_candidate = closest_socket

                # offset_grasping_distance 
                og_distance = grasping_distance - 5

                # difference_between_distances 
                difference = detection_distance - og_distance

                # store percentage of difference from socket candidate
                # to mouse

                self.percentage_to_mouse = (
                    1 - ((distance - og_distance) / difference)
                )

    def check_nearby_socket_for_segment_definition(self):

        ### depending on the socket detection graphics, and regardless of
        ### whether we have a socket_b or not, turn on the mouse visibility

        if USER_PREFS['SOCKET_DETECTION_GRAPHICS'] != 'assisting_line':
            SERVICES_NS.set_mouse_visibility(True)

        ### if there's a socket_b, trigger operation to define segment

        if self.socket_b:
            self.resume_defining_segment()

        ### otherwise, cancel the segment definition;
        ###
        ### this automatically triggers the restart of the loop

        else:
            self.cancel_defining_segment()


    def resume_defining_segment(self):
        """Resume definition of new line segment.

        Parameters
        ==========
        socket_b (reference to socket instance)
            reference of socket to where line is being
            defined.
        """
        ### reference sockets a and b locally and delete the respective
        ### attributes
        ### attribute

        socket_a, socket_b = self.socket_a, self.socket_b
        del self.socket_a, self.socket_b

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
                    signal_child=False,
                )

                self.signal_severance_of_removed_sockets()

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

            ### also, indicate that changes were made to the data and
            ### that the birdseye view state of window manager must have its
            ### objects updated next time it is set

            indicate_unsaved()
            APP_REFS.ea.must_update_birdseye_view_objects = True

        ### change window manager state to the loaded
        ### file state
        APP_REFS.wm.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException

    def cancel_defining_segment(self):
        """Cancel definition of a new line segment."""
        ### delete attribute holding socket reference
        ### from where to define a line
        del self.socket_a

        ### change window manager state to the loaded
        ### file state
        APP_REFS.wm.set_state("loaded_file")

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
        APP_REFS.wm.set_state("segment_severance")

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
        APP_REFS.wm.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException

    def cancel_severing_segments(self):
        """Cancel severance of line segments."""
        ### delete attribute holding start point for
        ### "cutting" line segment
        del self.cut_start_pos

        ### change window manager state to the loaded
        ### file state
        APP_REFS.wm.set_state("loaded_file")

        ### restart the loop
        raise ContinueLoopException


get_output_sockets = attrgetter('output_sockets')

def get_connectable_input_sockets(node):

    yield from node.input_sockets

    if (
        hasattr(node, 'placeholder_sockets')
        and node.placeholder_sockets
        and node.data.get('mode') == 'expanded_signature'
    ):
        yield from node.placeholder_sockets

def get_all_connectable_sockets(node):
    yield from node.output_sockets
    yield from get_connectable_input_sockets(node)
