.. index:: Example; Area Detector

.. _ad_pe:

Example: Perkin-Elmer EPICS Area Detector
=========================================

In this example, we'll show how to create an ophyd object
that operates a Perkin-Elmer Camera as a detector.  We'll start
with the :ref:`Pilatus example <ad_pilatus.summary>`.

The only difference from the Pilatus example is the detector class
(``PerkinElmerDetector``), the PV prefix (we'll use ``PE1:`` here), and
possibly the plugin version. For simplicity, we'll assume the same
version of EPICS Area Detector (3.7) is used in this example.  We'll use
a different object name, ``det_pe``, for this detector and different
directories (where the write and read directories are the same).

Here is
the Perkin-Elmer support, derived from the Pilatus support
(:ref:`ad_pilatus`).

.. code-block:: python
    :caption: Perkin-Elmer Area Detector support, writing HDF5 image files
    :linenos:

    from ophyd import ImagePlugin
    from ophyd import PerkinElmerDetector
    from ophyd import SingleTrigger
    from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
    from ophyd.areadetector.plugins import HDF5Plugin_V34
    import os

    IMAGE_FILES_ROOT = "/local/data"
    TEST_IMAGE_DIR = "test/"

    class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin_V34): ...

    class MyPilatusDetector(SingleTrigger, PerkinElmerDetector):
        """Perkin-Elmer detector"""

        image = ADComponent(ImagePlugin, "image1:")
        hdf1 = ADComponent(
            MyHDF5Plugin,
            "HDF1:",
            write_path_template=os.path.join(
                IMAGE_FILES_ROOT, TEST_IMAGE_DIR
            ),
        )

    det_pe = MyPilatusDetector("PE1:", name="det_pe")
    det_pe.hdf1.create_directory.put(-5)
    det_pe.hdf1.stage_sigs["compression"] = "LZ4"
    det_pe.hdf1.stage_sigs["lazy_open"] = 1
    det_pe.hdf1.stage_sigs["file_template"] = "%s%s_%3.3d.h5"
    det_pe det.hdf1.stage_sigs["capture"]
    det_pe.hdf1.stage_sigs["capture"] = 1
