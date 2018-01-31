
"""
(ophyd) Devices that might be useful at the APS using BlueSky

.. autosummary::
   
    ~sscanRecord  
    ~sscanDevice
    ~swaitRecord
    ~swait_setup_random_number
    ~swait_setup_gaussian
    ~swait_setup_lorentzian
    ~swait_setup_incrementer
    ~userCalcsDevice
    ~EpicsMotorWithDial
    ~EpicsMotorWithServo

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.


from .synApps_ophyd import *
from ophyd import Component, EpicsMotor


class EpicsMotorWithDial(EpicsMotor):
    """
    add motor record's dial coordinates to EpicsMotor
    
    USAGE::
    
        m1 = EpicsMotorWithDial('xxx:m1', name='m1')
    
    """
    dial = Component(EpicsSignal, ".DRBV", write_pv=".DVAL")


class EpicsMotorWithServo(EpicsMotor):
    """extend basic motor support to enable/disable the servo loop controls"""
    
    # values: "Enable" or "Disable"
    servo = Component(EpicsSignal, ".CNEN", string=True)
