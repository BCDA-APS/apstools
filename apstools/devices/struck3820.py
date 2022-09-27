"""
Struck 3820
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~Struck3820
"""

from ophyd import Component
from ophyd import Device
from ophyd.mca import EpicsMCARecord
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO


class Struck3820(Device):
    """
    Struck/SIS 3820 Multi-Channel Scaler (as used by USAXS)

    .. index:: Ophyd Device; Struck3820
    """

    start_all = Component(EpicsSignal, "StartAll")
    stop_all = Component(EpicsSignal, "StopAll")
    erase_start = Component(EpicsSignal, "EraseStart")
    erase_all = Component(EpicsSignal, "EraseAll")
    mca1 = Component(EpicsMCARecord, "mca1")
    mca2 = Component(EpicsMCARecord, "mca2")
    mca3 = Component(EpicsMCARecord, "mca3")
    mca4 = Component(EpicsMCARecord, "mca4")
    clock_frequency = Component(EpicsSignalRO, "clock_frequency")
    current_channel = Component(EpicsSignalRO, "CurrentChannel")
    channel_max = Component(EpicsSignalRO, "MaxChannels")
    channels_used = Component(EpicsSignal, "NuseAll")
    elapsed_real_time = Component(EpicsSignalRO, "ElapsedReal")
    preset_real_time = Component(EpicsSignal, "PresetReal")
    dwell_time = Component(EpicsSignal, "Dwell")
    prescale = Component(EpicsSignal, "Prescale")
    acquiring = Component(EpicsSignalRO, "Acquiring", string=True)
    acquire_mode = Component(EpicsSignalRO, "AcquireMode", string=True)
    model = Component(EpicsSignalRO, "Model", string=True)
    firmware = Component(EpicsSignalRO, "Firmware")
    channel_advance = Component(EpicsSignal, "ChannelAdvance")
    count_on_start = Component(EpicsSignal, "CountOnStart")
    software_channel_advance = Component(EpicsSignal, "SoftwareChannelAdvance")
    channel1_source = Component(EpicsSignal, "Channel1Source")
    user_led = Component(EpicsSignal, "UserLED")
    mux_output = Component(EpicsSignal, "MUXOutput")
    input_mode = Component(EpicsSignal, "InputMode")
    output_mode = Component(EpicsSignal, "OutputMode")
    output_polarity = Component(EpicsSignal, "OutputPolarity")
    read_rate = Component(EpicsSignal, "ReadAll.SCAN")
    do_readl_all = Component(EpicsSignal, "DoReadAll")

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
