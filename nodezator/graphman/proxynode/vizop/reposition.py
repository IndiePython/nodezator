from ..constants import (
    NODE_OUTLINE_THICKNESS,
    LABEL_X_PADDING,
)


def reposition_elements(self):
    """Reposition elements within proxy node.

    As an administrative task, self.rect is properly
    resized and repositioned as well.
    """
    header_rect = self.header.rect

    self.label.rect.midleft = header_rect.move(LABEL_X_PADDING, 0).midleft

    proxy_socket = self.proxy_socket

    proxy_socket.rect.center = header_rect.midleft

    self.output_socket.rect.center = header_rect.midright

    try:
        widget = self.widget

    except AttributeError:
        self.add_button.rect.topleft = header_rect.bottomleft

        bottom = self.add_button.rect.bottom

    else:

        widget.rect.topleft = header_rect.bottomleft

        self.remove_button.rect.topleft = widget.rect.topright

        bottom = widget.rect.bottom

    ###

    self.rect.topleft = (proxy_socket.rect.left, header_rect.top)

    self.rect.size = (
        (self.output_socket.rect.right - proxy_socket.rect.left),
        (bottom - header_rect.top),
    )
