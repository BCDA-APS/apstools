import logging

from ophyd import EpicsSignal

logger = logging.getLogger(__name__)


class EpicsScanIdSignal(EpicsSignal):
    """
    Use an EPICS PV as the source of the RunEngine's ``scan_id``.

    Uses a writable EPICS integer PV (such as longout record).

    EXAMPLE::

        scan_id = EpicsScanIdDevice("ioc:scan_id:longout", name="scan_id")
        # ...
        RE = bluesky.RunEngine({}, scan_id_source=scan_id.cb_scan_id_source)

    (new in release 1.6.3)
    """

    def cb_scan_id_source(self, *args, **kwargs):
        """
        Callback function for RunEngine.  Returns *next* scan_id to be used.

        * Get current scan_id from PV.
        * Apply lower limit of zero.
        * Increment.
        * Set PV with new value.
        * Return new value.
        """
        new_scan_id = max(self.get(), 0) + 1
        self.put(new_scan_id)
        return new_scan_id


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
