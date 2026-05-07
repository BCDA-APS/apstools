"""
Bragg-Gap double-crystal monochromator
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~BraggGap_Monochromator
"""
from ophyd import Device, EpicsSignal, EpicsSignalRO, EpicsMotor
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt

class BraggGap_Monochromator(Device):
    """
    synApps Bragg Gap double-crystal monochromator epics support

    .. index:: Ophyd Device; BraggGap_Monochromator
    """

    def __init__(
        self,
        prefix: str,
        bragg_motor: str,
        gap_motor: str,
        *args,
        **kwargs,
    ):

        self._bragg_motor = bragg_motor
        self._gap_motor = gap_motor

        super().__init__(prefix, *args, **kwargs)

    # Real motors that directly control the monochromator
    bragg_motor = FCpt(EpicsMotor, "{_bragg_motor}", labels={"motors"})
    gap_motor = FCpt(EpicsMotor, "{_gap_motor}", labels={"motors"})

	# Pseudo motors that relay into real motors based on offset mode
    energy = Cpt(EpicsMotor, "Energy", kind="hinted")
    theta = Cpt(EpicsMotor, "Bragg", kind="normal")
    # lambda is reserved word in Python, can't use it for wavelength
    wavelength = Cpt(EpicsMotor, "Lambda", kind="normal")

    offset = Cpt(EpicsMotor, "Offset", kind="hinted")
    gap = Cpt(EpicsMotor, "Gap", kind="normal")


    offset_mode = Cpt(EpicsSignal, "offset_mode", kind="config", string=True)
    moving = Cpt(EpicsSignal, "EO:Done", kind="omitted")
    allstop_button = Cpt(EpicsSignal, "Bragg.STOP", string=True, kind="omitted")
    use_set = Cpt(EpicsSignal, "UseSet", string=True, kind="config")

    crystal_mode = Cpt(EpicsSignal, "crystal_mode", string=True, kind="config")
    crystal_h = Cpt(EpicsSignal, "BraggHAO", kind="config")
    crystal_k = Cpt(EpicsSignal, "BraggKAO", kind="config")
    crystal_l = Cpt(EpicsSignal, "BraggLAO", kind="config")
    crystal_lattice_constant = Cpt(EpicsSignal, "BraggAAO", kind="config")
    crystal_2d_spacing = Cpt(EpicsSignal, "Bragg2dSpacingAO", kind="config")
    
    def calibrate_energy(self, value):
        """Calibrate the monochromator energy.

        PARAMETERS

        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put("Set")
        self.energy.move(value)
        self.use_set.put("Use")


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2026, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
