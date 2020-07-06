
File Writers
------------

The file writer callbacks are:

* :class:`~apstools.filewriters.FileWriterCallbackBase`
* :class:`~apstools.filewriters.NXWriterAPS`
* :class:`~apstools.filewriters.NXWriter`
* :class:`~apstools.filewriters.SpecWriterCallback`


Overview
++++++++

Each filewriter can be used as a callback to the Bluesky RunEngine
for live data acquisition or later as a handler for a document set
from the databroker.  Methods are provided to handle each document
type.  The callback method, ``receiver(document_type, document)``, receives
the set of documents, one-by-one, and sends them to the appropriate
handler.  Once the ``stop`` document is received, the ``writer()`` method
is called to write the output file.

Examples
^^^^^^^^

Write SPEC file automatically from data acquisition::

    specwriter = apstools.filewriters.SpecWriterCallback()
    RE.subscribe(specwriter.receiver)

Write NeXus file automatically from data acquisition::

    nxwriter = apstools.filewriters.NXWriter()
    RE.subscribe(nxwriter.receiver)

Write APS-specific NeXus file automatically from data acquisition::

    nxwriteraps = apstools.filewriters.NXWriterAPS()
    RE.subscribe(nxwriteraps.receiver)

Programmer's Note
^^^^^^^^^^^^^^^^^

Subclassing from ``object`` (or no superclass)
avoids the need to import ``bluesky.callbacks.core.CallbackBase``.  
One less import when only accessing the Databroker.
The *only* advantage to subclassing from ``CallbackBase``
seems to be a simpler setup call to ``RE.subscribe()``.

============  ===============================
superclass    subscription code
============  ===============================
object        ``RE.subscribe(specwriter.receiver)``
CallbackBase  ``RE.subscribe(specwriter)``
============  ===============================

HDF5/NeXus File Writers
++++++++++++++++++++++++++

FileWriterCallbackBase
^^^^^^^^^^^^^^^^^^^^^^

Base class for filewriter callbacks.

Applications should subclass and rewrite the ``writer()`` method.

The local buffers are cleared when a start document is received.
Content is collected here from each document until the stop document.
The content is written once the stop document is received.

Output File Name and Path
~~~~~~~~~~~~~~~~~~~~~~~~~

The output file will be written to the file named in
``self.file_name``.  (Include the output directory if
different from the current working directory.)

When ``self.file_name`` is ``None`` (the default), the
:meth:`~apstools.filewriters.FileWriterCallbackBase.make_file_name()`
method will construct
the file name using a combination of the date and time
(from the ``start`` document), the ``start`` document
``uid``, and the ``scan_id``.
The default file extension (given in ``NEXUS_FILE_EXTENSION``)
is used in
:meth:`~apstools.filewriters.FileWriterCallbackBase.make_file_name()`.
The directory will be
``self.file_path`` (or the current working directory
if ``self.file_path`` is ``None`` which is the default).

Either specify ``self.file_name`` or override 
:meth:`~apstools.filewriters.FileWriterCallbackBase.make_file_name()`
in a subclass to change the procedure for default output file names.

Metadata
~~~~~~~~

Almost all metadata keys (additional attributes added to the run's
``start`` document) are completely optional.  Certain keys are
specified by the RunEngine, some keys are specified by the plan
(or plan support methods), and other keys are supplied by the
user or the instrument team.

These are the keys used by this callback to help guide how
information is stored in a NeXus HDF5 file structure.

=========== ============= ===================================================
key         creator       how is it used
=========== ============= ===================================================
detectors   inconsistent  name(s) of the signals used as detectors
motors      inconsistent  synonym for ``positioners``
plan_args   inconsistent  parameters (arguments) given
plan_name   inconsistent  name of the plan used to collect data
positioners inconsistent  name(s) of the signals used as positioners
scan_id     RunEngine     incrementing number of the run, user can reset
uid         RunEngine     unique identifier of the run
versions    instrument    documents the software versions used to collect data
=========== ============= ===================================================

For more information about Bluesky *events* and document types, see
https://blueskyproject.io/event-model/data-model.html.

NXWriter
^^^^^^^^

General class for writing HDF5/NeXus file (using only NeXus base classes).

One scan is written to one HDF5/NeXus file.

Output File Name and Path
~~~~~~~~~~~~~~~~~~~~~~~~~

The output file will be written to the file named in
``self.file_name``.  (Include the output directory if
different from the current working directory.)

When ``self.file_name`` is ``None`` (the default), the
:meth:`~apstools.filewriters.FileWriterCallbackBase.make_file_name()`
method will construct
the file name using a combination of the date and time
(from the `start` document), the ``start`` document
``uid``, and the ``scan_id``.
The default file extension (given in ``NEXUS_FILE_EXTENSION``) is
used in
:meth:`~apstools.filewriters.FileWriterCallbackBase.make_file_name()`.
The directory will be
``self.file_path`` (or the current working directory
if ``self.file_path`` is ``None`` which is the default).

Either specify ``self.file_name`` of override 
:meth:`~apstools.filewriters.FileWriterCallbackBase.make_file_name()`
in a subclass
to change the procedure for default output file names.

Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~

Almost all metadata keys (additional attributes added to the run's
``start`` document) are completely optional.  Certain keys are
specified by the RunEngine, some keys are specified by the plan
(or plan support methods), and other keys are supplied by the
user or the instrument team.

These are the keys used by this callback to help guide how
information is stored in a NeXus HDF5 file structure.

