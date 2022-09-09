from ...our3rdlibs.behaviour import indicate_unsaved


def update_with_widget(data, key, widget):
    """Update data's key with value from widget.

    Parameters
    ==========
    data (dict)
        dict whose given key is to be updated.
    key (string)
        key to be update.
    widget (custom Python class)
        use its 'get' method to retrieve the value.
    """
    ### check whether changes in data must be indicated

    ## get current and new value

    current = data[key]
    new = widget.get()

    ## if the new value is equal to the current one,
    ## return earlier
    if new == current:
        return

    ### otherwise update the value in the data and indicate
    ### that the data was changed

    data[key] = widget.get()
    indicate_unsaved()
