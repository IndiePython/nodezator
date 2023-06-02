"""Function to extend VisualRelatedOperations class."""

### local imports
from ..constants import BODY_CONTENT_OFFSET, NODE_OUTLINE_THICKNESS



def reposition_callable_elements(self):
    """Reposition objects inside the node in callable mode.

    The repositioning is made from the input
    downwards (the top rectsman doesn't need to be
    repositioned, it always stays at the same relative
    position within the node).

    Another administrative task is performed, which is
    updating the height of self.rect.
    """
    ### reference the top rectsman locally
    top_rectsman = self.top_rectsman

    ### position callable output socket
    self.callable_output_socket.rect.midtop = top_rectsman.move(0, -2).bottomright

    ### define a top coordinate which is the bottom of
    ### the top of the node plus the body content
    ### offset given as a constant
    top = top_rectsman.bottom + BODY_CONTENT_OFFSET

    ### position the id text object

    ## reference the rect of the id text object locally
    id_text_rect = self.id_text_obj.rect

    ## align its top with the last defined top, which
    ## is the bottom of the pair last output socket
    ## and the text rect; also push it 4 pixels down
    ## for extra padding

    id_text_rect.top = top
    id_text_rect.top += 4

    ## align the centerx of the id text object with
    ## the centerx of the top rectsman, so it is
    ## horizontally centered on the node
    id_text_rect.centerx = top_rectsman.centerx

    ### position the bottom rectsman

    ## reference the bottom rectsman in a local variable
    bottom_rectsman = self.bottom_rectsman

    ## align the centerx of the bottom rectsman with
    ## the centerx of the top rectsman, so it is
    ## horizontally centered on the node
    bottom_rectsman.centerx = top_rectsman.centerx

    ## align the bottom of the bottom rectsman with
    ## the bottom of the id text object, then push
    ## the bottom rectsman just a bit down in order
    ## to compensate for the node outline and add
    ## a bit of padding

    bottom_rectsman.bottom = id_text_rect.bottom
    bottom_rectsman.top += NODE_OUTLINE_THICKNESS + 4

    ### perform extra administrative task: updating
    ### the height of self.rect
    self.rect.height = bottom_rectsman.bottom - top_rectsman.top
