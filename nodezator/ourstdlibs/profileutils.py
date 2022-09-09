"""Facility for profiling tools."""

### standard library imports

from time import time

from contextlib import contextmanager

from functools import wraps


### local imports

from .timeutils import friendly_delta_from_secs

from .pyl import load_pyl, save_pyl


@contextmanager
def elapsed_time_printed(current_time_func=time, formatter=friendly_delta_from_secs):
    """Print time elapsed during "with block" execution.

    That is, print the time between the beginning
    of the "with block" (just before yielding) and
    its end (just after yielding, when execution
    flow returns to this generator).

    Parameters
    ==========
    current_time_func (callable)
        used to obtain the value of the current time;
        default is time.time() from standard library,
        which returns the current time in seconds since
        the Epoch.
    formatter (callable)
        execution time is passed through this callable
        before being printed.
    """
    ### store the start time
    start = current_time_func()

    ### yield so we enter the "with block"
    yield

    ### store difference between current and start time
    execution_time = current_time_func() - start

    ### print formated execution time
    print(formatter(execution_time))


def get_time_tracking_ctman(
    filepath,
    profiling_title="Different ways of doing a task",
    solution_title="Solution A",
    quantity_at_which_to_save=10,
    current_time_func=time,
):
    """Return context manager which stores time intervals.

    Returns a function similar to elapsed_time_printed(),
    but instead of printing the time interval, every time
    it is used it stores the interval.

    Once a predefined number of intervals are stored, the
    intervals are saved in a custom .json file using the
    save_intervals() function.

    Parameters
    ==========
    filepath, profiling_title, solution_title (string)
        check save_intervals() function's docstring for a
        description of such parameters.
    quantity_at_which_to_save (integer)
        intervals are saved when reaching this quantity.
    current_time_func (callable)
        used to obtain the value of the current time;
        default is time.time() from standard library,
        which returns the current time in seconds since
        the Epoch.
    """
    ### create a list wherein to store the intervals
    intervals = []

    @contextmanager
    def execution_time_stored():
        """Store execution time of "with block".

        Also triggers the saving of such data when it
        reaches a predefined quantity.
        """
        ### store the start time
        start = current_time_func()

        ### yield so we enter the "with block"
        yield

        ### store difference between current and start time
        intervals.append(current_time_func() - start)

        ### save intervals if the predefined quantity is
        ### reached

        if len(intervals) == quantity_at_which_to_save:

            save_intervals(intervals, filepath, profiling_title, solution_title)

    return execution_time_stored


def get_time_tracking_deco(
    filepath,
    profiling_title="Different ways of doing a task",
    solution_title="Solution A",
    quantity_at_which_to_save=10,
    current_time_func=time,
):
    """Return decorator function which stores time intervals.

    Works just like get_time_tracking_ctman(), but instead
    of returning a context manager, it returns a decorator
    function instead, which stores the execution time of
    each run of the callable decorated.

    Parameters
    ==========
    Same parameters as in get_time_tracking_ctman() as
    save_intervals().
    """
    ### define the decorator function

    def time_tracking_decorator(callable_obj):
        """Decorates given callable to track its time."""

        ### create a list wherein to store the intervals
        intervals = []

        ### define the wrapper function

        @wraps(callable_obj)
        def time_tracking_wrapper(*args, **kwargs):
            """Store execution time of wrapped callable.

            Also triggers the saving of such data when it
            reaches a predefined quantity.
            """
            ### store the start time
            start = current_time_func()

            ### execute wrapped callable w/ given arguments
            callable_obj(*args, **kwargs)

            ### store difference between current and
            ### start time
            intervals.append(current_time_func() - start)

            ### save intervals if the predefined quantity is
            ### reached

            if len(intervals) == quantity_at_which_to_save:

                save_intervals(intervals, filepath, profiling_title, solution_title)

        ### return the wrapper function
        return time_tracking_wrapper

    ### return the decorator function
    return time_tracking_decorator


def save_intervals(
    intervals,
    filepath,
    profiling_title="Different ways of doing a task",
    solution_title="Solution A",
):
    """Save intervals in custom .json format.

    Works by saving the given intervals (a list of floats)
    in a given path as a .json file, within a nested
    dictionary where the top level stores data within
    a named group and the bottom level stores the given
    intervals using the dataset name as the key.

    Parameters
    ==========
    intervals (list of floats)
        list of time intervals to be saved; the type of the
        items depend on the function used to obtain the
        current time, but this kind of function usually
        returns time in seconds as a float.
    filepath (string)
        represents location of file wherein to save the
        intervals.
    profiling_title (string)
        name used to group different sets of time
        intervals; it is used as a key in a dictionary
        wherein we store different lists of time intervals
        belonging to this group.
    solution_title (string)
        name to identify the specific set of time intervals
        to be stored; it is used as a key in a dictionary
        wherein the intervals are stored; these time
        intervals represent the performance of a specific
        solution.
    """
    ### try loading the json data from the given path
    try:
        data = load_pyl(filepath)

    ### create it if it doesn't exist
    except FileNotFoundError:
        data = {}

    ### store the given data

    ## try retrieving the dictionary where the group data is
    ## stored
    try:
        group_data = data[profiling_title]

    ## create it if it doesn't exist
    except KeyError:
        group_data = data[profiling_title] = {}

    ## store the intervals in the group data using the
    ## provided key
    group_data[solution_title] = intervals

    ### finally save the json data in the given path
    save_pyl(data, filepath)
