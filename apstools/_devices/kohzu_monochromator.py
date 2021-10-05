"""
Kohzu double-crystal monochromator
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~KohzuSeqCtl_Monochromator
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO


class KohzuSeqCtl_Monochromator(Device):
    """
    synApps Kohzu double-crystal monochromator sequence control program

    .. index:: Ophyd Device; KohzuSeqCtl_Monochromator
    """

    # lambda is reserved word in Python, can't use it
    wavelength = Component(EpicsSignal, "BraggLambdaRdbkAO", write_pv="BraggLambdaAO")
    energy = Component(EpicsSignal, "BraggERdbkAO", write_pv="BraggEAO")
    theta = Component(EpicsSignal, "BraggThetaRdbkAO", write_pv="BraggThetaAO")
    y1 = Component(EpicsSignalRO, "KohzuYRdbkAI")
    z2 = Component(EpicsSignalRO, "KohzuZRdbkAI")
    message2 = Component(EpicsSignalRO, "KohzuSeqMsg2SI")
    operator_acknowledge = Component(EpicsSignal, "KohzuOperAckBO")
    use_set = Component(EpicsSignal, "KohzuUseSetBO")
    mode = Component(EpicsSignal, "KohzuModeBO")
    move_button = Component(EpicsSignal, "KohzuPutBO")
    moving = Component(EpicsSignal, "KohzuMoving")
    y_offset = Component(EpicsSignal, "Kohzu_yOffsetAO")

    crystal_mode = Component(EpicsSignal, "KohzuMode2MO")
    crystal_h = Component(EpicsSignal, "BraggHAO")
    crystal_k = Component(EpicsSignal, "BraggKAO")
    crystal_l = Component(EpicsSignal, "BraggLAO")
    crystal_lattice_constant = Component(EpicsSignal, "BraggAAO")
    crystal_2d_spacing = Component(EpicsSignal, "Bragg2dSpacingAO")
    crystal_type = Component(EpicsSignal, "BraggTypeMO")

    def move_energy(self, energy):
        """for command-line use:  ``kohzu_mono.energy_move(8.2)``"""
        self.energy.put(energy)
        self.move_button.put(1)

    def calibrate_energy(self, value):
        """Calibrate the mono energy.

        PARAMETERS

        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put("Set")
        self.energy.put(value)
        self.use_set.put("Use")
