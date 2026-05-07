"""
ACS Motors
==========

:class:`~AcsMotors` provides extra signals that are part of AcsMotionControl motor support.

.. autosummary::

    ~AcsMotion
    ~AcsMotorMixin
    ~EpicsMotorWithRes
    ~EpicsMotorWithResAndCNEN
    ~EpicsMotorWithResAndCNENAndDial
"""

from ophyd import Component as Cpt
from ophyd import EpicsMotor
from ophyd import EpicsSignalRO

from .motor_mixins import DeviceMixinBase
from .motor_mixins import EpicsMotorDialMixin
from .motor_mixins import EpicsMotorResolutionMixin
from .motor_mixins import EpicsMotorServoMixin


class EpicsMotorWithRes(EpicsMotorResolutionMixin, EpicsMotor):
    """Adds support for motor record resolution fields."""


class EpicsMotorWithResAndCNEN(EpicsMotorServoMixin, EpicsMotorWithRes):
    """
    Adds "servo" enable/disable (CNEN) field.

    ACS support uses for steppers as well.
    """


class EpicsMotorWithResAndCNENAndDial(EpicsMotorDialMixin, EpicsMotorWithResAndCNEN):
    """Adds support for motor record dial coordinates."""


class AcsMotorMixin(DeviceMixinBase):
    """Components used by EPICS database for ACS Motion Controller."""

    eoffs = Cpt(EpicsSignalRO, ":EOFFS", kind="config")
    """Encoder offset (doesn't persist through power cycle)"""

    e_aoffs = Cpt(EpicsSignalRO, ":E_AOFFS", kind="config")
    """Absolute encoder offset (persists through ACS power cycle)"""

    e2offs = Cpt(EpicsSignalRO, ":E2OFFS", kind="config")
    """Secondary encoder offset (doesn't persist through power cycle)"""

    roffs = Cpt(EpicsSignalRO, ":ROFFS", kind="config")
    """Reference offset"""

    stepf = Cpt(EpicsSignalRO, ":STEPF", kind="config")
    """Step factor (distance per [micro]step)"""

    efac = Cpt(EpicsSignalRO, ":EFAC", kind="config")
    """Encoder factor (distance per encoder count)"""

    e2fac = Cpt(EpicsSignalRO, ":E2FAC", kind="config")
    """Secondary encoder factor (distance per encoder count)"""

    etype = Cpt(EpicsSignalRO, ":E_TYPE", kind="config")
    """Encoder type"""

    e2type = Cpt(EpicsSignalRO, ":E2_TYPE", kind="config")
    """Secondary encoder type"""

    homed = Cpt(EpicsSignalRO, ":HOMED", kind="config")
    """Homing status (using ACS algorithms)"""


class AcsMotor(AcsMotorMixin, EpicsMotorWithResAndCNENAndDial):
    """AcsMotionControl motor support."""
