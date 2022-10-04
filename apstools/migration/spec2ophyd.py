#!/usr/bin/env python

"""
read SPEC config file and convert to ophyd setup commands

output of ophyd configuration to stdout

*new in apstools release 1.1.7*

**USAGE**

.. code-block:: bash

    user@host ~ $ ./spec2ophyd.py
    usage: spec2ophyd.py [-h] [-v] configFileName
    spec2ophyd.py: error: the following arguments are required: configFileName

    user@host ~ $ ./spec2ophyd.py -h
    usage: spec2ophyd.py [-h] [-v] configFileName

    read SPEC config file and convert to ophyd setup commands

    positional arguments:
    configFileName  SPEC config file name

    optional arguments:
    -h, --help      show this help message and exit
    -v, --version   print version number and exit

"""

from collections import OrderedDict
import re


KNOWN_DEVICES = "PSE_MAC_MOT VM_EPICS_M1 VM_EPICS_PV VM_EPICS_SC".split()


class Spec2ophydBase(object):

    str_keys = []
    mne = ""
    name = ""

    def obj_keys_to_list(self):
        items = []
        keys = list(self.str_keys)

        if (
            "mne" in keys
            and "name" in keys
            and hasattr(self, "mne")
            and hasattr(self, "name")
            and self.mne == self.name
        ):
            keys.pop(keys.index("name"))  # redundant, do not show

        for k in keys:
            if hasattr(self, k):
                v = self.__getattribute__(k)
                items.append(f"{k}='{v}'")
        return items

    def __str__(self):
        items = self.obj_keys_to_list()
        return f"{self.__class__.__name__}({', '.join(items)})"


class SpecDevice(Spec2ophydBase):
    """
    SPEC configuration of a device, e.g. multi-channel motor controller

    SPEC "devices" are components which counters or motors to controllers
    """

    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
        self.raw = config_text
        # VM_EPICS_M1    = 9idcLAX:m58:c0: 8
        nm, args = config_text.split("=")
        self.name = nm.strip()
        prefix, num_channels = args.split()
        self.prefix = prefix
        self.config_line = None
        self.index = None
        self.num_channels = int(num_channels)
        self.ophyd_device = None
        self.str_keys = (
            "config_line name index, prefix num_channels".split()
        )


class ItemNameBase(Spec2ophydBase):

    ignore = False
    str_keys = "mne config_line name"

    def item_name_value(self, item):
        if hasattr(self, item):
            return f"{item}={self.__getattribute__(item)}"

    def ophyd_config(self):
        return f"{self.mne} = {self} # FIXME: not valid ophyd"


class SpecSignal(ItemNameBase):
    """
    SPEC configuration of a single EPICS PV
    """

    def __init__(self, mne, nm, pvname, config_text):
        """data provided by caller"""
        self.raw = config_text
        self.mne = mne
        self.name = nm
        self.pvname = pvname
        self.device = None
        self.signal_name = "EpicsSignal"

        lr = config_text.split(sep="=", maxsplit=1)

        def pop_word(line, int_result=False):
            line = line.strip()
            pos = line.find(" ")
            l, r = line[:pos].strip(), line[pos:].strip()
            if int_result:
                l = int(l)
            return l, r

        self.ctrl, r = pop_word(lr[1])
        self.unit, r = pop_word(r, True)
        self.chan, r = pop_word(r, True)
        self.scale, r = pop_word(r, True)
        self.flags = pop_word(r)[0]

        self.str_keys = "mne config_line name pvname signal_name".split()
        self.cntpar = {}

    def setDevice(self, devices):
        if self.ctrl.startswith("EPICS_PV"):
            device_list = devices.get("VM_EPICS_PV")
            if device_list is not None:
                self.device = device_list[self.unit]
                self.pvname = self.device.prefix
                self.ophyd_device = "EpicsSignal"
        elif self.ctrl.startswith("NONE"):
            self.ignore = True

    def ophyd_config(self):
        s = (
            f"{self.mne} = {self.signal_name}"
            f"('{self.pvname}', name='{self.mne}', labels=('detectors',))"
        )
        suffix = None
        if "misc_par_1" in self.cntpar:
            suffix = self.cntpar.pop("misc_par_1")
            pvname = f"{self.device.prefix}{suffix}"
            s = (
                f"{self.mne} = EpicsSignal"
                f"('{pvname}', name='{self.mne}', labels=('detectors',))"
            )
        if self.mne != self.name:
            s += f"  # {self.name}"
        if self.ignore:
            s = "# NONE: " + s
        if len(self.cntpar) > 0:
            terms = [f"{k}={v}" for k, v in self.cntpar.items()]
            s += f" # {', '.join(terms)}"
        return s


