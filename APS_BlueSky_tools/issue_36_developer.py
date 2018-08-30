
from ophyd.scaler import ScalerCH
from ophyd import EpicsMotor, Signal, Component, Device
from APS_BlueSky_tools.devices import use_EPICS_scaler_channels, AxisTunerMixin
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback

from APS_BlueSky_tools.plans import TuneAxis

import datetime
from bluesky.callbacks.fitting import PeakStats
from bluesky import preprocessors as bpp
from bluesky import plan_stubs as bps
from bluesky import plan_patterns as bpat

from bluesky.utils import ts_msg_hook


RE = RunEngine({})
RE.subscribe(BestEffortCallback())

m1 = EpicsMotor("gov:m1", name="m1")
scaler = ScalerCH("gov:scaler1", name="scaler")
scaler.match_names()
use_EPICS_scaler_channels(scaler)
for k, v in scaler.read().items():
    print(k, v)
print("scaler.preset_time", scaler.preset_time.value)
RE.msg_hook = ts_msg_hook


class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
    pass

class MyTuneAxis(TuneAxis):
    
    # override the default tune() method

    def tune(self, width=None, num=None, md=None):
        """
        BlueSky plan to execute one pass through the current scan range
        
        Scan self.axis centered about current position from
        ``-width/2`` to ``+width/2`` with ``num`` observations.
        If a peak was detected (default check is that max >= 4*min), 
        then set ``self.tune_ok = True``.

        PARAMETERS
    
        width : float
            width of the tuning scan in the units of ``self.axis``
            Default value in ``self.width`` (initially 1)
        num : int
            number of steps
            Default value in ``self.num`` (initially 10)
        md : dict, optional
            metadata
        """
        width = width or self.width
        num = num or self.num
        
        if self.peak_choice not in self._peak_choices_:
            msg = "peak_choice must be one of {}, geave {}"
            msg = msg.format(self._peak_choices_, self.peak_choice)
            raise ValueError(msg)

        initial_position = self.axis.position
        start = initial_position - width/2
        finish = initial_position + width/2
        self.tune_ok = False

        tune_md = dict(
            width = width,
            initial_position = self.axis.position,
            time_iso8601 = str(datetime.datetime.now()),
            )
        _md = {'tune_md': tune_md,
               'plan_name': self.__class__.__name__ + '.tune',
               'tune_parameters': dict(
                    num = num,
                    width = width,
                    initial_position = self.axis.position,
                    peak_choice = self.peak_choice,
                    x_axis = self.axis.name,
                    y_axis = self.signal_name,
                   )
               }
        _md.update(md or {})
        if "pass_max" not in _md:
            self.stats = []
        self.peaks = PeakStats(x=self.axis.name, y=self.signal_name)
        
        def tune_scan(detectors, axis, start, finish, num, _md):
            """run the tune scan"""
            cycler = bpat.inner_product(num, (axis, start, finish))
            
            signal_list = list(detectors)
            signal_list += [axis,]

            def inner_scan_nd():
                for step in list(cycler):
                    pos = list(step.values())[0]    # TODO: simplify?
                    yield from bps.mv(axis, pos)
                    yield from bps.trigger_and_read(signal_list)

            return (yield from inner_scan_nd())
            
        class Results(Device):
            """because bps.read() needs a Device or a Signal)"""
            x = Component(Signal, name="x")
            y = Component(Signal, name="y")
            cen = Component(Signal, name="cen")
            com = Component(Signal, name="com")
            fwhm = Component(Signal, name="fwhm")
            min = Component(Signal, name="min")
            max = Component(Signal, name="max")
            crossings = Component(Signal, name="crossings")
            read_attrs = "x y cen com fwhm min max crossings".split()

        def add_results_stream(stream_name="tune_PeakStats"):
            """add a stream with the tuning results (from PeakStats)"""
            tune_PeakStats = Results(
                name="tune_PeakStats",
                read_attrs=Results.read_attrs,
                )
            tune_PeakStats.hints["fields"] = ["tune_PeakStats",]
            for key in tune_PeakStats.read_attrs:
                getattr(tune_PeakStats, key).put(getattr(self.peaks, key))
            yield from bps.create(name=stream_name)
            yield from bps.read(tune_PeakStats)
            yield from bps.save()
        
        @bpp.subs_decorator(self.peaks)
        def _scan():
            yield from bps.open_run()
            yield from tune_scan(
                self.signals, self.axis, start, finish, num, _md)
            
            final_position = initial_position
            if self.peak_detected():
                self.tune_ok = True
                if self.peak_choice == "cen":
                    final_position = self.peaks.cen
                elif self.peak_choice == "com":
                    final_position = self.peaks.com
                else:
                    final_position = None
                self.center = final_position

            # add stream with results
            yield from add_results_stream()
            
            yield from bps.mv(self.axis, final_position)
            self.stats.append(self.peaks)
            yield from bps.close_run()
    
        return (yield from _scan())


def myCallback(key, doc):
    if key in ("start", "descriptor", "event", "stop"):
        print("-"*20)
        for k, v in doc.items():
            print("\t", key, k, v)


m1 = TunableEpicsMotor("gov:m1", name="m1")
m1.tuner = MyTuneAxis([scaler], m1, signal_name="scint")
m1.tuner.width = 0.02
m1.tuner.num = 21


#RE(bp.count([scaler]))
#RE(bp.scan([scaler], m1, -1, 1, 5))
RE(m1.tune(), myCallback)
