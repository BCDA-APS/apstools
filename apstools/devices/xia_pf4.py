"""
XIA PF4 Filters
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~Pf4FilterSingle
   ~Pf4FilterDual
   ~Pf4FilterTriple
   ~Pf4FilterCommon
   ~Pf4FilterBank
   ~DualPf4FilterBox
"""

from typing import Any, Dict, Optional, Union

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent


class Pf4FilterBank(Device):
    """
    A single module of XIA PF4 filters (4-blades).

    .. index:: Ophyd Device; Pf4FilterBank

    This class represents a single bank of XIA PF4 filters, which contains
    4 filter blades. It provides control and monitoring of the filter positions
    and transmission values.

    Attributes:
        fPos: Signal for filter position
        control: Read-only signal for bank control status
        bits: Read-only signal for bit flags
        transmission: Read-only signal for transmission value

    EXAMPLES::

        pf4B = Pf4FilterBank("ioc:pf4:", name="pf4B", bank="B")

        # -or-

        class MyTriplePf4(Pf4FilterCommon):
            A = Component(Pf4FilterBank, "", bank="A")
            B = Component(Pf4FilterBank, "", bank="B")
            C = Component(Pf4FilterBank, "", bank="C")

        pf4 = MyTriplePf4("ioc:pf4:", name="pf4")

    :see: https://github.com/epics-modules/optics/blob/master/opticsApp/Db/pf4bank.db
    """

    fPos: EpicsSignal = FormattedComponent(EpicsSignal, "{prefix}fPos{_bank}", kind="config")
    control: EpicsSignalRO = FormattedComponent(EpicsSignalRO, "{prefix}bank{_bank}", string=True, kind="config")
    bits: EpicsSignalRO = FormattedComponent(EpicsSignalRO, "{prefix}bitFlag{_bank}", kind="config")
    transmission: EpicsSignalRO = FormattedComponent(EpicsSignalRO, "{prefix}trans{_bank}", kind="config")

    def __init__(
        self,
        prefix: str,
        bank: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the PF4 filter bank.

        Args:
            prefix: The EPICS PV prefix for the device
            bank: The bank identifier (A, B, C, etc.)
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        self._bank = bank
        super().__init__(prefix=prefix, **kwargs)


class Pf4FilterCommon(Device):
    """
    XIA PF4 filters - common support.

    .. index:: Ophyd Device; Pf4FilterCommon

    This class provides common functionality for XIA PF4 filter configurations.
    It includes signals for transmission, filter thicknesses, and energy settings.

    Attributes:
        transmission: Read-only signal for overall transmission
        inverse_transmission: Read-only signal for inverse transmission
        thickness_Al_mm: Read-only signal for aluminum filter thickness
        thickness_Ti_mm: Read-only signal for titanium filter thickness
        thickness_glass_mm: Read-only signal for glass filter thickness
        energy_keV_local: Signal for local energy setting
        energy_keV_mono: Signal for monochromator energy display
        mode: Signal for operation mode

    EXAMPLE::

        class MyTriplePf4(Pf4FilterCommon):
            A = Component(Pf4FilterBank, "", bank="A")
            B = Component(Pf4FilterBank, "", bank="B")
            C = Component(Pf4FilterBank, "", bank="C")

        pf4 = MyTriplePf4("ioc:pf4:", name="pf4")

    :see: https://github.com/epics-modules/optics/blob/master/opticsApp/Db/pf4common.db
    """

    transmission: EpicsSignalRO = Component(EpicsSignalRO, "trans", kind="hinted")
    inverse_transmission: EpicsSignalRO = Component(EpicsSignalRO, "invTrans", kind="normal")

    thickness_Al_mm: EpicsSignalRO = Component(EpicsSignalRO, "filterAl", kind="config")
    thickness_Ti_mm: EpicsSignalRO = Component(EpicsSignalRO, "filterTi", kind="config")
    thickness_glass_mm: EpicsSignalRO = Component(EpicsSignalRO, "filterGlass", kind="config")

    energy_keV_local: EpicsSignal = Component(EpicsSignal, "E:local", kind="config")
    energy_keV_mono: EpicsSignal = Component(EpicsSignal, "displayEnergy", kind="config")

    mode: EpicsSignal = Component(EpicsSignal, "useMono", string=True, kind="config")


class Pf4FilterSingle(Pf4FilterCommon):
    """
    XIA PF4 Filter: one set of 4 filters (A).

    This class represents a single PF4 filter configuration with one bank of filters.
    """

    A: Pf4FilterBank = Component(Pf4FilterBank, "", bank="A")


class Pf4FilterDual(Pf4FilterSingle):
    """
    XIA PF4 Filter: two sets of 4 filters (A, B).

    This class represents a dual PF4 filter configuration with two banks of filters.
    """

    B: Pf4FilterBank = Component(Pf4FilterBank, "", bank="B")


class Pf4FilterTriple(Pf4FilterDual):
    """
    XIA PF4 Filter: three sets of 4 filters (A, B, C).

    This class represents a triple PF4 filter configuration with three banks of filters.
    """

    C: Pf4FilterBank = Component(Pf4FilterBank, "", bank="C")


class DualPf4FilterBox(Device):
    """
    LEGACY (use Pf4FilterDual now): Dual (Al, Ti) Xia PF4 filter boxes.

    Support from synApps (using Al, Ti foils).

    .. index:: Ophyd Device; DualPf4FilterBox

    This class provides legacy support for dual PF4 filter boxes using aluminum
    and titanium foils. It is recommended to use Pf4FilterDual instead.

    Attributes:
        fPosA: Signal for filter position A
        fPosB: Signal for filter position B
        bankA: Read-only signal for bank A status
        bankB: Read-only signal for bank B status
        bitFlagA: Read-only signal for bank A bit flags
        bitFlagB: Read-only signal for bank B bit flags
        transmission: Read-only signal for overall transmission
        transmission_a: Read-only signal for bank A transmission
        transmission_b: Read-only signal for bank B transmission
        inverse_transmission: Read-only signal for inverse transmission
        thickness_Al_mm: Read-only signal for aluminum filter thickness
        thickness_Ti_mm: Read-only signal for titanium filter thickness
        thickness_glass_mm: Read-only signal for glass filter thickness
        energy_keV_local: Signal for local energy setting
        energy_keV_mono: Signal for monochromator energy display
        mode: Signal for operation mode

    EXAMPLE::

        pf4 = DualPf4FilterBox("2bmb:pf4:", name="pf4")
        pf4_AlTi = DualPf4FilterBox("9idcRIO:pf4:", name="pf4_AlTi")
    """

    fPosA: EpicsSignal = Component(EpicsSignal, "fPosA")
    fPosB: EpicsSignal = Component(EpicsSignal, "fPosB")
    bankA: EpicsSignalRO = Component(EpicsSignalRO, "bankA")
    bankB: EpicsSignalRO = Component(EpicsSignalRO, "bankB")
    bitFlagA: EpicsSignalRO = Component(EpicsSignalRO, "bitFlagA")
    bitFlagB: EpicsSignalRO = Component(EpicsSignalRO, "bitFlagB")
    transmission: EpicsSignalRO = Component(EpicsSignalRO, "trans")
    transmission_a: EpicsSignalRO = Component(EpicsSignalRO, "transA")
    transmission_b: EpicsSignalRO = Component(EpicsSignalRO, "transB")
    inverse_transmission: EpicsSignalRO = Component(EpicsSignalRO, "invTrans")
    thickness_Al_mm: EpicsSignalRO = Component(EpicsSignalRO, "filterAl")
    thickness_Ti_mm: EpicsSignalRO = Component(EpicsSignalRO, "filterTi")
    thickness_glass_mm: EpicsSignalRO = Component(EpicsSignalRO, "filterGlass")
    energy_keV_local: EpicsSignal = Component(EpicsSignal, "E:local")
    energy_keV_mono: EpicsSignal = Component(EpicsSignal, "displayEnergy")
    mode: EpicsSignal = Component(EpicsSignal, "useMono", string=True)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
