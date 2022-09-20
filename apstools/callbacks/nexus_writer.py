"""
NeXus File Writer Callbacks
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~NXWriter
   ~NXWriterAPS
"""

import datetime
import h5py
import logging
import numpy as np
import os
import yaml

from .callback_base import FileWriterCallbackBase


NEXUS_FILE_EXTENSION = "hdf"  # use this file extension for the output
NEXUS_RELEASE = "v2020.1"  # NeXus release to which this file is written
logger = logging.getLogger(__name__)


class NXWriter(FileWriterCallbackBase):
    """
    General class for writing HDF5/NeXus file (using only NeXus base classes).

    .. index:: Bluesky Callback; NXWriter

    New with apstools release 1.3.0.

    One scan is written to one HDF5/NeXus file.

    METHODS

    .. autosummary::

       ~writer
       ~h5string
       ~add_dataset_attributes
       ~assign_signal_type
       ~create_NX_group
       ~get_sample_title
       ~get_stream_link
       ~write_data
       ~write_detector
       ~write_entry
       ~write_instrument
       ~write_metadata
       ~write_monochromator
       ~write_positioner
       ~write_root
       ~write_sample
       ~write_slits
       ~write_source
       ~write_streams
       ~write_user
    """

    warn_on_missing_content = True
    file_extension = NEXUS_FILE_EXTENSION
    instrument_name = None  # name of this instrument
    # NeXus release to which this file is written
    nexus_release = NEXUS_RELEASE
    nxdata_signal = None  # name of dataset for Y axis on plot
    nxdata_signal_axes = None  # name of dataset for X axis on plot
    root = None  # instance of h5py.File

    # convention: methods written in alphabetical order

    def add_dataset_attributes(self, ds, v, long_name=None):
        """
        add attributes from v dictionary to dataset ds
        """
        ds.attrs["units"] = self.h5string(v["units"])
        ds.attrs["source"] = self.h5string(v["source"])
        if long_name is not None:
            ds.attrs["long_name"] = self.h5string(long_name)
        if v["dtype"] not in ("string",):
            ds.attrs["precision"] = v["precision"]

            def cautious_set(key):
                if v[key] is not None:
                    ds.attrs[key] = v[key]

            cautious_set("lower_ctrl_limit")
            cautious_set("upper_ctrl_limit")

    def assign_signal_type(self):
        """
        decide if a signal in the primary stream is a detector or a positioner
        """
        try:
            primary = self.root[
                "/entry/instrument/bluesky/streams/primary"
            ]
        except KeyError:
            raise KeyError(
                f"no primary data stream in "
                f"scan {self.scan_id} ({self.uid[:7]})"
            )
        for k, v in primary.items():
            # logger.debug(v.name)
            # logger.debug(v.keys())
            if k in self.detectors:
                signal_type = "detector"
            elif k in self.positioners:
                signal_type = "positioner"
            else:
                signal_type = "other"
            v.attrs["signal_type"] = signal_type  # group
            try:
                v["value"].attrs["signal_type"] = signal_type  # dataset
            except KeyError:
                if self.warn_on_missing_content:
                    logger.warning(
                        "Could not assign %s as signal type %s", k, signal_type
                    )

    def create_NX_group(self, parent, specification):
        """
        create an h5 group with named NeXus class (specification)
        """
        local_address, nx_class = specification.split(":")
        if not nx_class.startswith("NX"):
            raise ValueError(
                "NeXus base class must start with 'NX',"
                f" received {nx_class}"
            )
        group = parent.create_group(local_address)
        group.attrs["NX_class"] = nx_class
        group.attrs["target"] = group.name  # for use as NeXus link
        return group

    def getResourceFile(self, resource_id):
        """
        full path to the resource file specified by uid ``resource_id``

        override in subclass as needed
        """
        # reject unsupported specifications
        resource = self.externals[resource_id]
        if resource["spec"] not in ("AD_HDF5",):
            # HDF5-specific implementation for now
            raise ValueError(
                f'{resource_id}: spec {resource["spec"]} not handled'
            )

        # logger.debug(yaml.dump(resource))
        fname = os.path.join(resource["root"], resource["resource_path"],)
        return fname

    def get_sample_title(self):
        """
        return the title for this sample

        default title: {plan_name}-S{scan_id}-{short_uid}
        """
        return f"{self.plan_name}-S{self.scan_id:04d}-{self.uid[:7]}"

    def get_stream_link(self, signal, stream=None, ref=None):
        """
        return the h5 object for ``signal``

        DEFAULTS

        ``stream`` : ``baseline``
        ``key`` : ``value_start``
        """
        stream = stream or "baseline"
        ref = ref or "value_start"
        h5_addr = (
            f"/entry/instrument/bluesky/streams/{stream}/{signal}/{ref}"
        )
        if h5_addr not in self.root:
            raise KeyError(f"HDF5 address {h5_addr} not found.")
        # return the h5 object, to make a link
        return self.root[h5_addr]

    def h5string(self, text):
        """Format string for h5py interface."""
        if isinstance(text, (tuple, list)):
            return [self.h5string(str(t)) for t in text]
        text = text or ""
        return text.encode("utf8")

    def writer(self):
        """
        write collected data to HDF5/NeXus data file
        """
        fname = self.file_name or self.make_file_name()
        with h5py.File(fname, "w") as self.root:
            self.write_root(fname)

        self.root = None
        logger.info(f"wrote NeXus file: {fname}")  # lgtm [py/clear-text-logging-sensitive-data]
        self.output_nexus_file = fname

    def write_data(self, parent):
        """
        group: /entry/data:NXdata
        """
        nxdata = self.create_NX_group(parent, "data:NXdata")

        primary = parent["instrument/bluesky/streams/primary"]
        for k in primary.keys():
            nxdata[k] = primary[k + "/value"]

        # pick the timestamps from one of the datasets (the last one)
        nxdata["EPOCH"] = primary[k + "/time"]

        signal_attribute = self.nxdata_signal
        if signal_attribute is None:
            if len(self.detectors) > 0:
                # arbitrary but consistent choice
                signal_attribute = self.detectors[0]
        axes_attribute = self.nxdata_signal_axes
        if axes_attribute is None:
            if len(self.positioners) > 0:
                # TODO: what if wrong shape here?
                axes_attribute = self.positioners

        # TODO: rabbit-hole alert!  simplify
        # this code is convoluted (like the selection logic)
        # Is there a library to help? databroker? event_model? area_detector_handlers?
        fmt = "Cannot set %s as %s attribute, no such dataset"
        if signal_attribute is not None:
            if signal_attribute in nxdata:
                nxdata.attrs["signal"] = signal_attribute

                axes = []
                for ax in axes_attribute or []:
                    if ax in nxdata:
                        axes.append(ax)
                    else:
                        if self.warn_on_missing_content:
                            logger.warning(fmt, ax, "axes")
                if axes_attribute is not None:
                    nxdata.attrs["axes"] = axes_attribute
            else:
                if self.warn_on_missing_content:
                    logger.warning(fmt, signal_attribute, "signal")

        return nxdata

    def write_detector(self, parent):
        """
        group: /entry/instrument/detectors:NXnote/DETECTOR:NXdetector
        """
        if len(self.detectors) == 0:
            logger.info("No detectors identified.")
            return

        primary = parent["/entry/instrument/bluesky/streams/primary"]

        group = self.create_NX_group(parent, "detectors:NXnote")
        for k, v in primary.items():
            if v.attrs.get("signal_type") != "detector":
                continue
            nxdetector = self.create_NX_group(group, f"{k}:NXdetector")
            nxdetector["data"] = v

        return group

    def write_entry(self):
        """
        group: /entry/data:NXentry
        """
        nxentry = self.create_NX_group(
            self.root, self.root.attrs["default"] + ":NXentry"
        )

        nxentry.create_dataset(
            "start_time",
            data=datetime.datetime.fromtimestamp(
                self.start_time
            ).isoformat(),
        )
        nxentry.create_dataset(
            "end_time",
            data=datetime.datetime.fromtimestamp(
                self.stop_time
            ).isoformat(),
        )
        ds = nxentry.create_dataset(
            "duration", data=self.stop_time - self.start_time
        )
        ds.attrs["units"] = "s"

        nxentry.create_dataset("program_name", data="bluesky")

        self.write_instrument(nxentry)  # also writes streams and metadata
        try:
            nxdata = self.write_data(nxentry)
            nxentry.attrs["default"] = nxdata.name.split("/")[-1]
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning(exc)

        self.write_sample(nxentry)
        self.write_user(nxentry)

        # apply links
        h5_addr = "/entry/instrument/source/cycle"
        if h5_addr in self.root:
            nxentry["run_cycle"] = self.root[h5_addr]
        else:
            if self.warn_on_missing_content:
                logger.warning("No data for /entry/run_cycle")

        nxentry["title"] = self.get_sample_title()
        nxentry["plan_name"] = self.root[
            "/entry/instrument/bluesky/metadata/plan_name"
        ]
        nxentry["entry_identifier"] = self.root[
            "/entry/instrument/bluesky/uid"
        ]

        return nxentry

    def write_instrument(self, parent):
        """
        group: /entry/instrument:NXinstrument
        """
        nxinstrument = self.create_NX_group(
            parent, "instrument:NXinstrument"
        )
        bluesky_group = self.create_NX_group(
            nxinstrument, "bluesky:NXnote"
        )

        md_group = self.write_metadata(bluesky_group)
        self.write_streams(bluesky_group)

        bluesky_group["uid"] = md_group["run_start_uid"]
        bluesky_group["plan_name"] = md_group["plan_name"]

        try:
            self.assign_signal_type()
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning(exc)

        self.write_slits(nxinstrument)
        try:
            self.write_detector(nxinstrument)
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning(exc)

        self.write_monochromator(nxinstrument)
        try:
            self.write_positioner(nxinstrument)
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning(exc)
        self.write_source(nxinstrument)
        return nxinstrument

    def write_metadata(self, parent):
        """
        group: /entry/instrument/bluesky/metadata:NXnote

        metadata from the bluesky start document
        """
        group = self.create_NX_group(parent, "metadata:NXnote")

        ds = group.create_dataset("run_start_uid", data=self.uid)
        ds.attrs["long_name"] = "bluesky run uid"
        ds.attrs["target"] = ds.name

        for k, v in self.metadata.items():
            is_yaml = False
            if isinstance(v, (dict, tuple, list)):
                # fallback technique: save complicated structures as YAML text
                v = yaml.dump(v)
                is_yaml = True
            if isinstance(v, str):
                v = self.h5string(v)
            ds = group.create_dataset(k, data=v)
            ds.attrs["target"] = ds.name
            if is_yaml:
                ds.attrs["text_format"] = "yaml"

        return group

    def write_monochromator(self, parent):
        """
        group: /entry/instrument/monochromator:NXmonochromator
        """
        pre = "monochromator_dcm"
        keys = "wavelength energy theta y_offset mode".split()

        try:
            links = {
                key: self.get_stream_link(f"{pre}_{key}") for key in keys
            }
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning(
                    "%s -- not creating monochromator group", str(exc)
                )
            return

        pre = "monochromator"
        key = "feedback_on"
        try:
            links[key] = self.get_stream_link(f"{pre}_{key}")
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning("%s -- feedback signal not found", str(exc))

        nxmonochromator = self.create_NX_group(
            parent, "monochromator:NXmonochromator"
        )
        for k, v in links.items():
            nxmonochromator[k] = v
        return nxmonochromator

    def write_positioner(self, parent):
        """
        group: /entry/instrument/positioners:NXnote/POSITIONER:NXpositioner
        """
        if len(self.positioners) == 0:
            logger.info("No positioners identified.")
            return

        primary = parent["/entry/instrument/bluesky/streams/primary"]

        group = self.create_NX_group(parent, "positioners:NXnote")
        for k, v in primary.items():
            if v.attrs.get("signal_type") != "positioner":
                continue
            nxpositioner = self.create_NX_group(group, f"{k}:NXpositioner")
            nxpositioner["value"] = v

        return group

    def write_root(self, filename):
        """
        root of the HDF5 file
        """
        self.root.attrs["file_name"] = filename
        self.root.attrs["file_time"] = datetime.datetime.now().isoformat()
        if self.instrument_name is not None:
            self.root.attrs["instrument"] = self.instrument_name
        self.root.attrs["creator"] = self.__class__.__name__
        self.root.attrs["NeXus_version"] = self.nexus_release
        self.root.attrs["HDF5_Version"] = h5py.version.hdf5_version
        self.root.attrs["h5py_version"] = h5py.version.version
        self.root.attrs["default"] = "entry"

        self.write_entry()

    def write_sample(self, parent):
        """
        group: /entry/sample:NXsample
        """
        pre = "sample_data"
        keys = """
            chemical_formula
            concentration
            description
            electric_field
            magnetic_field
            rotation_angle
            scattering_length_density
            stress_field
            temperature
            volume_fraction
            x_translation
        """.split()

        links = {}
        for key in keys:
            try:
                links[key] = self.get_stream_link(f"{pre}_{key}")
            except KeyError as exc:
                if self.warn_on_missing_content:
                    logger.warning("%s", str(exc))
        if len(links) == 0:
            if self.warn_on_missing_content:
                logger.warning(
                    "no sample data found, not creating sample group"
                )
            return

        nxsample = self.create_NX_group(parent, "sample:NXsample")
        for k, v in links.items():
            nxsample[k] = v

        for key in "electric_field magnetic_field stress_field".split():
            ds = nxsample[key]
            ds.attrs["direction"] = self.get_stream_link(
                f"{pre}_{key}_dir"
            )[()].lower()

        return nxsample

    def write_slits(self, parent):
        """
        group: /entry/instrument/slits:NXnote/SLIT:NXslit

        override in subclass to store content, name patterns
        vary with each instrument
        """
        # group = self.create_NX_group(parent, f"slits:NXnote")

    def write_source(self, parent):
        """
        group: /entry/instrument/source:NXsource

        Note: this is (somewhat) generic, override for a different source
        """
        nxsource = self.create_NX_group(parent, "source:NXsource")

        ds = nxsource.create_dataset("name", data="Bluesky framework")
        ds.attrs["short_name"] = "bluesky"
        nxsource.create_dataset("type", data="Synchrotron X-ray Source")
        nxsource.create_dataset("probe", data="x-ray")

        return nxsource

    def write_stream_external(
        self, parent, d, subgroup, stream_name, k, v
    ):
        # TODO: rabbit-hole alert! simplify
        # lots of variations possible

        # count number of unique resources (expect only 1)
        resource_id_list = []
        for datum_id in d:
            resource_id = self.externals[datum_id]["resource"]
            if resource_id not in resource_id_list:
                resource_id_list.append(resource_id)
        if len(resource_id_list) != 1:
            raise ValueError(
                f"{len(resource_id_list)}"
                f" unique resource UIDs: {resource_id_list}"
            )

        fname = self.getResourceFile(resource_id)
        logger.info("reading %s from EPICS AD data file: %s", k, fname)
        with h5py.File(fname, "r") as hdf_image_file_root:
            h5_obj = hdf_image_file_root["/entry/data/data"]
            ds = subgroup.create_dataset(
                "value",
                data=h5_obj[()],
                compression="lzf",
                # compression="gzip",
                # compression_opts=9,
                shuffle=True,
                fletcher32=True,
            )
            ds.attrs["target"] = ds.name
            ds.attrs["source_file"] = fname
            ds.attrs["source_address"] = h5_obj.name
            ds.attrs["resource_id"] = resource_id
            ds.attrs["units"] = ""

        subgroup.attrs["signal"] = "value"

    def write_stream_internal(
        self, parent, d, subgroup, stream_name, k, v
    ):
        # fmt: off
        subgroup.attrs["signal"] = "value"
        subgroup.attrs["axes"] = ["time", ]
        # fmt: on
        if isinstance(d, list) and len(d) > 0:
            if v["dtype"] in ("string",):
                d = self.h5string(d)
            elif v["dtype"] in ("integer", "number"):
                d = np.array(d)
        try:
            ds = subgroup.create_dataset("value", data=d)
            ds.attrs["target"] = ds.name
            try:
                self.add_dataset_attributes(ds, v, k)
            except Exception as exc:
                logger.error("%s %s %s %s", v["dtype"], type(d), k, exc)
        except TypeError as exc:
            logger.error(
                "%s %s %s %s",
                v["dtype"],
                k,
                f"TypeError({exc})",
                v["data"],
            )
        if stream_name == "baseline":
            # make it easier to pick single values
            # identify start/end of acquisition
            ds = subgroup.create_dataset("value_start", data=d[0])
            self.add_dataset_attributes(ds, v, k)
            ds.attrs["target"] = ds.name
            ds = subgroup.create_dataset("value_end", data=d[-1])
            self.add_dataset_attributes(ds, v, k)
            ds.attrs["target"] = ds.name

    def write_streams(self, parent):
        """
        group: /entry/instrument/bluesky/streams:NXnote

        data from all the bluesky streams
        """
        bluesky = self.create_NX_group(parent, "streams:NXnote")
        for stream_name, uids in self.streams.items():
            if len(uids) != 1:
                raise ValueError(
                    f"stream {len(uids)} has descriptors, expecting only 1"
                )
            group = self.create_NX_group(bluesky, stream_name + ":NXnote")
            uid0 = uids[0]  # just get the one descriptor uid
            group.attrs["uid"] = uid0
            # just get the one descriptor
            acquisition = self.acquisitions[uid0]
            for k, v in acquisition["data"].items():
                d = v["data"]
                # NXlog is for time series data but NXdata makes an automatic plot
                subgroup = self.create_NX_group(group, k + ":NXdata")

                if v["external"]:
                    self.write_stream_external(
                        parent, d, subgroup, stream_name, k, v
                    )
                else:
                    self.write_stream_internal(
                        parent, d, subgroup, stream_name, k, v
                    )

                t = np.array(v["time"])
                ds = subgroup.create_dataset("EPOCH", data=t)
                ds.attrs["units"] = "s"
                ds.attrs["long_name"] = "epoch time (s)"
                ds.attrs["target"] = ds.name

                t_start = t[0]
                ds = subgroup.create_dataset("time", data=t - t_start)
                ds.attrs["units"] = "s"
                ds.attrs["long_name"] = "time since first data (s)"
                ds.attrs["target"] = ds.name
                ds.attrs["start_time"] = t_start
                ds.attrs[
                    "start_time_iso"
                ] = datetime.datetime.fromtimestamp(t_start).isoformat()

            # link images to parent names
            for k in group:
                if k.endswith("_image") and k[:-6] not in group:
                    group[k[:-6]] = group[k]

        return bluesky

    def write_user(self, parent):
        """
        group: /entry/contact:NXuser
        """
        keymap = dict(
            name="bss_user_info_contact",
            affiliation="bss_user_info_institution",
            email="bss_user_info_email",
            facility_user_id="bss_user_info_badge",
        )

        try:
            links = {k: self.get_stream_link(v) for k, v in keymap.items()}
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning("%s -- not creating source group", str(exc))
            return

        nxuser = self.create_NX_group(parent, "contact:NXuser")
        nxuser.create_dataset("role", data="contact")
        for k, v in links.items():
            nxuser[k] = v
        return nxuser


