.. _filewriters:

============
File Writers
============

The file writer callbacks are:

.. autosummary::

   ~apstools.callbacks.callback_base.FileWriterCallbackBase
   ~apstools.callbacks.nexus_writer.NXWriterAPS
   ~apstools.callbacks.nexus_writer.NXWriter
   ~apstools.callbacks.spec_file_writer.SpecWriterCallback


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

    specwriter = apstools.callbacks.SpecWriterCallback()
    RE.subscribe(specwriter.receiver)

Write NeXus file automatically from data acquisition::

    nxwriter = apstools.callbacks.NXWriter()
    RE.subscribe(nxwriter.receiver)

Write APS-specific NeXus file automatically from data acquisition::

    nxwriteraps = apstools.callbacks.NXWriterAPS()
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
:meth:`~apstools.callbacks.callback_base.FileWriterCallbackBase.make_file_name()`
method will construct
the file name using a combination of the date and time
(from the ``start`` document), the ``start`` document
``uid``, and the ``scan_id``.
The default file extension (given in ``NEXUS_FILE_EXTENSION``)
is used in
:meth:`~apstools.callbacks.callback_base.FileWriterCallbackBase.make_file_name()`.
The directory will be
``self.file_path`` (or the current working directory
if ``self.file_path`` is ``None`` which is the default).

Either specify ``self.file_name`` or override
:meth:`~apstools.callbacks.callback_base.FileWriterCallbackBase.make_file_name()`
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
:meth:`~apstools.callbacks.callback_base.FileWriterCallbackBase.make_file_name()`
method will construct
the file name using a combination of the date and time
(from the `start` document), the ``start`` document
``uid``, and the ``scan_id``.
The default file extension (given in ``NEXUS_FILE_EXTENSION``) is
used in
:meth:`~apstools.callbacks.callback_base.FileWriterCallbackBase.make_file_name()`.
The directory will be
``self.file_path`` (or the current working directory
if ``self.file_path`` is ``None`` which is the default).

Either specify ``self.file_name`` of override
:meth:`~apstools.callbacks.callback_base.FileWriterCallbackBase.make_file_name()`
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

.. index:: templates

.. _filewriters.templates:

Templates
~~~~~~~~~~~~~~~~~~~~~~~~~

Use templates to build NeXus base classes or application definitions with data
already collected by the nxwriter and saved in other places in the NeXus/HDF5
file (such as `/entry/instrument/bluesky`).  Templates are used to:

* make links from existing fields or groups to new locations
* create new groups as directed
* create constants for attributes or fields

A template is a ``[source, target]`` list, where source is a string and target
varies depending on the type of template.  A list of templates is stored as a
JSON string in the run's metadata under a pre-arranged key.

For reasons of expediency, always use absolute HDF5 addresses. Relative
addresses are not supported now.

A *link* template makes a pointer from an existing field or group to another
location. In a link template, the source is an existing HDF5 address.  The
target is a NeXus class path.  If the path contains a group which is not yet
defined, the addtional component names the NeXus class to be used. See the
examples below.

A *constant* template defines a new NeXus field.  The source string, which can be
a class path (see above), ends with an ``=``.  The target can be a text, a
number, or an array.  Anything that can be converted into a JSON document and
then written to an HDF5 dataset.

An *attribute* template adds a new attribute to a field or group.  Use the `@`
symbol in the source string as shown in the examples below.  The target is the
value of the attribute.

EXAMPLE:

.. code-block:: python
    :linenos:

    template_examples = [
        # *constant* template
        # define a constant array in a new NXdata group
        ["/entry/example:NXdata/array=", [1, 2, 3]],

        # *attribute* template
        # set the example group "signal" attribute
        #   (new array is the default plottable data)
        ["/entry/example/@signal", "array"],

        # *link* template
        # link the new array into a new NXnote group as field "x"
        ["/entry/example/array", "/entry/example/note:NXnote/x"],
    ]

    md = {
        "title": "NeXus/HDF5 template support example",

        # encode the Python dictionary as a JSON string
        nxwriter.template_key: json.dumps(template_examples),
    }

The templates in this example add this structure to the ``/entry`` group in the
HDF5 file:

