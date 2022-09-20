"""
snapshot Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~snapshot
"""

import datetime
import sys

from bluesky import plan_stubs as bps
from ophyd import Signal, EpicsSignal


def snapshot(obj_list, stream="primary", md=None):
    """
    bluesky plan: record current values of list of ophyd signals

    .. index:: Bluesky Plan; snapshot

    PARAMETERS

    obj_list
        *list* :
        list of ophyd Signal or EpicsSignal objects
    stream
        *str* :
        document stream, default: "primary"
    md
        *dict* :
        metadata
    """
    from .__init__ import __version__
    from bluesky import __version__ as bluesky_version
    from databroker import __version__ as databroker_version
    from epics import __version__ as pyepics_version
    from ophyd import __version__ as ophyd_version
    import socket
    import getpass

    objects = []
    for obj in obj_list:
        # TODO: consider supporting Device objects
        if isinstance(obj, (Signal, EpicsSignal)) and obj.connected:
            objects.append(obj)
        else:
            if hasattr(obj, "pvname"):
                nm = obj.pvname
            else:
                nm = obj.name
            print(f"ignoring object: {nm}")

        if len(objects) == 0:
            raise ValueError("No signals to log.")

    hostname = socket.gethostname() or "localhost"
    username = getpass.getuser() or "bluesky_user"

    # we want this metadata to appear
    _md = dict(
        plan_name="snapshot",
        plan_description=(
            "archive snapshot of ophyd Signals (usually EPICS PVs)",
        ),
        iso8601=str(datetime.datetime.now()),  # human-readable
        hints={},
        software_versions=dict(
            python=sys.version,
            PyEpics=pyepics_version,
            bluesky=bluesky_version,
            ophyd=ophyd_version,
            databroker=databroker_version,
            apstools=__version__,
        ),
        hostname=hostname,
        username=username,
        login_id=f"{username}@{hostname}",
    )
    # caller may have given us additional metadata
    _md.update(md or {})

    def _snap(md=None):
        yield from bps.open_run(md)
        yield from bps.create(name=stream)
        for obj in objects:
            # passive observation: DO NOT TRIGGER, only read
            yield from bps.read(obj)
        yield from bps.save()
        yield from bps.close_run()

    return (yield from _snap(md=_md))

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