class NXWriterAPS(NXWriter):
    """
    Customize :class:`~NXWriter` with APS-specific content.

    .. index:: Bluesky Callback; NXWriterAPS

    New with apstools release 1.3.0.

    * Adds `/entry/instrument/undulator` group if metadata exists.
    * Adds APS information to `/entry/instrument/source` group.

    .. autosummary::

       ~write_instrument
       ~write_source
       ~write_undulator
    """

    # convention: methods written in alphabetical order

    def write_instrument(self, parent):
        """
        group: /entry/instrument:NXinstrument
        """
        nxinstrument = super().write_instrument(parent)
        self.write_undulator(nxinstrument)

    def write_source(self, parent):
        """
        group: /entry/instrument/source:NXsource

        Note: this is specific to the APS, override for a different source
        """
        pre = "aps"
        keys = "current fill_number".split()

        try:
            # fmt: off
            links = {
                key: self.get_stream_link(f"{pre}_{key}")
                for key in keys
            }
            # fmt: on
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning("%s -- not creating source group", str(exc))
            return

        nxsource = self.create_NX_group(parent, "source:NXsource")
        for k, v in links.items():
            nxsource[k] = v

        ds = nxsource.create_dataset("name", data="Advanced Photon Source")
        ds.attrs["short_name"] = "APS"
        nxsource.create_dataset("type", data="Synchrotron X-ray Source")
        nxsource.create_dataset("probe", data="x-ray")
        ds = nxsource.create_dataset("energy", data=6)
        ds.attrs["units"] = "GeV"

        try:
            nxsource["cycle"] = self.get_stream_link("aps_aps_cycle")
        except KeyError:
            pass  # Should we compute the cycle?

        return nxsource

    def write_undulator(self, parent):
        """
        group: /entry/instrument/undulator:NXinsertion_device
        """
        pre = "undulator_downstream"
        keys = """
            device location
            energy
            energy_taper
            gap
            gap_taper
            harmonic_value
            total_power
            version
        """.split()

        try:
            links = {
                key: self.get_stream_link(f"{pre}_{key}") for key in keys
            }
        except KeyError as exc:
            if self.warn_on_missing_content:
                logger.warning("%s -- not creating undulator group", str(exc))
            return

        undulator = self.create_NX_group(
            parent, "undulator:NXinsertion_device"
        )
        undulator.create_dataset("type", data="undulator")
        for k, v in links.items():
            undulator[k] = v
        return undulator

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
