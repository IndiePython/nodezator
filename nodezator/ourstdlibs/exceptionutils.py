"""Facility for exception related utilities."""

### local imports
from .behaviour import return_untouched, get_decorator_from_wrapper


def bool_func_from_raiser(
    raiser_func,
    *,
    expected_exceptions=None,
    exceptions_to_reraise=(KeyboardInterrupt, SystemExit),
    reporting_func=return_untouched,
    new_message="",
    message_formatter=return_untouched,
    include_exception_name=True
):
    """Return a boolean function from exception raising one.

    Usage
    =====

    Used when you have a function which raises exceptions
    under certain conditions and want to replace it with a
    boolean function.

    The replacement function works in such manner that if
    an expected exception is thrown, it is caught and the
    execution proceeds normally until None is returned and,
    if no exception is raise, True is returned.

    Parameters
    ==========

    raiser_func (callable)
        raises exceptions under certain conditions; might
        have an 'expected_exceptions' attribute containing
        an exception class or tuple thereof.

    expected_exceptions (None, exception or tuple thereof)
        exception(s) to be supressed. If it is None, we
        try to retrieve this value from the attribute with
        the same name from the received raiser function.
        If such attribute doesn't exist, we use Exception.

    exceptions_to_reraise (exception or tuple thereof)
        indicate exception(s) you don't want to catch, but
        let them "bubble up"; we recommend to use the
        default value (both the KeyboardInterrupt and
        SystemExit exceptions).

    reporting_func (callable)
        used to report supressed exceptions; must accept
        a single argument which is the exception message
        from the supressed exception; default behaviour
        does nothing (besides returning the string
        untouched); we recommend using a logging function;

    new_message (string)
        if provided (not an empty string), it completely
        replaces the exception message from the exception
        caught.

    message_formatter (callable)
        must accept a single argument which is the message
        from the caught exception in order to format it to
        the user liking; it is used only if the new_message
        argument is an empty empty string; if you want to
        provide it, we recommend using the 'format' method
        of a custom string of your choice, otherwise the
        default value makes it so the received message is
        returned as-is.

    include_exception_name (boolean)
        indicates whether the message from the exception
        caught must include '[exception class name]: ' at
        the beginning or not, before being passed to the
        message_formatter callable, when it is used.
    """
    ### if no expected exception(s) are specified, check
    ### the function 'expected_exceptions' attribute;
    ### use Exception if the attribute doesn't exist

    if expected_exceptions is None:

        expected_exceptions = getattr(raiser_func, "expected_exceptions", Exception)

    ### define function

    def didnt_raise_expected(*args, **kwargs):
        """Return whether expected exception wasn't raised.

        When an exception is thrown, that is, an exception
        marked as expected, it is caught and reported, then
        the function proceeds to the end returning None.

        Otherwise, if no exception is thrown, we return True.
        """
        ### try executing the function with the received
        ### arguments
        try:
            raiser_func(*args, **kwargs)

        ### if an exception marked to be reraise is raised,
        ### reraise it as expected

        except exceptions_to_reraise as err:
            raise err

        ### if an exception marked as expected is raised,
        ### it is caught and the exception message is passed
        ### reported;

        except expected_exceptions as err:

            ### first of all define the exception message to
            ### be reported

            ## if a new message was given, use it
            if new_message:
                msg = new_message

            ## otherwise assemble a message from the
            ## message of the exception caught, whether
            ## preformated or not

            else:

                ## grab exception message

                raw_msg = (
                    ## preformat exception message
                    "{}: {}".format(err.__class__.__name__, str(err))
                    if include_exception_name
                    ## or use it as-is
                    else str(err)
                )

                ## then pass it through the custom
                ## formatter
                msg = message_formatter(raw_msg)

            ### then pass the message to the reporting
            ### function
            reporting_func(msg)

        ### if no exception is raised, though, we just
        ### return True
        else:
            return True

    ### return defined function
    return didnt_raise_expected


