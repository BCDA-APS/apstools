"""
Documentation of batch runs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~addDeviceDataAsStream
   ~documentation_run
"""

from ..utils import ipython_shell_namespace
from bluesky import plan_stubs as bps
from ophyd import Signal


def addDeviceDataAsStream(devices, label):
    """
    add an ophyd Device as an additional document stream

    .. index:: Bluesky Plan; addDeviceDataAsStream

    Use this within a custom plan, such as this example::

        from apstools.plans import addDeviceStream
        ...
        yield from bps.open_run()
        # ...
        yield from addDeviceDataAsStream(prescanDeviceList, "metadata_prescan")
        # ...
        yield from custom_scan_procedure()
        # ...
        yield from addDeviceDataAsStream(postscanDeviceList, "metadata_postscan")
        # ...
        yield from bps.close_run()

    """
    yield from bps.create(name=label)
    if not isinstance(devices, list):  # just in case...
        devices = [devices]
    for d in devices:
        yield from bps.read(d)
    yield from bps.save()


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

    _md = dict(purpose="save text as bluesky run", plan_name="documentation_run",)
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
