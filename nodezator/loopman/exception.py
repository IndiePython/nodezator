"""Loop management exceptions."""

### third-party import
from pygame.event import clear as clear_events


### local import
from ..config import APP_REFS


class SwitchLoopException(Exception):
    """Raised when the loop holder is switched.

    Check the application glossary to know about GUD
    managers.
    """

    def __init__(self, loop_holder=None):
        """Store loop holder."""
        ### store a loop holder instance according to the
        ### value of the loop_holder argument

        self.loop_holder = (
            loop_holder if loop_holder is not None else APP_REFS.wm
        )

        ### admin task: clear event queue to prevent events
        ### generated in the current loop holder to spill into
        ### the new loop holder
        clear_events()

        ### initialize superclass with custom message
        super().__init__("Switch loop holder.")


class ContinueLoopException(Exception):
    """Raised whenever we need to restart the loop.

    By restart, we mean going into the beginning of
    loop then continuing normally, just like a
    "continue" statements does inside a "while" block,
    hence the name of this exception.
    """


class QuitAppException(Exception):
    """Raise whenever you want to quit the app."""

class CloseFileException(Exception):
    """Raise whenever you want to close the loaded file."""


EXISTING_MODES = frozenset({'normal', 'play', 'record' })

class ResetAppException(Exception):
    """Raised whenever you want to reset the app.

    Resetting the app means bring it back to an initial state.
    Such initial state is when it is just launched, either
    with or without a loaded file.
    """

    def __init__(self, mode, data=None):
        """Store loop holder."""

        ### check mode

        if mode not in EXISTING_MODES:
            raise ValueError(f"'mode' must be one of {EXISTING_MODES}")

        ### store/set arguments

        self.mode = mode
        self.filepath = None

        ### store data if any (might override 'filepath' attribute)

        if data is not None:

            ## data cannot reset the 'mode' though
            if 'mode' in data:
                raise ValueError("'data' dict cannot have 'mode' as key")

            ## store data as attributes
            self.__dict__.update(data)

        ### initialize superclass with custom message
        super().__init__("Reset the app.")
