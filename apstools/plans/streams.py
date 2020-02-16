
"""
plans for document streams

.. autosummary::
   
   ~addDeviceDataAsStream
"""

__all__ = ["addDeviceDataAsStream",]

import logging
logger = logging.getLogger(__name__)

from bluesky import plan_stubs as bps


def addDeviceDataAsStream(devices, label):
    """
    plan: add an ophyd Device (or list of Devices) as an additional document stream
    
    Use this within a custom plan, such as this example::

        from apstools.plans import addDeviceStream
        ...
        yield from bps.open_run()
        # ...
        yield from addDeviceDataAsStream(prescanDeviceList, "metadata_prescan")
        # ...
        yield from custom_scan_procedure()
        # ...
        yield from addDeviceDataAsStream(postscanDeviceList, "metadata_postscan")
        # ...
        yield from bps.close_run()

    """
    yield from bps.create(name=label)
    if not isinstance(devices, list):     # just in case...
        devices = [devices]
    for d in devices:
        yield from bps.read(d)
    yield from bps.save()
