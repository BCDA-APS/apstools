import bluesky
import databroker
from bluesky import plans as bp
from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import PVPositioner

from ...synApps import UserCalcsDevice
from ...synApps import UserTransformsDevice
from ...tests import IOC
from ...tests import setup_transform_as_soft_motor
from ..nexus_writer import NXWriter

CALC_COMPONENT_SELECTED = "calc10"
CALC_PV_SELECTED = "userCalc10"
TRANSFORMS_COMPONENT_SELECTED = "transform10"
TRANSFORMS_PV_SELECTED = "userTran10"
MOTOR_PV = f"{IOC}m1"
NOISY_PV = f"{IOC}{CALC_PV_SELECTED}.VAL"


class Undulator(PVPositioner):
    setpoint = Component(EpicsSignal, f"{TRANSFORMS_PV_SELECTED}.A")
    readback = Component(EpicsSignalRO, f"{TRANSFORMS_PV_SELECTED}.O")
    actuate = Component(EpicsSignal, f"{TRANSFORMS_PV_SELECTED}.I")
    stop_signal = Component(EpicsSignal, f"{TRANSFORMS_PV_SELECTED}.H")
    done = Component(EpicsSignalRO, f"{TRANSFORMS_PV_SELECTED}.D")
    actuate_value = 3
    stop_value = 0
    done_value = 1


def test_as_reported():
    cat = databroker.temp().v2
    nx = NXWriter()  # Arquivo no formato Nexus (HDF5)
    RE = bluesky.RunEngine()

    RE.subscribe(cat.v1.insert)
    RE.subscribe(nx.receiver)

    assert nx.file_name is None
    nx.file_name = "file_name.h5"
    assert isinstance(nx.file_name, str)  # issue #806
    # assert isinstance(nx.file_name, pathlib.Path)  # TODO: issue #807

    und = Undulator(IOC, name="und")
    motor = EpicsMotor(MOTOR_PV, name="motor")
    noisy = EpicsSignalRO(NOISY_PV, name="noisy")
    user_transforms = UserTransformsDevice(IOC, name="user_transforms")
    for obj in (motor, noisy, und, user_transforms):
        obj.wait_for_connection()

    assert TRANSFORMS_COMPONENT_SELECTED in dir(user_transforms)
    t_rec = getattr(user_transforms, TRANSFORMS_COMPONENT_SELECTED)
    t_rec.reset()
    assert t_rec.description.get() != "simulated motor"

    setup_transform_as_soft_motor(t_rec)
    assert t_rec.description.get() == "simulated motor"
