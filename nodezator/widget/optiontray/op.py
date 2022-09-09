"""Option tray class extension with lifetime operations."""

### local import
from ...classes2d.single import Object2D


class OptionTrayLifetimeOperations(Object2D):
    """Operations for the lifetime of the OptionTray.

    That is, operations that are mostly or only used while
    the option menu is alive, as opposed to the ones used
    to assist in instantiating/setting it up.
    """

    def update_image(self):
        """Set image attribute according to value."""
        self.image = self.surface_map[self.value]

    def get(self):
        """Return current value of OptionTray instance."""
        return self.value

    def set(self, value, custom_command=True):
        """Set the current value of this OptionTray instance.

        Parameters
        ==========
        value (any python object)
            value to which the widget will be set. It must
            be equal to one of the available options in the
            list from the "options" attribute;
            no type checking is performed, since the items
            of the option list are already type checked;
        custom_command (boolean)
            indicates whether the custom command must be
            executed or not after updating the value.
        """
        ### if the value is already set, exit the method by
        ### returning, since choosing a value which is
        ### already chosen isn't considered a change at all
        if self.value == value:
            return

        ### if value received isn't within allowed values
        ### (values inside list in "options" attribute),
        ### report and cancel this operation by returning

        if value not in self.options:

            print("'value' isn't among available options")
            return

        ### if we reach this point in the method, then we
        ### can safely set the new value and perform other
        ### related operations

        ## assign the value to the "value" attribute
        self.value = value

        ## update image so it corresponds with value
        self.update_image()

        ## execute custom command if requested
        if custom_command:
            self.command()

    def reset_value_and_options(self, value, options, custom_command=True):
        """Reset available options and set given value.

        Parameters
        ==========
        value (Python value)
            the value must be inside the options iterable
            as well, and be of one of the allowed types
            (str, int, float, bool) or must be None.
        options (iterable of values)
            values the widget is allowed to assume. Each
            value in the options must be of type str, int
            float, bool or must be None.
        custom_command (boolean)
            indicates whether the custom command must be
            executed or not.
        """
        ### make sure options is a list
        options = list(options)

        ### check conditions that justify cancelling the
        ### operation; if any of them are confirmed, just
        ### exit the method by returning

        ## check whether the options are the same as the
        ## current ones (and in the same order)

        if options == self.options:

            print(
                "new options provided are the same as the"
                " current ones and in the same order"
            )

            return

        ## check whether the value and options are valid

        try:
            self.validate_value_and_options(value, options)
        except (ValueError, TypeError) as err:

            print(err)
            return

        ### if we reach this point in the method, then we
        ### can safely replace the options and set the new
        ### value as well as perform other related
        ### operations

        ## backup the current topleft position
        topleft = self.rect.topleft

        ## set the value and the options

        self.value = value
        self.options = options

        ## set the surface map and right coordinates;
        ## this also automatically updates the 'image'
        ## attribute with a new surface and creates a
        ## new pygame.Rect for the 'rect' attribute
        self.set_surface_map_and_right_coordinates()

        ## restore the topleft position
        self.rect.topleft = topleft

        ## execute custom command if requested
        if custom_command:
            self.command()

    def on_mouse_release(self, event):
        """Set the value under the mouse.

        That is, we determine which value is under the
        mouse based on the position of the relative to
        the right coordinate of each available option
        in this option tray widget and then passes the
        value to the set() method, which sets it as the
        new value of this widget, if it is different
        than the current one.

        Parameters
        ==========
        event
            (pygame.event.Event of pygame.MOUSEBUTTONUP
            type)

            we retrieve the position of the mouse from it,
            to find which value was pressed;

            check pygame.event module documentation on
            pygame website for more info about this event
            object.
        """
        ### retrieve mouse x position
        mouse_x = event.pos[0]

        ### retrieve x position of this widget
        widget_x = self.rect.x

        ### obtain the mouse x coordinate relative to
        ### the widget's x coordinate (horizontal origin)
        relative_mouse_x = mouse_x - widget_x

        ### iterate over the available options and their
        ### respective right coordinates looking for the
        ### value whose right coordinate is located after
        ### the mouse relative x position;
        ###
        ### after we leave "for loop", the 'value'
        ### variable will be holding the value for which
        ### we are looking, that is, the one that we
        ### clicked (actually, the one over which we
        ### released the mouse)

        for value, value_right in zip(self.options, self.right_coordinates):
            if relative_mouse_x < value_right:
                break

        ### we finally pass the value to set(), which will
        ### set it as the new value for this widget, if it
        ### is different than the current one
        self.set(value)
