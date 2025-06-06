import math
import pytest

from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import in_gha_workflow
from ...tests import timed_pause
from ...utils import SlitGeometry
from ..db_2slit import Optics2Slit1D
from ..db_2slit import Optics2Slit2D_HV
from ..db_2slit import Optics2Slit2D_InbOutBotTop

# TODO: test "sync" signal


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [Optics2Slit1D, f"{IOC_GP}Slit1H", False, "read_attrs", 12],
        [Optics2Slit1D, f"{IOC_GP}Slit1H", False, "configuration_attrs", 16],
        [Optics2Slit1D, f"{IOC_GP}Slit1H", True, "read()", 8],
        [Optics2Slit1D, f"{IOC_GP}Slit1H", True, "summary()", 63],
        [Optics2Slit2D_HV, f"{IOC_GP}Slit1", False, "read_attrs", 26],
        [Optics2Slit2D_HV, f"{IOC_GP}Slit1", False, "configuration_attrs", 34],
        [Optics2Slit2D_HV, f"{IOC_GP}Slit1", True, "read()", 16],
        [Optics2Slit2D_HV, f"{IOC_GP}Slit1", True, "summary()", 114],
        [Optics2Slit2D_InbOutBotTop, f"{IOC_GP}Slit1", False, "read_attrs", 24],
        [Optics2Slit2D_InbOutBotTop, f"{IOC_GP}Slit1", False, "configuration_attrs", 32],
        [Optics2Slit2D_InbOutBotTop, f"{IOC_GP}Slit1", True, "read()", 16],
        [Optics2Slit2D_InbOutBotTop, f"{IOC_GP}Slit1", True, "summary()", 112],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_2slit1D():
    axis = Optics2Slit1D(f"{IOC_GP}Slit1H", name="axis")
    assert axis is not None

    axis.wait_for_connection()
    assert axis.connected

    cns = "xn xp size center sync".split()
    assert axis.component_names == tuple(cns)


@pytest.mark.skipif(
    in_gha_workflow(),
    reason="Random failures in GHA workflows.",
)
def test_2slit2D_HV():
    slit1 = Optics2Slit2D_HV(f"{IOC_GP}Slit1", name="slit1")
    assert slit1 is not None

    slit1.wait_for_connection()
    assert slit1.connected
    assert slit1.component_names == ("h", "v")

    slit1.h.size.move(0.1)
    slit1.v.size.move(0.2)
    slit1.h.center.move(0.0)
    slit1.v.center.move(0.0)
    timed_pause()
    assert round(slit1.h.size.position, 4) == 0.1
    assert round(slit1.v.size.position, 4) == 0.2
    assert round(slit1.h.center.position, 4) == 0.0
    assert round(slit1.v.center.position, 4) == 0.0

    g = slit1.geometry
    assert isinstance(g, SlitGeometry)
    assert g == SlitGeometry(0.1, 0.2, 0, 0)
    assert round(slit1.h.xn.position, 4) == -0.05
    assert round(slit1.h.xp.position, 4) == 0.05
    assert round(slit1.v.xn.position, 4) == -0.1
    assert round(slit1.v.xp.position, 4) == 0.1


def test_2slit2D_InbOutBotTop():
    slit1 = Optics2Slit2D_InbOutBotTop(f"{IOC_GP}Slit1", name="slit1")
    assert slit1 is not None

    slit1.wait_for_connection()
    assert slit1.connected

    cns = """
    inb out bot top
    hsize hcenter
    vsize vcenter
    hsync vsync
    """.split()
    assert slit1.component_names != tuple(cns)

    slit1.hsize.move(0.3)
    slit1.vsize.move(0.4)
    slit1.hcenter.move(0.0)
    slit1.vcenter.move(0.0)
    timed_pause()
    assert round(slit1.hsize.position, 4) == 0.3
    assert round(slit1.vsize.position, 4) == 0.4
    assert round(slit1.hcenter.position, 4) == 0.0
    assert round(slit1.vcenter.position, 4) == 0.0

    g = slit1.geometry
    assert isinstance(g, SlitGeometry)
    assert g == SlitGeometry(0.3, 0.4, 0, 0)
    assert round(slit1.inb.position, 4) == -0.15
    assert round(slit1.out.position, 4) == 0.15
    assert round(slit1.bot.position, 4) == -0.2
    assert round(slit1.top.position, 4) == 0.2


@pytest.mark.parametrize(
    "class_, prefix, tolerance",
    [
        [Optics2Slit2D_HV, f"{IOC_GP}Slit1", 0.01],
        [Optics2Slit2D_InbOutBotTop, f"{IOC_GP}Slit1", 0.01],
    ],
)
def test_geometry_property(class_, prefix, tolerance):
    slit1 = class_(prefix, name="slit1")
    assert slit1 is not None

    slit1.wait_for_connection()
    assert slit1.connected

    h, v, x, y = (0.3, 0.1, 0.5, -0.4)
    slit1.geometry = (h, v, x, y)
    assert math.isclose(slit1.geometry[0], h, abs_tol=tolerance)
    assert math.isclose(slit1.geometry[1], v, abs_tol=tolerance)
    assert math.isclose(slit1.geometry[2], x, abs_tol=tolerance)
    assert math.isclose(slit1.geometry[3], y, abs_tol=tolerance)

    sg = SlitGeometry(h, v, x, y)
    assert math.isclose(slit1.geometry[0], sg.width, abs_tol=tolerance)
    assert math.isclose(slit1.geometry[1], sg.height, abs_tol=tolerance)
    assert math.isclose(slit1.geometry[2], sg.x, abs_tol=tolerance)
    assert math.isclose(slit1.geometry[3], sg.y, abs_tol=tolerance)
