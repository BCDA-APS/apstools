"""Ophyd definitions for digital delay and pulse generators."""

from ophyd import Device, Component as Cpt, EpicsSignal, EpicsSignalRO, Kind


__all__ = ["DG645Delay"]


class EpicsSignalWithIO(EpicsSignal):
    # An EPICS signal that simply uses the DG-645 convention of
    # 'AO' being the setpoint and 'AI' being the read-back

    def __init__(self, prefix, **kwargs):
        super().__init__(f"{prefix}I", write_pv=f"{prefix}O", **kwargs)


class DG645Channel(Device):
    reference = Cpt(EpicsSignalWithIO, "ReferenceM", kind=Kind.config)
    delay = Cpt(EpicsSignalWithIO, "DelayA", kind=Kind.normal)


class DG645Output(Device):
    output_mode_ttl = Cpt(EpicsSignal, "OutputModeTtlSS.PROC", kind=Kind.omitted)
    output_mode_nim = Cpt(EpicsSignal, "OutputModeNimSS.PROC", kind=Kind.omitted)
    polarity = Cpt(EpicsSignalWithIO, "OutputPolarityB", kind=Kind.config)
    amplitude = Cpt(EpicsSignalWithIO, "OutputAmpA", kind=Kind.config)
    offset = Cpt(EpicsSignalWithIO, "OutputOffsetA", kind=Kind.config)


class DG645DelayOutput(DG645Output):
    trigger_prescale = Cpt(EpicsSignalWithIO, "TriggerPrescaleL", kind=Kind.config)
    trigger_phase = Cpt(EpicsSignalWithIO, "TriggerPhaseL", kind=Kind.config)


class DG645Delay(Device):
    """An SRS DG-645 digial delay/pulse generator.

    This device has four delayed outputs: AB, CD, EF, GH.

    Configuration of the output parameters (e.g. amplitude, polarity)
    is done using components ``output_AB``, etc. The individual delays
    for the start and end of the output pulse are configured using
    individual channels ``channel_A`` etc.

    There is also a ``T0`` output which is the reference pulses used
    for the remaining delayed outputs.

    """

    # Individual delay channels
    channel_A = Cpt(DG645Channel, "A")
    channel_B = Cpt(DG645Channel, "B")
    channel_C = Cpt(DG645Channel, "C")
    channel_D = Cpt(DG645Channel, "D")
    channel_E = Cpt(DG645Channel, "E")
    channel_F = Cpt(DG645Channel, "F")
    channel_G = Cpt(DG645Channel, "G")
    channel_H = Cpt(DG645Channel, "H")

    # 2-channel delay outputs
    output_T0 = Cpt(DG645Output, "T0", kind=Kind.config)
    output_AB = Cpt(DG645DelayOutput, "AB", kind=Kind.config)
    output_CD = Cpt(DG645DelayOutput, "CD", kind=Kind.config)
    output_EF = Cpt(DG645DelayOutput, "EF", kind=Kind.config)
    output_GH = Cpt(DG645DelayOutput, "GH", kind=Kind.config)

    # General settings
    label = Cpt(EpicsSignal, "Label", kind=Kind.config)
    status = Cpt(EpicsSignalRO, "StatusSI", kind=Kind.omitted)
    clear_error = Cpt(EpicsSignal, "StatusClearBO", kind=Kind.omitted)
    device_id = Cpt(EpicsSignalRO, "IdentSI", kind=Kind.config)
    goto_remote = Cpt(EpicsSignal, "GotoRemoteBO", kind=Kind.omitted)
    goto_local = Cpt(EpicsSignal, "GotoLocalBO", kind=Kind.omitted)
    reset = Cpt(EpicsSignal, "ResetBO", kind=Kind.omitted)
    status_checking = Cpt(EpicsSignal, "StatusCheckingBO", kind=Kind.omitted)
    reset_serial = Cpt(EpicsSignal, "IfaceSerialResetBO", kind=Kind.omitted)
    serial_state = Cpt(EpicsSignalWithIO, "IfaceSerialStateB", kind=Kind.config)
    serial_baud = Cpt(EpicsSignalWithIO, "IfaceSerialBaudM", kind=Kind.config)
    reset_gpib = Cpt(EpicsSignal, "IfaceGpibResetBO", kind=Kind.omitted)
    gpib_state = Cpt(EpicsSignalWithIO, "IfaceGpibStateB", kind=Kind.config)
    gpib_address = Cpt(EpicsSignalWithIO, "IfaceGpibAddrL", kind=Kind.config)
    reset_lan = Cpt(EpicsSignal, "IfaceLanResetBO", kind=Kind.omitted)
    mac_address = Cpt(EpicsSignalRO, "IfaceMacAddrSI", kind=Kind.config)
    lan_state = Cpt(EpicsSignalWithIO, "IfaceLanStateB", kind=Kind.config)
    dhcp_state = Cpt(EpicsSignalWithIO, "IfaceDhcpStateB", kind=Kind.config)
    autoip_state = Cpt(EpicsSignalWithIO, "IfaceAutoIpStateB", kind=Kind.config)
    static_ip_state = Cpt(EpicsSignalWithIO, "IfaceStaticIpStateB", kind=Kind.config)
    bare_socket_state = Cpt(EpicsSignalWithIO, "IfaceBareSocketStateB", kind=Kind.config)
    telnet_state = Cpt(EpicsSignalWithIO, "IfaceTelnetStateB", kind=Kind.config)
    vxi11_state = Cpt(EpicsSignalWithIO, "IfaceVxiStateB", kind=Kind.config)
    ip_address = Cpt(EpicsSignalWithIO, "IfaceIpAddrS", kind=Kind.config)
    network_mask = Cpt(EpicsSignalWithIO, "IfaceNetMaskS", kind=Kind.config)
    gateway = Cpt(EpicsSignalWithIO, "IfaceGatewayS", kind=Kind.config)

    # Trigger control
    trigger_source = Cpt(EpicsSignalWithIO, "TriggerSourceM", kind=Kind.config)
    trigger_inhibit = Cpt(EpicsSignalWithIO, "TriggerInhibitM", kind=Kind.config)
    trigger_level = Cpt(EpicsSignalWithIO, "TriggerLevelA", kind=Kind.config)
    trigger_rate = Cpt(EpicsSignalWithIO, "TriggerRateA", kind=Kind.config)
    trigger_advanced_mode = Cpt(EpicsSignalWithIO, "TriggerAdvancedModeB", kind=Kind.config)
    trigger_holdoff = Cpt(EpicsSignalWithIO, "TriggerHoldoffA", kind=Kind.config)
    trigger_prescale = Cpt(EpicsSignalWithIO, "TriggerPrescaleL", kind=Kind.config)

    # Burst settings
    burst_mode = Cpt(EpicsSignalWithIO, "BurstModeB", kind=Kind.config)
    burst_count = Cpt(EpicsSignalWithIO, "BurstCountL", kind=Kind.config)
    burst_mode = Cpt(EpicsSignalWithIO, "BurstConfigB", kind=Kind.config)
    burst_delay = Cpt(EpicsSignalWithIO, "BurstDelayA", kind=Kind.config)
    burst_period = Cpt(EpicsSignalWithIO, "BurstPeriodA", kind=Kind.config)
