.. index:: Example; Pilatus Area Detector

.. _ad_pilatus:

Example: Pilatus EPICS Area Detector
====================================

In this example, we'll show how to create an ophyd object
that operates our Pilatus camera as a detector.  We'll show how to use
the EPICS Area Detector support to save images into HDF5 data files.  In
the course of this example, we'll describe how an ophyd Device, such as
this area detector support, is configured (a.k.a. :ref:`staged
<ad_pilatus.staging>`) for data acquisition and also describe how ophyd
waits for acquisition to complete using a :ref:`status object
<ad_pilatus.status_object>`.

If you just want the final result, we'll present that first.  Or, skip
ahead if you want the full :ref:`ad_pilatus.explanation`.

.. _ad_pilatus.summary:

Pilatus Support Code
--------------------

We built a Python class to describe our Pilatus area detector, then
created an ophyd ``det`` object to talk with our EPICS IOC for the
Pilatus.  Finally, we configured the ``det`` object to save HDF files
when we count with the detector in Bluesky.  When Bluesky is not
operating the detector, the controls will revert back to their settings
before Bluesky started.

Here is the complete support code:

.. code-block:: python
    :caption: Pilatus Area Detector support, writing HDF5 image files
    :linenos:

    from ophyd import ImagePlugin
    from ophyd import PilatusDetector
    from ophyd import SingleTrigger
    from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
    from ophyd.areadetector.plugins import HDF5Plugin_V34
    import os

    PILATUS_FILES_ROOT = "/mnt/fileserver/data"
    BLUESKY_FILES_ROOT = "/export/raid5/fileshare/data"
    TEST_IMAGE_DIR = "test/pilatus/%Y/%m/%d/"

    class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin_V34): ...

    class MyPilatusDetector(SingleTrigger, PilatusDetector):
        """Pilatus detector"""

        image = ADComponent(ImagePlugin, "image1:")
        hdf1 = ADComponent(
            MyHDF5Plugin,
            "HDF1:",
            write_path_template=os.path.join(PILATUS_FILES_ROOT, TEST_IMAGE_DIR),
            read_path_template=os.path.join(BLUESKY_FILES_ROOT, TEST_IMAGE_DIR),
        )

    det = MyPilatusDetector("Pilatus:", name="det")
    det.hdf1.create_directory.put(-5)
    det.hdf1.stage_sigs["compression"] = "LZ4"
    det.hdf1.stage_sigs["lazy_open"] = 1
    det.hdf1.stage_sigs["file_template"] = "%s%s_%3.3d.h5"
    del det.hdf1.stage_sigs["capture"]
    det.hdf1.stage_sigs["capture"] = 1


.. _ad_pilatus.explanation:

Pilatus Support Code Explained
------------------------------

