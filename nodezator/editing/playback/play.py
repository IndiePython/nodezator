"""Facility for triggering session playing."""

### local imports

from ...fileman.main import select_paths

from ...loopman.exception import ResetAppException



def set_session_playing():
    """Select path to recorded data and trigger playing it."""

    ### pick new path

    paths = (
        select_paths(caption="Select file containing data to be played")
    )

    ### if paths were given, there can only be one,
    ### it should be used as the new filepath

    if paths:

        ### gather data
        data = {"playing_data_path" : paths[0]}

        ### trigger session recording
        raise ResetAppException(mode='play', data=data)