.. code-block:: text
    :linenos:

    /entry:NXentry
        @NX_class = "NXentry"
        ...
        example:NXdata
            @NX_class = "NXdata"
            @signal = "array"
            @target = "/entry/example"
            array:NX_INT64[3] = [1, 2, 3]
                @target = "/entry/example/array"
            note:NXnote
                @NX_class = "NXnote"
                @target = "/entry/example/note"
                x --> /entry/example/array

NXWriterAPS
^^^^^^^^^^^

Customize :class:`~apstools.callbacks.nexus_writer.NXWriter` with APS-specific content.

* Adds ``/entry/instrument/undulator`` group if metadata exists.
* Adds APS information to ``/entry/instrument/source`` group.

APS instruments should subclass :class:`~apstools.callbacks.nexus_writer.NXWriterAPS`
to make customizations for specific plans or other considerations.

HDF5/NeXus File Structures
++++++++++++++++++++++++++

Bluesky stores a wealth of information about a measurement in a *run*.
Raw data from the Bluesky *run* is stored in the HDF5/NeXus structure
under the ``/entry/instrument/bluesky`` group as shown in this example:

.. literalinclude:: ../resources/demo_nxwriter_bluesky.txt
    :linenos:
    :language: text

The NeXus structure is built using links to the raw data in
``/entry/instrument/bluesky``.

Metadata
^^^^^^^^

Metadata from the ``start`` document is stored in the ``metadata`` subgroup
as shown in this example:

.. literalinclude:: ../resources/demo_nxwriter_metadata.txt
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

.. literalinclude:: ../resources/demo_nxwriter_stream_primary.txt
    :linenos:
    :language: text

Baseline
^^^^^^^^

In Bluesky, *baseline* streams record the value (and timestamp) of a
signal at the start and end of the run.  Similar to the handling for
streams (above), a subgroup is created for each baseline stream.
The datasets include ``value``, ``EPOCH``, ``time`` (as above) and
``value_start`` and ``value_end``.  Here's an example:

.. literalinclude:: ../resources/demo_nxwriter_baseline.txt
    :linenos:
    :language: text

Full Structure
^^^^^^^^^^^^^^

The full structure of the example HDF5/NeXus file (omitting the attributes
and array data for brevity) is shown next.  You can see that most of the
NeXus structure is completed by making links to data from either
``/entry/instrument/bluesky/metadata`` or ``/entry/instrument/bluesky/streams``:

.. literalinclude:: ../resources/demo_nxwriter_tree.txt
    :linenos:
    :language: text

APS-specific HDF5/NeXus File Structures
+++++++++++++++++++++++++++++++++++++++

Examples of additional structure in NeXus file added by
:class:`~apstools.callbacks.nexus_writer.NXWriterAPS()`:

.. literalinclude:: ../resources/demo_nxapswriter.txt
    :linenos:
    :language: text


SPEC File Structure
+++++++++++++++++++

EXAMPLE : use as Bluesky callback::

    from apstools import SpecWriterCallback
    specwriter = SpecWriterCallback()
    RE.subscribe(specwriter.receiver)

EXAMPLE : use as writer from Databroker::

    from apstools import SpecWriterCallback
    specwriter = SpecWriterCallback()
    for key, doc in db.get_documents(db["a123456"]):
        specwriter.receiver(key, doc)
    print("Look at SPEC data file: "+specwriter.spec_filename)

EXAMPLE : use as writer from Databroker with customizations::

    from apstools import SpecWriterCallback

    # write into file: /tmp/cerium.spec
    specwriter = SpecWriterCallback(filename="/tmp/cerium.spec")
    for key, doc in db.get_documents(db["abcd123"]):
        specwriter.receiver(key, doc)

    # write into file: /tmp/barium.dat
    specwriter.newfile("/tmp/barium.dat")
    for key, doc in db.get_documents(db["b46b63d4"]):
        specwriter.receiver(key, doc)

Example output from ``SpecWriterCallback()``:

.. literalinclude:: ../resources/demo_specdata.dat
    :linenos:
    :language: text


Source Code
++++++++++++++++

.. automodule:: apstools.callbacks.callback_base
    :members:

.. automodule:: apstools.callbacks.nexus_writer
    :members:

.. automodule:: apstools.callbacks.spec_file_writer
    :members:
