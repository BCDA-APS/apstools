"""
Ophyd support for the EPICS synApps swait record

EXAMPLES::

    import apstools.synApps
    calcs = apstools.synApps.UserCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    apstools.synApps.setup_random_number_swait(calc1)

    apstools.synApps.setup_incrementer_swait(calcs.calc2)

    calc1.reset()


.. autosummary::

    ~UserCalcN
    ~UserCalcsDevice
    ~SwaitRecord
    ~SwaitRecordChannel
    ~setup_random_number_swait
    ~setup_gaussian_swait
    ~setup_lorentzian_swait
    ~setup_incrementer_swait

:see: https://htmlpreview.github.io/?https://raw.githubusercontent.com/epics-modules/calc/R3-6-1/documentation/swaitRecord.html
"""

from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import FormattedComponent as FC
from ophyd.signal import EpicsSignalBase

from .. import utils as APS_utils
from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsSynAppsRecordEnableMixin

CHANNEL_LETTERS_LIST = "A B C D E F G H I J K L".split()


class SwaitRecordChannel(Device):
    """
    EPICS synApps synApps swait record: single channel [A-L]

    .. index:: Ophyd Device; synApps SwaitRecordChannel
    """

    input_value = FC(EpicsSignal, "{self.prefix}.{self._ch_letter}", kind="config")
    input_pv = FC(EpicsSignal, "{self.prefix}.IN{self._ch_letter}N", kind="config")
    input_trigger = FC(EpicsSignal, "{self.prefix}.IN{self._ch_letter}P", kind="config")
    read_attrs = [
        "input_value",
    ]
    hints = {"fields": read_attrs}

    def __init__(self, prefix: str, letter: str, **kwargs: Any) -> None:
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)

    def reset(self) -> None:
        """Set all fields to default values."""
        self.input_pv.put("")
        self.input_value.put(0)
        self.input_trigger.put("Yes")


def _swait_channels(channel_list: List[str]) -> Dict[str, tuple]:
    """Create channel definitions."""
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (SwaitRecordChannel, "", {"letter": chan})
    return defn


class SwaitRecord(EpicsRecordDeviceCommonAll):
    """
    EPICS synApps swait record: used as ``$(P):userCalc$(N)``

    .. index:: Ophyd Device; synApps SwaitRecord

    .. autosummary::

        ~reset

    """

    precision = Cpt(EpicsSignal, ".PREC", kind="config")
    high_operating_range = Cpt(EpicsSignal, ".HOPR", kind="config")
    low_operating_range = Cpt(EpicsSignal, ".LOPR", kind="config")

    calculated_value = Cpt(EpicsSignal, ".VAL", kind="hinted")
    calculation = Cpt(EpicsSignal, ".CALC", kind="config")

    output_link_pv = Cpt(EpicsSignal, ".OUTN", kind="config")
    output_location_name = Cpt(EpicsSignal, ".DOLN", kind="config")
    output_location_data = Cpt(EpicsSignal, ".DOLD", kind="config")
    output_data_option = Cpt(EpicsSignal, ".DOPT", kind="config")

    output_execute_option = Cpt(EpicsSignal, ".OOPT", kind="config")
    output_execution_delay = Cpt(EpicsSignal, ".ODLY", kind="config")
    event_to_issue = Cpt(EpicsSignal, ".OEVT", kind="config")

    read_attrs = APS_utils.itemizer("channels.%s", CHANNEL_LETTERS_LIST)
    hints = {"fields": read_attrs}

    channels = DDC(_swait_channels(CHANNEL_LETTERS_LIST))

    @property
    def value(self) -> Any:
        """Get calculated value."""
        return self.calculated_value.get()

    def reset(self) -> None:
        """Set all fields to default values."""
        pvname = self.description.pvname.split(".")[0]
        self.description.put(pvname)
        self.scanning_rate.put("Passive")
        self.calculation.put("0")
        self.precision.put("5")
        self.output_location_data.put(0)
        self.output_location_name.put("")
        self.output_data_option.put("Use VAL")
        self.forward_link.put("0")
        self.output_execution_delay.put(0)
        self.output_execute_option.put("Every Time")
        self.output_link_pv.put("")
        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(channel, SwaitRecordChannel):
                channel.reset()

        self.read_attrs = ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]
        self.hints = {"fields": self.read_attrs}

        self.read_attrs.append("calculated_value")


class UserCalcN(EpicsSynAppsRecordEnableMixin, SwaitRecord):
    """Single instance of the userCalcN database."""


class UserCalcsDevice(Device):
    """
    EPICS synApps XXX IOC setup of userCalcs: ``$(P):userCalc$(N)``

    .. index:: Ophyd Device; synApps UserCalcsDevice

    .. autosummary::

        ~reset

    """

    enable = Cpt(EpicsSignal, "userCalcEnable", kind="config")
    calc1 = Cpt(UserCalcN, "userCalc1")
    calc2 = Cpt(UserCalcN, "userCalc2")
    calc3 = Cpt(UserCalcN, "userCalc3")
    calc4 = Cpt(UserCalcN, "userCalc4")
    calc5 = Cpt(UserCalcN, "userCalc5")
    calc6 = Cpt(UserCalcN, "userCalc6")
    calc7 = Cpt(UserCalcN, "userCalc7")
    calc8 = Cpt(UserCalcN, "userCalc8")
    calc9 = Cpt(UserCalcN, "userCalc9")
    calc10 = Cpt(UserCalcN, "userCalc10")

    def reset(self) -> None:  # lgtm [py/similar-function]
        """Set all fields to default values."""
        self.calc1.reset()
        self.calc2.reset()
        self.calc3.reset()
        self.calc4.reset()
        self.calc5.reset()
        self.calc6.reset()
        self.calc7.reset()
        self.calc8.reset()
        self.calc9.reset()
        self.calc10.reset()
        self.read_attrs = ["calc%d" % (c + 1) for c in range(10)]


