"""
12-bank Filters from A-V-S

Device uses PyDevice for attenuation calculation and filter configuration

    Parameters
    ==========
    prefix:
      EPICS prefix required to communicate with filter IOC, ex: "100idPyFilter:FL2:"
    translation_motor:
      The motor record PV controlling the lateral translation of the filter system

"""

from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import EpicsMotor
from ophyd import PVPositioner


class filter_index(PVPositioner):
    """
    filter index; increasing index, increasing attenuation
    """

    readback = Cpt(EpicsSignalRO, "sortedIndex_RBV")
    setpoint = Cpt(EpicsSignal, "sortedIndex")
    done = Cpt(EpicsSignalRO, "filterBusy")


class filter_atten(PVPositioner):
    """
    filter attenuation positioner
    """

    readback = Cpt(EpicsSignalRO, "attenuation_actual")
    setpoint = Cpt(EpicsSignal, "attenuation")
    done = Cpt(EpicsSignalRO, "filterBusy")


class filter_trans(PVPositioner):
    """
    filter transmission positioner
    """

    readback = Cpt(EpicsSignalRO, "transmission_RBV")
    setpoint = Cpt(EpicsSignal, "transmission")
    done = Cpt(EpicsSignalRO, "filterBusy")


class AVSfilters(Device):
    def __init__(
        self,
        prefix: str,
        translation_motor: str,
        *args,
        **kwargs,
    ):
        self._translation = translation_motor

        super().__init__(prefix, *args, **kwargs)

    index = FCpt(filter_index, "{prefix}")
    attenuation = FCpt(filter_atten, "{prefix}")
    transmission = FCpt(filter_trans, "{prefix}")
    translation = FCpt(EpicsMotor, "{_translation}", labels={"motors"})

    binary_crl1_config = Cpt(EpicsSignalRO, "filterConfig", kind="hinted")
    bw_crl1_config = Cpt(EpicsSignalRO, "filterConfig_BW")
    rbv_crl1_config = Cpt(EpicsSignalRO, "filterConfig_RBV", kind="hinted")
    inMask_config = Cpt(EpicsSignalRO, "inMask_RBV", kind="config")
    outMask_config = Cpt(EpicsSignalRO, "outMask_RBV", kind="config")
