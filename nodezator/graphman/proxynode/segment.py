

from graphman.socket.surfs import type_to_codename


class SegmentOps:
    """Segment defining operations for proxy node."""

    def signal_connection(self):
        """Act on establishment of incomming connection."""
        ## update source name and type_codename

        source_name = self.data['source_name'] = (
          self.proxy_socket.parent.output_name
        )

        type_codename = self.proxy_socket.type_codename

        self.data['source_type_codename'] = type_codename

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

        del self.data['source_name']
        del self.data['source_type_codename']

        ## update label surface
        self.update_label_surface()

        ## check header width
        self.check_header_width()

        ###

        try: widget = self.widget

        except AttributeError:
            type_codename = None

        else:

            expected_type = widget.get_expected_type()

            type_codename = (
              type_to_codename(expected_type)
            )

        self.proxy_socket.update_type_codename(
                            type_codename
                          )

        output_socket = self.output_socket

        output_socket.update_type_codename(type_codename)

        self.propagate_output(
               self.label_text, type_codename
             )

    def propagate_output(self, source_name, type_codename):

        ## propagate type codename

        try: children = self.output_socket.children

        except AttributeError: pass

        else:

            for child in children:
                
                node = child.node
                
                if any(

                  not hasattr(node, attr_name)

                  for attr_name in (
                    'output_socket',
                    'proxy_socket',
                  )

                ): continue

                output_socket = node.output_socket

                node.data['source_name'] = source_name
                node.data['source_type_codename'] = (
                       type_codename
                     )

                node.proxy_socket.update_type_codename(
                                    type_codename
                                  )

                node.output_socket.update_type_codename(
                                     type_codename
                                   )

                ## update label surface
                node.update_label_surface()

                ## check header width
                node.check_header_width()

                node.propagate_output(
                       source_name, type_codename
                     )
