"""
Save text as a bluesky run.
"""

__all__ = ["documentation_run", ]

from .. plans import addDeviceDataAsStream
from .. utils import ipython_shell_namespace
from bluesky import plan_stubs as bps
from ophyd import Signal


def documentation_run(text, stream=None, bec=None, md=None):
    """
    Save text as a bluesky run.

    PARAMETERS

    text
        *str* :
        Text to be written.
    stream
        *str* :
        document stream, default: "primary"
    bec
        *object* :
        Instance of `bluesky.BestEffortCallback`,
        default: get from IPython shell
    md
        *dict*
        (optional):
        metadata dictionary
    """
    bec = bec or ipython_shell_namespace().get("bec")
    stream = stream or "primary"

    text_signal = Signal(value=text, name="text")

    _md = dict(
        purpose="save text as bluesky run",
        plan_name="documentation_run",
    )
    _md.update(md or {})

    if bec is not None:
        bec.disable_plots()
        bec.disable_table()

    uid = yield from bps.open_run(md=_md)
    yield from addDeviceDataAsStream(text_signal, stream)
    yield from bps.close_run()

    if bec is not None:
        bec.enable_table()
        bec.enable_plots()

    return uid
