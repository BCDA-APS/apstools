.. _callbacks:

=========
Callbacks
=========

Receive *documents* from the bluesky RunEngine.
:ref:`filewriters` are a specialized type of callback.

For complete API details see the :doc:`Full API Reference <autoapi/apstools/index>`.

.. rubric:: Callbacks

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :func:`~apstools.callbacks.doc_collector.document_contents_callback`
     - print document contents for diagnosing a document stream
   * - :class:`~apstools.callbacks.doc_collector.DocumentCollectorCallback`
     - collect *all* documents from the most-recent plan
   * - :class:`~apstools.callbacks.scan_signal_statistics.SignalStatsCallback`
     - collect peak and other statistics during a scan


.. rubric:: File Writing Callbacks

.. list-table::
   :header-rows: 0
   :widths: 40 60

   * - :class:`~apstools.callbacks.nexus_writer.NXWriter`
     - write HDF5/NeXus file using NeXus base classes
   * - :class:`~apstools.callbacks.nexus_writer.NXWriterAPS`
     - customize :class:`~apstools.callbacks.nexus_writer.NXWriter` with APS-specific content
   * - :class:`~apstools.callbacks.spec_file_writer.SpecWriterCallback`
     - (*deprecated*) write SPEC data file line-by-line
   * - :class:`~apstools.callbacks.spec_file_writer.SpecWriterCallback2`
     - write SPEC data file as data is collected, line-by-line

