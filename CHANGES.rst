..
  This file describes user-visible changes between the versions.

Change History
##############

:1.1.16:  expected by *tba* : 

    * `#269 <https://github.com/prjemian/spec2nexus/issues/269>`_
       bug: shutter does not move when expected
    * `#268 <https://github.com/prjemian/spec2nexus/issues/268>`_
       add `redefine_motor_position()` plan
    * `#267 <https://github.com/prjemian/spec2nexus/issues/267>`_
       remove `lineup()` plan for now
    * `#266 <https://github.com/prjemian/spec2nexus/issues/266>`_
       bug fix for #265
    * `#265 <https://github.com/prjemian/spec2nexus/issues/265>`_
       refactor of #264
    * `#264 <https://github.com/prjemian/spec2nexus/issues/264>`_
       Limit number of traces shown on a plot - use a FIFO
    * `#263 <https://github.com/prjemian/spec2nexus/issues/263>`_
       `device_read2table()` should print unless optioned False
    * `#262 <https://github.com/prjemian/spec2nexus/issues/262>`_
       add `lineup()` plan (from APS 8-ID-I XPCS)

:1.1.15:  expected by *2019-11-21* : bug fixes, adds asyn record support

    * `#259 <https://github.com/prjemian/spec2nexus/issues/259>`_
       resolve AssertionError from setup_lorentzian_swait
    * `#258 <https://github.com/prjemian/spec2nexus/issues/258>`_
       swait record does not units, some other fields
    * `#255 <https://github.com/prjemian/spec2nexus/issues/255>`_
       plans: resolve indentation error
    * `#254 <https://github.com/prjemian/spec2nexus/issues/254>`_
       add computed APS cycle as signal
    * `#252 <https://github.com/prjemian/spec2nexus/issues/252>`_
       synApps: add asyn record support

:1.1.14:  released *2019-09-03* : bug fixes, more synApps support

    * `#246 <https://github.com/prjemian/spec2nexus/issues/246>`_
       synApps: shorten name from synApps_ophyd
    * `#245 <https://github.com/prjemian/spec2nexus/issues/245>`_
       swait & calcout: change from *EpicsMotor* to any *EpicsSignal*
    * `#240 <https://github.com/prjemian/spec2nexus/issues/240>`_
       swait: refactor swait record & userCalc support
    * `#239 <https://github.com/prjemian/spec2nexus/issues/239>`_
       transform: add support for transform record
    * `#238 <https://github.com/prjemian/spec2nexus/issues/238>`_
       calcout: add support for calcout record & userCalcOuts
    * `#237 <https://github.com/prjemian/spec2nexus/issues/237>`_
       epid: add support for epid record
    * `#234 <https://github.com/prjemian/spec2nexus/issues/234>`_
       utils: replicate the `unix()` command
    * `#230 <https://github.com/prjemian/spec2nexus/issues/230>`_
       signals: resolve TypeError

:1.1.13:  released *2019-08-15* : enhancements, bug fix, rename

    * `#226 <https://github.com/prjemian/spec2nexus/issues/226>`_
       writer: unit tests for empty #O0 & P0 control lines
    * `#224 <https://github.com/prjemian/spec2nexus/issues/224>`_
       rename: list_recent_scans --> listscans
    * `#222 <https://github.com/prjemian/spec2nexus/issues/222>`_
       writer: add empty #O0 and #P0 lines
    * `#220 <https://github.com/prjemian/spec2nexus/issues/220>`_
       ProcessController: bug fix - raised TypeError

:1.1.12:  released *2019-08-05* : bug fixes & updates

    * `#219 <https://github.com/BCDA-APS/apstools/issues/219>`_
       ``ProcessController``: bug fixes
    * `#218 <https://github.com/BCDA-APS/apstools/issues/218>`_
       ``replay()``: sort chronological by default
    * `#216 <https://github.com/BCDA-APS/apstools/issues/216>`_
       ``replay()``: fails when not list

