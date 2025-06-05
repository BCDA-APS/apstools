.. _callbacks:

=========
Callbacks
=========

Receive *documents* from the bluesky RunEngine.
:ref:`filewriters` are a specialized type of callback.

.. rubric:: Callbacks
.. autosummary::
    :nosignatures:

    ~apstools.callbacks.doc_collector.DocumentCollectorCallback
    ~apstools.callbacks.doc_collector.document_contents_callback
    ~apstools.callbacks.scan_signal_statistics.SignalStatsCallback

.. rubric:: File Writing Callbacks
.. autosummary::
    :nosignatures:

   ~apstools.callbacks.nexus_writer.NXWriterAPS
   ~apstools.callbacks.nexus_writer.NXWriter
   ~apstools.callbacks.spec_file_writer.SpecWriterCallback
   ~apstools.callbacks.spec_file_writer.SpecWriterCallback2

.. automodule:: apstools.callbacks.doc_collector
    :members:

.. automodule:: apstools.callbacks.scan_signal_statistics
    :members:
    :private-members:
