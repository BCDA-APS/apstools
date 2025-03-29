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

import re
from collections import OrderedDict
from typing import Union, Tuple, Optional, Dict, List, Any

KNOWN_DEVICES: List[str] = "PSE_MAC_MOT VM_EPICS_M1 VM_EPICS_PV VM_EPICS_SC".split()


class Spec2ophydBase(object):
    str_keys: List[str] = []
    mne: str = ""
    name: str = ""

    def obj_keys_to_list(self) -> List[str]:
        items: List[str] = []
        keys: List[str] = list(self.str_keys)

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

    def __str__(self) -> str:
        items: List[str] = self.obj_keys_to_list()
        return f"{self.__class__.__name__}({', '.join(items)})"


class SpecDevice(Spec2ophydBase):
    """
    SPEC configuration of a device, e.g. multi-channel motor controller

    SPEC "devices" are components which counters or motors to controllers
    """

    def __init__(self, config_text: str) -> None:
        """parse the line from the SPEC config file"""
        self.raw: str = config_text
        # VM_EPICS_M1    = 9idcLAX:m58:c0: 8
        nm, args = config_text.split("=")
        self.name: str = nm.strip()
        prefix, num_channels = args.split()
        self.prefix: str = prefix
        self.config_line: Optional[int] = None
        self.index: Optional[int] = None
        self.num_channels: int = int(num_channels)
        self.ophyd_device: Optional[str] = None
        self.str_keys = "config_line name index, prefix num_channels".split()


class ItemNameBase(Spec2ophydBase):
    ignore: bool = False
    str_keys: List[str] = "mne config_line name".split()

    def item_name_value(self, item: str) -> Optional[str]:
        if hasattr(self, item):
            return f"{item}={self.__getattribute__(item)}"
        return None

    def ophyd_config(self) -> str:
        return f"{self.mne} = {self} # FIXME: not valid ophyd"


