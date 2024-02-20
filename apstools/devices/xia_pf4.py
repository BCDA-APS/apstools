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

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent


class Pf4FilterBank(Device):
    """
    A single module of XIA PF4 filters (4-blades).

    .. index:: Ophyd Device; Pf4FilterBank

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

    fPos = FormattedComponent(EpicsSignal, "{prefix}fPos{_bank}", kind="config")
    control = FormattedComponent(EpicsSignalRO, "{prefix}bank{_bank}", string=True, kind="config")
    bits = FormattedComponent(EpicsSignalRO, "{prefix}bitFlag{_bank}", kind="config")
    transmission = FormattedComponent(EpicsSignalRO, "{prefix}trans{_bank}", kind="config")

    def __init__(self, prefix, bank=None, **kwargs):
        self._bank = bank
        super().__init__(prefix, **kwargs)


class Pf4FilterCommon(Device):
    """
    XIA PF4 filters - common support.

    .. index:: Ophyd Device; Pf4FilterCommon

    Use ``Pf4FilterCommon`` to build support for a configuration
    of PF4 filters (such as 3 or 4 filter banks).

    EXAMPLE::

        class MyTriplePf4(Pf4FilterCommon):
            A = Component(Pf4FilterBank, "", bank="A")
            B = Component(Pf4FilterBank, "", bank="B")
            C = Component(Pf4FilterBank, "", bank="C")

        pf4 = MyTriplePf4("ioc:pf4:", name="pf4")

    :see: https://github.com/epics-modules/optics/blob/master/opticsApp/Db/pf4common.db
    """

    transmission = Component(EpicsSignalRO, "trans", kind="hinted")
    inverse_transmission = Component(EpicsSignalRO, "invTrans", kind="normal")

    thickness_Al_mm = Component(EpicsSignalRO, "filterAl", kind="config")
    thickness_Ti_mm = Component(EpicsSignalRO, "filterTi", kind="config")
    thickness_glass_mm = Component(EpicsSignalRO, "filterGlass", kind="config")

    energy_keV_local = Component(EpicsSignal, "E:local", kind="config")
    energy_keV_mono = Component(EpicsSignal, "displayEnergy", kind="config")

    mode = Component(EpicsSignal, "useMono", string=True, kind="config")


class Pf4FilterSingle(Pf4FilterCommon):
    """XIA PF4 Filter: one set of 4 filters (A)."""

    A = Component(Pf4FilterBank, "", bank="A")


class Pf4FilterDual(Pf4FilterSingle):
    """XIA PF4 Filter: two sets of 4 filters (A, B)."""

    B = Component(Pf4FilterBank, "", bank="B")


class Pf4FilterTriple(Pf4FilterDual):
    """XIA PF4 Filter: three sets of 4 filters (A, B, C)."""

    C = Component(Pf4FilterBank, "", bank="C")


class DualPf4FilterBox(Device):
    """
    LEGACY (use Pf4FilterDual now): Dual (Al, Ti) Xia PF4 filter boxes

    Support from synApps (using Al, Ti foils)

    .. index:: Ophyd Device; DualPf4FilterBox

    EXAMPLE::

        pf4 = DualPf4FilterBox("2bmb:pf4:", name="pf4")
        pf4_AlTi = DualPf4FilterBox("9idcRIO:pf4:", name="pf4_AlTi")

    """

    fPosA = Component(EpicsSignal, "fPosA")
    fPosB = Component(EpicsSignal, "fPosB")
    bankA = Component(EpicsSignalRO, "bankA")
    bankB = Component(EpicsSignalRO, "bankB")
    bitFlagA = Component(EpicsSignalRO, "bitFlagA")
    bitFlagB = Component(EpicsSignalRO, "bitFlagB")
    transmission = Component(EpicsSignalRO, "trans")
    transmission_a = Component(EpicsSignalRO, "transA")
    transmission_b = Component(EpicsSignalRO, "transB")
    inverse_transmission = Component(EpicsSignalRO, "invTrans")
    thickness_Al_mm = Component(EpicsSignalRO, "filterAl")
    thickness_Ti_mm = Component(EpicsSignalRO, "filterTi")
    thickness_glass_mm = Component(EpicsSignalRO, "filterGlass")
    energy_keV_local = Component(EpicsSignal, "E:local")
    energy_keV_mono = Component(EpicsSignal, "displayEnergy")
    mode = Component(EpicsSignal, "useMono", string=True)


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
