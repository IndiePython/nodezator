"""Facility for datetime utilities."""

### local import
import datetime, timezone



UTC_OFFSET = datetime.now(timezone.utc).astimezone().strftime("%z")
