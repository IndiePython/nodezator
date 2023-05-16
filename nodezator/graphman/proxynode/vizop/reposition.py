

from ..constants import (
    NODE_OUTLINE_THICKNESS,
    LABEL_X_PADDING,
)


def reposition_elements(self):
    """Reposition elements within proxy node.

    As administrative tasks, references to visible
    objects are collected in dedicated collections
    and self.rect is properly resized and repositioned.
    """
    ###

    visual_objects = self.visual_objects
    mouse_aware_objects = self.mouse_aware_objects
    all_rects = self.all_rects

    visual_objects.clear()
    mouse_aware_objects.clear()
    all_rects.clear()

    ###

    header = self.header
    header_rect = header.rect

    bottom = header_rect.bottom

    visual_objects.append(header)
    all_rects.append(header_rect)

    ###

    label = self.label

    label.rect.midleft = header_rect.move(LABEL_X_PADDING, 0).midleft

    visual_objects.append(label)
    all_rects.append(label.rect)

    ### check whether proxy socket has a parent
    has_parent = 'source_name' in self.data

    ###

    proxy_socket = self.proxy_socket

    proxy_socket.rect.center = header_rect.midleft

    visual_objects.append(proxy_socket)
    mouse_aware_objects.append(proxy_socket)
    all_rects.append(proxy_socket.rect)

    ###

    output_socket = self.output_socket

    output_socket.rect.center = header_rect.midright

    visual_objects.append(output_socket)
    mouse_aware_objects.append(output_socket)
    all_rects.append(output_socket.rect)

    ###

    try:
        widget = self.widget

    except AttributeError:

        if not has_parent:

            add_button = self.add_button

            add_button.rect.topleft = header_rect.bottomleft

            visual_objects.append(add_button)
            mouse_aware_objects.append(add_button)
            all_rects.append(add_button.rect)

            bottom = self.add_button.rect.bottom

    else:

        if not has_parent:

            widget.rect.topleft = header_rect.bottomleft

            remove_button = self.remove_button

            remove_button.rect.topleft = widget.rect.topright

            for obj in (widget, remove_button):

                visual_objects.append(obj)
                mouse_aware_objects.append(obj)
                all_rects.append(obj.rect)

            bottom = max(widget.rect.bottom, remove_button.rect.bottom)

    ###

    self.rect.topleft = (proxy_socket.rect.left, header_rect.top)

    self.rect.size = (
        (output_socket.rect.right - proxy_socket.rect.left),
        (bottom - header_rect.top),
    )

    all_rects.append(self.rect)
