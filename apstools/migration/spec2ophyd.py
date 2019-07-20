#!/usr/bin/env python

"""
read SPEC config file and convert to ophyd setup commands

output of ophyd configuration to stdout
"""


from collections import OrderedDict
import re


CONFIG_FILE = 'config-8idi'
KNOWN_DEVICES = "PSE_MAC_MOT VM_EPICS_M1 VM_EPICS_PV VM_EPICS_SC".split()


class SpecDeviceBase(object):
    """
    SPEC configuration of a device, such as a multi-channel motor controller
    """
    
    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
        # VM_EPICS_M1    = 9idcLAX:m58:c0: 8
        nm, args = config_text.split("=")
        self.name = nm.strip()
        prefix, num_channels = args.split()
        self.prefix = prefix
        self.index = None
        self.num_channels = int(num_channels)
        self.ophyd_device = None
    
    def __str__(self):
        items = [f"{k}={self.__getattribute__(k)}" for k in "index name prefix num_channels".split()]
        return f"{self.__class__.__name__}({', '.join(items)})"


class ItemNameBase(object):
    def item_name_value(self, item):
        if hasattr(self, item):
            return f"{item}={self.__getattribute__(item)}"
    
    def ophyd_config(self):
        return f"{self.mne} = {self} # FIXME: not valid ophyd"


class SpecSignal(ItemNameBase):
    """
    SPEC configuration of a single EPICS PV
    """
    
    def __init__(self, mne, nm, pvname):
        """data provided by caller"""
        self.mne = mne
        self.name = nm
        self.pvname = pvname
        self.signal_name = "EpicsSignal"

    def __str__(self):
        items = [f"{k}={self.__getattribute__(k)}" for k in "mne name pvname signal_name".split()]
        return f"{self.__class__.__name__}({', '.join(items)})"
    
    def ophyd_config(self):
        s = f"{self.mne} = {self.signal_name}('{self.pvname}', name='{self.mne}')"
        if self.mne != self.name:
            s += f"  # {self.name}"
        return s


class SpecMotor(ItemNameBase):
    """
    SPEC configuration of a motor channel
    """
    
    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
        # Motor    ctrl steps sign slew base backl accel nada  flags   mne  name
        # MOT002 = EPICS_M2:0/3   2000  1  2000  200   50  125    0 0x003       my  my
        lr = config_text.split(sep="=", maxsplit=1)
        self.index = int(lr[0].strip("MOT"))
        
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
        self.motpar = []
    
    def __str__(self):
        items = [self.item_name_value(k) for k in "index mne name".split()]
        txt = self.item_name_value("pvname")
        if txt is not None:
            items.append(txt)
        else:
            items.append(self.item_name_value("ctrl"))
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
            pass        # TODO:
        elif self.ctrl.startswith("NONE"):
            pass        # TODO:
    
    def ophyd_config(self):
        s = f"{self.mne} = EpicsMotor('{self.pvname}', name='{self.mne}')"
        if self.mne != self.name:
            s += f"  # {self.name}"
        if len(self.motpar) > 0:
            s += f" # {', '.join(self.motpar)}"
        return s



class SpecCounter(ItemNameBase):
    """
    SPEC configuration of a counter channel
    """
    
    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
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
        self.index = int(l.strip("CNT"))
        l, r = pop_word(r)      # ignore "="
        self.ctrl, r = pop_word(r)
        self.unit, r = pop_word(r, True)
        self.chan, r = pop_word(r, True)
        self.scale, r = pop_word(r, True)
        self.flags, r = pop_word(r)
        self.mne, self.name = pop_word(r)
        self.device = None
        self.pvname = None
        self.reported_pvs = []

    def __str__(self):
        items = [self.item_name_value(k) for k in "mne name unit chan".split()]
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
                # scalers are goofy, SPEC uses 0-based numbering, scaler uses 1-based
                self.pvname = "{}.S{}".format(self.device.prefix, self.chan+1)
        elif self.ctrl.startswith("EPICS_PV"):
            device_list = devices.get("VM_EPICS_PV")
            if device_list is not None:
                self.device = device_list[self.unit]
                self.pvname = self.device.prefix
                self.ophyd_device = "EpicsSignal"
        elif self.ctrl.startswith("NONE"):
            pass        # TODO:
    
    def ophyd_config(self):
        return f"# counter: {self.mne} = {self}"


class SpecConfig(object):
    """
    SPEC configuration
    """
    
    def __init__(self, config_file):
        self.config_file = config_file or CONFIG_FILE
        self.devices = OrderedDict()
        self.motors = OrderedDict()
        self.counters = OrderedDict()
        self.signals = OrderedDict()
        self.scalers = []
        self.collection = []
        self.unhandled = []
    
    def read_config(self, config_file=None):
        self.config_file = config_file or self.config_file
        motor = None
        with open(self.config_file, 'r') as f:
            for line in f.readlines():
                line = line.strip()

                if line.startswith("#"):
                    continue

                word0 = line.split(sep="=", maxsplit=1)[0].strip()
                if word0 in KNOWN_DEVICES:
                    device = SpecDeviceBase(line)
                    if device.name not in self.devices:
                        self.devices[device.name] = []
                    # 0-based numbering
                    device.index = len(self.devices[device.name])
                    self.devices[device.name].append(device)
                elif word0.startswith("MOTPAR:"):
                    if motor is not None:
                        motor.motpar.append(line[len("MOTPAR:"):])
                elif re.match("CNT\d*", line) is not None:
                    counter = SpecCounter(line)
                    counter.setDevice(self.devices)
                    if counter.ctrl == "EPICS_PV":
                        signal = SpecSignal(counter.mne, counter.name, counter.pvname)
                        self.signals[signal.mne] = signal
                        self.collection.append(signal)
                    else:
                        if counter.pvname is not None:
                            pvname = counter.pvname.split(".")[0]
                            if pvname not in self.scalers:
                                mne = pvname.lower().split(":")[-1]
                                scaler = SpecSignal(mne, mne, pvname)
                                scaler.signal_name = "ScalerCH"
                                self.scalers.append(pvname)
                                self.collection.append(scaler)
                        
                        self.counters[counter.mne] = counter
                        self.collection.append(counter)
                elif re.match("MOT\d*", line) is not None:
                    motor = SpecMotor(line)
                    motor.setDevice(self.devices)
                    self.motors[motor.mne] = motor
                    self.collection.append(motor)
                else:
                    self.unhandled.append(line)


def create_ophyd_setup(spec_config):
    for device in spec_config.collection:
        print(f"{device.ophyd_config()}")


def main():
    spec_cfg = SpecConfig(CONFIG_FILE)
    spec_cfg.read_config()
    create_ophyd_setup(spec_cfg)


if __name__ == "__main__":
    main()
