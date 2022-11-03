from ..socket.surfs import type_to_codename


class SegmentOps:
    """Segment defining operations for proxy node."""

    def signal_connection(self):
        """Act on establishment of incomming connection."""
        ## update source name and type_codename

        source_name = self.data["source_name"] = next(
            get_source_name(self.proxy_socket.parent)
        )

        type_codename = self.proxy_socket.type_codename

        self.data["source_type_codename"] = type_codename

        ## update label surface
        self.update_label_surface()

        ## check header width
        self.check_header_width()

        ## update style and output name of output socket

        output_socket = self.output_socket

        output_socket.update_type_codename(type_codename)

        self.propagate_output(source_name, type_codename)

    def signal_severance(self):
        """Act on severance of incomming connection."""
        ## delete source name and type codename

        del self.data["source_name"]
        del self.data["source_type_codename"]

        ## update label surface
        self.update_label_surface()

        ## check header width
        self.check_header_width()

        ###

        try:
            widget = self.widget

        except AttributeError:
            type_codename = None

        else:

            expected_type = widget.get_expected_type()

            type_codename = type_to_codename(expected_type)

        output_socket = self.output_socket

        output_socket.update_type_codename(type_codename)

        self.propagate_output(self.title, type_codename)

    def propagate_output(self, source_name, type_codename):

        ## propagate type codename

        try:
            children = self.output_socket.children

        except AttributeError:
            pass

        else:

            for child in children:

                node = child.node

                if any(
                    not hasattr(node, attr_name)
                    for attr_name in (
                        "output_socket",
                        "proxy_socket",
                    )
                ):
                    continue

                output_socket = node.output_socket

                node.data["source_name"] = source_name
                node.data["source_type_codename"] = type_codename

                node.proxy_socket.update_type_codename(type_codename)

                node.output_socket.update_type_codename(type_codename)

                ## update label surface
                node.update_label_surface()

                ## check header width
                node.check_header_width()

                node.propagate_output(source_name, type_codename)


### utility function

def get_source_name(parent):
    """Yield source name once you find it.
    
    The source name is found by travelling the graph backwards
    until we find the output socket of a regular node or of an
    orphan redirect node.

    Parameters
    ==========

    parent (an output socket)
        socket containing data needed to determine the source
        name to use; it is called "parent" because it is further
        up in the socket parenthood tree.
    """
    ### if the parent node has 'source_name' in its data, it means
    ### the previous node is a redirect node with a parent, so
    ### we look further backwards

    if 'source_name' in parent.node.data:
        yield from get_source_name(parent.node.proxy_socket.parent)

    ### otherwise, we just use the output name of the output socket found,
    ### regardless of whether it is an orphan redirect node or another
    ### kind of node
    else:
        yield parent.output_name
