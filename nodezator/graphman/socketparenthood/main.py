"""Facility for socket tree management.

Contains a class extension for the GraphManager class which
defines methods related to management of socket trees.
"""

### local imports (class extensions)

from .draw import DrawingOperations
from .action import UserActions
from .support import SupportOperations
from .export import ExportOperations


class SocketParenthood(
    DrawingOperations,
    UserActions,
    SupportOperations,
    ExportOperations,
):
    def setup_parent_sockets_data(self):
        """Store data and perform setups.

        Setups performed:

        - Organizing sockets into general tree structures
          of height 1
            Works by having sockets reference each other
            using 'parent' and 'children' attributes.

        - Store references for each parent
            We do so in order to be able to to easily
            retrieve data about socket trees whenever
            needed.
        """
        ### iterate over the data for each tree in the
        ### parent sockets data attribute, grabbing references
        ### for each socket in each tree and making it so parents
        ### reference the children and vice-versa;
        ###
        ### the parent of each tree is returned in the process and
        ### gathered in a list stored in the 'parents' attribute

        self.parents = [
            self.reference_parent_children(parent_data)
            for parent_data in self.parent_sockets_data
        ]

        ### create collections to temporarily store sockets and
        ### their nodes to be signaled after the sockets' segments are
        ### severed (check the sever_segment_between_sockets method to
        ### know more about their usage)

        self.parents_for_signaling = []
        self.children_for_signaling = []

        self.nodes_for_signaling = set()

    def reference_parent_children(
        self,
        parent_data,
        parent=None,
    ):
        """Make parent and children reference each other.

        Works recursively through the tree structure.
        """
        class_name = parent_data["class_name"]

        ### treat ids according to class name

        if class_name == "OutputSocket":

            ## retrieve the node id and output name from
            ## the 'id' field of the tree data
            node_id, output_name = parent_data["id"]

            ## use the node id to find the node, and the
            ## output name to find the output socket
            ## in the respective map in the node

            node = self.node_map[node_id]

            ## TODO review this try/except/else clauses

            ## try retrieving a reference to an
            ## output socket live map

            try:
                oslm = node.output_socket_live_map

            ## if you are not able to, it means we have
            ## a proxy node, so we just retrieve its output
            ## socket

            except AttributeError:
                socket = node.output_socket

            ## otherwise, if try retrieving the socket
            ## depending on the node's mode

            else:

                ## if in callable mode, there's only a single
                ## output socket available, so just reference it
                if node.data.get('mode', 'expanded_signature') == 'callable':
                    socket = node.output_sockets[0]

                ## otherwise, the socket is retrieve from the output
                ## socket live map directly, using the output name
                else:
                    socket = oslm[output_name]

        elif class_name == "InputSocket":

            ## retrieve the parts of the 'id' field of the
            ## tree data
            parts = parent_data["id"]

            ## calculate length
            length = len(parts)

            ## treat id parts depending on the length

            if length == 2:

                ## retrieve a node id and param name
                ## from the split parts
                node_id, param_name = parts

                ## use the retrieved data to find the node
                ## and then the input socket

                node = self.node_map[node_id]

                ## TODO review this try/except/else clauses

                try:
                    islf = node.input_socket_live_flmap

                except AttributeError:

                    socket = next(
                        socket
                        for socket in (node.input_sockets)
                        if (socket.parameter_name == param_name)
                    )

                else:
                    socket = islf[param_name]

            elif length == 3:

                ## retrieve a node id, param name and
                ## subparam_index from the split parts
                node_id, param_name, subparam_index = parts

                ## use the retrieved data to find the node
                ## and then the input socket

                node = self.node_map[node_id]

                socket = node.input_socket_live_flmap[param_name][subparam_index]

        elif class_name == "ProxySocket":

            ## retrieve the node id from the 'id' field of
            ## the tree data
            node_id, _ = parent_data["id"]

            ## use the retrieved data to find the node
            ## and then the proxy socket

            node = self.node_map[node_id]
            socket = node.input_sockets[0]

        ### reference parent and child among themselves

        ## if parent is not None...

        if parent is not None:

            ## assign parent to socket
            socket.parent = parent

            ## try storing socket reference in list in
            ## parent's children attribute
            try:
                parent.children.append(socket)

            ## if list doesn't exist, we create it already
            ## holding our socket

            except AttributeError:
                parent.children = [socket]

        ### if the tree data has a 'children' field,
        ### pass each of them to this method recursively;
        ### input sockets are never supposed to have
        ### children, so this check should always
        ### fail for them; the other types of sockets
        ### may have children or not;

        try:
            children_data = parent_data["children"]

        except KeyError:
            pass

        else:

            for child_data in children_data:

                self.reference_parent_children(
                    child_data,
                    socket,
                )

        ### finally, return the socket
        return socket
