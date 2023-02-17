import bluesky
import databroker
import ophyd
import ophyd.sim
import pytest
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.simulators import summarize_plan

from ..doc_run import addDeviceDataAsStream
from ..doc_run import documentation_run
from ..doc_run import write_stream

TEXT = "two words"

bec = BestEffortCallback()


@pytest.mark.parametrize(
    "text, stream, bec, md",
    [
        [TEXT, None, None, None],
        [TEXT, "documentation", None, None],
        [TEXT, "documentation", bec, None],
    ],
)
def test_documentation_run(text, stream, bec, md):
    cat = databroker.temp().v2
    RE = bluesky.RunEngine()
    RE.subscribe(cat.v1.insert)
    if bec is not None:
        RE.subscribe(bec)

    uids = RE(documentation_run(text, stream, bec, md))
    assert len(uids) == 1

    stream_names = cat.v1[uids[-1]].stream_names
    assert len(stream_names) == 1
    if stream is not None:
        assert stream_names[0] == stream

    ds = getattr(cat.v2[uids[-1]], stream_names[0]).read()
    assert ds is not None
    assert "text" in ds
    assert ds["text"] == text


@pytest.mark.parametrize(
    "objects, name, expected",
    [
        ([ophyd.sim.motor1], "test-device", "  Read ['motor1']\n"),
        (
            [[ophyd.sim.motor2, ophyd.sim.motor3]],
            "test-device-list",
            "  Read ['motor2', 'motor3']\n",
        ),
    ],
)
def test_addDeviceDataAsStream(objects, name, expected, capsys):
    with pytest.warns(UserWarning):
        summarize_plan(addDeviceDataAsStream(*objects, name))

    captured = capsys.readouterr()
    assert captured.out == expected


@pytest.mark.parametrize(
    "objects, name, expected",
    [
        ([ophyd.sim.motor1], "test-device", "  Read ['motor1']\n"),
        (
            [[ophyd.sim.motor2, ophyd.sim.motor3]],
            "test-device-list",
            "  Read ['motor2', 'motor3']\n",
        ),
    ],
)
def test_write_stream(objects, name, expected, capsys):
    summarize_plan(write_stream(*objects, name))

    captured = capsys.readouterr()
    assert captured.out == expected
