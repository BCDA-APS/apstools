"""
sscan Record plans
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~sscan_1D
"""

import time
from collections import OrderedDict
from typing import Any, Dict, Generator, Optional, Union

from bluesky import plan_stubs as bps
from ophyd import Device, DeviceStatus

from .doc_run import write_stream

new_data: bool = False  # sscan has new data, boolean
inactive_deadline: float = 0  # sscan timeout, absolute time.time()


def _get_sscan_data_objects(sscan: Device) -> OrderedDict[str, Any]:
    """
    prepare a dictionary of the "interesting" ophyd data objects for this sscan

    Args:
        sscan: one EPICS sscan record (instance of `apstools.synApps.sscanRecord`)

    Returns:
        OrderedDict of data objects
    """
    scan_data_objects = OrderedDict()
    for part in (sscan.positioners, sscan.detectors):
        for chname in part.read_attrs:
            if not chname.endswith("_value"):
                continue
            obj = getattr(part, chname)
            key = obj.name.lstrip(sscan.name + "_")
            scan_data_objects[key] = obj
    return scan_data_objects


def sscan_1D(
    sscan: Device,
    poll_delay_s: float = 0.001,
    phase_timeout_s: Optional[float] = 60.0,
    running_stream: Optional[str] = "primary",
    final_array_stream: Optional[str] = None,
    device_settings_stream: Optional[str] = "settings",
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, str]:
    """
    simple 1-D scan using EPICS synApps sscan record

    Args:
        sscan: one EPICS sscan record (instance of `apstools.synApps.sscanRecord`)
        poll_delay_s: How long to sleep during each polling loop (default: 0.001)
        phase_timeout_s: How long to wait after last update of the sscan.FAZE (default: 60.0)
        running_stream: Name of document stream for running data (default: "primary")
        final_array_stream: Name of document stream for final data (default: None)
        device_settings_stream: Name of document stream for device settings (default: "settings")
        md: Metadata dictionary (default: None)

    Returns:
        Generator yielding the run UID
    """
    global new_data, inactive_deadline

    if not (0 <= poll_delay_s <= 0.1):
        # fmt: off
        raise ValueError(
            "poll_delay_s must be a number between 0 and 0.1,"
            f" received {poll_delay_s}"
        )
        # fmt: on

    t0 = time.time()
    sscan_status = DeviceStatus(sscan.execute_scan)
    started = False
    new_data = False
    inactive_deadline = time.time()
    if phase_timeout_s is not None:
        inactive_deadline += phase_timeout_s

    def execute_cb(value: Union[int, str], timestamp: float, **kwargs: Any) -> None:
        """watch for sscan to complete"""
        if started and value in (0, "IDLE"):
            sscan_status._finished()
            sscan.execute_scan.unsubscribe_all()
            sscan.scan_phase.unsubscribe_all()

    def phase_cb(value: Union[int, str], timestamp: float, **kwargs: Any) -> None:
        """watch for new data"""
        global new_data, inactive_deadline
        if phase_timeout_s is not None:
            inactive_deadline = time.time() + phase_timeout_s
        if value in (15, "RECORD SCALAR DATA"):
            new_data = True  # set flag for main plan

    # acquire only the channels with non-empty configuration in EPICS
    sscan.select_channels()
    # pre-identify the configured channels
    sscan_data_objects = _get_sscan_data_objects(sscan)

    # watch for sscan to complete
    sscan.execute_scan.subscribe(execute_cb)
    # watch for new data to be read out
    sscan.scan_phase.subscribe(phase_cb)

    _md = dict(plan_name="sscan_1D")
    _md.update(md or {})

    uid = yield from bps.open_run(_md)  # start data collection
    yield from bps.mv(sscan.execute_scan, 1)  # start sscan
    started = True

    # collect and emit data, wait for sscan to end
    while not sscan_status.done or new_data:
        if new_data and running_stream is not None:
            yield from write_stream(sscan_data_objects.values(), running_stream)
        new_data = False
        if phase_timeout_s is not None and time.time() > inactive_deadline:
            print(f"No change in sscan record for {phase_timeout_s} seconds.")
            print("ending plan early as unsuccessful")
            sscan_status._finished(success=False)
        yield from bps.sleep(poll_delay_s)

    # dump the complete data arrays
    if final_array_stream is not None:
        # fmt: off
        yield from write_stream(
            [
                # TODO: write just the acquired data, not the FULL arrays!
                getattr(part, nm).array
                # we have to search for the arrays since they have ``kind="omitted"``
                # (which means they do not get reported by the ``.read()`` method)
                for part in (sscan.positioners, sscan.detectors)
                for nm in part.read_attrs
                if "." not in nm
            ],
            final_array_stream
        )
        # fmt: on

    # dump the entire sscan record into another stream
    if device_settings_stream is not None:
        yield from write_stream(sscan, device_settings_stream)

    yield from bps.close_run()

    elapsed = time.time() - t0
    print(f"total time for sscan_1D: {elapsed} s")

    return uid


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
