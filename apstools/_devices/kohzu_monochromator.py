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
from ophyd import Signal
from ophyd import PVPositioner

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

        # setup callbacks on done and setpoint
        self.setpoint.subscribe(self.cb_setpoint)
        self.parent.moving.subscribe(self.cb_done)

        # the readback needs no adjective
        self.readback.name = self.name

    @property
    def inposition(self):
        """
        Report (boolean) if positioner is done.
        """
        return self.done.get() == self.done_value

    def stop(self, *, success=False):
        """
        Hold at readback value when the stop() method is called and not done.
        """
        if not self.done.get():
            self.setpoint.put(self.position)

    def move(self, *args, **kwargs):
        @run_in_thread
        def push_the_move_button_soon():
            time.sleep(0.01)  # wait a short time
            self.parent.move_button.put(1)

        push_the_move_button_soon()
        return super().move(*args, **kwargs)


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
    mode = Component(EpicsSignal, "KohzuModeBO", kind="config")
    move_button = Component(
        EpicsSignal, "KohzuPutBO", put_complete=True, kind="omitted"
    )
    moving = Component(EpicsSignal, "KohzuMoving", kind="omitted")
    y_offset = Component(EpicsSignal, "Kohzu_yOffsetAO", kind="config")

    crystal_mode = Component(EpicsSignal, "KohzuMode2MO", string=True, kind="config")
    crystal_h = Component(EpicsSignal, "BraggHAO", kind="config")
    crystal_k = Component(EpicsSignal, "BraggKAO", kind="config")
    crystal_l = Component(EpicsSignal, "BraggLAO", kind="config")
    crystal_lattice_constant = Component(EpicsSignal, "BraggAAO", kind="config")
    crystal_2d_spacing = Component(EpicsSignal, "Bragg2dSpacingAO", kind="config")
    crystal_type = Component(EpicsSignal, "BraggTypeMO", string=True, kind="config")

    def move_energy(self, energy):
        """
        DEPRECATED: Simple command-line use to change the energy.

        USAGE::

            kohzu_mono.energy_move(8.2)

        INSTEAD::

            %mov kohzu_mono.mode "Auto" kohzu_mono.energy 8.2

        To be removed in apstools release 1.6.0
        """
        self.move_button.put(1)
        self.energy.put(energy)

    def calibrate_energy(self, value):
        """Calibrate the mono energy.

        PARAMETERS

        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put("Set")
        self.energy.put(value)
        self.use_set.put("Use")
