import pytest

from ..xia_slit import XiaSlit2D
from ...utils import SlitGeometry
from ...tests import IOC

PV_PREFIX = f"{IOC}phony_hsc1:"

# Full testing requires two XIA Slit controllers (a 2D H & V set)
# We don't have that for unit testing.  Proceed with best efforts.


def test_XiaSlit_not_connected():
    slit1 = XiaSlit2D(PV_PREFIX, name="slit1")
    assert slit1 is not None

    # slit1.wait_for_connection()
    assert not slit1.connected


def test_XiaSlit_geometry(capsys):
    slit1 = XiaSlit2D(PV_PREFIX, name="slit1")

    g = None
    with pytest.raises(TypeError):
        g = slit1.geometry
    assert not isinstance(g, SlitGeometry)

    captured = capsys.readouterr()
    assert captured.out.split("\n") == [""]
    assert captured.err.split("\n") == [""]


def test_XiaSlit_components():
    slit1 = XiaSlit2D(PV_PREFIX, name="slit1")
    cns = """
        inb out bot top
        hsize vsize hcenter vcenter
        hID horientation hbusy
        vID vorientation vbusy
        enable
        error_code error_message message1 message2 message3
        calibrate initialize locate stop_button
        precision
    """.split()
    assert sorted(slit1.component_names) == sorted(cns)
