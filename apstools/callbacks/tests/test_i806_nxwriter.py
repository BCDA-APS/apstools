import pathlib
import tempfile

import bluesky
import databroker
import h5py
from bluesky import plans as bp
from ophyd import Component
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import PVPositioner

from ...synApps import UserTransformsDevice
from ...tests import IOC_GP
from ...tests import setup_transform_as_soft_motor
from ..nexus_writer import NXWriter

CALC_COMPONENT_SELECTED = "calc10"
CALC_PV_SELECTED = "userCalc10"
TRANSFORMS_COMPONENT_SELECTED = "transform10"
TRANSFORMS_PV_SELECTED = "userTran10"
MOTOR_PV = f"{IOC_GP}m1"
NOISY_PV = f"{IOC_GP}{CALC_PV_SELECTED}.VAL"


class Undulator(PVPositioner):
    setpoint = Component(EpicsSignal, f"{TRANSFORMS_PV_SELECTED}.A")
    readback = Component(EpicsSignalRO, f"{TRANSFORMS_PV_SELECTED}.O")
    actuate = Component(EpicsSignal, f"{TRANSFORMS_PV_SELECTED}.I")
    stop_signal = Component(EpicsSignal, f"{TRANSFORMS_PV_SELECTED}.H")
    done = Component(EpicsSignalRO, f"{TRANSFORMS_PV_SELECTED}.D")
    actuate_value = 3
    stop_value = 0
    done_value = 1


class UndulatorFixed(Undulator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.readback.name = self.name


def test_i806_root_cause():
    """Root cause: NXdata group wanted ``und`` but found ``und_readback``."""
    und = Undulator(IOC_GP, name="und")
    und.wait_for_connection()
    assert "und" not in und.read()
    assert "und_readback" in und.read()
    assert "und_setpoint" in und.read()

    und_fixed = UndulatorFixed(IOC_GP, name="und")
    und_fixed.wait_for_connection()
    assert "und" in und_fixed.read()
    assert "und_readback" not in und_fixed.read()
    assert "und_setpoint" in und_fixed.read()


def test_as_reported():
    cat = databroker.temp().v2
    nx = NXWriter()  # Arquivo no formato Nexus (HDF5)
    nx.warn_on_missing_content = False  # less noisy
    RE = bluesky.RunEngine()

    RE.subscribe(cat.v1.insert)
    RE.subscribe(nx.receiver)

    tempdir = pathlib.Path(tempfile.mkdtemp())
    filename = tempdir / "file_name.h5"
    if filename.exists():
        filename.unlink()  # remove any previous version
    assert isinstance(filename, pathlib.Path)

    assert nx.file_name is None
    nx.file_name = str(filename)
    assert isinstance(nx.file_name, pathlib.Path)

    und = UndulatorFixed(IOC_GP, name="und")
    motor = EpicsMotor(MOTOR_PV, name="motor")
    noisy = EpicsSignalRO(NOISY_PV, name="noisy")
    user_transforms = UserTransformsDevice(IOC_GP, name="user_transforms")
    for obj in (motor, noisy, und, user_transforms):
        obj.wait_for_connection(timeout=20.0)

    assert und.name == "und"
    assert und.name in und.read()

    assert TRANSFORMS_COMPONENT_SELECTED in dir(user_transforms)
    t_rec = getattr(user_transforms, TRANSFORMS_COMPONENT_SELECTED)
    t_rec.reset()
    assert t_rec.description.get(use_monitor=False) != "simulated motor"

    setup_transform_as_soft_motor(t_rec)
    assert t_rec.description.get(use_monitor=False) == "simulated motor"

    dets = [noisy]
    und_pos_list = [5.4651, 5.9892, 6.539]
    motor_pos_list = [0.02, 0.11, 0]
    assert len(und_pos_list) == len(motor_pos_list)

    uids = RE(bp.list_scan(dets, und, und_pos_list, motor, motor_pos_list))
    nx.wait_writer()
    assert len(uids) == 1
    assert filename.exists()

    # check the HDF5 file for the correct /entry/data (NXdata) structure
    with h5py.File(filename, "r") as nxroot:
        default = nxroot.attrs.get("default")
        assert default is not None
        assert default in nxroot

        nxentry = nxroot[default]
        default = nxentry.attrs.get("default")
        assert default is not None, f"{filename=} {dict(nxentry.attrs.items())=}"
        assert default in nxentry

        nxdata = nxentry[default]
        axes = nxdata.attrs.get("axes")
        for field in axes:
            assert field in nxdata, f"{filename=} {field=}"
