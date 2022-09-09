"""Facility with class extension with support operations."""

### local imports

from ..socket.output import OutputSocket

from .utils import do_segments_cross

from ..utils import yield_subgraph_nodes

from ...our3rdlibs.behaviour import (
    indicate_unsaved,
    set_status_message,
)


class SupportOperations:
    """Support operations for other higher-level ones."""

    def validate_line_segment(self, socket_a, socket_b):
        """Raise error if segment between sockets isn't valid.

        Parameters
        ==========
        socket_a, socket_b (references to sockets)
            the sockets to be connected by a line segment.
        """
        ### there must be one, and only one output
        ### socket among the given ones, otherwise
        ### the connections can't be stablished

        output_socket_n = sum(
            1 for socket in (socket_a, socket_b) if type(socket) is OutputSocket
        )

        if output_socket_n == 0:

            raise TypeError(
                "Can't connect sockets cause both of" " them represent inputs"
            )

        elif output_socket_n == 2:

            raise TypeError(
                "Can't connect sockets cause both of" " them represent outputs"
            )

        ### there's no need to connect sockets which are
        ### already connected
        self.check_existing_segment(socket_a, socket_b)

        ### check the existence of a cycle in data flow
        ### (whether the user is trying to connect the
        ### output socket to an input socket which ends
        ### up feeding the output socket in the first
        ### place, creating a cycle)
        self.check_cyclic_flow(socket_a, socket_b)

    def check_existing_segment(self, socket_a, socket_b):
        """Check whether sockets are already connected."""
        ### check whether socket_b is inside socket_a
        ### children

        try:
            result = socket_b in socket_a.children

        ### if socket_a doesn't even have a 'children'
        ### attribute, that's ok, just pass
        except AttributeError:
            pass

        ### otherwise check whether socket_b is indeed
        ### among the socket_b children, in which case
        ### you must raise an error, since there's no
        ### point in connecting them again

        else:

            if result:

                raise ValueError("Sockets are connected already")

    def check_cyclic_flow(self, socket_a, socket_b):
        """Check whether connecting sockets form a cycle.

        Works by checking whether the input socket is
        somehow already connected to the output socket
        by being part of a node that ends up feeding the
        output socket in the first place. Such kind of
        connections is forbidden, as it creates a cycle
        in the data flow, preventing the data from
        advancing in the graph.

        So, if such kind of connection is detected,
        we raise a ValueError to prevent the connection
        from existing and thereby causing a cycle.
        """
        ### retrieve the node from the socket a
        node = socket_a.node

        ### check whether socket_b has the same node of
        ### socket_a, raising a ValueError if so, since
        ### connecting the sockets in this circunstance
        ### would create a cycle in the data flow

        if socket_b.node is node:

            raise ValueError(
                "Connecting given sockets would create a" " cycle in the data flow"
            )

        ### keep checking the parents of the input sockets
        ### further up in the node layout branch until all
        ### existing "ancestors" are checked

        for input_socket in node.input_sockets:

            ## check whether the input socket has a parent
            try:
                parent = input_socket.parent

            ## if not, that's ok, just pass
            except AttributeError:
                pass

            ## otherwise keep checking the input
            ## sockets embedded in the parent's node
            ## recursively until no "ancestors" are
            ## left
            else:
                self.check_cyclic_flow(
                    parent,
                    socket_b,
                )

    def sever_segment_between_sockets(
        self,
        parent,
        child,
        store_for_signaling=True,
    ):
        """Sever segment between given sockets.

        Also performs other needed tasks.

        Parameters
        ==========
        parent (graphman.socket.output.OutputSocket instance)
            parent socket.
        child (
             graphman.socket.input.InputSocket instance
          or graphman.socket.proxy.ProxySocket instance
        )
            child socket.
        store_for_signaling (boolean)
            indicates whether a reference of the child must
            be stored so that the severance of the segment
            can be signaled to its node (this may be
            desirable to made the node aware of the
            segment's severance, in order to perform admin
            tasks if needed. The reason why the reference
            is kept for being signaled later is because
            when a severance is made, its effects can
            reposition other sockets and their segments,
            and end up severing other segments accidentally,
            hence the signaling being made later, so such
            effects only take place after the severance
            is performed.
        """
        ### begin by removing the child from the parent
        parent.children.remove(child)

        ### perform extra tasks depending on whether the
        ### parent still has children left or not

        if parent.children:

            ## update the parent's tree data to take into
            ## accound the removal of the child socket

            parent_id = parent.get_id()
            child_id = child.get_id()

            for parent_data in self.parent_sockets_data:

                if not parent_data["id"] == parent_id:
                    continue

                for child_data in parent_data["children"]:
                    if child_data["id"] == child_id:
                        break

                break

            parent_data["children"].remove(child_data)

        else:

            ## delete its children attribute
            del parent.children

            ## remove it from the list of existing parents
            self.parents.remove(parent)

            ## remove parent tree data, since it doesn't
            ## form a tree anymore (the socket alone isn't
            ## considered a valid tree, that is, the tree
            ## must have at least height 1)

            parent_id = parent.get_id()

            for parent_data in self.parent_sockets_data:

                if parent_data["id"] == parent_id:
                    break

            self.parent_sockets_data.remove(parent_data)

        ### the children must then have its 'parent'
        ### attribute removed
        del child.parent

        ### finally, if requested, the child must be stored
        ### so that its node can later be signaled about the
        ### severance we just performed

        if store_for_signaling:
            self.sockets_for_signaling.append(child)

    def establish_segment(self, socket_a, socket_b):
        """Perform setups to establish new line segment."""
        ### perform extra setups depending on whether or not
        ### socket_a has children

        ## check whether socket_a has children
        try:
            children = socket_a.children

        ## setups in case the socket_a has no children

        except AttributeError:

            # make it so socket_a has None as its parent
            socket_a.parent = None

            # add it to self.parents
            self.parents.append(socket_a)

            # create and append a new tree data entry for
            # the socket_a in the socket trees

            parent_data = {
                "id": socket_a.get_id(),
                "class_name": socket_a.__class__.__name__,
                "children": [],
            }

            self.parent_sockets_data.append(parent_data)

            # also reference the list in the 'children'
            # field of the tree data
            children_data = parent_data["children"]

            # create a new 'children' attribute containing
            # a list
            children = socket_a.children = []

        ## setups in case the socket_a already has children

        else:

            ## reference the 'children' field of the
            ## tree data for the socket_a

            socket_a_id = socket_a.get_id()

            for parent_data in self.parent_sockets_data:

                if parent_data["id"] == socket_a_id:
                    break

            children_data = parent_data["children"]

        ### append the socket_b as a child of socket_a and
        ### reference socket_a as its parent in its 'parent'
        ### attribute

        children.append(socket_b)
        socket_b.parent = socket_a

        ### check whether socket_b has a
        ### 'signal_connection' method
        try:
            signal_connection = socket_b.signal_connection

        ### if it doesn't have one, just pass
        except AttributeError:
            pass

        ### if it has, though, it is a proxy socket, so use
        ### the retrieved method to perform extra setups
        ### needed
        else:
            signal_connection()

        ### create and append the tree data for the socket_b
        ### in the children data of the socket_a

        child_data = {
            "id": socket_b.get_id(),
            "class_name": socket_b.__class__.__name__,
        }

        children_data.append(child_data)

        ### finally, if any of the nodes (the node of the
        ### socket_a or the node of the socket_b) is
        ### commented out, comment out the whole subgraph
        ### (the nodes which aren't already commented out)

        if any(
            socket.node.data.get("commented_out", False)
            for socket in (socket_a, socket_b)
        ):

            ## create a generator expression which yields
            ## uncommented nodes

            uncommented_nodes = (
                node
                for node in yield_subgraph_nodes(socket_a.node)
                if not node.data.get("commented_out", False)
            )

            ## iterate over such uncommented nodes,
            ## commenting them out

            for node in uncommented_nodes:

                node.data["commented_out"] = True
                node.perform_commenting_uncommenting_setups()

    def cut_crossing_segments(
        self,
        cut_start_pos,
        cut_end_pos,
    ):
        """Sever segments crossed by the "cutting" segment.

        Parameters
        ==========
        cut_start_pos (2-tuple of integers)
            start position of "cutting" segment.
        cut_end_pos (2-tuple of integers)
            end position of "cutting" segment.
        """
        ### define the cutting segment
        cutting_segment = (cut_start_pos, cut_end_pos)

        ### reference all existing socket pairs which
        ### are connected by line segments

        socket_pairs = [
            (parent, child) for parent in self.parents for child in parent.children
        ]

        ### create a flag indicating whether any segment
        ### was severed
        any_severed = False

        ### iterate over each socket pair, checking whether
        ### the segment they form is crossed by the cutting
        ### segment, in which case it must be severed (and
        ### the 'any_severed' flag set to True)

        for parent, child in socket_pairs:

            existing_segment = (parent.rect.center, child.rect.center)

            if do_segments_cross(
                cutting_segment,
                existing_segment,
            ):

                self.sever_segment_between_sockets(
                    parent,
                    child,
                )

                any_severed = True

        self.signal_severance_of_removed_sockets()

        ### if any segment was severed, indicate the
        ### change in the data
        if any_severed:
            indicate_unsaved()

    def signal_severance_of_removed_sockets(self):
        """Signal severance of gathered sockets."""
        ### while there are sockets kept for signaling, keep
        ### removing them and signaling the severance of
        ### their segments to their nodes

        while self.sockets_for_signaling:

            (self.sockets_for_signaling.pop().signal_severance())

    def fix_input_socket_id(self, input_socket, old_id):
        """Fix input socket id on socket tree."""
        ### get the id of the parent
        parent_id = input_socket.parent.get_id()

        ### iterate over the tree data in the socket,
        ### trees, looking for the one with the parent id

        for parent_data in self.parent_sockets_data:
            if parent_data["id"] == parent_id:
                break

        ### now iterate over the children data, looking
        ### for the data whose id matches the old id
        ### received

        for child_data in parent_data["children"]:
            if child_data["id"] == old_id:
                break

        ### finally update the id of the child data with
        ### the current id of the input socket
        child_data["id"] = input_socket.get_id()

    def fix_output_socket_id(self, output_socket, old_id):
        """Fix output socket id on socket tree."""
        ### iterate over the tree data in the socket,
        ### trees, looking for the one with the old id

        for parent_data in self.parent_sockets_data:
            if parent_data["id"] == old_id:
                break

        ### update the id of the parent data with the
        ### current id of the output socket
        parent_data["id"] = output_socket.get_id()

    def sever_all_connections(self, node):
        """Sever all existing connections on given node."""
        ### sever connections from input sockets, if any

        for socket in node.input_sockets:

            try:
                parent = socket.parent

            except AttributeError:
                pass

            else:

                # we can freely remove the connections
                # of the input sockets without worrying
                # about the effects on the 'flat_values'
                # list we are iterating, because the
                # effects of these operations on the
                # list are only accounted for (if any),
                # in the step further ahead where we
                # execute the severance signaling method

                self.sever_segment_between_sockets(
                    parent,
                    socket,
                )

        ### sever connections from output sockets

        for socket in node.output_sockets:

            try:
                children = socket.children

            except AttributeError:
                pass

            else:

                # note that we use a copy of the children
                # list; this is so because the children
                # list itself is altered while executing
                # the segment severing method

                for child in children[:]:

                    self.sever_segment_between_sockets(
                        socket,
                        child,
                    )

        ### signal the severances performed
        self.signal_severance_of_removed_sockets()

    def sever_children(self, output_socket):
        """Sever all children of given output socket."""

        try:
            children = output_socket.children

        except AttributeError:

            ### notify user of impossibility
            set_status_message("No children to disconnect")

        else:

            # note that we use a copy of the children
            # list; this is so because the children
            # list itself is altered while executing
            # the segment severing method

            for child in children[:]:

                self.sever_segment_between_sockets(
                    output_socket,
                    child,
                )

            ### signal the severances performed
            self.signal_severance_of_removed_sockets()

            ### notify user of success
            set_status_message("All children disconnected")

            ### indicate the change in the data
            indicate_unsaved()

    def sever_parent(self, socket):
        """Sever parent of given socket."""

        try:
            parent = socket.parent

        except AttributeError:

            ### notify user of impossibility
            set_status_message("No parent to disconnect")

        else:

            # we can freely remove the connection
            # of the input sockets without worrying
            # about the effects on the 'flat_values'
            # list we are iterating, because the
            # effects of the operation on the list are
            # only accounted for (if any), when we
            # execute the severance signaling method

            self.sever_segment_between_sockets(
                parent,
                socket,
            )

            ### signal the severance performed
            self.signal_severance_of_removed_sockets()

            ### notify user of success
            set_status_message("Disconnected socket")

            ### indicate the change in the data
            indicate_unsaved()
