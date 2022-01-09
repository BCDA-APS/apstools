from ..xia_slit import XiaSlitController
# from ...utils import SlitGeometry

import pytest

IOC = "gp:"

# Full testing requires two XIA Slit controllers (a 2D H & V set)
# We don't have that for unit testing.  Proceed with best efforts.


def test_XiaSlit(capsys):
    slit1 = XiaSlitController("gp:hsc1:", name="slit1")
    assert slit1 is not None

    # slit1.wait_for_connection()
    assert not slit1.connected
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
    assert slit1.component_names == tuple(cns)

    with pytest.raises(TypeError):
        print(slit1.geometry)
    
    captured = capsys.readouterr()
    assert captured.out.split("\n") == [""]
    assert captured.err.split("\n") == [""]
