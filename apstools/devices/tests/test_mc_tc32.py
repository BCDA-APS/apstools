from ..measComp_tc32_support import BI_CHANNEL_LIST
from ..measComp_tc32_support import BO_CHANNEL_LIST
from ..measComp_tc32_support import TC_CHANNEL_LIST
from ..measComp_tc32_support import MeasCompTc32
from ..measComp_tc32_support import Tc32BinaryInput
from ..measComp_tc32_support import Tc32BinaryOutput
from ..measComp_tc32_support import Tc32ThermocoupleChannel

STRUCTURE = dict(
    binary_inputs=[BI_CHANNEL_LIST, Tc32BinaryInput, ["bit"]],
    binary_outputs=[BO_CHANNEL_LIST, Tc32BinaryOutput, ["bit"]],
    thermocouples=[
        TC_CHANNEL_LIST,
        Tc32ThermocoupleChannel,
        "thermocouple_type filter open_detect scale temperature".split(),
    ],
)


def test_structure():
    device = MeasCompTc32("phony:epics:name:", name="device")
    # no need to wait for connect since the PVs do not exist

    for k, v in STRUCTURE.items():
        assert k in device.component_names, f"{k=}"
        obj0 = getattr(device, k)
        for chan in v[0]:
            assert chan in obj0.component_names, f"{k=} {chan=}"
            ch_obj = getattr(obj0, chan)
            assert isinstance(ch_obj, v[1]), f"{k=} {chan=} {v[1]=}"
            for sig in v[2]:
                assert sig in ch_obj.component_names, f"{k=} {chan=} {sig=}"
