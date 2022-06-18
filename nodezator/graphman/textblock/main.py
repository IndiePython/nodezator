"""Facility for text block class definition."""

### standard library import
from functools import partialmethod


### third-party import
from pygame.draw import rect as draw_rect


### local imports

from pygameconstants import SCREEN

from classes2d.single import Object2D

from graphman.textblock.surf  import get_text_block_surf
from graphman.textblock.check import check_text_block_text

### function for injection
from graphman.textblock.export import svg_repr


class TextBlock(Object2D):
    """Stores and manages text blocks."""

    ### inject function to work as method
    svg_repr = svg_repr


    ### method definitions


    def __init__(self, data, midtop=None):
        """Setup attributes for storage and control.

        Parameters
        ==========
        data (dict)
            data representing the comment instance.
        midtop (2-tuple of integers; or None)
            represents the absolute midtop position of
            the comment on screen. If no midtop is received
            (the default None is used), then the midtop
            information is retrieved from the comment data.
        """
        ### store the instance data argument in its own
        ### attribute
        self.data = data

        ### check whether text of text block is valid,
        ### raising exception if not;
        check_text_block_text(self.data['text'])

        ### store the midtop position

        self.midtop = (
          midtop if midtop is not None 
          else self.data['midtop']
        )

        ### create surface for image attribute
        self.image = get_text_block_surf(self.data['text'])

        ### create and position rect

        self.rect = self.image.get_rect()
        self.rect.midtop = self.midtop

        ### create controls to indicate when the text block
        ### was subject to a mouse events

        self.mouse_release_target = False
        self.mouse_click_target   = False

    def on_mouse_action(self, method_name, event):
        """Set flags according to given method name.

        Works by marking the text block as a target of the
        mouse release or mouse click action by change the
        values of the respective flags in specific ways.
        
        The flags are used to support the object selection
        and "move by dragging" features.

        Parameters
        ==========
        event
            (pygame.event.Event of
            pygame.MOUSEBUTTONDOWN/MOUSEBUTTONUP type)

            though we don't use it in this method, it is
            required in order to comply with protocol used;
          
            Check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        if method_name == 'on_mouse_click':
            self.mouse_click_target = True

        elif method_name == 'on_mouse_release':

            self.mouse_release_target = True
            self.mouse_click_target   = False

    on_mouse_click = partialmethod(
                         on_mouse_action, 'on_mouse_click')

    on_mouse_release = partialmethod(
                         on_mouse_action, 'on_mouse_release')

    def draw_selection_outline(self, color):
        """Draw outline around to indicate it is selected."""
        draw_rect(SCREEN, color, self.rect.inflate(4, 4), 4)

    def rebuild_surf(self):
        """Rebuild surf and update rect."""
        ### store the rect' current midtop coordinates
        midtop = self.rect.midtop

        ### recreate surface for image attribute from
        ### the text in self.data['text']
        self.image = get_text_block_surf(self.data['text'])

        ### update size of rect
        self.rect.size = self.image.get_size()

        ### restore the rect' midtop coordinates
        self.rect.midtop = midtop
