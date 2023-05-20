import pathlib
from collections import OrderedDict

import pytest

from ...migration import spec2ophyd

path = pathlib.Path(__file__).parent.parent


def test_Version():
    from ... import __version__

    version = spec2ophyd.get_apstools_version()
    assert isinstance(version, str)
    assert len(version) > len("#.#.#")
    assert version == __version__


def test_SpecConfig():
    sc = spec2ophyd.SpecConfig(path / "config_fourc")
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

    sc = spec2ophyd.SpecConfig(path / "config")  # USAXS
    sc.read_config()
    assert len(sc.devices) == 3
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 68
    assert len(sc.unhandled) == 2

    sc = spec2ophyd.SpecConfig(path / "config_fourc")
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

    sc = spec2ophyd.SpecConfig(path / "config-CNTPAR")
    sc.read_config()
    assert len(sc.devices) == 4
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 78
    assert len(sc.unhandled) == 7

    sc = spec2ophyd.SpecConfig(path / "config-MOTPAR")
    sc.read_config()
    assert len(sc.devices) == 4
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 124
    assert len(sc.unhandled) == 1

    sc = spec2ophyd.SpecConfig(path / "config_spec")
    sc.read_config()
    assert len(sc.devices) == 3
    assert len(sc.scalers) == 1
    assert len(sc.collection) == 121
    assert len(sc.unhandled) == 12


def test_SpecConfig_find_pv_in_collection():
    sc = spec2ophyd.SpecConfig(path / "config")  # USAXS
    sc.read_config()
    assert isinstance(sc.find_pv_in_collection("9idcLAX:aero:c1:m1"), spec2ophyd.SpecMotor)
    assert isinstance(sc.find_pv_in_collection("9idcLAX:vsc:c0"), spec2ophyd.SpecSignal)
    # FIXME:
    # assert isinstance(
    #     sc.find_pv_in_collection("9idcLAX:vsc:c0.S1"),
    #     spec2ophyd.SpecCounter
    # )


def test_create_ophyd_setup(capsys):
    sc = spec2ophyd.SpecConfig(path / "config_fourc")
    sc.read_config()
    spec2ophyd.create_ophyd_setup(sc)
    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert len(lines) == 22
    assert len(err.splitlines()) == 0
    # TODO:


def test_issue499(capsys):
    """
    failed when parsing this SPEC config line

        MOT022 = MAC_MOT:1/0/0   2000  1  2000  200   50  125    0 0x003   suvgap  SlitUpVGap

    * Only expecting 2 arguments after `MAC_MOT:`  chan/ignore.
    * This seems to be: chan/axis/num
    * only chan is used
    * assign the others into SpecMotor.ctrl_parms as [int]
    """
    sc = spec2ophyd.SpecConfig(path / "config_spec")
    sc.read_config()
    spec2ophyd.create_ophyd_setup(sc)
    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert len(lines) == 137  # this may change if other items are processed
    assert len(err.splitlines()) == 0

    # assert out == "DEBUG"  # enable to show output from create_ophyd_setup(sc)

    # verify the correct configuration line is selected
    m = sc.collection[22]
    assert isinstance(m, spec2ophyd.SpecMotor)
    assert m.mne == "suvgap"
    assert m.name == "SlitUpVGap"
    assert m.motpar == dict(misc_par_1="19", misc_par_2="18")
    assert m.mac_parms == [0, 0]
    assert m.device.prefix == "slit"
    assert m.device.num_channels == 8
    assert m.device.config_line == 15

    # test for the parameters that triggered the issue
    assert sc.collection[22].mac_parms == [0, 0]
    assert sc.collection[23].mac_parms == [0, 1]
    assert sc.collection[24].mac_parms == [1, 0]
    assert sc.collection[25].mac_parms == [1, 1]