:1.1.11:  released *2019-07-31* : updates & new utility

    * `#214 <https://github.com/BCDA-APS/apstools/issues/214>`_
       new: ``apstools.utils.APS_utils.replay()``
    * `#213 <https://github.com/BCDA-APS/apstools/issues/213>`_
       ``list_recent_scans`` show ``exit_status`` 
    * `#212 <https://github.com/BCDA-APS/apstools/issues/212>`_
       ``list_recent_scans`` show reconstructed scan command

:1.1.10:  released *2019-07-30* : updates & bug fix

    * `#211 <https://github.com/BCDA-APS/apstools/issues/211>`_
       ``devices`` calls to superclass ``__init__()``
    * `#209 <https://github.com/BCDA-APS/apstools/issues/209>`_
       ``devices`` call to superclass ``__init__()``
    * `#207 <https://github.com/BCDA-APS/apstools/issues/207>`_
       ``show_ophyd_symbols`` also shows labels
    * `#206 <https://github.com/BCDA-APS/apstools/issues/206>`_
       new: ``apstools.utils.APS_utils.list_recent_scans()``
    * `#205 <https://github.com/BCDA-APS/apstools/issues/205>`_
       ``show_ophyd_symbols`` uses ipython shell's namespace
    * `#202 <https://github.com/BCDA-APS/apstools/issues/202>`_
       add ``labels`` attribute to enable ``wa`` and ``ct`` magic commands

:1.1.9:  released *2019-07-28* : updates & bug fix

    * `#203 <https://github.com/BCDA-APS/apstools/issues/203>`_
       `SpecWriterCallback`: `#N` is number of data columns
    * `#199 <https://github.com/BCDA-APS/apstools/issues/199>`_
       `spec2ophyd` handle CNTPAR:read_misc_1

:1.1.8:  released *2019-07-25* : updates

    * `#196 <https://github.com/BCDA-APS/apstools/issues/196>`_
       `spec2ophyd` handle MOTPAR:read_misc_1
    * `#194 <https://github.com/BCDA-APS/apstools/issues/194>`_
       new ``show_ophyd_symbols`` shows table of global ophyd `Signal`s and `Device`s
    * `#193 <https://github.com/BCDA-APS/apstools/issues/193>`_
       `spec2ophyd` ignore None items in SPEC config file
    * `#192 <https://github.com/BCDA-APS/apstools/issues/192>`_
       `spec2ophyd` handles VM_EPICS_PV in SPEC config file
    * `#191 <https://github.com/BCDA-APS/apstools/issues/191>`_
       `spec2ophyd` handles PSE_MAC_MOT in SPEC config file
    * `#190 <https://github.com/BCDA-APS/apstools/issues/190>`_
       `spec2ophyd` handles MOTPAR in SPEC config file

:1.1.7:  released 2019-07-04

    * `DEPRECATION <https://github.com/BCDA-APS/apstools/issues/90#issuecomment-483405890>`_
	   `apstools.plans.run_blocker_in_plan()` will be removed by 2019-12-31.
	   Do not write blocking code in bluesky plans.
    * Dropped python 3.5 from supported versions
    * `#175 <https://github.com/BCDA-APS/apstools/issues/175>`_
       move `plans.run_in_thread()` to `utils.run_in_thread()`
    * `#168 <https://github.com/BCDA-APS/apstools/issues/168>`_
       new `spec2ophyd`  migrates SPEC config file to ophyd setup
    * `#166 <https://github.com/BCDA-APS/apstools/issues/166>`_
       `device_read2table()`: format `device.read()` results in a pyRestTable.Table
    * `#161 <https://github.com/BCDA-APS/apstools/issues/161>`_
       `addDeviceDataAsStream()`: add Device as named document stream event
    * `#159 <https://github.com/BCDA-APS/apstools/issues/159>`_
       convert xlrd.XLRDError into apstools.utils.ExcelReadError
    * `#158 <https://github.com/BCDA-APS/apstools/issues/158>`_
       new ``run_command_file()`` runs a command list from text file or Excel spreadsheet