class SpecMotor(ItemNameBase):
    """
    SPEC configuration of a motor channel
    """

    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
        self.raw = config_text
        # Motor    ctrl steps sign slew base backl accel nada  flags   mne  name
        # MOT002 = EPICS_M2:0/3   2000  1  2000  200   50  125    0 0x003       my  my
        # MOT022 = MAC_MOT:1/0/0   2000  1  2000  200   50  125    0 0x003   suvgap  SlitUpVGap
        lr = config_text.split(sep="=", maxsplit=1)
        self.config_line = int(lr[0].strip("MOT"))

        def pop_word(line, int_result=False):
            line = line.strip()
            pos = line.find(" ")
            l, r = line[:pos].strip(), line[pos:].strip()
            if int_result:
                l = int(l)
            return l, r

        self.ctrl, r = pop_word(lr[1])
        self.steps, r = pop_word(r, True)
        self.sign, r = pop_word(r, True)
        self.slew, r = pop_word(r, True)
        self.base, r = pop_word(r, True)
        self.backl, r = pop_word(r, True)
        self.accel, r = pop_word(r, True)
        self.nada, r = pop_word(r, True)
        self.flags, r = pop_word(r)
        self.mne, self.name = pop_word(r)
        self.device = None
        self.pvname = None
        self.motpar = {}
        self.mac_parms = None
        self.macro_prefix = None
        self.str_keys = "mne config_line name macro_prefix mac_parms".split()

    def __str__(self):
        items = self.obj_keys_to_list()
        txt = self.item_name_value("pvname") or self.item_name_value(
            "ctrl"
        )
        if not txt.endswith("=None"):
            items.append(txt)
        return f"{self.__class__.__name__}({', '.join(items)})"

    def setDevice(self, devices):
        if self.ctrl.startswith("EPICS_M2"):
            device_list = devices.get("VM_EPICS_M1")
            if device_list is not None:
                uc_str = self.ctrl[len("EPICS_M2:"):]
                unit, chan = list(map(int, uc_str.split("/")))
                self.device = device_list[unit]
                self.pvname = "{}m{}".format(self.device.prefix, chan)
        elif self.ctrl.startswith("MAC_MOT"):
            device_list = devices.get("PSE_MAC_MOT")
            if device_list is not None:
                uc_str = self.ctrl[len("MAC_MOT:"):]
                unit, *self.mac_parms = list(map(int, uc_str.split("/")))
                self.device = device_list[unit]
                self.macro_prefix = self.device.prefix
                # TODO: what else?
        elif self.ctrl.startswith("NONE"):
            self.ignore = True

    def ophyd_config(self):
        s = (
            f"{self.mne} = EpicsMotor"
            f"('{self.pvname}', name='{self.mne}', labels=('motor',))"
        )
        suffix = None
        if "misc_par_1" in self.motpar:
            # suffix = self.motpar.pop("misc_par_1")
            suffix = self.motpar["misc_par_1"]
            pvname = f"{self.device.prefix}{suffix}"
            s = (
                f"{self.mne} = EpicsMotor"
                f"('{pvname}', name='{self.mne}', labels=('motor',))"
            )
        if self.pvname is None:
            if self.macro_prefix is not None:
                s = f"# Macro Motor: {self}"
            else:
                s = f"# {self.config_line}: {self.raw}"
        if self.mne != self.name:
            s += f"  # {self.name}"
        if len(self.motpar) > 0:
            terms = [f"{k}={v}" for k, v in self.motpar.items()]
            s += f" # {', '.join(terms)}"
        return s


