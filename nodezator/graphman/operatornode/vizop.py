"""Facility for visuals related node class extension."""

### standard library imports

from itertools import chain

from functools import partialmethod


### third-party import
from pygame.draw import rect as draw_rect


### local import
from ...pygameconstants import SCREEN


class VisualRelatedOperations:
    """Manages operations on visual node object."""

    def on_mouse_action(self, method_name, event):
        """Check whether any object was targeted by mouse.

        Works by checking if any object collided with
        mouse position when it was clicked/released and
        calling its respective method method if it exists.

        Parameters
        ==========

        event (pygame.event.Event of
            pygame.MOUSEBUTTONDOWN/MOUSEBUTTONUP type)

            required in order to comply with protocol
            used; needed here so we can retrieve the
            position of the mouse click in order to
            know over which object the mouse button was
            clicked/released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve mouse position
        mouse_pos = event.pos

        ### check whether any of the objects collided with
        ### the mouse position when it was clicked,
        ### calling the on_mouse_click method of the
        ### object if available

        for obj in chain(
          self.input_sockets,
          self.output_sockets,
        ):

            if obj.rect.collidepoint(mouse_pos):

                ### if the mouse release method exists,
                ### we store it and execute it, otherwise
                ### we just pass

                try: method = getattr(obj, method_name)
                except AttributeError: pass
                else: method(event)

                ### we then break out of the loop, since
                ### at this moment there will be no point
                ### in looking whether the other objects
                ### collided (we assume none of the
                ### objects' rects intersect)
                break

        ### if we don't collide with any object though, set
        ### flags according to the given method name;
        ###
        ### the flags are used to support the selection and
        ### "move by dragging" features

        else:

            if method_name == 'on_mouse_click':
                self.mouse_click_target = True

            elif method_name == 'on_mouse_release':

                self.mouse_release_target = True
                self.mouse_click_target   = False

    on_mouse_click = partialmethod(
                         on_mouse_action, 'on_mouse_click')

    on_mouse_release = partialmethod(
                         on_mouse_action, 'on_mouse_release')

    ### TODO should be used to trigger a popup menu with
    ### options specific to this node and its objects, like
    ### editing the label or marking the output socket to
    ### return data to the outside of the graph, etc.

    def on_right_mouse_release(self, event):
        """Check whether any object was targeted by mouse.

        Works by checking if any object collided with
        mouse position when its right button was released and
        calling its respective method method if it exists.

        Parameters
        ==========

        event (pygame.event.Event of
            pygame.MOUSEBUTTONUP type)

            required in order to comply with protocol
            used; needed here so we can retrieve the
            position of the mouse click in order to
            know over which object the mouse button was
            clicked/released.

            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        mouse_pos = event.pos

        for obj in chain(
          self.input_sockets,
          self.output_sockets,
        ):

            if obj.rect.collidepoint(mouse_pos):

                try: method = obj.on_right_mouse_release
                except AttributeError: pass
                else: method(event)

                break

    def draw(self):
        """Draw node visual elements on screen."""
        for obj in self.visual_objects: obj.draw()

    def draw_selection_outline(self, color):
        """Draw outline around to indicate it is selected."""
        draw_rect(SCREEN, color, self.rect.inflate(-8, 4), 4)

    def check_sockets_for_segment_definition(self, event):
        """Check whether any socket collides w/ event.pos.

        event.pos is the position of a mouse left button
        release event. If the output socket collides with
        it the socket must be sent for line segment
        definition.

        If the socket doesn't collide, line segment
        definition is cancelled.
        """
        mouse_pos = event.pos

        for socket in chain(
          self.input_sockets,
          self.output_sockets,
        ):

            if socket.rect.collidepoint(mouse_pos):
                break

        else: self.graph_manager.cancel_defining_segment()

        self.graph_manager.resume_defining_segment(socket)