:1.1.6:  released *2019-05-26*

    * `#156 <https://github.com/BCDA-APS/apstools/issues/156>`_
       add ProcessController Device
    * `#153 <https://github.com/BCDA-APS/apstools/issues/153>`_
       print dictionary contents as table
    * `#151 <https://github.com/BCDA-APS/apstools/issues/151>`_
       EpicsMotor support for enable/disable
    * `#148 <https://github.com/BCDA-APS/apstools/issues/148>`_
       more LGTM recommendations
    * `#146 <https://github.com/BCDA-APS/apstools/issues/146>`_
       LGTM code review recommendations
    * `#143 <https://github.com/BCDA-APS/apstools/issues/143>`_
       filewriter fails to raise IOError
    * `#141 <https://github.com/BCDA-APS/apstools/issues/141>`_
       ValueError during tune()

:1.1.5:  released *2019-05-14*

    * `#135 <https://github.com/BCDA-APS/apstools/issues/135>`_
       add refresh button to snapshot GUI

:1.1.4:  released *2019-05-14*

    * `#140 <https://github.com/BCDA-APS/apstools/issues/140>`_
       `event-model` needs at least v1.8.0
    * `#139 <https://github.com/BCDA-APS/apstools/issues/139>`_
       `ValueError` in `plans.TuneAxis.tune._scan `

:1.1.3:  released *2019-05-10*

    * adds packaging dependence on event-model
    * `#137 <https://github.com/BCDA-APS/apstools/issues/137>`_
       adds `utils.json_export()` and `utils.json_import()`

:1.1.1:  released *2019-05-09*

    * adds packaging dependence on spec2nexus
    * `#136 <https://github.com/BCDA-APS/apstools/issues/136>`_
       get json document stream(s)
    * `#134 <https://github.com/BCDA-APS/apstools/issues/134>`_
       add build on travis-ci with py3.7
    * `#130 <https://github.com/BCDA-APS/apstools/issues/130>`_
       fix conda recipe and pip dependencies (thanks to Maksim Rakitin!)
    * `#128 <https://github.com/BCDA-APS/apstools/issues/128>`_
       SpecWriterCallback.newfile() problem with scan_id = 0 
    * `#127 <https://github.com/BCDA-APS/apstools/issues/127>`_
       fixed: KeyError from SPEC filewriter
    * `#126 <https://github.com/BCDA-APS/apstools/issues/126>`_
       add uid to metadata
    * `#125 <https://github.com/BCDA-APS/apstools/issues/125>`_
       SPEC filewriter scan numbering when "new" data file exists
    * `#124 <https://github.com/BCDA-APS/apstools/issues/124>`_
       fixed: utils.trim_string_for_EPICS() trimmed string too long
    * `#100 <https://github.com/BCDA-APS/apstools/issues/100>`_
       fixed: SPEC file data columns in wrong places

:1.1.0:  released *2019.04.16*

    * change release numbering to Semantic Versioning (remove all previous tags and releases)
    * batch scans using Excel spreadsheets
    * bluesky_snapshot_viewer and bluesky_snapshot
    * conda package available

:2019.0321.1:

    * tag only: #103

:2019.0321.0:

    * tag only: #103

:2019.0301.0:

    * [release notes](https://github.com/BCDA-APS/apstools/wiki/release-notes-2019.0301.0)

:2019.0227.0:

    * tag only: #100, #101, #102

:2019.0225.0:

    * tag only: #99

:2019.0223.0:

    * tag only: #97, #98, additions from USAXS, add specfile comments any time, example databroker -> SPEC file

:2019.0220.0:

    * tag only, add a simple Tkinter-based snapshot viewer

:2019.0219.3:

    * tag only, bring code from USAXS, standardize shutter support

:2019.0128.0:

    * rename to *apstools*

:2019.0103.0:

    * first production release (as *APS_BlueSky_tools*)
