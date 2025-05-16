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

from typing import Any, Dict, Optional, Tuple, Union

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import Signal

from ..devices import PVPositionerSoftDone
from ..utils import SlitGeometry


class XiaSlit2D(Device):
    """
    EPICS synApps optics xia_slit.db 2D support: inb out bot top ...

    This class provides an interface to the XIA slit controller, which controls
    a 2D slit with four blades (inboard, outboard, bottom, top). The controller
    operates in a cylindrical coordinate system where positive motion moves blades
    outward from the center with backlash correction.

    Attributes:
        inb: Inboard blade positioner
        out: Outboard blade positioner
        bot: Bottom blade positioner
        top: Top blade positioner
        hsize: Horizontal size positioner
        vsize: Vertical size positioner
        hcenter: Horizontal center positioner
        vcenter: Vertical center positioner
        hID: Horizontal ID signal
        horientation: Horizontal orientation signal
        hbusy: Horizontal busy status signal
        vID: Vertical ID signal
        vorientation: Vertical orientation signal
        vbusy: Vertical busy status signal
        enable: Enable signal
        error_code: Error code signal
        error_message: Error message signal
        message1-3: Diagnostic message signals
        calibrate: Calibration signal
        initialize: Initialization signal
        locate: Location signal
        stop_button: Stop button signal
        precision: Precision setting signal
    """

    inb: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="l", readback_pv="lRB")
    out: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="r", readback_pv="rRB")
    bot: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="b", readback_pv="bRB")
    top: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="t", readback_pv="tRB")

    hsize: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="width", readback_pv="widthRB")
    vsize: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="height", readback_pv="heightRB")
    hcenter: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="h0", readback_pv="h0RB")
    vcenter: PVPositionerSoftDone = Component(PVPositionerSoftDone, "", setpoint_pv="v0", readback_pv="v0RB")

    hID: EpicsSignal = Component(EpicsSignal, "hID", kind="config", string=True)
    horientation: EpicsSignal = Component(EpicsSignal, "hOrient", kind="config", string=True)
    hbusy: EpicsSignalRO = Component(EpicsSignalRO, "hBusy", kind="omitted", string=True)

    vID: EpicsSignal = Component(EpicsSignal, "vID", kind="config", string=True)
    vorientation: EpicsSignal = Component(EpicsSignal, "vOrient", kind="config", string=True)
    vbusy: EpicsSignalRO = Component(EpicsSignalRO, "vBusy", kind="omitted", string=True)

    enable: EpicsSignal = Component(EpicsSignal, "enable", kind="config", string=True)

    # diagnostics
    error_code: EpicsSignalRO = Component(EpicsSignalRO, "err", kind="config")
    error_message: EpicsSignalRO = Component(EpicsSignalRO, "errMsg", kind="config", string=True)
    message1: EpicsSignalRO = Component(EpicsSignalRO, "msg1", kind="config", string=True)
    message2: EpicsSignalRO = Component(EpicsSignalRO, "msg2", kind="config", string=True)
    message3: EpicsSignalRO = Component(EpicsSignalRO, "msg3", kind="config", string=True)

    # configuration
    calibrate: EpicsSignal = Component(EpicsSignal, "calib", kind="omitted", put_complete=True)
    initialize: EpicsSignal = Component(EpicsSignal, "init", kind="omitted", put_complete=True)
    locate: EpicsSignal = Component(EpicsSignal, "locate", kind="omitted", put_complete=True)
    stop_button: EpicsSignal = Component(EpicsSignal, "stop", kind="omitted", put_complete=True)

    precision: Signal = Component(Signal, value=3, kind="config")

    def __init__(
        self,
        prefix: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the XIA Slit 2D device.

        Args:
            prefix: The EPICS PV prefix for the device
            *args: Additional positional arguments to pass to the parent class
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(prefix=prefix, *args, **kwargs)

    @property
    def geometry(self) -> SlitGeometry:
        """
        Return the slit 2D size and center as a namedtuple.

        Returns:
            SlitGeometry: A namedtuple containing (width, height, x_center, y_center)
        """
        pppp = [
            round(obj.position, self.precision.get())
            for obj in (self.hsize, self.vsize, self.hcenter, self.vcenter)
        ]

        return SlitGeometry(*pppp)

    @geometry.setter
    def geometry(self, value: Tuple[float, float, float, float]) -> None:
        """
        Set the slit geometry (size and center).

        Args:
            value: A tuple of (width, height, x_center, y_center)

        Raises:
            ValueError: If the input tuple does not have exactly 4 elements
        """
        # first, test the input by assigning it to local vars
        width, height, x, y = value

        self.hsize.move(width)
        self.vsize.move(height)
        self.hcenter.move(x)
        self.vcenter.move(y)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
