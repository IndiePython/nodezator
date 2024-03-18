
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
    ... #?



def perform_test_setup(test_case_key):
    """Grab and perform setup funcion (if any)."""

    getattr(
        getattr(test_cases, test_case_key),
        'perform_setup',
        empty_function,
    )()


def finish_test_case(test_case_key):
    """"""

    ### grab test case module
    test_module = getattr(testcases, test_case_key)

    ### perform assertions (tests)

    ## create dict to store test results
    result_data = {}

    ## perform them
    try:
        test_module.perform_assertions(result_data)

    ## store error, if occurs

    except Exception as err:
        _store_error(err, test_case_key)


    ### store results for test

    else:
        _store_test_results(result_data, test_case_key)


    ### grab and perform teardown funcion (if any)
    getattr(test_module, 'perform_teardown', empty_function)()


def _store_test_results(result_data, test_case_key):
    ...

def finish_system_testing_session():
    """"""
    SESSION_DATA['session_end_time'] = str(datetime.now())
    ... #?
