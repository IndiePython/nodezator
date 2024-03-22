"""Facility for datetime utilities."""

### local import
from datetime import datetime, timezone



UTC_OFFSET = datetime.now(timezone.utc).astimezone().strftime("%z")
