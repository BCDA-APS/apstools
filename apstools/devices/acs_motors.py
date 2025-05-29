"""
acsMotors provides extra signals that are part of AcsMotionControl motor support

    eoffs   : Encoder offset (doesn't persist through power cycle)
    e_aoffs : Absolute encoder offset (persists through ACS power cycle)
    e2offs  : Secondary encoder offset (doesn't persist through power cycle)
    roffs   : Reference offset
    stepf   : Step factor (distance per [micro]step)
    efac    : Encoder factor (distance per encoder count)
    e2fac   : Secondary encoder factor (distance per encoder count)
    etype   : Encoder type
    e2type  : Secondary encoder type
    homed   : Homing status (using ACS algorithms)
    
It also includes (from apstools)
   - motor resolution fields
   - "servo" enable/disable (CNEN field) which ACS support uses for steppers as well
   - the dial readback/setpoint
    
"""

from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import EpicsMotor
from ophyd import Component as Cpt

from apstools.devices.mixin_base import DeviceMixinBase

from apstools.devices import EpicsMotorResolutionMixin
from apstools.devices import EpicsMotorServoMixin
from apstools.devices import EpicsMotorDialMixin

class EpicsMotorWithRes(EpicsMotorResolutionMixin, EpicsMotor):
	pass

class EpicsMotorWithResAndCNEN(EpicsMotorServoMixin, EpicsMotorWithRes):
	pass 
	
class EpicsMotorWithResAndCNENAndDial(EpicsMotorDialMixin, EpicsMotorWithResAndCNEN):
	pass 
	
class AcsMotorMixin(DeviceMixinBase):

    # Encoder offset (doesn't persist through power cycle)
    eoffs = Cpt(EpicsSignalRO, ":EOFFS", kind="config")
    # Absolute encoder offset (persists through ACS power cycle)
    e_aoffs = Cpt(EpicsSignalRO, ":E_AOFFS", kind="config")
    # Secondary encoder offset (doesn't persist through power cycle)
    e2offs = Cpt(EpicsSignalRO, ":E2OFFS", kind="config")
    # Reference offset
    roffs = Cpt(EpicsSignalRO, ":ROFFS", kind="config")
    # Step factor (distance per [micro]step)
    stepf = Cpt(EpicsSignalRO, ":STEPF", kind="config")
    # Encoder factor (distance per encoder count)
    efac = Cpt(EpicsSignalRO, ":EFAC", kind="config")
    # Secondary encoder factor (distance per encoder count)
    e2fac = Cpt(EpicsSignalRO, ":E2FAC", kind="config")
    # Encoder type
    etype = Cpt(EpicsSignalRO, ":E_TYPE", kind="config")
    # Secondary encoder type
    e2type =   Cpt(EpicsSignalRO, ":E2_TYPE", kind="config")
    # Homing status (using ACS algorithms)
    homed =   Cpt(EpicsSignalRO, ":HOMED", kind="config")

class AcsMotor(AcsMotorMixin, EpicsMotorWithResAndCNENAndDial):
	pass


