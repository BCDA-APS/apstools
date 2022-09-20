"""
Generalized ophyd Device base class for preamplifiers.

.. autosummary::

   ~PreamplifierBaseDevice
"""

from ophyd import Component
from ophyd import Device
from ophyd import Signal


class PreamplifierBaseDevice(Device):
    """
    Generalized interface (base class) for preamplifiers.

    All subclasses of ``PreamplifierBaseDevice`` must define how to update the
    gain with the correct value from the amplifier. An example is
    :class:`~apstools._devices.srs570_preamplifier.SRS570_PreAmplifier`.

    :see: https://github.com/BCDA-APS/apstools/issues/544
    """

    gain = Component(Signal, kind="normal", value=1)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
