"""Utilities to assist in logging operations."""

### standard library import
from functools import partial


### local import
from ..ourstdlibs.collections.general import CallList


def get_logging_wrapper(logging_method):
    """Return wrapper function with logging behaviour.

    This is useful when instead of decorating a function
    so every call is logged, you just want to log specific
    calls. For instance, when you want to know when/from
    where an specific call was made.

    For instance, this function was originally created
    because we needed to log the specific calls made
    when the user clicked a command on the menu. That is,
    rather than know that the function executed, we wanted
    to know that the call was made from there.

    Parameters
    ==========
    logging_method (callable)
        the method of a logger used to perform logging
        from a specific level. One of 'debug', 'info',
        'warning', 'error', 'critical' or 'exception'
        methods.
    """

    def log_wrap_callable(message, callable_obj):
        """Wrap callable in logging call.

        This wrapper function, given a message and another
        callable object returns an object which, when called,
        performs the logging call just before calling the
        given object as well.

        Parameters
        ==========
        message (string)
            log message.
        callable_obj (callable)
            callable to be called just after the logging
            call is performed.
        """
        return CallList((partial(logging_method, message), callable_obj))

    return log_wrap_callable
