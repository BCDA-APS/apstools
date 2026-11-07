.. _devices_async:

============================
Async Devices (experimental)
============================

Awaitable devices based on the `ophyd-async <https://github.com/bluesky/ophyd-async>`__
library.  These devices are separate from the classic :ref:`Ophyd Devices <devices>`
and require installing *apstools* with the ``[async]`` extra.

For complete API details see the :doc:`Full API Reference <autoapi/apstools/index>`.

Devices
-------

* :class:`~apstools.devices_async.aps_machine.ApsMachine` — APS storage-ring machine status and operating parameters.

See the :doc:`generated API reference <autoapi/apstools/devices_async/index>` for
complete details.

The ``devices_async`` package is experimental.  The ``(experimental)`` label
will be removed when *ophyd-async* becomes a required dependency.
