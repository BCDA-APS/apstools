
"""
scanning with synApps sscan record

.. autosummary::
   
   ~sscan_1D
"""

__all__ = ["sscan_1D",]

import logging
logger = logging.getLogger(__name__)

from bluesky import plan_stubs as bps
from collections import OrderedDict
from ophyd import DeviceStatus
import time


new_data = False
inactive_deadline = time.time()


def _get_sscan_data_objects(sscan):
    """
    prepare a dictionary of the "interesting" ophyd data objects for this sscan

    PARAMETERS

    sscan : Device
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
        phase_timeout_s = 60.0,
        running_stream="primary", 
        final_array_stream=None, 
        device_settings_stream="settings", 
        md={}):
    """
    simple 1-D scan using EPICS synApps sscan record
    
    assumes the sscan record has already been setup properly for a scan

    PARAMETERS

    sscan : Device
        one EPICS sscan record (instance of `apstools.synApps.sscanRecord`)
    running_stream : str or `None`
        (default: ``"primary"``)
        Name of document stream to write positioners and detectors data
        made available while the sscan is running.  This is typically 
        the scan data, row by row.
        If set to `None`, this stream will not be written.
    final_array_stream : str or `None`
        (default: ``None``)
        Name of document stream to write positioners and detectors data 
        posted *after* the sscan has ended.
        If set to `None`, this stream will not be written.
    device_settings_stream : str or `None`
        (default: ``"settings"``)
        Name of document stream to write *settings* of the sscan device.
        This is all the information returned by ``sscan.read()``.
        If set to `None`, this stream will not be written.
    poll_delay_s : float
        (default: 0.001 seconds)
        How long to sleep during each polling loop while collecting
        interim data values and waiting for sscan to complete.
        Must be a number between zero and 0.1 seconds.
    phase_timeout_s : float
        (default: 60 seconds)
        How long to wait after last update of the ``sscan.FAZE``.
        When scanning, we expect the scan phase to update regularly
        as positioners move and detectors are triggered.  If the scan
        hangs for some reason, this is a way to end the plan early.
        To cancel this feature, set it to ``None``.
    
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
    
    msg = f"poll_delay_s must be a number between 0 and 0.1, received {poll_delay_s}"
    assert 0 <= poll_delay_s <= 0.1, msg
    
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
            new_data = True            # set flag for main plan
    
    # acquire only the channels with non-empty configuration in EPICS
    sscan.select_channels()
    # pre-identify the configured channels
    sscan_data_objects = _get_sscan_data_objects(sscan)
    
    # watch for sscan to complete
    sscan.execute_scan.subscribe(execute_cb)
    # watch for new data to be read out
    sscan.scan_phase.subscribe(phase_cb)
    
    md["plan_name"] = "sscan_1D"

    yield from bps.open_run(md)               # start data collection
    yield from bps.mv(sscan.execute_scan, 1)   # start sscan
    started = True

    # collect and emit data, wait for sscan to end
    while not sscan_status.done or new_data:
        if new_data and running_stream is not None:
            yield from bps.create(running_stream)
            for _k, obj in sscan_data_objects.items():
                yield from bps.read(obj)
            yield from bps.save()
        new_data = False
        if phase_timeout_s is not None and time.time() > inactive_deadline:
            print(f"No change in sscan record for {phase_timeout_s} seconds.")
            print("ending plan early as unsuccessful")
            sscan_status._finished(success=False)
        yield from bps.sleep(poll_delay_s)

    # dump the complete data arrays
    if final_array_stream is not None:
        yield from bps.create(final_array_stream)
        # we have to search for the arrays since they have ``kind="omitted"``
        # (which means they do not get reported by the ``.read()`` method)
        for part in (sscan.positioners, sscan.detectors):
            for nm in part.read_attrs:
                if "." not in nm:
                    # TODO: write just the acquired data, not the FULL arrays!
                    yield from bps.read(getattr(part, nm).array)
        yield from bps.save()

    # dump the entire sscan record into another stream
    if device_settings_stream is not None:
        yield from bps.create(device_settings_stream)
        yield from bps.read(sscan)
        yield from bps.save()

    yield from bps.close_run()
    
    elapsed = time.time() - t0
    print(f"total time for sscan_1D: {elapsed} s")

    return sscan_status