=========== ============= ===================================================
key         creator       how is it used
=========== ============= ===================================================
detectors   inconsistent  name(s) of the signals used as plottable values
motors      inconsistent  synonym for ``positioners``
plan_args   inconsistent  parameters (arguments) given
plan_name   inconsistent  name of the plan used to collect data
positioners inconsistent  name(s) of the positioners used for plotting
scan_id     RunEngine     incrementing number of the run, user can reset
subtitle    user          -tba-
title       user          /entry/title
uid         RunEngine     unique identifier of the run
versions    instrument    documents the software versions used to collect data
=========== ============= ===================================================

Notes:

1. ``detectors[0]`` will be used as the ``/entry/data@signal`` attribute
2. the *complete* list in ``positioners`` will be used as the ``/entry/data@axes`` attribute

NXWriterAPS
^^^^^^^^^^^

Customize :class:`~apstools.filewriters.NXWriter` with APS-specific content.

* Adds ``/entry/instrument/undulator`` group if metadata exists.
* Adds APS information to ``/entry/instrument/source`` group.

APS instruments should subclass :class:`~apstools.filewriters.NXWriterAPS`
to make customizations for specific plans or other considerations.

HDF5/NeXus File Structures
++++++++++++++++++++++++++

Bluesky stores a wealth of information about a measurement in a *run*.
Raw data from the Bluesky *run* is stored in the HDF5/NeXus structure
under the ``/entry/instrument/bluesky`` group as shown in this example:

.. literalinclude:: ../../../examples/demo_nxwriter_bluesky.txt
    :linenos:
    :language: text

The NeXus structure is built using links to the raw data in
``/entry/instrument/bluesky``.

Metadata
^^^^^^^^

Metadata from the ``start`` document is stored in the ``metadata`` subgroup
as shown in this example:

.. literalinclude:: ../../../examples/demo_nxwriter_metadata.txt
    :linenos:
    :language: text

Note that complex structures (lists and dictionaries)
are written as YAML.  YAML is easily converted back into the
python structure using ``yaml.load(yaml_text)`` where ``yaml_text``
is the YAML text from the HDF5 file.

Streams
^^^^^^^

Data from each ophyd signal in a *document stream* is stored as datasets
within a ``NXdata`` [#]_ subgroup of that stream.  Bluesky collects value(s) and timestamp(s)
which are stored in the datasets ``value`` and ``EPOCH``, respectively.
Since ``EPOCH`` is the absolute number of seconds from some time in the deep past,
an additional ``time`` dataset repeats this data as time *relative* to the first time.
(This makes it much easier for some visualization programs to display
value v. time plots.)  Additional information, as available (such as units),
is added as NeXus attributes.  The ``@target`` attribute is automatically added
to simplify linking any item into the NeXus tree structure.

.. [#] ``NXdata`` is used since some visualization tools recognize it to make a plot.

For example, the main data in a run is usually stored in the ``primary`` stream.
Here, we show the tree structure for one signal (``I0_USAXS``) from the primary stream:

.. literalinclude:: ../../../examples/demo_nxwriter_stream_primary.txt
    :linenos:
    :language: text

Baseline
^^^^^^^^

In Bluesky, *baseline* streams record the value (and timestamp) of a
signal at the start and end of the run.  Similar to the handling for
streams (above), a subgroup is created for each baseline stream.
The datasets include ``value``, ``EPOCH``, ``time`` (as above) and 
``value_start`` and ``value_end``.  Here's an example:

.. literalinclude:: ../../../examples/demo_nxwriter_baseline.txt
    :linenos:
    :language: text

Full Structure
^^^^^^^^^^^^^^

The full structure of the example HDF5/NeXus file (omitting the attributes
and array data for brevity) is shown next.  You can see that most of the
NeXus structure is completed by making links to data from either
``/entry/instrument/bluesky/metadata`` or ``/entry/instrument/bluesky/streams``:

.. literalinclude:: ../../../examples/demo_nxwriter_tree.txt
    :linenos:
    :language: text

APS-specific HDF5/NeXus File Structures
+++++++++++++++++++++++++++++++++++++++

Examples of additional structure in NeXus file added by :class:`~apstools.filewriters.NXWriterAPS()`:

.. literalinclude:: ../../../examples/demo_nxapswriter.txt
    :linenos:
    :language: text


SPEC File Structure
+++++++++++++++++++

EXAMPLE : use as Bluesky callback::

    from apstools.filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback()
    RE.subscribe(specwriter.receiver)

EXAMPLE : use as writer from Databroker::

    from apstools.filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback()
    for key, doc in db.get_documents(db["a123456"]):
        specwriter.receiver(key, doc)
    print("Look at SPEC data file: "+specwriter.spec_filename)

EXAMPLE : use as writer from Databroker with customizations::

    from apstools.filewriters import SpecWriterCallback
    
    # write into file: /tmp/cerium.spec
    specwriter = SpecWriterCallback(filename="/tmp/cerium.spec")
    for key, doc in db.get_documents(db["abcd123"]):
        specwriter.receiver(key, doc)
    
    # write into file: /tmp/barium.dat
    specwriter.newfile("/tmp/barium.dat")
    for key, doc in db.get_documents(db["b46b63d4"]):
        specwriter.receiver(key, doc)

Example output from ``SpecWriterCallback()``:

.. literalinclude:: ../../../examples/demo_specdata.dat
    :linenos:
    :language: text

Source Code Documentation
+++++++++++++++++++++++++

.. automodule:: apstools.filewriters
    :members: 
