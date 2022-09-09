"""Label related class extension for WindowManager."""

### standard library imports

from math import floor
from functools import partial
from itertools import cycle


### third-party import
from pygame.mouse import get_pos as get_mouse_pos


### local imports

from ..config import APP_REFS

from ..translation import TRANSLATION_HOLDER as t

from ..pygameconstants import SCREEN_RECT

from ..fontsman.constants import (
    FIRA_MONO_BOLD_FONT_HEIGHT,
    FIRA_MONO_BOLD_FONT_PATH,
)

from ..colorsman.colors import WM_LABEL_FG, WM_LABEL_BG

from ..textman.label.autolabel import AutoLabel


##### constant definition

AUTOLABEL_KWARGS = {
    "font_height": FIRA_MONO_BOLD_FONT_HEIGHT,
    "font_path": FIRA_MONO_BOLD_FONT_PATH,
    "foreground_color": WM_LABEL_FG,
    "background_color": (*WM_LABEL_BG, 130),
}

##### utility functions and objects


def get_scrolling_amount(assistant):
    """Return custom formatted, scroll amount.

    assistant (the editing.EditingAssistant instance)
    """
    ### we get the opposite of the scrolling amount
    ### vector (using the opposite is an usability measure,
    ### so the scrolling amount shows a number as if the
    ### screen had moved, when in fact it was the objects in
    ### the world which moved in the opposite direction) and
    ### map it to the int constructor
    result = map(int, -assistant.scrolling_amount)

    ### then return the formated version of the result
    return "({:>4}, {:>4})".format(*result)


##### class definition


class MonitorLabelSetup:
    """Data and behaviour for monitor label setup."""

    def instantiate_labels(self):
        """Instantiate and set monitoring labels."""
        ### status label

        self.status_label = AutoLabel(
            partial(getattr, APP_REFS, "status_message"),
            formatter=(t.window_manager.status + ": {}").format,
            text="Opened file",
            **AUTOLABEL_KWARGS,
        )

        ### scrolling amount

        self.scrolling_label = AutoLabel(
            partial(get_scrolling_amount, APP_REFS.ea),
            formatter="x, y: {}".format,
            text="(    0,    0)",
            **AUTOLABEL_KWARGS,
        )

        ### position labels
        self.reposition_labels()

        ### gather draw and update behaviours from labels

        labels = (
            self.status_label,
            self.scrolling_label,
        )

        self.labels_update_methods = [label.update for label in labels]

        self.labels_drawing_methods = [label.draw for label in labels]

    def reposition_labels(self):

        self.status_label.rect.bottomleft = SCREEN_RECT.bottomleft

        self.scrolling_label.rect.bottomleft = self.status_label.rect.topleft