class SpecCounter(ItemNameBase):
    """
    SPEC configuration of a counter channel

    In SPEC's config file, a single PV signal is described as a counter,
    attached to an EPICS_PV (as described by a VM_EPICS_PV device).
    """

    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
        self.raw = config_text
        # # Counter   ctrl unit chan scale flags    mne  name
        # CNT000 = EPICS_SC  0  0 10000000 0x001      sec  seconds

        def pop_word(line, int_result=False):
            line = line.strip()
            pos = line.find(" ")
            l, r = line[:pos].strip(), line[pos:].strip()
            if int_result:
                l = int(l)
            return l, r

        l, r = pop_word(config_text)
        self.config_line = int(l.strip("CNT"))
        l, r = pop_word(r)  # ignore "="
        self.ctrl, r = pop_word(r)
        self.unit, r = pop_word(r, True)
        self.chan, r = pop_word(r, True)
        self.scale, r = pop_word(r, True)
        self.flags, r = pop_word(r)
        self.mne, self.name = pop_word(r)
        self.device = None
        self.pvname = None
        self.reported_pvs = []
        self.str_keys = "mne config_line name unit chan".split()
        self.cntpar = {}

    def __str__(self):
        items = self.obj_keys_to_list()
        txt = self.item_name_value("pvname")
        if txt is not None:
            items.append(txt)
        else:
            items.append(self.item_name_value("ctrl"))
        return f"{self.__class__.__name__}({', '.join(items)})"

    def setDevice(self, devices):
        if self.ctrl.startswith("EPICS_SC"):
            device_list = devices.get("VM_EPICS_SC")
            if device_list is not None:
                self.device = device_list[self.unit]
                # scalers are goofy,
                # SPEC uses 0-based numbering,
                # scaler uses 1-based
                self.pvname = "{}.S{}".format(
                    self.device.prefix, self.chan + 1
                )
        elif self.ctrl.startswith("EPICS_PV"):
            device_list = devices.get("VM_EPICS_PV")
            if device_list is not None:
                self.device = device_list[self.unit]
                self.pvname = self.device.prefix
                self.ophyd_device = "EpicsSignal"
        elif self.ctrl.startswith("NONE"):
            self.ignore = True

    def ophyd_config(self):
        s = f"# counter: {self.mne} = {self}"
        suffix = None
        if "misc_par_1" in self.cntpar:
            suffix = self.cntpar.pop("misc_par_1")
            if self.device is None:
                self.ignore = True
            else:
                prefix = self.device.prefix
                pvname = f"{prefix}{suffix}"
                s = f"{self.mne} = EpicsSignal("
                s += (
                    f"'{pvname}', name='{self.mne}',"
                    f" labels=('detectors',)"
                )
                s += ")"
        if self.ignore:
            s = f"# {self.config_line}: {self.raw}"
        if len(self.cntpar) > 0:
            terms = [f"{k}={v}" for k, v in self.cntpar.items()]
            s += f" # {', '.join(terms)}"
        return s