class SpecSignal(ItemNameBase):
    """
    SPEC configuration of a single EPICS PV
    """

    def __init__(self, mne: str, nm: str, pvname: str, config_text: str) -> None:
        """data provided by caller"""
        self.raw: str = config_text
        self.mne: str = mne
        self.name: str = nm
        self.pvname: str = pvname
        self.device: Optional[Any] = None
        self.signal_name: str = "EpicsSignal"

        lr: List[str] = config_text.split(sep="=", maxsplit=1)

        def pop_word(line: str, int_result: bool = False) -> Tuple[Union[int, str], str]:
            line = line.strip()
            pos = line.find(" ")
            l: Union[int, str] = line[:pos].strip()
            r: str = line[pos:].strip()
            if int_result:
                l = int(l)  # type: ignore
            return l, r

        self.ctrl, r = pop_word(lr[1])
        self.unit, r = pop_word(r, True)
        self.chan, r = pop_word(r, True)
        self.scale, r = pop_word(r, True)
        self.flags = pop_word(r)[0]

        self.str_keys = "mne config_line name pvname signal_name".split()
        self.cntpar: Dict[str, str] = {}

    def setDevice(self, devices: Dict[str, List[Any]]) -> None:
        if self.ctrl.startswith("EPICS_PV"):
            device_list = devices.get("VM_EPICS_PV")
            if device_list is not None:
                self.device = device_list[self.unit]  # type: ignore
                self.pvname = self.device.prefix  # type: ignore
                self.ophyd_device = "EpicsSignal"
        elif self.ctrl.startswith("NONE"):
            self.ignore = True

    def ophyd_config(self) -> str:
        s: str = f"{self.mne} = {self.signal_name}('{self.pvname}', name='{self.mne}', labels=('detectors',))"
        suffix: Optional[str] = None
        if "misc_par_1" in self.cntpar:
            suffix = self.cntpar.pop("misc_par_1")
            pvname: str = f"{self.device.prefix}{suffix}"  # type: ignore
            s = f"{self.mne} = EpicsSignal('{pvname}', name='{self.mne}', labels=('detectors',))"
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

    def __init__(self, config_text: str) -> None:
        """parse the line from the SPEC config file"""
        self.raw: str = config_text
        # Motor    ctrl steps sign slew base backl accel nada  flags   mne  name
        # MOT002 = EPICS_M2:0/3   2000  1  2000  200   50  125    0 0x003       my  my
        # MOT022 = MAC_MOT:1/0/0   2000  1  2000  200   50  125    0 0x003   suvgap  SlitUpVGap
        lr: List[str] = config_text.split(sep="=", maxsplit=1)
        self.config_line: int = int(lr[0].strip("MOT"))

        def pop_word(line: str, int_result: bool = False) -> Tuple[Union[int, str], str]:
            line = line.strip()
            pos = line.find(" ")
            l: Union[int, str] = line[:pos].strip()
            r: str = line[pos:].strip()
            if int_result:
                l = int(l)  # type: ignore
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
        self.device: Optional[Any] = None
        self.pvname: Optional[str] = None
        self.motpar: Dict[str, str] = {}
        self.mac_parms: Optional[Any] = None
        self.macro_prefix: Optional[str] = None
        self.str_keys = "mne config_line name macro_prefix mac_parms".split()

    def __str__(self) -> str:
        items: List[str] = self.obj_keys_to_list()
        txt: Optional[str] = self.item_name_value("pvname") or self.item_name_value("ctrl")
        if not txt.endswith("=None"):  # type: ignore
            items.append(txt)
        return f"{self.__class__.__name__}({', '.join(items)})"

    def setDevice(self, devices: Dict[str, List[Any]]) -> None:
        if self.ctrl.startswith("EPICS_M2"):
            device_list = devices.get("VM_EPICS_M1")
            if device_list is not None:
                uc_str: str = self.ctrl[len("EPICS_M2:") :]
                unit, chan = list(map(int, uc_str.split("/")))
                self.device = device_list[unit]  # type: ignore
                self.pvname = "{}m{}".format(self.device.prefix, chan)  # type: ignore
        elif self.ctrl.startswith("MAC_MOT"):
            device_list = devices.get("PSE_MAC_MOT")
            if device_list is not None:
                uc_str: str = self.ctrl[len("MAC_MOT:") :]
                parts = list(map(int, uc_str.split("/")))
                unit = parts[0]
                self.mac_parms = parts[1:]
                self.device = device_list[unit]  # type: ignore
                self.macro_prefix = self.device.prefix  # type: ignore
                # TODO: what else?
        elif self.ctrl.startswith("NONE"):
            self.ignore = True

    def ophyd_config(self) -> str:
        s: str = f"{self.mne} = EpicsMotor('{self.pvname}', name='{self.mne}', labels=('motor',))"
        suffix: Optional[str] = None
        if "misc_par_1" in self.motpar:
            # suffix = self.motpar.pop("misc_par_1")
            suffix = self.motpar["misc_par_1"]
            pvname: str = f"{self.device.prefix}{suffix}"  # type: ignore
            s = f"{self.mne} = EpicsMotor('{pvname}', name='{self.mne}', labels=('motor',))"
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

    def __init__(self, config_text: str) -> None:
        """parse the line from the SPEC config file"""
        self.raw: str = config_text
        # # Counter   ctrl unit chan scale flags    mne  name
        # CNT000 = EPICS_SC  0  0 10000000 0x001      sec  seconds

        def pop_word(line: str, int_result: bool = False) -> Tuple[Union[int, str], str]:
            line = line.strip()
            pos = line.find(" ")
            l: Union[int, str] = line[:pos].strip()
            r: str = line[pos:].strip()
            if int_result:
                l = int(l)  # type: ignore
            return l, r

        l, r = pop_word(config_text)
        self.config_line: int = int(l.strip("CNT"))
        _, r = pop_word(r)  # ignore "="
        self.ctrl, r = pop_word(r)
        self.unit, r = pop_word(r, True)
        self.chan, r = pop_word(r, True)
        self.scale, r = pop_word(r, True)
        self.flags, r = pop_word(r)
        self.mne, self.name = pop_word(r)
        self.device: Optional[Any] = None
        self.pvname: Optional[str] = None
        self.reported_pvs: List[str] = []
        self.str_keys = "mne config_line name unit chan".split()
        self.cntpar: Dict[str, str] = {}

    def __str__(self) -> str:
        items: List[str] = self.obj_keys_to_list()
        txt: Optional[str] = self.item_name_value("pvname")
        if txt is not None:
            items.append(txt)
        else:
            items.append(self.item_name_value("ctrl") or "")
        return f"{self.__class__.__name__}({', '.join(items)})"

    def setDevice(self, devices: Dict[str, List[Any]]) -> None:
        if self.ctrl.startswith("EPICS_SC"):
            device_list = devices.get("VM_EPICS_SC")
            if device_list is not None:
                self.device = device_list[self.unit]  # type: ignore
                # scalers are goofy,
                # SPEC uses 0-based numbering,
                # scaler uses 1-based
                self.pvname = "{}.S{}".format(self.device.prefix, self.chan + 1)  # type: ignore
        elif self.ctrl.startswith("EPICS_PV"):
            device_list = devices.get("VM_EPICS_PV")
            if device_list is not None:
                self.device = device_list[self.unit]  # type: ignore
                self.pvname = self.device.prefix  # type: ignore
                self.ophyd_device = "EpicsSignal"
        elif self.ctrl.startswith("NONE"):
            self.ignore = True

    def ophyd_config(self) -> str:
        s: str = f"# counter: {self.mne} = {self}"
        suffix: Optional[str] = None
        if "misc_par_1" in self.cntpar:
            suffix = self.cntpar.pop("misc_par_1")
            if self.device is None:
                self.ignore = True
            else:
                prefix: str = self.device.prefix  # type: ignore
                pvname: str = f"{prefix}{suffix}"
                s = f"{self.mne} = EpicsSignal("
                s += f"'{pvname}', name='{self.mne}', labels=('detectors',)"
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

    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.devices: OrderedDict = OrderedDict()
        self.scalers: List[str] = []
        self.collection: List[Any] = []
        self.unhandled: List[str] = []

    def find_pv_in_collection(self, pv: str) -> Optional[Any]:
        for obj in self.collection:
            if pv == obj.pvname:
                return obj
        return None

    def read_config(self, config_file: Optional[str] = None) -> None:
        self.config_file = config_file or self.config_file
        motor: Optional[Any] = None
        counter: Optional[Any] = None
        with open(self.config_file, "r") as f:
            for line_number, line in enumerate(f.readlines()):
                line = line.strip()

                if line.startswith("#"):
                    continue

                word0: str = line.split(sep="=", maxsplit=1)[0].strip()
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
                        k, v = line[len("CNTPAR:") :].split("=")
                        item.cntpar[k.strip()] = v.strip()
                elif word0.startswith("MOTPAR:"):
                    if motor is not None:
                        k, v = line[len("MOTPAR:") :].split("=")
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
                            scaler = self.find_pv_in_collection(counter.pvname.split(".")[0])
                        if scaler is not None:
                            # clock = scaler.channels.chan01.s
                            fmt: str = "%s = %s.channels.chan%02d.s"
                            reassignment: str = fmt % (
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


def create_ophyd_setup(spec_config: SpecConfig) -> None:
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
            if hasattr(device, "signal_name") and device.signal_name == "ScalerCH":
                print(f"{device.name}.select_channels(None)")
        else:
            print(device)


def get_apstools_version() -> str:
    """Get the version string from the parent package."""
    from .. import __version__

    return __version__


def get_options() -> "argparse.Namespace":
    """Handle command line arguments."""
    import argparse
    import pathlib
    import sys

    version: str = get_apstools_version()

    parser = argparse.ArgumentParser(
        prog=pathlib.Path(sys.argv[0]).name,
        description=__doc__.strip().splitlines()[0],
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="print version number and exit",
        version=version,
    )

    parser.add_argument("configFileName", type=str, help="SPEC config file name")

    return parser.parse_args()


def main() -> None:
    args = get_options()
    spec_cfg = SpecConfig(args.configFileName)
    spec_cfg.read_config()
    create_ophyd_setup(spec_cfg)


if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------