"""
Define symbols used by other modules to define time (seconds).

.. autosummary::

    ~DAY
    ~HOUR
    ~MINUTE
    ~SECOND
    ~WEEK
    ~ts2iso

"""

__all__ = """DAY HOUR MINUTE SECOND WEEK ts2iso""".split()

import datetime

#: One second of time (the base unit).
SECOND = 1

#: 60 seconds (in seconds)
MINUTE = 60 * SECOND

#: 60 minutes (in seconds)
HOUR = 60 * MINUTE

#: 24 hours (in seconds)
DAY = 24 * HOUR

#: 7 days (in seconds)
WEEK = 7 * DAY


def ts2iso(ts: float, sep: str = " ") -> str:
    """Convert Python timestamp (float) to IS8601 time in current time zone."""
    return datetime.datetime.fromtimestamp(ts).isoformat(sep=sep)
