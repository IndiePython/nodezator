
### standard library imports

from datetime import datetime

from copy import deepcopy


### local imports

from ..ourstdlibs.datetimeutils import UTC_OFFSET

from ..ourstdlibs.behaviour import empty_function

from . import testcases



### dict to hold system testing data for each session

_SESSION_DATA = {}
_TEST_CASES_STATS = {}


### functions

def prepare_system_testing_session(test_case_keys):
    """Store relevant data beforing beginning testing session.

    Data will be included in the full report at the end of the
    testing session, after the last test finished.
    """

    _SESSION_DATA['cases_requested'] = test_case_keys
    _SESSION_DATA['session_start_time'] = str(datetime.now())
    _SESSION_DATA['utc_offset'] = UTC_OFFSET

    _SESSION_DATA['test_cases_stats'] = _TEST_CASES_STATS



def perform_test_setup(test_case_key, data):
    """Grab and perform setup funcion."""
    ### grab and execute setup function, passing data namespace to it
    getattr(testcases, test_case_key).perform_setup(data)

    ### store dict for case stats
    case_stats = _TEST_CASES_STATS[test_case_key] = {}

    ### store case start time
    case_stats['start_time'] = str(datetime.now())


def finish_test_case(test_case_key):
    """Evaluate assertions for test case and store results."""
    ### grab test case module
    test_module = getattr(testcases, test_case_key)

    ### reference dict for stats
    case_stats = _TEST_CASES_STATS[test_case_key]

    ### perform assertions (tests)

    ## create dict to store test results
    result_data = {}

    ## perform them
    try:
        test_module.perform_assertions(result_data)

    ## store error, if occurs

    except Exception as err:

        case_stats['error'] = str(err)
        case_stats['final_result'] = 'error'

    ## store final results

    else:
        
        case_stats['final_result'] = (
            'passed'
            if all(result_data.values())
            else 'failed'
        )

    ### store result of individual assertions
    case_stats['assertions_results'] = result_data

    ### store end time
    case_stats['end_time'] = str(datetime.now())

    ### grab and perform teardown funcion (if any)
    getattr(test_module, 'perform_teardown', empty_function)()



def finish_system_testing_session_and_get_report():
    """Finish, copy and return full session report.

    Also clear collections to free memory.
    """
    ### Add the last missing data

    ## session end time
    _SESSION_DATA['session_end_time'] = str(datetime.now())

    ## overall result

    result_set = {
        case_stats['final_result']
        for case_stats in _TEST_CASES_STATS.values() 
    }

    if 'error' in result_set:
        _SESSION_DATA['overall_result'] = 'error'

    elif 'failed' in result_set:
        _SESSION_DATA['overall_result'] = 'failed'

    else:
        _SESSION_DATA['overall_result'] = 'passed'

    ### deepcopy session data
    full_session_report = deepcopy(_SESSION_DATA)

    ### clear collections

    for dict_obj in (
        _SESSION_DATA,
        _TEST_CASES_STATS,
    ):
        dict_obj.clear()

    ### return full session report
    return full_session_report
