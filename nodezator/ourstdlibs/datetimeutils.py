"""Facility for datetime utilities."""

### local import
from datetime import datetime, timezone



### constants

UTC_OFFSET = datetime.now(timezone.utc).astimezone().strftime("%z")

## format code for datetime strings produced with "str(datetime.now())"
DATETIME_STR_FORMAT_CODE = "%Y-%m-%d %H:%M:%S.%f"


### utility function

def get_timestamp(datetime_obj=None):
    """Return timestamp string in 'YYYY_MM_DD_HH_MM_SS' format."""

    ### if no datetime object is given, use datetime.now()
    if datetime_obj is None:
        datetime_obj = datetime.now()

    ### build and return the timestamp
    return  "".join(
        ## use either a digit or '_'
        char if char.isdigit() else "_"
        ## for each char from the first
        ## 19 ones in string from
        ## datetime.now()
        for char in str(datetime_obj)[:19]
    )
