"""Facility for specialized label for value monitoring."""

### local imports

from .main import Label

from ...colorsman.colors import BLACK


class AutoLabel(Label):
    """A label with custom autoupdating ability."""

    def __init__(self, monitor_routine, formatter=str, **kwargs):
        """Perform setups and assign data for reuse.

        Extends appcommon.text.label.main.Label.__init__

        monitor_routine (callable)
            to be executed every loop to check for changes
            in its return value.
        formatter
        (any callable which returns a string,
        default is str)
            use to format the output of the monitor
            routine. You'll usually want to use a custom
            str.format bound method (for instance:
            "Distance: {} meters".format), but you can go
            crazy and use any callable you want, as long as
            it returns a string.
        kwargs (keyword arguments)
            keyword arguments for the
            appcommon.text.label.main.Label constructor.
            Check Label class constructor in
            appcommon/text/label/main.py for the list of
            available keyword arguments.
        """
        ### store arguments

        self.monitor_routine = monitor_routine
        self.formatter = formatter

        ### apply formatter to text if text was provided
        try:
            formatted_text = self.formatter(kwargs["text"])
        except KeyError:
            pass
        else:
            kwargs["text"] = formatted_text

        ### initialize superclass
        super().__init__(**kwargs)

    def update(self):
        """Update and draw label.

        Uses BasicObj.draw and
        appcommon.text.label.main.Label.set.
        """
        text = self.formatter(self.monitor_routine())
        self.set(text)
