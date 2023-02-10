import pytest
from ophyd import EpicsMotor
from ophyd import EpicsSignal

from ..profile_support import getDefaultNamespace
from ..support_labeled_devices import read_labeled_devices

IOC = "gp:"
MOTOR_PV = f"{IOC}m1"
AO_PV = f"{IOC}gp:float1"


@pytest.fixture(scope="function")
def ao():
    signal = EpicsSignal(AO_PV, name="ao", labels="signal".split())
    signal.wait_for_connection()

    namespace = getDefaultNamespace()
    namespace[signal.name] = signal  # put it in the user namespace
    assert signal.name in namespace
    yield signal

    namespace.pop(signal.name)


@pytest.fixture(scope="function")
def motor():
    device = EpicsMotor(MOTOR_PV, name="motor", labels="motor".split())
    device.wait_for_connection()

    namespace = getDefaultNamespace()
    namespace[device.name] = device  # put it in the user namespace
    assert device.name in namespace
    yield device

    namespace.pop(device.name)


def test_in_namespace(ao, motor):
    assert ao.name == "ao"
    assert motor.name == "motor"

    readings = read_labeled_devices()
    assert len(readings) == 2
    for label in ao._ophyd_labels_:
        assert label in readings
    for label in motor._ophyd_labels_:
        assert label in readings
    assert len(read_labeled_devices()) == len(read_labeled_devices(["motor", "signal"]))

    readings = read_labeled_devices("signal")
    assert len(readings) == 1
    assert "signal" in readings
    assert len(readings["signal"]) == len(ao.read())
    assert ao.name in readings["signal"]

    reading = readings["signal"][ao.name]
    assert isinstance(reading, dict)
    assert len(reading) == 2
    assert "timestamp" in reading
    assert "value" in reading

    readings = read_labeled_devices("motor")
    assert len(readings) == 1
    assert "motor" in readings
    assert len(readings["motor"]) == len(motor.read())


def test_KeyError_raised():
    for label in "motor signal this_key_not_found".split():
        with pytest.raises(KeyError) as exinfo:
            read_labeled_devices([label])
        assert f"'{label}'" in str(exinfo.value)
