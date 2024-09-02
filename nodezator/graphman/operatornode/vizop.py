"""Facility for visuals related node class extension."""

### standard library imports

from itertools import chain

from functools import partialmethod


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ...config import APP_REFS

from ...pygamesetup import SCREEN

from .surfs import PARAM_DYS_FROM_TOP

from .constants import NODE_OUTLINE_THICKNESS


class VisualRelatedOperations:
    """Manages operations on visual node object."""

    def on_mouse_action(self, method_name, event):
        """Check whether any object was targeted by mouse.

        if not, act as though the node itself was the
        target of the mouse action.

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

                try:
                    method = getattr(obj, method_name)
                except AttributeError:
                    pass
                else:
                    method(event)

                ### we then break out of the loop, since
                ### at this moment there will be no point
                ### in looking whether the other objects
                ### collided (we assume none of the
                ### objects' rects intersect)
                break

        ### if we don't collide with any object though, we
        ### consider as though the node itself was the
        ### target of the mouse method;
        ###
        ### if such method is 'on_mouse_click' or
        ### 'on_mouse_release', set on or off
        ### 'mouse_click_target' flag according to the
        ### method name; the flag is used to support the
        ### "move by dragging" feature; if the event is
        ### 'on_mouse_release' we also change the selection
        ### state of this node;
        ###
        ### if we are dealing with a right mouse release
        ### method, we show the popup menu

        else:

            if method_name == "on_mouse_click":
                self.mouse_click_target = True

            elif method_name == "on_mouse_release":

                self.mouse_click_target = False
                APP_REFS.ea.change_selection_state(self)

            elif method_name == "on_right_mouse_release":

                (APP_REFS.ea.operator_node_popup_menu.show(self, event.pos))

    on_mouse_click = partialmethod(on_mouse_action, "on_mouse_click")

    on_mouse_release = partialmethod(on_mouse_action, "on_mouse_release")

    on_right_mouse_release = partialmethod(
        on_mouse_action,
        "on_right_mouse_release",
    )

    def draw(self):
        """Draw node visual elements on screen."""
        for obj in self.visual_objects:
            obj.draw()

    def draw_selection_outline(self, color):
        """Draw outline around to indicate it is selected."""
        draw_rect(SCREEN, color, self.body_rect.inflate(8, 8), 4)

    def update_body_surface(self):
        """Updates body's surface and rect."""
        ### update body's surface and size while keeping its midtop

        body = self.body

        midtop = body.rect.midtop

        body.image = self.get_node_surf()
        body.rect.size = body.image.get_size()

        body.rect.midtop = midtop

    def reposition_elements(self):
        """Used to reposition elements when setting mode.

        Also updates self.rect's size and position
        """
        ###
        body_rect = self.body.rect

        ###

        dx = NODE_OUTLINE_THICKNESS + 2
        dy = NODE_OUTLINE_THICKNESS

        self.label.rect.topleft = body_rect.move(dx, dy).topleft

        body_left = body_rect.left
        body_top  = body_rect.top

        ###

        if self.input_sockets:

            ## dys = delta ys, vertical distances
            dys = PARAM_DYS_FROM_TOP[self.data['operation_id']]

            for input_socket, dy in zip(self.input_sockets, dys):
                input_socket.rect.center = body_left, body_top + dy

        ###
        self.output_socket.rect.center = self.body.rect.midright

        ###
        rect = self.rect

        rect_left = rect.left = (
            ##
            self.input_sockets[0].rect.left
            if self.input_sockets
            ##
            else body_left
        )

        rect.width = self.output_socket.rect.right - rect_left

        ###
        rect.height = body_rect.height

        ###
        rect.top = body_top

