"""
XIA Slit from EPICS synApps optics: xia_slit.db
+++++++++++++++++++++++++++++++++++++++++++++++

Coordinates (viewing from detector towards source)::

        top
    inb     out
        bot

Each blade [#]_ (in the XIA slit controller) travels in a _cylindrical_
coordinate system.  Positive motion moves a blade **outwards** from the center
with a backlash correction. No backlash correction is applied for negative
motion (as the blades close).  Size and center are computed
by the underlying EPICS support.

    hsize = inb + out
    vsize = top + bot

..  [#] Note that the blade names here are different than the EPICS support.
    The difference is to make the names of the blades consistent with other
    slits with the Bluesky framework.

USAGE:

    slit = XiaSlitController("IOC:hsc1:", name="slit")
    print(slit.geometry)

.. autosummary::

   ~XiaSlit2D
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ..devices import PVPositionerSoftDone
from ophyd import Signal

from ..utils import SlitGeometry


class XiaSlit2D(Device):
    """
    EPICS synApps optics xia_slit.db 2D support: inb out bot top ...
    """

    inb = Component(
        PVPositionerSoftDone, "", setpoint_pv="l", readback_pv="lRB"
    )
    out = Component(
        PVPositionerSoftDone, "", setpoint_pv="r", readback_pv="rRB"
    )
    bot = Component(
        PVPositionerSoftDone, "", setpoint_pv="b", readback_pv="bRB"
    )
    top = Component(
        PVPositionerSoftDone, "", setpoint_pv="t", readback_pv="tRB"
    )

    hsize = Component(
        PVPositionerSoftDone, "", setpoint_pv="width", readback_pv="widthRB"
    )
    vsize = Component(
        PVPositionerSoftDone, "", setpoint_pv="height", readback_pv="heightRB"
    )
    hcenter = Component(
        PVPositionerSoftDone, "", setpoint_pv="h0", readback_pv="h0RB"
    )
    vcenter = Component(
        PVPositionerSoftDone, "", setpoint_pv="v0", readback_pv="v0RB"
    )

    hID = Component(EpicsSignal, "hID", kind="config", string=True)
    horientation = Component(EpicsSignal, "hOrient", kind="config", string=True)
    hbusy = Component(EpicsSignalRO, "hBusy", kind="omitted", string=True)

    vID = Component(EpicsSignal, "vID", kind="config", string=True)
    vorientation = Component(EpicsSignal, "vOrient", kind="config", string=True)
    vbusy = Component(EpicsSignalRO, "vBusy", kind="omitted", string=True)

    enable = Component(EpicsSignal, "enable", kind="config", string=True)

    # diagnostics
    error_code = Component(EpicsSignalRO, "err", kind="config")
    error_message = Component(EpicsSignalRO, "errMsg", kind="config", string=True)
    message1 = Component(EpicsSignalRO, "msg1", kind="config", string=True)
    message2 = Component(EpicsSignalRO, "msg2", kind="config", string=True)
    message3 = Component(EpicsSignalRO, "msg3", kind="config", string=True)

    # configuration
    calibrate = Component(EpicsSignal, "calib", kind="omitted", put_complete=True)
    initialize = Component(EpicsSignal, "init", kind="omitted", put_complete=True)
    locate = Component(EpicsSignal, "locate", kind="omitted", put_complete=True)
    stop_button = Component(EpicsSignal, "stop", kind="omitted", put_complete=True)

    precision = Component(Signal, value=3, kind="config")

    @property
    def geometry(self):
        """Return the slit 2D size and center as a namedtuple."""
        pppp = [
            round(obj.position, self.precision.get())
            for obj in (
                self.hsize,
                self.vsize,
                self.hcenter,
                self.vcenter
            )
        ]

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
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
