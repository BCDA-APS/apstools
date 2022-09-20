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

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
