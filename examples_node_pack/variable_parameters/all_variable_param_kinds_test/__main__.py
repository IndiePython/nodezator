"""Facility for all parameter kinds testing."""

### function definition

def all_var_param_kinds(
    pos_or_key, *var_pos, key_only, **var_key):
    """Return all arguments received."""
    return pos_or_key, var_pos, key_only, var_key

### functions used must always be aliased as 'main'
main_callable = all_var_param_kinds
