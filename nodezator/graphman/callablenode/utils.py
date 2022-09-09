"""Facility for widget data update for node classes."""

### local import
from ...our3rdlibs.behaviour import indicate_unsaved


def update_with_widget(data, key, widget, remove_button=None):
    """Update data's key with value from widget.

    Parameters
    ==========
    data (dict)
        dict whose given key is to be updated.
    key (string)
        key to be update.
    widget (custom Python class)
        use its 'get' method to retrieve the value.
    remove_button (None or obj)
        if an obj is given, align its right side with the
        left side of the widget when the value changes
        if their rects collide.
    """
    ### check whether changes in data must be indicated

    ## get current and new value

    current = data[key]
    new = widget.get()

    ## if the new value is equal to the current one,
    ## return earlier
    if new == current:
        return

    ### otherwise update the value in the data,
    ### align the button with the widget if the button
    ### is given and indicate that the data was changed

    data[key] = widget.get()

    if remove_button is not None:
        remove_button.rect.left = widget.rect.right

    indicate_unsaved()