The EPICS Area Detector [#]_ has support for many different types of
area detector.  While the full feature set varies amongst the supported
camera types, the general approach to building the necessary device
support in ophyd follows a common sequence.

.. [#] https://areadetector.github.io/master/index.html

An excellent first step to building the device for an area detector is
to first check the list of area detector cameras already supported in
ophyd. [#]_  If your camera is not supported, your next step is to
build custom support.  [#]_  [#]_

.. [#] https://blueskyproject.io/ophyd/area-detector.html#specific-hardware
.. [#] https://blueskyproject.io/ophyd/area-detector.html#custom-devices
.. [#] https://blueskyproject.io/ophyd/area-detector.html#custom-plugins-or-cameras

On the list of supported cameras, we find the ``PilatusDetector``. [#]_

.. [#] https://blueskyproject.io/ophyd/generated/ophyd.areadetector.detectors.PilatusDetector.html

Note that ophyd makes a distinction (using the Pilatus here as an
example) between ``PilatusDetector` and ``PilatusDetectorCam``.  We'll
clarify that distinction below.

Pay special attention to the :ref:`ad_pilatus.staging` section.  Staging is
fundamental to use of the detector with data acquisition.

General Structure
-----------------

Before you can create an ophyd object for your Pilatus detector, you'll
need to create an ophyd class that describes the features of the EPICS
Area Detector interface you plan to use, such as the camera
(*ADPilatus*, in this case) and any plugins such as computations or file
writers.

.. tip::  If your EPICS configuration uses **any** of the plugins,
    you **must** configure them in ophyd.  You can check if you
    missed any once you have created your detector object by calling
    its ``.missing_plugins()`` method.  For example, where our
    example Pilatus IOC uses the ``Pilatus:`` PV prefix::

       from ophyd import PilatusDetector
       det = PilatusDetector("Pilatus:", name="det")
       det.missing_plugins()

    We expect to see an empty list ``[]`` as the result of this last
    command. Otherwise, the list will describe the plugins we'll need to
    define.

The general support structure is a Python class that such as this one,
that provides for triggering and viewing the image (but not file
saving):

.. code-block:: python
    :caption: General Area Detector support Python code
    :linenos:

    class MyPilatusDetector(SingleTrigger, PilatusDetector):
        """Ophyd support class describing this detector"""

        # cam is already defined by PilatusDetector
        image = ADComponent(ImagePlugin, "image1:")
        # define other plugins here, as needed

    det = MyPilatusDetector("Pilatus:", name="det")

The Python class is defined where it derives from ``PilatusDetector``
and adds the ``SingleTrigger`` capabilities.  Note the class we are
customizing is always listed last, with additional features (also known
as *mixin* classes) given first.  That's the way Python wants it.

Then, a Python docstring that describes this structure.

Then, any additional *attributes* (class variable names) and their
associated ``ADComponent`` constructions, such as the Image plugin
shown. The second argument to the ``ADComponent`` comes from the EPICS
PV for that plugin, such as ``Pilatus:image1:`` for the Image plugin.

Finally, we show how the object is created with just the PV prefix for
EPICS IOC.  The ``name="det"`` keyword argument is required.  It is
customary that the name matches the object name for the
``MyPilatusDetector()`` object.

.. index: Staging; ophyd Device
.. _ad_pilatus.staging:

Staging an Ophyd Device
-----------------------

An important part of data acquisition is configuration of each ophyd
*Device* [#]_ for the acquisition steps.  In Bluesky, this is called
*staging* [#]_ and the acquisition is called *triggering*. [#]_  The
complete data acquisition sequence of any ophyd Device proceeds in this
order:

==========  ==================
step        actions
==========  ==================
*stage*     save the current device settings, then prepare the device for trigger
*trigger*   tell the device to run its acquisition sequence (returns a status object [#]_ after starting acquisition)
*wait*      wait until the status object indicates ``done=True``
*read*      get the data from the device (with timestamps)
*unstage*   restore the previous device settings (as saved in the stage step)
==========  ==================

We won't use the *read* step in this example:

* The EPICS IOC saves the image to a file
* Area detector images, unlike most other data we might handle for data
  acquisition, consume large resources.  We should only load that data
  into memory at the time we choose, not as a routine practice.
* When using the detector in a Bluesky plan, the RunEngine will get the
  information *about* the image (name and directory of the file created
  and the address in the file for the image).  This information about
  the image will be part of the document sent to the databroker.

The ophyd Area Detector ``SingleTrigger`` mixin provides the
configuration to stage and trigger the `.cam` for acquisition.   The
staging settings, defined as a Python dictionary, will be applied in the
order they have been added to the dictionary (and the restored in
reverse order).  The dictionary is in each Device's `.stage_sigs`
attribute.  Without the ``SingleTrigger`` mixin::

    >>> from ophyd import PilatusDetector
    >>> det = PilatusDetector("Pilatus:", name="det")
    >>> det.stage_sigs
    OrderedDict()

With the ``SingleTrigger`` mixin::

    >>> from ophyd import PilatusDetector
    >>> from ophyd import SingleTrigger
    >>> class MyPilatusDetector(SingleTrigger, PilatusDetector): ...
    >>> det = MyPilatusDetector("Pilatus:", name="det")
    >>> det.stage_sigs
    OrderedDict([('cam.acquire', 0), ('cam.image_mode', 1)])

The ophyd documentation has more information about *Staging*.

.. [#] https://blueskyproject.io/ophyd/device-overview.html?highlight=device
.. [#] https://blueskyproject.io/ophyd/device-overview.html?highlight=staging#stage-and-unstage
.. [#] https://blueskyproject.io/ophyd/device-overview.html?highlight=device#trd

Build the Support: ``MyPilatusDetector``
----------------------------------------

In most cases, you'll want to describe more than just the camera module
that EPICS Area Detector supplies for your detector (such as
``ADPilatus`` [#]_).  We want to trigger the camera during data
collection, view the image during collection [#]_, and write the image
to a file. [#]_

The ophyd ``PilatusDetector`` class only provides an area detector with
support for the *cam* module (the camera controls).  Since the
additional features we want are not supported by ``PilatusDetector``,
we'll need to add them.

We'll begin customizing the support in the sections below.

.. [#] https://areadetector.github.io/master/ADPilatus/pilatusDoc.html
.. [#] https://areadetector.github.io/master/ADViewers/ad_viewers.html
.. [#] https://areadetector.github.io/master/ADCore/NDPluginFile.html
.. [#] https://blueskyproject.io/ophyd/status.html#status-objects-futures

``MyPilatusDetector`` class
+++++++++++++++++++++++++++

So, following the general structure shown above, we start our
``MyPilatusDetector`` class, importing the necessary ophyd packages:

.. code-block:: python
    :caption: starting our MyPilatusDetector() Python code
    :linenos:

    from ophyd import ImagePlugin
    from ophyd import PilatusDetector
    from ophyd import SingleTrigger

    class MyPilatusDetector(SingleTrigger, PilatusDetector):
        """Ophyd support class describing this detector"""

        image = ADComponent(ImagePlugin, "image1:")

We could get the same structure with this class instead:

.. code-block:: python
    :caption: alternative, equivalent to above
    :linenos:

    from ophyd import AreaDetector
    from ophyd import ImagePlugin
    from ophyd import PilatusDetectorCam
    from ophyd import SingleTrigger

    class MyPilatusDetector(SingleTrigger, AreaDetector):
        """Ophyd support class describing this detector"""

        cam = ADComponent(PilatusDetectorCam, "cam1:")
        image = ADComponent(ImagePlugin, "image1:")

``PilatusDetectorCam`` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ophyd.areadetector.PilatusDetectorCam`` class provides
an ophyd ``Device`` interface for the *ADPilatus* camera controls.
This support is already included in the ``PilatusDetector`` class
so we do not need to add it (although there is no problem if we
add it anyway).

Any useful implementation of an EPICS area detector will support the
camera module, which controls the features of the camera and image
acquisition.  The detector classes defined in ``ophyd.areadetector.detectors``
all support the cam module appropriate for that detector.  They are convenience
classes for the repetitive step of adding ``cam`` support.

HDF5Plugin: Writing images to an HDF5 File
++++++++++++++++++++++++++++++++++++++++++

The ophyd ``HDF5Plugin`` class [#]_, provides support
for the HDF5 File Writing Plugin of EPICS Area Detector.

As the EPICS Area Detector support has changed between various releases,
the PVs available have also changed.  There are several version of the
ophyd ``HDF5Plugin`` class to track those changes.  Pick the highest
version of ophyd support that is equal or less than the EPICS Area
Detector version used in the IOC.  For AD 3.7, the highest available
ophyd plugin is ``ophyd.areadetector.plugins.HDF5Plugin_V34``::

    from ophyd.areadetector.plugins import HDF5Plugin_V34

We *could* just add this to our custom structure::

    hdf1 = ADComponent(HDF5Plugin_V34, "HDF:")

but we still need an additional mixin to control *where* the files
should be written (by the IOC) and read (by Bluesky)::

    from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite

which means we need to define a custom plugin class to bring these
two parts together::

    class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin_V34): ...

The ``FileStoreHDF5IterativeWrite`` mixin allows for the file directory
paths to be different on the two computers, but expects the files to be
available to both the EPICS IOC and the Bluesky session.  Thus, the
paths may have different first parts, up to a point where they match.

The Pilatus detector is a good example that needs the two paths to be
different.  It saves files to its own file systems.  (If the paths are
the same on both computers, it is not necessary to specify the
``read_path_template``.) For the Bluesky computer to *see* these files,
both computers must share the same filesystem.  The exact mount point
for the shared filesystem can be different on each.  Consider these
hypothetical mount points for the same shared ``data`` directory::

    PILATUS_FILES_ROOT = "/mnt/fileserver/data"
    BLUESKY_FILES_ROOT = "/export/raid5/fileshare/data"

To configure the ``HDF5Plugin()``, we must configure the
``write_path_template`` for how the shared filesystem is mounted on the
Pilatus computer and the ``read_path_template`` for how the same shared
filesystem is mounted on the Bluesky computer.  To set these paths, we
modify the above line to be::

    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=f"{PILATUS_FILES_ROOT}/",
        read_path_template=f"{BLUESKY_FILES_ROOT}/",
    )

.. tip:: EPICS Area Detector file writers require the directory
    separator at the end of the path and will add one if it is not
    given. Because ophyd expects the PV to become the value it has set,
    ophyd will timeout when writing the path if the final directory
    separator is not provided.

.. sidebar:: Use Python ``os.path.join`` to create directory paths!

    Instead of constructing a file path as::

        "/mnt/fileserver/data"

    you may see::

        os.path.join("/", "mnt", "fileserver", "data")

    which builds the path using the separator of the current
    operating system.

Additionally, we add to the mount point the directory path where our
files are to be stored on the shared.  Bluesky allows this path to
include ``datetime`` formatting.  We use this formatting to add the year
(``%Y``), month (``%m``), and day (``%d``) into the path for both
``write_path_template`` and ``read_path_template``::

    TEST_IMAGE_DIR = "test/pilatus/%Y/%m/%d"

With this change, our final change is complete::

    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=f"{PILATUS_FILES_ROOT}/{TEST_IMAGE_DIR}/",
        read_path_template=f"{BLUESKY_FILES_ROOT}/{TEST_IMAGE_DIR}/",
    )

.. tip:: Later, when it is decided to *change* the directory
    for the HDF5 image files, be sure to set *both* templates,
    using the proper mount points for each.  Follow the
    pattern as shown::

        path = "user_name/experiment/"  # note the trailing slash
        det.hdf1.write_path_template.put(os.path.join(PILATUS_FILES_ROOT, path))
        det.hdf1.read_path_template.put(os.path.join(BLUESKY_FILES_ROOT, path))

.. [#] https://blueskyproject.io/ophyd/generated/ophyd.areadetector.plugins.HDF5Plugin.html

Create the Ophyd object
-----------------------

With the custom support for our Pilatus, it is simple
to create the ophyd object, once we know the PV prefix
used by the EPICS IOC.  For this example, we'll assume
the prefix is ``Pilatus:``::

    det = MyPilatusDetector("Pilatus:", name="det")

Directory for the HDF5 files
++++++++++++++++++++++++++++

Previously, we set the ``write_path_template`` and
``read_path_template`` to control the directory where the Pilatus IOC
writes the HDF5 files and where Bluesky expects to find them once they
are created.

If these additional directories do not exist, we'll get an error when we
try to write the HDF5 file.  EPICS AD HDF5 plugin will create those
directories if the *CreateDirectory* PV (the ``create_directory``
attribute of the ``HDF5Plugin()``) is set to a negative number at least
as large as the number of directories to be created.  A value of ``-5``
is usually sufficent.  Such as::

    det.hdf1.create_directory.put(-5)

Make this adjustment after creating the ``det`` object and before
acquiring an image.

To change the directory for new HDF5 files::

        path = "user_name/experiment/"  # note the trailing slash
        det.hdf1.write_path_template.put(os.path.join(PILATUS_FILES_ROOT, path))
        det.hdf1.read_path_template.put(os.path.join(BLUESKY_FILES_ROOT, path))

Staging the HDF5Plugin
++++++++++++++++++++++

We need to configure the HDF5 plugin for staging.  The defaults are::

    >>> det.hdf1.stage_sigs
    OrderedDict([('enable', 1),
                ('blocking_callbacks', 'Yes'),
                ('parent.cam.array_callbacks', 1),
                ('auto_increment', 'Yes'),
                ('array_counter', 0),
                ('auto_save', 'Yes'),
                ('num_capture', 0),
                ('file_template', '%s%s_%6.6d.h5'),
                ('file_write_mode', 'Stream'),
                ('capture', 1)])

These settings enable the HDF5 writer and will pause the next
acquisition until the HDF5 file is written.  They will increment the
file numbering and will automatically save the file once the image is
captured.  By default, ophyd will choose a file name based on a random
``uuid``. [#]_  It is possible to change this naming style but those
steps are beyond this example.

We want to add LZ4 compression::

    >>> det.hdf1.stage_sigs["compression"] = "LZ4"

and enable the ``LazyOpen`` feature [#]_  (so we do not have to acquire
an image into the HDF5 plugin before our first data acquisition)::

    >>> det.hdf1.stage_sigs["lazy_open"] = 1

The ``LazyOpen`` setting *must* happen before the plugin is set to
``Capture``, so we must delete that and then add it as the last action::

    >>> del det.hdf1.stage_sigs["capture"]
    >>> det.hdf1.stage_sigs["capture"] = 1

We might reduce the number of digits written into the file name (this
will change the value in place instead of moving the setting to the end
of the actions)::

    >>> det.hdf1.stage_sigs["file_template"] = "%s%s_%3.3d.h5"

.. [#] https://docs.python.org/3/library/uuid.html#uuid.uuid4
.. [#] ``LazyOpen`` first appeared in AD 2.2

Acquire and Save an Image
-------------------------

Now that the ``det`` object is ready for data acquisition,
let's acquire an image using the ophyd tools::

    >>> det.stage()
    >>> st = det.trigger()

The return result was a Status object.  If we check its value before 
the image is saved to an HDF5 file, the result looks like this::

    >>> st
    ADTriggerStatus(device=det, done=False, success=False)

.. _ad_pilatus.status_object:
.. sidebar:: Status objects

    :index:`Status objects` are used when a Device does not complete its
    action right away.  Without Status objects, we would either have to
    poll the Device to learn if it is finished or we would need to set
    up an EPICS Channel Access monitor callback function to receive news
    of changes from the EPICS support.  And handle timeouts and failure
    scenarios.  Status objects handle all this routine work for us.

Once the image acquisition is complete, the status object will
indicate it is done.  We must wait until then by checking it.  Or, we
can call the ``.wait()`` method of the status object::

    >>> st.wait()

Once the acquisition is finished and the HDF5 file is written,
the ``wait()`` method will return.  We can check its value::

    >>> st
    ADTriggerStatus(device=det, done=True, success=True)

Acquisition is complete.  Don't forget to ``unstage()``::

    >>> det.unstage()

When we use ``det`` as a detector in a bluesky plan with the
``RunEngine``, the ``RunEngine`` will do all these steps (including
the wait for the status object to finish).

We can find the name of the HDF5 that was written (by the IOC)::

    >>> det.hdf1.full_file_name.get()
    /mnt/fileserver/data/test/pilatus/2021/01/22/4e26f601-df6d-4848-bf3f_000.h5

and we can get a local directory listing of the same file::

    >>> !ls -lAFgh /export/raid5/fileshare/data/test/pilatus/2021/01/22/4e26f601-df6d-4848-bf3f_000.h5
    -rw-r--r-- 1 root 2.2M Jan 22 00:41 /export/raid5/fileshare/data/test/pilatus/2021/01/22/4e26f601-df6d-4848-bf3f_000.h5

Note: The file size might be different for your detector.
