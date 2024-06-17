
### standard library imports

from datetime import datetime

from copy import deepcopy


### local imports

from ..config import APP_REFS

from ..ourstdlibs.behaviour import empty_function

from .constants import ID_FORMAT_SPEC

from . import testcases



### dict to hold system testing data for each session

_SESSION_DATA = {}
_TEST_CASES_STATS = {}


### functions

def prepare_system_testing_session(test_cases_ids, playback_speed):
    """Store relevant data beforing beginning testing session.

    Data will be included in the full report at the end of the
    testing session, after the last test finished.
    """

    _SESSION_DATA['requested_cases'] = test_cases_ids

    _SESSION_DATA['start_time'] = str(datetime.now())

    _SESSION_DATA['playback_speed'] = playback_speed

    _SESSION_DATA['test_cases_stats'] = _TEST_CASES_STATS


def perform_test_setup(test_case_id, data):
    """Grab and perform setup funcion."""
    ### grab test case module

    test_module = (
        getattr(

            testcases,
            'stc' + format(test_case_id, ID_FORMAT_SPEC)

        )
    )

    ### execute setup function, passing data namespace to it
    test_module.perform_setup(data)

    ### check whether test module has frame assertions and reference
    ### the indices on the data namespace if so

    if hasattr(test_module, 'FRAME_ASSERTION_MAP'):
        data.test_frames = test_module.FRAME_ASSERTION_MAP.keys()

    ### store dict for case stats
    case_stats = _TEST_CASES_STATS[test_case_id] = {}

    ### store case start time
    case_stats['start_time'] = str(datetime.now())

    ### create list to store triplets (3-tuples) containing assertion
    ### data (frame, text and result of that assertion)
    case_stats['assertions_result_triplets'] = []


def perform_frame_assertions(test_case_id, frame_index):
    """Grab and perform frame assertion for given case and frame index.

    We don't need to check for the existence of the map cause this is done
    in a previous step during playback.
    """
    ### reference dict for stats
    case_stats = _TEST_CASES_STATS[test_case_id]

    ### get special callable for storing results of individual assertions
    ### taking frame into consideration

    assertion_result_appender = (
        _get_appender_with_frame(
            frame_index,
            case_stats['assertions_result_triplets'].append
        )
    )

    ### grab test callable for the given frame

    test_callable = (

        ## grab test module

        (
            getattr(

                testcases,
                'stc' + format(test_case_id, ID_FORMAT_SPEC)

            )
        )

        ## then its map which references frame assertion callables
        .FRAME_ASSERTION_MAP

        ## and finally the test callable using the index as a key
        [frame_index]

    )

    ### try performing the test

    try:
        test_callable(assertion_result_appender)

    ## store error, if it occurs

    except Exception as err:

        if 'errors' in case_stats:
            case_states['errors'].append(str(err))

        else:

            case_stats['errors'] = [str(err)]
            case_stats['result'] = 'error'


def finish_test_case(test_case_id, frame_index):
    """Evaluate assertions for test case and store results."""
    ### grab test case module

    test_module = (
        getattr(
            testcases,
            'stc' + format(test_case_id, ID_FORMAT_SPEC)
        )
    )

    ### reference dict for stats
    case_stats = _TEST_CASES_STATS[test_case_id]

    ### perform assertions (tests)

    ## get special callable for storing results of individual assertions
    ## taking frame into consideration

    assertion_result_appender = (
        _get_appender_with_frame(
            frame_index,
            case_stats['assertions_result_triplets'].append
        )
    )

    ## perform assertions

    try:
        test_module.perform_final_assertions(assertion_result_appender)

    ## store error, if it occurs

    except Exception as err:

        if 'errors' in case_stats:
            case_stats['errors'].append(str(err))

        else:

            case_stats['errors'] = [str(err)]
            case_stats['result'] = 'error'

    ## in case there are no errors when we performed the assertions,
    ## define the final result, if not defined already

    else:

        if 'result' not in case_stats:

            passed = (
                all(
                    item[2]
                    for item in case_stats['assertions_result_triplets']
                )
            )

            case_stats['result'] = 'passed' if passed else 'failed'

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
    _SESSION_DATA['end_time'] = str(datetime.now())

    ## session result

    result_set = {
        case_stats['result']
        for case_stats in _TEST_CASES_STATS.values() 
    }

    if 'error' in result_set:
        _SESSION_DATA['result'] = 'error'

    elif 'failed' in result_set:
        _SESSION_DATA['result'] = 'failed'

    else:
        _SESSION_DATA['result'] = 'passed'

    ### deepcopy session data
    full_session_report = deepcopy(_SESSION_DATA)

    ### include system information
    full_session_report.update(APP_REFS.system_info)

    ### clear collections
    clear_collections()

    ### return full session report
    return full_session_report

def finish_system_testing_session_earlier(test_case_id):

    ### grab test case module and perform teardown funcion (if any)

    test_module = (
        getattr(
            testcases,
            'stc' + format(test_case_id, ID_FORMAT_SPEC)
        )
    )

    getattr(test_module, 'perform_teardown', empty_function)()

    ### clear collections
    clear_collections()

def clear_collections():
    _SESSION_DATA.clear()
    _TEST_CASES_STATS.clear()

def _get_appender_with_frame(frame_index, append):

    def appender(a_tuple):
        append((frame_index, *a_tuple))

    return appender
