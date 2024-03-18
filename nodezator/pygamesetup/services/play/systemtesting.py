
### standard library import
from datetime import datetime


### local imports

from ....ourstdlibs.datetimeutils import UTF_OFFSET

from ....ourstdlibs.behaviour import empty_function

from . import testcases



### dict to hold system testing data for each session
SESSION_DATA = {}


### functions

def prepare_system_testing_session(data):
    """Store relevant data beforing beginning testing session.

    Data will be included in the full report at the end of the
    testing session, after the last test finished.
    """
    SESSION_DATA['cases_requested'] = data.test_case_keys
    SESSION_DATA['session_start_time'] = str(datetime.now())
    SESSION_DATA['utc_offset'] = UTC_OFFSET



def perform_test_setup(test_case_key):
    """Grab and perform setup funcion (if any)."""
    _grab_and_perform_operation(test_case_key, '_setup')


def finish_test_case(test_case_key):
    ### perform assertions (tests)

    ## grab function to perform assertions

    operation_name = f'perform_{test_case_keys}_assertions'
    perform_assertions = getattr(test_cases, operation_name)

    ## perform them, catching the results or errors
    try:
        result_data = perform_assertions()

    ## store error, if occurs

    except Exception as err:
        _store_error(err, test_case_key)


    ### store results for test

    else:
        _store_test_results(result_data, test_case_key)


    ### grab and perform teardown funcion (if any)
    _grab_and_perform_operation(test_case_key, '_teardown')


def _grab_and_perform_operation(key, suffix):
    """Put operation name together, grab it and execute it, if exists."""
    operation_name = key + suffix
    getattr(test_cases, operation_name, empty_function)()

def _store_test_results(results, test_case_key):

def finish_system_testing_session():
    """"""
    SESSION_DATA['session_end_time'] = str(datetime.now())
