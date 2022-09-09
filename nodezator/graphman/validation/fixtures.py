TEST_DATA = {
    "compliant_cases": {
        "compliant_case00": [{"name": "output_name01"}, {"name": "output_name02"}],
        "compliant_case01": [
            {"name": "output_name01", "type": "str"},
            {"name": "output_name02"},
        ],
        "compliant_case02": [
            {"name": "output_name01"},
            {"name": "output_name02", "type": "str"},
        ],
        "compliant_case03": [
            {"name": "output_name01"},
            {"name": "output_name02", "type": ["int", "float"]},
        ],
    },
    "non_compliant_cases": {
        "non_compliant_case_not_list_or_tuple": "str",
        "non_compliant_case_items_must_be_dict": [
            {"name": "output_name01"},
            {"name": "output_name02"},
            "output_name3",
        ],
        "non_compliant_case_items_must_have_name": [
            {"name": "output_name01"},
            {"name": "output_name02"},
            {"type": "str"},
        ],
        "non_compliant_case_item_names_must_be_str": [
            {"name": "output_name01"},
            {"name": "output_name02"},
            {"name": 42},
        ],
        "non_compliant_case_item_names_must_be_identifiers": [
            {"name": "output_name01"},
            {"name": "output_name02"},
            {"name": "output name03"},
        ],
        "non_compliant_case_item_names_must_not_be_equal": [
            {"name": "output_name01"},
            {"name": "output_name02"},
            {"name": "output_name02"},
        ],
    },
    "non_compliance_error_data": {
        "non_compliant_case_not_list_or_tuple": {
            "type": "TypeError",
            "message_excerpt": "return annotation must be of class 'list' or 'tuple'",
        },
        "non_compliant_case_items_must_be_dict": {
            "type": "TypeError",
            "message_excerpt": "items in 'return_annotation' must all be of class 'dict'",
        },
        "non_compliant_case_items_must_have_name": {
            "type": "ValueError",
            "message_excerpt": "items in 'return_annotation' must all have a 'name' field",
        },
        "non_compliant_case_item_names_must_be_str": {
            "type": "TypeError",
            "message_excerpt": "value of 'name' fields in 'return_annotation' items must all be of class 'str'",
        },
        "non_compliant_case_item_names_must_be_identifiers": {
            "type": "ValueError",
            "message_excerpt": "the value of 'name' fields in each item of the 'return_annotation' must pass the str.isidentifier test",
        },
        "non_compliant_case_item_names_must_not_be_equal": {
            "type": "ValueError",
            "message_excerpt": "items of 'return_annotation' must not have 'name' fields with the same value",
        },
    },
}