class SpecConfig(object):
    """
    SPEC configuration
    """

    def __init__(self, config_file):
        self.config_file = config_file
        self.devices = OrderedDict()
        self.scalers = []
        self.collection = []
        self.unhandled = []

    def find_pv_in_collection(self, pv):
        for obj in self.collection:
            if pv == obj.pvname:
                return obj

    def read_config(self, config_file=None):
        self.config_file = config_file or self.config_file
        motor = None
        counter = None
        with open(self.config_file, "r") as f:
            for line_number, line in enumerate(f.readlines()):
                line = line.strip()

                if line.startswith("#"):
                    continue

                word0 = line.split(sep="=", maxsplit=1)[0].strip()
                if word0 in KNOWN_DEVICES:
                    device = SpecDevice(line)
                    if device.name not in self.devices:
                        self.devices[device.name] = []
                    # 0-based numbering
                    device.config_line = line_number
                    device.index = len(self.devices[device.name])
                    self.devices[device.name].append(device)
                elif word0.startswith("CNTPAR:"):
                    item = self.collection[-1]  # most recent item
                    if isinstance(item, (SpecSignal, SpecCounter)):
                        k, v = line[len("CNTPAR:"):].split("=")
                        item.cntpar[k.strip()] = v.strip()
                elif word0.startswith("MOTPAR:"):
                    if motor is not None:
                        k, v = line[len("MOTPAR:"):].split("=")
                        motor.motpar[k.strip()] = v.strip()
                elif re.match(r"CNT\d*", line) is not None:
                    counter = SpecCounter(line)
                    if counter.ctrl == "EPICS_PV":
                        # fmt: off
                        signal = SpecSignal(
                            counter.mne, counter.name,
                            counter.pvname, line
                        )
                        # fmt: on
                        signal.setDevice(self.devices)
                        self.collection.append(signal)
                    else:
                        counter.setDevice(self.devices)
                        if counter.pvname is not None:
                            pvname = counter.pvname.split(".")[0]
                            if pvname not in self.scalers:
                                mne = pvname.lower().split(":")[-1]
                                scaler = SpecSignal(mne, mne, pvname, line)
                                scaler.signal_name = "ScalerCH"
                                self.scalers.append(pvname)
                                self.collection.append(scaler)

                        if counter.pvname is None:
                            scaler = None
                        else:
                            scaler = self.find_pv_in_collection(
                                counter.pvname.split(".")[0]
                            )
                        if scaler is not None:
                            # clock = scaler.channels.chan01.s
                            fmt = "%s = %s.channels.chan%02d.s"
                            reassignment = fmt % (
                                counter.mne,
                                scaler.name,
                                counter.chan + 1,
                            )
                            counter = reassignment
                        self.collection.append(counter)
                elif re.match(r"MOT\d*", line) is not None:
                    motor = SpecMotor(line)
                    motor.setDevice(self.devices)
                    self.collection.append(motor)
                else:
                    self.unhandled.append(line)


def create_ophyd_setup(spec_config):
    print('"""')
    print("ophyd commands from SPEC config file")
    print()
    print(f"file: {spec_config.config_file}")
    print()
    print("CAUTION: Review the object names below before using them!")
    print("    Some names may not be valid python identifiers")
    print("    or may be reserved (such as ``time`` or ``del``)")
    print("    or may be vulnerable to re-definition because")
    print("    they are short or common.")
    print('"""')
    print()
    print("from ophyd import EpicsMotor, EpicsSignal")
    print("from ophyd.scaler import ScalerCH")
    print()
    for device in spec_config.collection:
        if hasattr(device, "ophyd_config"):
            print(f"{device.ophyd_config()}")
            if (
                hasattr(device, "signal_name")
                and device.signal_name == "ScalerCH"
            ):
                print(f"{device.name}.select_channels(None)")
        else:
            print(device)


def get_apstools_version():
    """Get the version string from the parent package."""
    from .. import __version__
    return __version__


def get_options():
    """Handle command line arguments."""
    import argparse
    import os
    import sys

    version = get_apstools_version()

    parser = argparse.ArgumentParser(
        prog=os.path.split(sys.argv[0])[-1],
        description=__doc__.strip().splitlines()[0],
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="print version number and exit",
        version=version,
    )

    parser.add_argument(
        "configFileName", type=str, help="SPEC config file name"
    )

    return parser.parse_args()


def main():
    args = get_options()
    spec_cfg = SpecConfig(args.configFileName)
    spec_cfg.read_config()
    create_ophyd_setup(spec_cfg)


if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
