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
    def setup_parent_sockets_data(self, parent_sockets_data):
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
        ### store the socket trees data in a dedicated
        ### attribute
        self.parent_sockets_data = parent_sockets_data

        ### iterate over the data for each tree in the
        ### socket trees attribute, grabbing references
        ### for each socket in each tree and making it
        ### so parents reference the children and
        ### vice-versa; the parent of each tree is returned
        ### in the process and gathered in a list stored
        ### in the 'parents' attribute

        self.parents = [
            self.reference_parent_children(parent_data)
            for parent_data in self.parent_sockets_data
        ]

        ### create a list to store sockets to be signaled
        ### after their segments are severed (check the
        ### sever_segment_between_sockets method to know
        ### more about list's usage)
        self.sockets_for_signaling = []

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

            try:
                oslm = node.output_socket_live_map

            except AttributeError:
                socket = node.output_socket

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

        ## assign parent to socket
        socket.parent = parent

        ## try storing socket reference in list in
        ## parent's children attribute
        try:
            parent.children.append(socket)

        ## if list doesn't exist, we create it already
        ## holding our socket

        except AttributeError:

            # try assigning new list
            try:
                parent.children = [socket]

            # if this still fails, that's ok; we just
            # pass, since it means the parent is None;
            except AttributeError:
                pass

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
