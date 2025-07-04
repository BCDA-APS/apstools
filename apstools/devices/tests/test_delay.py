"""
test the SRS DG-645 digital delay device support

Hardware is not available so test with best efforts
"""

from ...tests import IOC_GP
from .. import delay

PV_PREFIX = f"phony:{IOC_GP}DG645:"


def test_dg645_device():
    dg645 = delay.DG645Delay(PV_PREFIX, name="delay")
    assert not dg645.connected

    read_names = [
        "channel_A",
        "channel_A.delay",
        "channel_B",
        "channel_B.delay",
        "channel_C",
        "channel_C.delay",
        "channel_D",
        "channel_D.delay",
        "channel_E",
        "channel_E.delay",
        "channel_F",
        "channel_F.delay",
        "channel_G",
        "channel_G.delay",
        "channel_H",
        "channel_H.delay",
    ]
    assert sorted(dg645.read_attrs) == sorted(read_names)

    cfg_names = [
        "autoip_state",
        "bare_socket_state",
        "burst_count",
        "burst_delay",
        "burst_mode",
        "burst_period",
        "burst_T0",
        "channel_A",
        "channel_A.reference",
        "channel_B",
        "channel_B.reference",
        "channel_C",
        "channel_C.reference",
        "channel_D",
        "channel_D.reference",
        "channel_E",
        "channel_E.reference",
        "channel_F",
        "channel_F.reference",
        "channel_G",
        "channel_G.reference",
        "channel_H",
        "channel_H.reference",
        "device_id",
        "dhcp_state",
        "gateway",
        "gpib_address",
        "gpib_state",
        "ip_address",
        "label",
        "lan_state",
        "mac_address",
        "network_mask",
        "output_AB",
        "output_AB.amplitude",
        "output_AB.offset",
        "output_AB.polarity",
        "output_AB.trigger_phase",
        "output_AB.trigger_prescale",
        "output_CD",
        "output_CD.amplitude",
        "output_CD.offset",
        "output_CD.polarity",
        "output_CD.trigger_phase",
        "output_CD.trigger_prescale",
        "output_EF",
        "output_EF.amplitude",
        "output_EF.offset",
        "output_EF.polarity",
        "output_EF.trigger_phase",
        "output_EF.trigger_prescale",
        "output_GH",
        "output_GH.amplitude",
        "output_GH.offset",
        "output_GH.polarity",
        "output_GH.trigger_phase",
        "output_GH.trigger_prescale",
        "output_T0",
        "output_T0.amplitude",
        "output_T0.offset",
        "output_T0.polarity",
        "serial_baud",
        "serial_state",
        "static_ip_state",
        "telnet_state",
        "trigger_advanced_mode",
        "trigger_holdoff",
        "trigger_inhibit",
        "trigger_level",
        "trigger_prescale",
        "trigger_rate",
        "trigger_source",
        "vxi11_state",
    ]
    assert sorted(dg645.configuration_attrs) == sorted(cfg_names)

    # List all the components
    cpt_names = [
        "autoip_state",
        "bare_socket_state",
        "burst_count",
        "burst_delay",
        "burst_mode",
        "burst_period",
        "burst_T0",
        "channel_A",
        "channel_B",
        "channel_C",
        "channel_D",
        "channel_E",
        "channel_F",
        "channel_G",
        "channel_H",
        "clear_error",
        "device_id",
        "dhcp_state",
        "gateway",
        "goto_local",
        "goto_remote",
        "gpib_address",
        "gpib_state",
        "ip_address",
        "label",
        "lan_state",
        "mac_address",
        "network_mask",
        "output_AB",
        "output_CD",
        "output_EF",
        "output_GH",
        "output_T0",
        "reset",
        "reset_gpib",
        "reset_lan",
        "reset_serial",
        "serial_baud",
        "serial_state",
        "static_ip_state",
        "status",
        "status_checking",
        "telnet_state",
        "trigger_advanced_mode",
        "trigger_arm",
        "trigger_holdoff",
        "trigger_inhibit",
        "trigger_level",
        "trigger_prescale",
        "trigger_rate",
        "trigger_source",
        "vxi11_state",
    ]
    assert sorted(dg645.component_names) == sorted(cpt_names)
