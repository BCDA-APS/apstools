..
  This file describes user-visible changes between the versions.

Change History
##############

:1.1.7:  released *tba* (on or before 2019-07-01)

	.. note:: DEPRECATION: 
	   `apstools.plans.run_blocker_in_plan()` will be removed by 2019-12-31.
	   `Do not write blocking code in bluesky plans.
	   <https://github.com/BCDA-APS/apstools/issues/90#issuecomment-483405890>`_

    * `#175 <https://github.com/BCDA-APS/apstools/issues/175>`_
       move `plans.run_in_thread()` to `utils.run_in_thread()`
    * `#168 <https://github.com/BCDA-APS/apstools/issues/168>`_
       add module to migrate SPEC config file to ophyd setup
    * `#166 <https://github.com/BCDA-APS/apstools/issues/166>`_
       `device_read2table()`: format `device.read()` results in a pyRestTable.Table
    * `#161 <https://github.com/BCDA-APS/apstools/issues/161>`_
       `addDeviceDataAsStream()`: add Device as named document stream event
    * `#159 <https://github.com/BCDA-APS/apstools/issues/159>`_
       convert xlrd.XLRDError into apstools.utils.ExcelReadError
    * `#158 <https://github.com/BCDA-APS/apstools/issues/158>`_
       run a command list from text file or Excel spreadsheet

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
