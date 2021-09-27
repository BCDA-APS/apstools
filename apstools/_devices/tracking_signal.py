"""
Tracking Signal for Device coordination
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~TrackingSignal
"""

from ophyd import Signal


class TrackingSignal(Signal):
    """
    Non-EPICS signal for use when coordinating Device actions.

    .. index:: Ophyd Signal; TrackingSignal

    Signal to decide if undulator will be tracked while changing the
    monochromator energy.
    """

    def check_value(self, value):
        """
        Check if the value is a boolean.

        RAISES

        ValueError
        """
        if not isinstance(value, bool):
            raise ValueError("tracking is boolean, it can only be True or False.")
