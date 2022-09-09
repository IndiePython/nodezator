"""Utilities for time related operations."""

from math import floor
from collections import OrderedDict
from datetime import datetime


### constants definitions

## second and its (sub)multiples

SECOND = 1

# multiples

MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24

# submultiples

MILLISECOND = SECOND / 1000
MICROSECOND = MILLISECOND / 1000

## create a map with each (sub)multiple of a second
## define above, except for the microseconds as
## values mapped to a string representing a name
## for the value

second_multiples_map = OrderedDict(
    (("day", DAY), ("hr", HOUR), ("min", MINUTE), ("s", SECOND), ("msecs", MILLISECOND))
)


### function definitions

### XXX maybe the friendly format below could change name
### of time measurements slightly depending on whether the
### quantity has a single unit or more: for instance,
### 1min/10mins.


def friendly_delta_from_secs(delta_in_seconds):
    """Return human-friendly str for time interval.

    Parameters
    ==========
    delta_in_seconds (float)
        number of seconds comprising the time interval.

    Doctests
    ========

    >>> # delta seconds below could, for instance, come
    >>> # from the difference between 02 time.time()
    >>> # calls
    >>> delta_in_secs = 2.035

    >>> # obtain a human-friendly format for the delta
    >>> friendly_delta_from_secs(delta_in_secs)
    '2s 35msecs'
    >>> # works with negative deltas too
    >>> friendly_delta_from_secs(-delta_in_secs)
    '-2s 35msecs'

    >>> ### let's try other value

    >>> delta_in_secs = 0.02244
    >>> friendly_delta_from_secs(delta_in_secs)
    '22msecs 440.000usecs'

    >>> delta_in_secs = 0.00001203
    >>> friendly_delta_from_secs(delta_in_secs)
    '12.030usecs'
    """
    ### if zero seconds were given, return a custom string
    if not delta_in_seconds:
        return "0 secs"

    ### if delta is negative, obtain its absolute value;
    ### also set a flag depending on whether the signal
    ### was negative or not, to use later before
    ### returning the string

    if delta_in_seconds < 0:

        delta_in_seconds = abs(delta_in_seconds)
        was_negative = True

    else:
        was_negative = False

    ### alias seconds to quantity
    quantity = delta_in_seconds

    ### initialize a string
    string = ""

    ### compare the quantity of seconds to each
    ### value in the map

    for name, value in second_multiples_map.items():

        ### if a quantity is not given, break out of
        ### the loop
        if not quantity:
            break

        units_reached = floor(quantity / value)

        ### if quantity reaches at least one unit for
        ### the current value, then use it and decrement
        ### it from the current quantity

        if units_reached >= 1:

            ## update string
            string += " {}{}".format(units_reached, name)

            ## update quantity with the remaining
            ## quantity
            quantity = quantity - (units_reached * value)

    ### if there's still a quantity of seconds remaining,
    ### they represent microseconds or an even smaller
    ### units of time;
    ###
    ### treat such quantity appropriately

    if quantity:

        ### obtain the quantity of microseconds
        usecs = quantity / MICROSECOND

        ### we only include the quantity of microseconds
        ### in our string if it is higher than 0.0009
        ### microseconds;
        ###
        ### otherwise we consider it to be too
        ### insignificant to take into acount

        if usecs > 0.0009:

            ## the quantity of microseconds is included
            ## in the string with 03 decimal digits for
            ## extra precision when needed, that is,
            ## such decimals the values until 01
            ## nanosecond;
            ##
            ## though we allow such extra precision (until
            ## 01 nanosecond), we assume that:
            ##
            ## 1) most computers doesn't offer such
            ##    precision;
            ## 2) even if they did, the extra decimal units
            ##    "lost" wouldn't be significant or the
            ##    use-case would probably warrant a
            ##    separate function with specialized tools
            ##    to deal with such extra precision;
            ## 3) such values wouldn't be reliable, since
            ##    we already divide the original value
            ##    many times before getting to this
            ##    instruction and we don't even use
            ##    decimal.Decimal for extra precision;
            string += " {:.3f}usecs".format(usecs)

    ### strip whitespace
    string = string.strip()

    ### if delta was negative, add a '-' at the beginning
    ### of the string
    if was_negative:
        string = "-" + string

    ### finally return the string
    return string


def get_friendly_time():
    """Return current time in a human friendly format."""
    return datetime.now().strftime("%H:%M:%S")
