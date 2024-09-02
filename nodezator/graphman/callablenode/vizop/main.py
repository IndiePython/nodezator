"""Facility for visuals related node class extension."""

### standard library imports

from itertools import chain
from functools import partialmethod


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from ....config import APP_REFS

from ....pygamesetup import SCREEN, SCREEN_RECT

## functions to extend class

from .expandedreposition import reposition_expanded_elements
from .collapsedreposition import reposition_collapsed_elements
from .callablereposition import reposition_callable_elements

from .collapsing import collapse_unconnected_elements



class VisualOperations:
    """Manages operations on visual node object."""

    ### functions to extend class operations

    reposition_expanded_elements = reposition_expanded_elements
    reposition_collapsed_elements = reposition_collapsed_elements
    reposition_callable_elements = reposition_callable_elements

    collapse_unconnected_elements = collapse_unconnected_elements

    ### method definitions

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

        for obj in self.yield_mouse_aware_objects():

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
        ### 'on_mouse_release', set on or off the
        ### mouse_click_target flag according to the
        ### method name; the flag is used to support the
        ### "move by dragging" feature; the method
        ### 'on_mouse_release' also causes the selection
        ### state of the object to change;
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
                self.show_popup_menu(event.pos)

    on_mouse_click = partialmethod(on_mouse_action, "on_mouse_click")

    on_mouse_release = partialmethod(on_mouse_action, "on_mouse_release")

    on_right_mouse_release = partialmethod(
        on_mouse_action,
        "on_right_mouse_release",
    )

    def yield_mouse_aware_objects_in_expmode(self):

        yield from chain(
            self.visible_widgets,
            self.live_keyword_entries,
            self.placeholder_add_buttons,
            self.visible_remove_widget_buttons,
            self.subparam_up_buttons,
            self.subparam_down_buttons,
            self.input_sockets,
            self.output_sockets,
            self.placeholder_sockets,
        )

        yield self.sigmode_toggle_button

    def yield_mouse_aware_objects_in_colmode(self):

        yield from chain(
            self.input_sockets,
            self.output_sockets,
            self.visible_widgets,
        )

        yield self.sigmode_toggle_button

    def yield_mouse_aware_objects_in_calmode(self):
        yield from self.output_sockets

    def draw(self):
        """Draw node elements on screen."""
        for obj in self.yield_visible_objects():
            obj.draw()

    def yield_visible_objects_in_expmode(self):

        yield from chain(
            self.background_and_text_elements,
            self.visible_widgets,
            self.live_keyword_entries,
            self.placeholder_add_buttons,
            self.visible_remove_widget_buttons,
            self.subparam_up_buttons,
            self.subparam_down_buttons,
            self.unpacking_icons,
            self.input_sockets,
            self.output_sockets,
            self.placeholder_sockets,
        )

        yield self.sigmode_toggle_button

    def yield_visible_objects_in_colmode(self):

        yield from chain(
            self.background_and_text_elements,
            self.input_sockets,
            self.output_sockets,
            self.visible_widgets,
        )

        yield self.sigmode_toggle_button

    def yield_visible_objects_in_calmode(self):

        yield from chain(
            self.background_and_text_elements,
            self.output_sockets,
        )

    def draw_selection_outline(self, color):
        """Draw outline around to indicate it is selected."""
        draw_rect(SCREEN, color, self.rect.inflate(-8, 4), 4)

    def yield_visible_sockets_in_expmode(self):

        yield from chain(
            self.input_sockets,
            self.output_sockets,
            self.placeholder_sockets,
        )

    def yield_visible_sockets_in_colmode(self):

        yield from chain(
            self.input_sockets,
            self.output_sockets,
        )

    def yield_visible_sockets_in_calmode(self):
        yield from self.output_sockets

    def toggle_sigmode(self, event):

        mode_name = self.data.get('mode', 'expanded_signature')

        if mode_name == 'expanded_signature':
            self.set_mode('collapsed_signature')


        elif mode_name == 'collapsed_signature':
            self.set_mode('expanded_signature')

    def anchor_viewer_objects_to_node(self):

        pos = self.get_anchor_pos()
        toolbar_rect = self.preview_toolbar.rect

        toolbar_rect.topleft = pos
        self.preview_panel.rect.topleft = toolbar_rect.bottomleft

    def get_anchor_below_output(self):
        return self.top_rectsman.right, self.output_rectsman.bottom + 5

    def get_anchor_below_visible_output(self):

        return self.top_rectsman.right, (
            self.visible_output_sockets[-1].rect.bottom
            if self.visible_output_sockets
            else self.top_rectsman.bottom
        ) + 5

    def viewer_objects_drawing(self):

        for obj in self.viewer_objects:

            if obj.rect.colliderect(SCREEN_RECT):
                obj.draw()
