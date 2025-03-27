"""
Struck 3820
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~Struck3820
"""

from typing import Any, Dict, Optional, Union

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd.mca import EpicsMCARecord


class Struck3820(Device):
    """
    Struck/SIS 3820 Multi-Channel Scaler (as used by USAXS).

    .. index:: Ophyd Device; Struck3820

    This class provides an interface to the Struck/SIS 3820 Multi-Channel Scaler
    device, commonly used in USAXS experiments. It includes various EPICS signals
    for controlling and monitoring the device's operation.

    Attributes:
        start_all: Signal to start all channels
        stop_all: Signal to stop all channels
        erase_start: Signal to erase and start
        erase_all: Signal to erase all channels
        mca1-mca4: Multi-channel analyzer records
        clock_frequency: Read-only signal for clock frequency
        current_channel: Read-only signal for current channel
        channel_max: Read-only signal for maximum channels
        channels_used: Signal for number of channels used
        elapsed_real_time: Read-only signal for elapsed real time
        preset_real_time: Signal for preset real time
        dwell_time: Signal for dwell time
        prescale: Signal for prescale value
        acquiring: Read-only signal for acquisition status
        acquire_mode: Read-only signal for acquisition mode
        model: Read-only signal for device model
        firmware: Read-only signal for firmware version
        channel_advance: Signal for channel advance
        count_on_start: Signal for count on start
        software_channel_advance: Signal for software channel advance
        channel1_source: Signal for channel 1 source
        user_led: Signal for user LED
        mux_output: Signal for multiplexer output
        input_mode: Signal for input mode
        output_mode: Signal for output mode
        output_polarity: Signal for output polarity
        read_rate: Signal for read rate
        do_read_all: Signal for read all command
    """

    start_all: EpicsSignal = Component(EpicsSignal, "StartAll")
    stop_all: EpicsSignal = Component(EpicsSignal, "StopAll")
    erase_start: EpicsSignal = Component(EpicsSignal, "EraseStart")
    erase_all: EpicsSignal = Component(EpicsSignal, "EraseAll")
    mca1: EpicsMCARecord = Component(EpicsMCARecord, "mca1")
    mca2: EpicsMCARecord = Component(EpicsMCARecord, "mca2")
    mca3: EpicsMCARecord = Component(EpicsMCARecord, "mca3")
    mca4: EpicsMCARecord = Component(EpicsMCARecord, "mca4")
    clock_frequency: EpicsSignalRO = Component(EpicsSignalRO, "clock_frequency")
    current_channel: EpicsSignalRO = Component(EpicsSignalRO, "CurrentChannel")
    channel_max: EpicsSignalRO = Component(EpicsSignalRO, "MaxChannels")
    channels_used: EpicsSignal = Component(EpicsSignal, "NuseAll")
    elapsed_real_time: EpicsSignalRO = Component(EpicsSignalRO, "ElapsedReal")
    preset_real_time: EpicsSignal = Component(EpicsSignal, "PresetReal")
    dwell_time: EpicsSignal = Component(EpicsSignal, "Dwell")
    prescale: EpicsSignal = Component(EpicsSignal, "Prescale")
    acquiring: EpicsSignalRO = Component(EpicsSignalRO, "Acquiring", string=True)
    acquire_mode: EpicsSignalRO = Component(EpicsSignalRO, "AcquireMode", string=True)
    model: EpicsSignalRO = Component(EpicsSignalRO, "Model", string=True)
    firmware: EpicsSignalRO = Component(EpicsSignalRO, "Firmware")
    channel_advance: EpicsSignal = Component(EpicsSignal, "ChannelAdvance")
    count_on_start: EpicsSignal = Component(EpicsSignal, "CountOnStart")
    software_channel_advance: EpicsSignal = Component(EpicsSignal, "SoftwareChannelAdvance")
    channel1_source: EpicsSignal = Component(EpicsSignal, "Channel1Source")
    user_led: EpicsSignal = Component(EpicsSignal, "UserLED")
    mux_output: EpicsSignal = Component(EpicsSignal, "MUXOutput")
    input_mode: EpicsSignal = Component(EpicsSignal, "InputMode")
    output_mode: EpicsSignal = Component(EpicsSignal, "OutputMode")
    output_polarity: EpicsSignal = Component(EpicsSignal, "OutputPolarity")
    read_rate: EpicsSignal = Component(EpicsSignal, "ReadAll.SCAN")
    do_read_all: EpicsSignal = Component(EpicsSignal, "DoReadAll")

    def __init__(
        self,
        prefix: str,
        *,
        name: Optional[str] = None,
        parent: Optional[Device] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Struck3820 device.

        Args:
            prefix: The EPICS PV prefix for the device
            name: The name of the device
            parent: The parent device, if any
            **kwargs: Additional keyword arguments to pass to the parent class
        """
        super().__init__(prefix=prefix, name=name, parent=parent, **kwargs)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
