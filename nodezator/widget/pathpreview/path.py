"""Path(s) preview widget."""

### local imports

from ...textman.viewer.main import view_text

from .base import _BasePreview


### message when displaying value of widget

VALUE_DISPLAY_MESSAGE = """
Below you can see the value stored on the widget. To change
the value, leave this text view and click on the small folder
icon in the topleft corner of the widget
""".strip()


### class definition


class PathPreview(_BasePreview):
    """"""

    def preview_paths(self):
        """Preview paths."""

        formatted_value = (
            repr(self.value)
            if isinstance(self.value, str)
            else ("(\n" + ",\n".join(repr(item) for item in self.value) + ")")
        )

        text = VALUE_DISPLAY_MESSAGE + "\n\n" + formatted_value

        view_text(text)