def new_raiser_from_existing(
    raiser_func,
    *,
    expected_exceptions=None,
    exceptions_to_reraise=(KeyboardInterrupt, SystemExit),
    new_exception=None,
    new_message="",
    message_formatter=return_untouched,
    include_exception_name=True
):
    """Wrap function in custom 'raise from' behaviour.

    Usage
    =====

    Used to provide better explanations about the cause of
    expected exceptions by providing a function which
    watches out for such exceptions, raising a custom
    exception if an expected exception is thrown.

    If the execution occurs without problems, though, the
    output is returned, in case it is needed somewhere.

    Parameters
    ==========

    raiser_func (callable)
        raises exceptions under certain conditions; might
        have an 'expected_exceptions' attribute containing
        an exception class or tuple thereof.

    expected_exceptions (None, exception or tuple thereof)
        exceptions(s) to be supressed. If it is None, we
        try to retrieve this value from the attribute with
        the same name from the received raiser function.
        If such attribute doesn't exist, we use Exception.

    exceptions_to_reraise (exception or tuple thereof)
        indicate exception(s) you don't want to catch, but
        let them "bubble up"; we recommend to use the
        default value (both the KeyboardInterrupt and
        SystemExit exceptions);

        One may thing whether this parameter should really
        exist at all, since we can just not catch such
        exceptions, instead of reraising them. However,
        this may be used to catch specific subclasses of
        exception that you don't want being caught by the
        except clause catching the expected exceptions.

        Say, for instance, that you want to catch an
        exception A, but it has a B subclass that you
        don't want to catch. The solution is simple, just
        define B as an exception to be reraised by
        passing it to this parameter.

    new_exception (new exception to be raised or None)
        exception to be raised from the caught one; if
        None is provided instead, we use the same class
        as the exception caught for the new exception
        to be raised.

    new_message (string)
        if provided (not an empty string), it completely
        replaces the exception message from the exception
        caught.

    message_formatter (callable)
        must accept a single argument which is the message
        from the caught exception in order to format it to
        the user liking; it is used only if the new_message
        argument is an empty empty string; if you want to
        provide it, we recommend using the 'format' method
        of a custom string of your choice, otherwise the
        default value makes it so the received message is
        returned as-is.

    include_exception_name (boolean)
        indicates whether the message from the exception
        caught must include '[exception class name]: ' at
        the beginning or not, before being passed to the
        message_formatter callable, when it is used.

    use_same_class (boolean)
        whether to use the same class of the exception
        caught to raise a new one. This works independently
        from the new_message/message_formatter mechanism
        (for more info, read the explanation about the
        parameters above), meaning you can still provide
        a custom message if you want.
    """
    ### if no expected exception(s) are specified, check
    ### the function 'expected_exceptions' attribute;
    ### use Exception if the attribute doesn't exist

    if expected_exceptions is None:

        expected_exceptions = getattr(raiser_func, "expected_exceptions", Exception)

    ### define function

    def raise_another_exception(*args, **kwargs):
        """If expected exception occurs, raise a new one."""
        ### try executing the function with the received
        ### arguments and storing the output
        try:
            output = raiser_func(*args, **kwargs)

        ### if an exception marked to be reraise is raised,
        ### do so

        except exceptions_to_reraise as err:
            raise err

        ### if an exception marked as expected is raised,
        ### it is caught and the new message is defined
        ### and the new exception is raiser in its place

        except expected_exceptions as err:

            ### first of all define the new exception
            ### message to use when raising

            ## if a new message was given, use it
            if new_message:
                msg = new_message

            ## otherwise assemble a message from the
            ## message of the exception caught, whether
            ## preformated or not

            else:

                ## grab exception message

                raw_msg = (
                    ## preformat exception message
                    "{}: {}".format(err.__class__.__name__, str(err))
                    if include_exception_name
                    ## or use it as-is
                    else str(err)
                )

                ## then pass it through the custom
                ## formatter
                msg = message_formatter(raw_msg)

            ### define the class for the new exceptions

            exception_class = (
                ## if new exception wasn't provided (it is
                ## None), use the same class as the exception
                ## caught
                err.__class__
                if new_exception is None
                ## otherwise use the new exception provided
                else new_exception
            )

            ### then pass the message to the exception
            ### class defined and raise the exception
            ### from the one we caught
            raise exception_class(msg) from err

        ### otherwise we just return the output
        else:
            return output

    ### return defined function
    return raise_another_exception


### get decorator version from new_raiser_from_existing
new_raiser_from_existing_deco = get_decorator_from_wrapper(new_raiser_from_existing)
