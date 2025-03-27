"""
EPICS Signal for Scan ID
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~EpicsScanIdSignal
"""

import logging
from typing import Any, Dict, Optional, Union

from ophyd import EpicsSignal

logger = logging.getLogger(__name__)


class EpicsScanIdSignal(EpicsSignal):
    """
    Use an EPICS PV as the source of the RunEngine's ``scan_id``.

    Uses a writable EPICS integer PV (such as longout record).

    Attributes:
        name: The name of the signal
        parent: The parent device, if any
        kind: The kind of device
        labels: List of labels associated with the device

    EXAMPLE::

        scan_id = EpicsScanIdDevice("ioc:scan_id:longout", name="scan_id")
        # ...
        RE = bluesky.RunEngine({}, scan_id_source=scan_id.cb_scan_id_source)

    (new in release 1.6.3)
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
        Initialize the EPICS scan ID signal.

        Args:
            name: The name of the signal
            parent: The parent device, if any
            kind: The kind of device
            labels: List of labels associated with the device
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(name=name, parent=parent, kind=kind, labels=labels, **kwargs)

    def cb_scan_id_source(self, *args: Any, **kwargs: Any) -> int:
        """
        Callback function for RunEngine. Returns *next* scan_id to be used.

        * Get current scan_id from PV.
        * Apply lower limit of zero.
        * Increment.
        * Set PV with new value.
        * Return new value.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            int: The next scan ID to be used
        """
        new_scan_id = max(self.get(), 0) + 1
        self.put(new_scan_id)
        return new_scan_id


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
