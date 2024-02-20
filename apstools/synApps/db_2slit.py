"""
db_2slit: synApps optics 2slit.db


There are two implementations, corresponding to differing and competing
opinions of how the support should be implemented.

Coordinates of ``Optics2Slit2D_InbOutBotTop`` (viewing from detector towards source)::

       top
    inb   out
       bot

Coordinates of ``Optics2Slit2D_HV`` (viewing from detector towards source)::

        v.xp
    h.xn    h.xp
        v.xn

Each blade [#]_ (in the XIA slit controller) travels in a _cartesian_ coordinate
system.  Positive motion moves a blade **outwards** (towards the ``p`` suffix).
Negative motion moves towards the ``n`` suffix.  Size and center are computed
by the underlying EPICS support.

    hsize = out - inb
    vsize = top - bot

..  [#] Note that the blade names here may be different than the EPICS support.
    The difference is to make the names of the blades consistent with other
    slits with the Bluesky framework.

USAGE::

    slit1 = Optics2Slit2D_HV("gp:Slit1", name="slit1")
    slit1.geometry = 0.1, 0.1, 0, 0  # moves the slits
    print(slit1.geometry)

    slit2 = Optics2Slit_InbOutBotTop("gp:Slit2", name="slit2")
    slit2.geometry = 0.1, 0.1, 0, 0  # moves the slits
    print(slit2.geometry)

Public Structures

.. autosummary::

    ~Optics2Slit1D
    ~Optics2Slit2D_HV
    ~Optics2Slit2D_InbOutBotTop

:see: https://github.com/epics-modules/optics

new in release 1.6.0
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal

from ..devices import PVPositionerSoftDone
from ..utils import SlitGeometry


class Optics2Slit1D(Device):
    """
    EPICS synApps optics 2slit.db 1D support: xn, xp, size, center, sync

    "sync" is used to tell the EPICS 2slit database to synchronize the
    virtual slit values with the actual motor positions.
    """

    xn = Component(PVPositionerSoftDone, "", setpoint_pv="xn", readback_pv="t2.B")
    xp = Component(PVPositionerSoftDone, "", setpoint_pv="xp", readback_pv="t2.A")
    size = Component(PVPositionerSoftDone, "", setpoint_pv="size", readback_pv="t2.C")
    center = Component(PVPositionerSoftDone, "", setpoint_pv="center", readback_pv="t2.D")

    sync = Component(EpicsSignal, "sync", put_complete=True, kind="omitted")


class Optics2Slit2D_HV(Device):
    """
    EPICS synApps optics 2slit.db 2D support: h.xn, h.xp, v.xn, v.xp
    """

    h = Component(Optics2Slit1D, "H")
    v = Component(Optics2Slit1D, "V")

    @property
    def geometry(self):
        """Return the slit 2D size and center as a namedtuple."""
        pppp = [
            round(obj.position, obj.precision) for obj in (self.h.size, self.v.size, self.h.center, self.v.center)
        ]

        return SlitGeometry(*pppp)

    @geometry.setter
    def geometry(self, value):
        # first, test the input by assigning it to local vars
        width, height, x, y = value

        self.h.size.move(width)
        self.v.size.move(height)
        self.h.center.move(x)
        self.v.center.move(y)


class Optics2Slit2D_InbOutBotTop(Device):
    """
    EPICS synApps optics 2slit.db 2D support: inb, out, bot, top
    """

    inb = Component(PVPositionerSoftDone, "H", setpoint_pv="xn", readback_pv="t2.B")
    out = Component(PVPositionerSoftDone, "H", setpoint_pv="xp", readback_pv="t2.A")
    hsize = Component(PVPositionerSoftDone, "H", setpoint_pv="size", readback_pv="t2.C")
    hcenter = Component(PVPositionerSoftDone, "H", setpoint_pv="center", readback_pv="t2.D")

    bot = Component(PVPositionerSoftDone, "V", setpoint_pv="xn", readback_pv="t2.B")
    top = Component(PVPositionerSoftDone, "V", setpoint_pv="xp", readback_pv="t2.A")
    vsize = Component(PVPositionerSoftDone, "V", setpoint_pv="size", readback_pv="t2.C")
    vcenter = Component(PVPositionerSoftDone, "V", setpoint_pv="center", readback_pv="t2.D")

    hsync = Component(EpicsSignal, "Hsync", put_complete=True, kind="omitted")
    vsync = Component(EpicsSignal, "Vsync", put_complete=True, kind="omitted")

    @property
    def geometry(self):
        """Return the slit 2D size and center as a namedtuple."""
        pppp = [round(obj.position, obj.precision) for obj in (self.hsize, self.vsize, self.hcenter, self.vcenter)]

        return SlitGeometry(*pppp)

    @geometry.setter
    def geometry(self, value):
        # first, test the input by assigning it to local vars
        width, height, x, y = value

        self.hsize.move(width)
        self.vsize.move(height)
        self.hcenter.move(x)
        self.vcenter.move(y)


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
