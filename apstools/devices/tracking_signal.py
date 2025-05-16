"""
Tracking Signal for Device coordination
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~TrackingSignal
"""

from typing import Any, Dict, Optional, Union

from ophyd import Signal


class TrackingSignal(Signal):
    """
    Non-EPICS signal for use when coordinating Device actions.

    .. index:: Ophyd Signal; TrackingSignal

    Signal to decide if undulator will be tracked while changing the
    monochromator energy.

    Attributes:
        name: The name of the signal
        parent: The parent device, if any
        kind: The kind of device
        labels: List of labels associated with the device
    """

    def __init__(
        self,
        name: str,
        *,
        parent: Optional[Any] = None,
        kind: str = "normal",
        labels: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the tracking signal.

        Args:
            name: The name of the signal
            parent: The parent device, if any
            kind: The kind of device
            labels: List of labels associated with the device
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(name=name, parent=parent, kind=kind, labels=labels, **kwargs)

    def check_value(self, value: Any) -> None:
        """
        Check if the value is a boolean.

        Args:
            value: The value to check

        Raises:
            ValueError: If the value is not a boolean
        """
        if not isinstance(value, bool):
            raise ValueError("tracking is boolean, it can only be True or False.")


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
