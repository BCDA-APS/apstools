import pytest
from apstools.migration import spec2ophyd
import os
# import sys
from collections import OrderedDict

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# for config_spec
# config_spec:MOT022 = MAC_MOT:1/0/0   2000  1  2000  200   50  125    0 0x003   suvgap  SlitUpVGap
# parse error
# # FIXME: `1/0/0` is a new case from 17BM
# unit, chan, = list(map(int, uc_str.split("/")))[:2]  # FIXME:

def test_SpecConfig():
    sc = spec2ophyd.SpecConfig(os.path.join(path, "config_fourc"))
    assert sc is not None
    assert isinstance(sc.devices, OrderedDict)
    assert isinstance(sc.scalers, list)
    assert isinstance(sc.collection, list)
    assert isinstance(sc.unhandled, list)
    assert sc.devices == {}
    assert sc.scalers == []
    assert sc.collection == []
    assert sc.unhandled == []

    # no exceptions yet
    sc = spec2ophyd.SpecConfig("cannot find this file")
    assert sc is not None
    assert isinstance(sc.devices, OrderedDict)


def test_SpecConfig_read_config():
    sc = spec2ophyd.SpecConfig("cannot find this file")
    # now the exception
    with pytest.raises(FileNotFoundError) as exinfo:
        sc.read_config()
    assert "No such file or directory:" in str(exinfo.value)

    sc = spec2ophyd.SpecConfig(os.path.join(path, "config"))  # USAXS
    sc.read_config()
    assert len(sc.devices) == 3
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 68
    assert len(sc.unhandled) == 2

    sc = spec2ophyd.SpecConfig(os.path.join(path, "config_fourc"))
    sc.read_config()
    assert len(sc.devices) == 0
    assert len(sc.scalers) == 0
    assert len(sc.collection) == 7
    assert isinstance(sc.collection[0], spec2ophyd.SpecMotor)
    assert isinstance(sc.collection[1], spec2ophyd.SpecMotor)
    assert isinstance(sc.collection[2], spec2ophyd.SpecMotor)
    assert isinstance(sc.collection[3], spec2ophyd.SpecMotor)
    assert isinstance(sc.collection[4], spec2ophyd.SpecCounter)
    assert isinstance(sc.collection[5], spec2ophyd.SpecCounter)
    assert isinstance(sc.collection[6], spec2ophyd.SpecCounter)
    assert len(sc.unhandled) == 2
    assert sc.unhandled == ["SW_SFTWARE\t = 1 INTR", ""]

    sc = spec2ophyd.SpecConfig(os.path.join(path, "config-CNTPAR"))
    sc.read_config()
    assert len(sc.devices) == 4
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 78
    assert len(sc.unhandled) == 7

    sc = spec2ophyd.SpecConfig(os.path.join(path, "config-MOTPAR"))
    sc.read_config()
    assert len(sc.devices) == 4
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 124
    assert len(sc.unhandled) == 1

    sc = spec2ophyd.SpecConfig(os.path.join(path, "config_spec"))
    sc.read_config()
    assert len(sc.devices) == 3
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 121
    assert len(sc.unhandled) == 12


def test_SpecConfig_find_pv_in_collection():
    sc = spec2ophyd.SpecConfig(os.path.join(path, "config"))  # USAXS
    sc.read_config()
    assert isinstance(
        sc.find_pv_in_collection("9idcLAX:aero:c1:m1"),
        spec2ophyd.SpecMotor
    )
    assert isinstance(
        sc.find_pv_in_collection("9idcLAX:vsc:c0"),
        spec2ophyd.SpecSignal
    )
    # FIXME:
    # assert isinstance(
    #     sc.find_pv_in_collection("9idcLAX:vsc:c0.S1"),
    #     spec2ophyd.SpecCounter
    # )


def test_create_ophyd_setup(capsys):
    sc = spec2ophyd.SpecConfig(os.path.join(path, "config_fourc"))
    sc.read_config()
    spec2ophyd.create_ophyd_setup(sc)
    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert len(lines) == 22
    assert len(err.splitlines()) == 0
    # TODO:
