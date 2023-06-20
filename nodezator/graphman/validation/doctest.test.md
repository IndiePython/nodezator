# Doctests for the graphman/validation/main.py module 

## Introduction

The module being tested here contains a function to validate function metadata called `check_return_annotation_mini_lang()`.


## Imports and data loaded from external files

Note that the doctests contain no import statements or data being loaded from other files, since the needed objects are imported, loaded and fed to the namespace automatically in the sibling `testmarkdown.py` module (using the `globs` parameter of `doctest.DocFileSuite()`). In the case of this doctest document in particular, the only import needed is the function we want to test: `check_return_annotation_mini_lang`. We also load a dictionary containing test data, which we call `TEST_DATA` in the doctests in this document.

## Utilities

Here we define some extra utilities to assist us in our tests.

```python
### an exception class map to convert strings into the exception classes
### to which they refer
>>> exception_class_map = {
...   "TypeError"  : TypeError,
...   "ValueError" : ValueError
... }

>>> ### a function to test another given function using given test data
>>> def test_function_with_test_data(function, test_data):
...     
...     ### store the function name
...     func_name = function.__name__
... 
...     ### let's test compliant cases
... 
...     ## load compliant cases
...     compliant_cases = test_data['compliant_cases']
... 
...     ## iterate over them
...     for case_name, case_data in compliant_cases.items():
... 
...         ## try executing function with case data
...         try: function(case_data)
... 
...         ## if an exception is raised, we report it along
...         ## with the case name by printing them, which
...         ## causes this doctest to fail, since it doesn't
...         ## expect anything to be printed
... 
...         except Exception as err:
...         
...             msg = (
...               '{} of function {} failed: {}'
...             ).format(case_name, func_name, str(err))
... 
...             print(msg)
... 
...     ### and let's now test all the non-compliant cases
... 
...     ## load the non-compliant cases
...     non_compliant_cases = test_data['non_compliant_cases']
... 
...     ## load the error data about the cases
...     error_data = test_data['non_compliance_error_data']
... 
...     ## iterate over non-compliant case items, testing them
... 
...     items = non_compliant_cases.items()
... 
...     for case_name, case_data in items:
... 
...         ## let's check whether the case actually raises
...         ## errors, as expected validates, reporting if
...         ## one of them succeeds
... 
...         # try executing function with case data
...         try: function(case_data)
... 
...         # if an exception is raised, check whether it is
...         # of the expected class and has an expect excerpt
...         # of text
... 
...         except Exception as err:
... 
...             # get error data for case
... 
...             specific_error_data = error_data[case_name]
... 
...             cls_string = specific_error_data['type']
...             cls = exception_class_map[cls_string]
... 
...             excerpt = specific_error_data[
...                                      'message_excerpt']
... 
...             # check whether actuall error is the expected
...             # error by checking its type and whether it
...             # contains an expected excerpt of the message
... 
...             if not isinstance(err, cls):
... 
...                 msg = (
...                   "non-compliant case {} of function {}"
...                   " failed with an unexpected error"
...                   " type: {}"
...                 ).format(case_name, func_name,
...                                          str(type(err)))
... 
...                 print(msg)
... 
...             if excerpt not in str(err):
... 
...                 msg = (
...                   "non-compliant case {} of function {}"
...                   " failed with an unexpected error"
...                   " message: {}"
...                 ).format(case_name, func_name, str(err))
... 
...                 print(msg)
... 
...         # if no exception is raise, then it meann
...         # something is wrong; report this by printing
...         # the case name, which will cause this test to
...         # fail, since it wasn't supposed to print
...         # anything
... 
...         else:
... 
...             msg = (
...               "non-compliant case {} of function {}"
...               " didn't raise an error when it should"
...             ).format(case_name, func_name)
... 
...             print(msg)

```

## Doctests for `check_return_annotation_mini_lang` function

```python
## pass function along with test data to the function used to test them
## together; no output must be generated
>>> test_function_with_test_data(
...   check_return_annotation_mini_lang, TEST_DATA)

```
