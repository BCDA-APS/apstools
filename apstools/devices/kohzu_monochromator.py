"""
Kohzu double-crystal monochromator
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~KohzuSeqCtl_Monochromator
"""

import logging
import time

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import PVPositioner
from ophyd import Signal

from ..utils import run_in_thread

logger = logging.getLogger(__name__)


class KohzuSoftPositioner(PVPositioner):
    setpoint = Component(EpicsSignal, "AO", kind="normal")
    readback = Component(EpicsSignalRO, "RdbkAO", kind="hinted")
    done = Component(Signal, value=0, kind="omitted")
    done_value = 0

    def cb_done(self, *args, **kwargs):
        """
        Called when parent's done signal changes (EPICS CA monitor event).
        """
        self.done.put(self.parent.moving.get())

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).

        When the setpoint is changed, force ``done=False``.  For any move,
        done must transition to ``!= done_value``, then back to ``done_value``.
        Next update will refresh value from parent device.
        """
        self.done.put(1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prepare the positioner to be stopped.
        # Tells monochromator to stop its motors.  Brutal.
        self.stop_signal = self.parent.allstop_button
        self.stop_value = 1

        # setup callbacks on done and setpoint
        self.setpoint.subscribe(self.cb_setpoint)
        self.parent.moving.subscribe(self.cb_done)

        # the readback needs no adjective
        self.readback.name = self.name

    @property
    def inposition(self):
        """Report (boolean) if positioner is done."""
        return self.done.get() == self.done_value

    def move(self, *args, **kwargs):
        """Reposition, with optional wait for completion."""

        @run_in_thread
        def push_the_move_button_soon(delay_s=0.01):
            time.sleep(delay_s)  # wait a short time
            self.parent.move_button.put(1)

        push_the_move_button_soon()
        return super().move(*args, **kwargs)

    def _setup_move(self, position):
        """Move and do not wait until motion is complete (asynchronous)."""
        self.log.debug("%s.setpoint = %s", self.name, position)
        self.setpoint.put(position, wait=False)  # was: wait=True
        if self.actuate is not None:
            self.log.debug("%s.actuate = %s", self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)


class KohzuSeqCtl_Monochromator(Device):
    """
    synApps Kohzu double-crystal monochromator sequence control program

    .. index:: Ophyd Device; KohzuSeqCtl_Monochromator
    """

    energy = Component(KohzuSoftPositioner, "BraggE", kind="hinted")
    theta = Component(KohzuSoftPositioner, "BraggTheta", kind="normal")
    # lambda is reserved word in Python, can't use it for wavelength
    wavelength = Component(KohzuSoftPositioner, "BraggLambda", kind="normal")

    y1 = Component(EpicsSignalRO, "KohzuYRdbkAI", kind="normal")
    z2 = Component(EpicsSignalRO, "KohzuZRdbkAI", kind="normal")

    message2 = Component(EpicsSignalRO, "KohzuSeqMsg2SI", kind="config")
    operator_acknowledge = Component(EpicsSignal, "KohzuOperAckBO", kind="omitted")
    use_set = Component(EpicsSignal, "KohzuUseSetBO", kind="omitted")
    mode = Component(EpicsSignal, "KohzuModeBO", kind="config", string=True)
    move_button = Component(EpicsSignal, "KohzuPutBO", put_complete=True, kind="omitted")
    moving = Component(EpicsSignal, "KohzuMoving", kind="omitted")
    y_offset = Component(EpicsSignal, "Kohzu_yOffsetAO", kind="config")
    allstop_button = Component(EpicsSignal, "allstop", string=True, kind="omitted")

    crystal_mode = Component(EpicsSignal, "KohzuMode2MO", string=True, kind="config")
    crystal_h = Component(EpicsSignal, "BraggHAO", kind="config")
    crystal_k = Component(EpicsSignal, "BraggKAO", kind="config")
    crystal_l = Component(EpicsSignal, "BraggLAO", kind="config")
    crystal_lattice_constant = Component(EpicsSignal, "BraggAAO", kind="config")
    crystal_2d_spacing = Component(EpicsSignal, "Bragg2dSpacingAO", kind="config")
    crystal_type = Component(EpicsSignal, "BraggTypeMO", string=True, kind="config")

    def calibrate_energy(self, value):
        """Calibrate the monochromator energy.

        PARAMETERS

        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put("Set")
        self.energy.put(value)
        self.use_set.put("Use")


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
