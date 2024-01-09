import databroker
from bluesky import RunEngine
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from ophyd import EpicsMotor
from ophyd.scaler import ScalerCH

from ...synApps import SscanDevice
from ...tests import IOC_GP

from ..sscan_support import _get_sscan_data_objects
from ..sscan_support import sscan_1D


def test_i108():
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)
    RE.subscribe(BestEffortCallback())
    RE.preprocessors.append(SupplementalData())

    motor = EpicsMotor(f"{IOC_GP}m1", name="motor")
    scaler = ScalerCH(f"{IOC_GP}scaler1", name="scaler")
    scans = SscanDevice(IOC_GP, name="scans")
    for item in (motor, scaler, scans):
        item.wait_for_connection(timeout=20)

    scans.scan1.reset()

    p1 = scans.scan1.positioners.p1
    p1.readback_pv.put(motor.user_readback.pvname)
    p1.setpoint_pv.put(motor.user_setpoint.pvname)
    p1.start.put(-0.1)
    p1.end.put(0)
    p1.step_size.put(0.05)
    num_pos = 2  # number of positioner data values (setpoint & readback)

    i = 0
    scaler.select_channels()
    for k in scaler.read_attrs:
        if k.endswith(".s"):
            i += 1
            chan = k.split(".")[1]
            det = getattr(scans.scan1.detectors, f"d{i:02d}")
            det.input_pv.put(getattr(scaler.channels, chan).s.pvname)
    num_det = i  # number of detector data values
    scaler.preset_time.put(0.2)

    scans.scan1.triggers.t1.trigger_pv.put(scaler.count.pvname)

    scans.select_channels()

    uids = RE(sscan_1D(scans.scan1, md=dict(issue="#108")))
    assert len(uids) == 1

    run = cat[-1]
    assert run is not None

    streams = list(run.metadata["stop"]["num_events"].keys())
    assert len(streams) == 1
    assert "settings" in streams  # Why not a primary stream?

    ds = run.settings.read()
    assert ds is not None
    assert scans.scan1.current_point.name in ds

    arr = ds[scans.scan1.current_point.name]
    assert arr is not None
    assert len(arr) == 1

    data = _get_sscan_data_objects(scans.scan1)
    assert len(data) == num_det + num_pos