def setup_random_number_swait(swait: SwaitRecord, **kwargs: Any) -> None:
    """Setup swait record to generate random numbers."""
    swait.reset()
    swait.scanning_rate.put("Passive")
    swait.description.put("uniform random numbers")
    swait.calculation.put("RNDM")
    swait.scanning_rate.put(".1 second")

    swait.read_attrs = [
        "calculated_value",
    ]
    swait.hints = {"fields": swait.read_attrs}


def _setup_peak_swait_(
    calc: str,
    desc: str,
    swait: SwaitRecord,
    ref_signal: EpicsSignalBase,
    center: float = 0,
    width: float = 1,
    scale: float = 1,
    noise: float = 0.05,
) -> None:
    """
    Internal: setup that is common to both Gaussian and Lorentzian swaits.

    Args:
        calc: Calculation type
        desc: Description
        swait: Instance of SwaitRecord
        ref_signal: Instance of EpicsSignal used as $A$
        center: EPICS record field $B$, default = 0
        width: EPICS record field $C$, default = 1
        scale: EPICS record field $D$, default = 1
        noise: EPICS record field $E$, default = 0.05
    """
    if not isinstance(swait, SwaitRecord):
        raise TypeError("expected SwaitRecord instance, received {type(swait)}")
    if not isinstance(ref_signal, EpicsSignalBase):
        raise TypeError("expected EpicsSignalBase instance, received {type(ref_signal)}")
    if width <= 0:
        raise ValueError(f"width must be positive, received {width}")
    if not (0.0 <= noise <= 1.0):
        raise ValueError(f"noise must be between 0 and 1, received {noise}")

    swait.reset()
    swait.scanning_rate.put("Passive")
    swait.description.put(desc)
    swait.channels.A.input_pv.put(ref_signal.pvname)
    swait.channels.B.input_value.put(center)
    swait.channels.C.input_value.put(width)
    swait.channels.D.input_value.put(scale)
    swait.channels.E.input_value.put(noise)
    swait.calculation.put(calc)


def setup_gaussian_swait(
    swait: SwaitRecord,
    ref_signal: EpicsSignalBase,
    center: float = 0,
    width: float = 1,
    scale: float = 1,
    noise: float = 0.05,
) -> None:
    """
    Setup swait record to generate Gaussian peak.

    Args:
        swait: Instance of SwaitRecord
        ref_signal: Instance of EpicsSignal used as $A$
        center: EPICS record field $B$, default = 0
        width: EPICS record field $C$, default = 1
        scale: EPICS record field $D$, default = 1
        noise: EPICS record field $E$, default = 0.05
    """
    _setup_peak_swait_(
        "D*EXP(-(A-B)^2/(2*C^2))*(1+E*(RNDM-0.5))",
        "Gaussian peak",
        swait,
        ref_signal,
        center,
        width,
        scale,
        noise,
    )


def setup_lorentzian_swait(
    swait: SwaitRecord,
    ref_signal: EpicsSignalBase,
    center: float = 0,
    width: float = 1,
    scale: float = 1,
    noise: float = 0.05,
) -> None:
    """
    Setup swait record to generate Lorentzian peak.

    Args:
        swait: Instance of SwaitRecord
        ref_signal: Instance of EpicsSignal used as $A$
        center: EPICS record field $B$, default = 0
        width: EPICS record field $C$, default = 1
        scale: EPICS record field $D$, default = 1
        noise: EPICS record field $E$, default = 0.05
    """
    _setup_peak_swait_(
        "D*C^2/((A-B)^2+C^2)*(1+E*(RNDM-0.5))",
        "Lorentzian peak",
        swait,
        ref_signal,
        center,
        width,
        scale,
        noise,
    )


def setup_incrementer_swait(swait: SwaitRecord, scan: Optional[Any] = None, limit: int = 100000) -> None:
    """
    Setup swait record to increment a value.

    Args:
        swait: Instance of SwaitRecord
        scan: Scan object
        limit: Maximum value, default = 100000
    """
    swait.reset()
    swait.scanning_rate.put("Passive")
    swait.description.put("incrementer")
    swait.calculation.put("A+1")
    swait.channels.A.input_value.put(0)
    swait.channels.B.input_value.put(limit)
    swait.channels.C.input_value.put(0)
    swait.channels.D.input_value.put(0)
    swait.channels.E.input_value.put(0)
    swait.channels.F.input_value.put(0)
    swait.channels.G.input_value.put(0)
    swait.channels.H.input_value.put(0)
    swait.channels.I.input_value.put(0)
    swait.channels.J.input_value.put(0)
    swait.channels.K.input_value.put(0)
    swait.channels.L.input_value.put(0)
    swait.scanning_rate.put(".1 second")

    if scan is not None:
        scan.add_callback(swait.channels.A.input_value)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
