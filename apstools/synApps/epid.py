"""
Ophyd support for the EPICS epid record


Public Structures

.. autosummary::

    ~EpidRecord
    ~Fb_EpidDatabase
    ~Fb_EpidDatabaseHeaterSimulator

:see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
:see: https://github.com/epics-modules/optics/blob/master/opticsApp/Db/fb_epid.db

.. note:: Keep in mind a bug report suggests an update to this database.
   (https://github.com/epics-modules/optics/issues/10)
"""

from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO

from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordFloatFields
from .sseq import SseqRecord
from .swait import SwaitRecord


class EpidRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS synApps epid record support in ophyd

    .. index:: Ophyd Device; synApps EpidRecord

    :see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
    """

    controlled_value_link = Component(EpicsSignal, ".INP", kind="config")
    controlled_value = Component(EpicsSignalRO, ".CVAL", kind="config")

    readback_trigger_link = Component(EpicsSignal, ".TRIG", kind="config")
    readback_trigger_link_value = Component(EpicsSignal, ".TVAL", kind="config")

    setpoint_location = Component(EpicsSignal, ".STPL", kind="config")
    setpoint_mode_select = Component(EpicsSignal, ".SMSL", kind="config")

    output_location = Component(EpicsSignal, ".OUTL", kind="config")
    feedback_on = Component(EpicsSignal, ".FBON", kind="config")

    proportional_gain = Component(EpicsSignal, ".KP", kind="config")
    integral_gain = Component(EpicsSignal, ".KI", kind="config")
    derivative_gain = Component(EpicsSignal, ".KD", kind="config")

    following_error = Component(EpicsSignalRO, ".ERR", kind="config")
    output_value = Component(EpicsSignalRO, ".OVAL", kind="config")
    final_value = Component(EpicsSignalRO, ".VAL", kind="normal")

    calculated_P = Component(EpicsSignalRO, ".P", kind="config")
    calculated_I = Component(EpicsSignal, ".I", kind="config")
    calculated_D = Component(EpicsSignalRO, ".D", kind="config")

    time_difference = Component(EpicsSignal, ".DT", kind="config")
    minimum_delta_time = Component(EpicsSignal, ".MDT", kind="config")

    # limits imposed by the record support:
    #     .LOPR <= .OVAL <= .HOPR
    #     .LOPR <= .I <= .HOPR
    high_limit = Component(EpicsSignal, ".DRVH", kind="config")
    low_limit = Component(EpicsSignal, ".DRVL", kind="config")

    @property
    def value(self):
        return self.output_value.get()


class Fb_EpidDatabase(EpidRecord):
    """
    EPICS synApps optics fb_epid database support in ophyd.

    .. see: https://github.com/epics-modules/optics/blob/master/opticsApp/Db/fb_epid.db
    """

    final_value = None  # replace final_value (RO) with setpoint (R/W)
    setpoint = Component(EpicsSignal, ".VAL", kind="config")

    on = Component(EpicsSignal, ":on", string=True, kind="config")
    feedback_on = Component(EpicsSignalRO, ".FBON", string=True, kind="omitted")

    enable_calc = Component(SwaitRecord, ":enable")
    in_calc = Component(SwaitRecord, ":in")
    obuf_calc = Component(SwaitRecord, ":obuf")
    out_calc = Component(SwaitRecord, ":out")
    resume_calc = Component(SwaitRecord, ":resume")
    outpv = Component(SseqRecord, ":outpv")

    @property
    def is_feedback_on(self):
        return str(self.feedback_on.get()).lower() in ("on", 1)


class Fb_EpidDatabaseHeaterSimulator(Fb_EpidDatabase):
    """
    Heater simulator in EPICS synApps optics fb_epid database.
    """

    sim_calc = Component(SwaitRecord, ":sim")

    def setup(self, scan=".2 second", Kp=0.0004, Ki=0.5, T0=25.5):
        for obj in (
            self.enable_calc,
            self.in_calc,
            self.obuf_calc,
            self.out_calc,
            self.resume_calc,
            self.sim_calc,
            self,
        ):
            # change from default ("I/O Intr" which is incorrect for swait records)
            obj.scanning_rate.put(scan)

        self.sim_calc.channels.H.input_value.put(0.1)  # simulated temperature sensor noise variation
        self.sim_calc.calculation.put("max(A,F*(1-B)+C*D*G+H*(RNDM-.5))")  # add random noise
        self.sim_calc.precision.put(2)  # temperature good to 2 digits
        self.high_limit.put(1.0)  # epid can ramp power up to 100% max
        self.proportional_gain.put(Kp)
        self.integral_gain.put(Ki)
        self.setpoint.put(T0)
        self.on.put("on")  # turn on the temperature control

    def reset(self):
        self.on.put("off")  # turn off the temperature control
        for obj in (
            self.enable_calc,
            self.in_calc,
            self.obuf_calc,
            self.out_calc,
            self.resume_calc,
            self.sim_calc,
            self,
        ):
            obj.scanning_rate.put("Passive")

        readback = self.sim_calc.channels.F.input_value.get()
        self.setpoint.put(round(readback, 1))
        self.proportional_gain.put(0)  # Kp
        self.integral_gain.put(0)  # Ki
        self.high_limit.put(1.0)  # epid can ramp power up to 100% max
        self.sim_calc.channels.H.input_value.put(0.1)  # simulated temperature sensor noise variation


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
