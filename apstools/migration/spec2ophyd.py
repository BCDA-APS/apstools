#!/usr/bin/env python

"""
read SPEC config file and convert to ophyd setup commands

output of ophyd configuration to stdout
"""


from collections import OrderedDict
import re


CONFIG_FILE = 'config-8idi'
KNOWN_DEVICES = "PSE_MAC_MOT VM_EPICS_M1 VM_EPICS_SC".split()


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
    
    def __str__(self):
        fmt = "SpecDeviceBase(index={}, name={}, prefix={}, num_channels={})"
        return fmt.format(
            self.index,
            self.name,
            self.prefix,
            self.num_channels
            )


class ItemNameBase(object):
    def item_name_value(self, item):
        if hasattr(self, item):
            return f"{item}={self.__getattribute__(item)}"


class SpecMotor(ItemNameBase):
    """
    SPEC configuration of a motor channel
    """
    
    def __init__(self, config_text):
        """parse the line from the SPEC config file"""
        # Motor    cntrl steps sign slew base backl accel nada  flags   mne  name
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
        
        self.cntrl, r = pop_word(lr[1])
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
            items.append(self.item_name_value("cntrl"))
        return "SpecMotor({})".format(", ".join(items))
    
    def setDevice(self, devices):
        if self.cntrl.startswith("EPICS_M2"):
            device_list = devices.get("VM_EPICS_M1")
            if device_list is not None:
                uc_str = self.cntrl[len("EPICS_M2:"):]
                unit, chan = list(map(int, uc_str.split("/")))
                self.device = device_list[unit]
                self.pvname = "{}m{}".format(self.device.prefix, chan)


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

    def __str__(self):
        items = [self.item_name_value(k) for k in "index mne name".split()]
        txt = self.item_name_value("pvname")
        if txt is not None:
            items.append(txt)
        else:
            items.append(self.item_name_value("ctrl"))
        return "SpecCounter({})".format(", ".join(items))
    
    def setDevice(self, devices):
        if self.ctrl.startswith("EPICS_SC"):
            device_list = devices.get("VM_EPICS_SC")
            if device_list is not None:
                self.device = device_list[self.unit]
                # scalers are goofy, SPEC uses 0-based numbering, scaler uses 1-based
                self.pvname = "{}.S{}".format(self.device.prefix, self.chan+1)


class SpecConfig(object):
    """
    SPEC configuration
    """
    
    def __init__(self, config_file):
        self.config_file = config_file or CONFIG_FILE
        self.devices = OrderedDict()
        self.motors = OrderedDict()
        self.counters = OrderedDict()
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
                    self.counters[counter.mne] = counter
                elif re.match("MOT\d*", line) is not None:
                    motor = SpecMotor(line)
                    motor.setDevice(self.devices)
                    self.motors[motor.mne] = motor
                else:
                    self.unhandled.append(line)


def create_ophyd_setup(spec_config):
    # ophyd configures the counters by device, not by channel
    device_list = spec_config.devices.get("VM_EPICS_SC")
    if device_list is not None:
        import_shown = False
        for device in device_list:
            mne = "scaler{}".format(device.index)
            if not import_shown:
                print("from ophyd.scaler import ScalerCH")
                import_shown = True
            print(f"{mne} = ScalerCH('{device.prefix}', name='{mne}')")
            chans = []
            for counter in spec_config.counters.values():
                if counter.device == device:
                    key = "chan%02d" % (counter.chan+1)
                    print(f"# {key} : {counter.mne} ({counter.name})")
                    chans.append(key)
            if len(chans) > 0:
                print(f"{mne}.channels.read_attrs = {chans}")

    mne_list = []
    for mne, motor in sorted(spec_config.motors.items()):
        if motor.pvname is not None:
            mne = mne.replace(".", "_")
            mne_list.append(mne)
            msg = f"{mne} = EpicsMotor('{motor.pvname}', name='{mne}')"
            comments = []
            if motor.mne != motor.name:
                comments.append(f"{motor.name}")
            if len(motor.motpar) > 0:
                comments.append(f" TODO: {', '.join(motor.motpar)}")
            if len(comments) > 0:
                msg += f"  # {(' '.join(comments)).strip()}"
            print(msg)



def main():
    spec_cfg = SpecConfig(CONFIG_FILE)
    spec_cfg.read_config()
    create_ophyd_setup(spec_cfg)


if __name__ == "__main__":
    main()
