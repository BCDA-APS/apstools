"""
sscan Record plans
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~sscan_1D
"""

import time
from collections import OrderedDict

from bluesky import plan_stubs as bps
from ophyd import DeviceStatus

from .doc_run import write_stream

new_data = False  # sscan has new data, boolean
inactive_deadline = 0  # sscan timeout, absolute time.time()


def _get_sscan_data_objects(sscan):
    """
    prepare a dictionary of the "interesting" ophyd data objects for this sscan

    PARAMETERS

    sscan
        *Device* :
        one EPICS sscan record (instance of `apstools.synApps.sscanRecord`)

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
    sscan,
    poll_delay_s=0.001,
    phase_timeout_s=60.0,
    running_stream="primary",
    final_array_stream=None,
    device_settings_stream="settings",
    md=None,
):
    """
    simple 1-D scan using EPICS synApps sscan record

    .. index:: Bluesky Plan; sscan_1D

    assumes the sscan record has already been setup properly for a scan

    PARAMETERS

    sscan *Device* :
        one EPICS sscan record (instance of `apstools.synApps.sscanRecord`)
    running_stream *str* : or `None`
        (default: ``"primary"``)
        Name of document stream to write positioners and detectors data
        made available while the sscan is running.  This is typically
        the scan data, row by row.
        If set to `None`, this stream will not be written.
    final_array_stream *str*  or ``None`` :
        Name of document stream to write positioners and detectors data
        posted *after* the sscan has ended.
        If set to `None`, this stream will not be written.
        (default: ``None``)
    device_settings_stream *str*  or ``None`` :
        Name of document stream to write *settings* of the sscan device.
        This is all the information returned by ``sscan.read()``.
        If set to `None`, this stream will not be written.
        (default: ``"settings"``)
    poll_delay_s *float* :
        How long to sleep during each polling loop while collecting
        interim data values and waiting for sscan to complete.
        Must be a number between zero and 0.1 seconds.
        (default: 0.001 seconds)
    phase_timeout_s *float* :
        How long to wait after last update of the ``sscan.FAZE``.
        When scanning, we expect the scan phase to update regularly
        as positioners move and detectors are triggered.  If the scan
        hangs for some reason, this is a way to end the plan early.
        To cancel this feature, set it to ``None``.
        (default: 60 seconds)

    NOTE about the document stream names

    Make certain the names for the document streams are different from
    each other.  If you make them all the same (such as ``primary``),
    you will have difficulty when reading your data later on.

    *Don't cross the streams!*

    EXAMPLE

    Assume that the chosen sscan record has already been setup.

        from apstools.devices import sscanDevice
        scans = sscanDevice(P, name="scans")

        from apstools.plans import sscan_1D
        RE(sscan_1D(scans.scan1), md=dict(purpose="demo"))

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

    def execute_cb(value, timestamp, **kwargs):
        """watch for sscan to complete"""
        if started and value in (0, "IDLE"):
            sscan_status._finished()
            sscan.execute_scan.unsubscribe_all()
            sscan.scan_phase.unsubscribe_all()

    def phase_cb(value, timestamp, **kwargs):
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
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
