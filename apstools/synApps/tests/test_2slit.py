from ..db_2slit import Optics2Slit1D
from ..db_2slit import Optics2Slit2D_HV
from ..db_2slit import Optics2Slit2D_InbOutBotTop
from ...utils import SlitGeometry

IOC = "gp:"

# TODO: test "sync" signal


def test_2slit1D():
    axis = Optics2Slit1D("gp:Slit1H", name="axis")
    assert axis is not None

    axis.wait_for_connection()
    assert axis.connected

    cns = "xn xp size center sync".split()
    assert axis.component_names == tuple(cns)


def test_2slit2D_HV():
    slit1 = Optics2Slit2D_HV("gp:Slit1", name="slit1")
    assert slit1 is not None

    slit1.wait_for_connection()
    assert slit1.connected
    assert slit1.component_names == ("h", "v")

    slit1.h.size.move(0.1)
    slit1.v.size.move(0.2)
    slit1.h.center.move(0.)
    slit1.v.center.move(0.)
    g = slit1.geometry
    assert isinstance(g, SlitGeometry)
    assert g == SlitGeometry(0.1, 0.2, 0, 0)
    assert round(slit1.h.xn.position, 4) == -0.05
    assert round(slit1.h.xp.position, 4) == 0.05
    assert round(slit1.v.xn.position, 4) == -0.1
    assert round(slit1.v.xp.position, 4) == 0.1


def test_2slit2D_InbOutBotTop():
    slit1 = Optics2Slit2D_InbOutBotTop("gp:Slit1", name="slit1")
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
    slit1.hcenter.move(0.)
    slit1.vcenter.move(0.)
    g = slit1.geometry
    assert isinstance(g, SlitGeometry)
    assert g == SlitGeometry(0.3, 0.4, 0, 0)
    assert round(slit1.inb.position, 4) == -0.15
    assert round(slit1.out.position, 4) == 0.15
    assert round(slit1.bot.position, 4) == -0.2
    assert round(slit1.top.position, 4) == 0.2
