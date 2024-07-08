"""
Documentation of batch runs
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~addDeviceDataAsStream
   ~documentation_run
   ~write_stream
"""

import logging
import warnings

from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
from ophyd import Signal

from ..utils import ipython_shell_namespace

logger = logging.getLogger(__name__)


def addDeviceDataAsStream(devices, label):
    """Renamed to write_stream().  Will remove with relase 1.7+."""
    # fmt: off
    warnings.warn(
        UserWarning(
            "Deprecation: addDeviceDataAsStream() renamed to write_stream()."
        )
    )
    # fmt: on
    yield from write_stream(devices, label)


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

    @bpp.run_decorator(md=_md)
    def inner():
        yield from write_stream(text_signal, stream)

    if bec is not None:
        bec.disable_plots()
        bec.disable_table()

    uid = yield from inner()

    if bec is not None:
        bec.enable_table()
        bec.enable_plots()

    return uid


def write_stream(devices, label):
    """
    add an ophyd Device as an additional document stream

    .. index:: Bluesky Plan; write_stream

    Use this within a custom plan, such as this example::

        from apstools.plans import write_stream
        ...
        yield from bps.open_run(md={})
        # ...
        yield from write_stream(prescanDeviceList, "metadata_prescan")
        # ...
        yield from custom_scan_procedure()
        # ...
        yield from write_stream(postscanDeviceList, "metadata_postscan")
        # ...
        yield from bps.close_run()

    """
    if not isinstance(devices, list):  # just in case...
        devices = [devices]
    yield from bps.create(name=label)
    for d in devices:
        try:
            yield from bps.read(d)
        except Exception as exc:
            logger.warning("device=%s, exception=%s", d, exc)
    yield from bps.save()


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
