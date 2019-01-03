.. _bluesky_snapshot:

bluesky_snapshot
----------------

Take a snapshot of a list of EPICS PVs and record it in the databroker.
Retrieve (and display) that snapshot later using 
``APS_BlueSky_tools.callbacks.SnapshotReport``.

.. TODO: example how to read would be useful

Example - command line
++++++++++++++++++++++

Before using the command-line interface, find out what
the *bluesky_snapshot* expects::

	$ bluesky_snapshot -h
	usage: bluesky_snapshot [-h] [-b BROKER_CONFIG] [-m METADATA]
	                        EPICS_PV [EPICS_PV ...]
	
	record a snapshot of some PVs using Bluesky, ophyd, and databroker
	
	positional arguments:
	  EPICS_PV          EPICS PV name
	
	optional arguments:
	  -h, --help        show this help message and exit
	  -b BROKER_CONFIG  YAML configuration for databroker
	  -m METADATA       additional metadata, enclose in quotes, such as -m
	                    "purpose=just tuned, situation=routine"

The help does not tell you that the default for BROKER_CONFIG is 
"mongodb_config", a YAML file in one of the default locations where 
the databroker expects to find it.  That's what we have.

We want to snapshot just a couple PVs to show basic use.  
Here are their current values::

	$ caget otz:IOC_CPU_LOAD otz:SYS_CPU_LOAD
	otz:IOC_CPU_LOAD               0.100096
	otz:SYS_CPU_LOAD               8.25789

Here's the snapshot (we'll also set a metadata that says this is an example)::

	$ bluesky_snapshot otz:IOC_CPU_LOAD otz:SYS_CPU_LOAD -m "purpose=example"

	========================================
	snapshot: 2018-12-20 18:18:27.052009
	========================================
	
	hints: {}
	iso8601: 2018-12-20 18:18:27.052009
	plan_description: archive snapshot of ophyd Signals (usually EPICS PVs)
	plan_name: snapshot
	plan_type: generator
	purpose: example
	scan_id: 1
	software_versions: {'python': '3.6.2 |Continuum Analytics, Inc.| (default, Jul 20 2017, 13:51:32) \n[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)]', 'PyEpics': '3.3.1', 'bluesky': '1.4.1', 'ophyd': '1.3.0', 'databroker': '0.11.3', 'APS_Bluesky_Tools': '0.0.37'}
	time: 1545351507.0527153
	uid: ab270806-0697-4056-ba44-80f7b462bedc
	
	========================== ====== ================ ===================
	timestamp                  source name             value              
	========================== ====== ================ ===================
	2018-12-20 18:18:17.109931 PV     otz:IOC_CPU_LOAD 0.10009559468607492
	2018-12-20 18:18:17.109927 PV     otz:SYS_CPU_LOAD 10.935451151721377 
	========================== ====== ================ ===================
	
	exit_status: success
	num_events: {'primary': 1}
	run_start: ab270806-0697-4056-ba44-80f7b462bedc
	time: 1545351507.0696447
	uid: a0b5b4ff-d9a7-47ce-ace7-1bba818da77b

We have a second IOC (*gov*) that has the same PVs.  Let's get them, too.::

	$ bluesky_snapshot {gov,otz}:{IOC,SYS}_CPU_LOAD -m "purpose=this is an example, example=example 2"

	========================================
	snapshot: 2018-12-20 18:21:53.371995
	========================================
	
	example: example 2
	hints: {}
	iso8601: 2018-12-20 18:21:53.371995
	plan_description: archive snapshot of ophyd Signals (usually EPICS PVs)
	plan_name: snapshot
	plan_type: generator
	purpose: this is an example
	scan_id: 1
	software_versions: {'python': '3.6.2 |Continuum Analytics, Inc.| (default, Jul 20 2017, 13:51:32) \n[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)]', 'PyEpics': '3.3.1', 'bluesky': '1.4.1', 'ophyd': '1.3.0', 'databroker': '0.11.3', 'APS_Bluesky_Tools': '0.0.37'}
	time: 1545351713.3727024
	uid: d5e15ba3-0393-4df3-8217-1b72d82b5cf9
	
	========================== ====== ================ ===================
	timestamp                  source name             value              
	========================== ====== ================ ===================
	2018-12-20 18:21:45.488033 PV     gov:IOC_CPU_LOAD 0.22522293126578166
	2018-12-20 18:21:45.488035 PV     gov:SYS_CPU_LOAD 10.335244804189122 
	2018-12-20 18:21:46.910976 PV     otz:IOC_CPU_LOAD 0.10009633509509736
	2018-12-20 18:21:46.910973 PV     otz:SYS_CPU_LOAD 11.360899731293234 
	========================== ====== ================ ===================
	
	exit_status: success
	num_events: {'primary': 1}
	run_start: d5e15ba3-0393-4df3-8217-1b72d82b5cf9
	time: 1545351713.3957422
	uid: e033cd99-dcac-4b56-848c-62eede1e4d77

You can log text and arrays, too.::

	$ bluesky_snapshot {gov,otz}:{iso8601,HOSTNAME,{IOC,SYS}_CPU_LOAD} compress \
	  -m "purpose=this is an example, example=example 2, look=can snapshot text and arrays too, note=no commas in metadata"

	========================================
	snapshot: 2018-12-20 18:28:28.825551
	========================================
	
	example: example 2
	hints: {}
	iso8601: 2018-12-20 18:28:28.825551
	look: can snapshot text and arrays too
	note: no commas in metadata
	plan_description: archive snapshot of ophyd Signals (usually EPICS PVs)
	plan_name: snapshot
	plan_type: generator
	purpose: this is an example
	scan_id: 1
	software_versions: {'python': '3.6.2 |Continuum Analytics, Inc.| (default, Jul 20 2017, 13:51:32) \n[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)]', 'PyEpics': '3.3.1', 'bluesky': '1.4.1', 'ophyd': '1.3.0', 'databroker': '0.11.3', 'APS_Bluesky_Tools': '0.0.37'}
	time: 1545352108.8262713
	uid: 7e77708e-9169-45ab-b2b6-4e31534d980a
	
	========================== ====== ================ ===================
	timestamp                  source name             value              
	========================== ====== ================ ===================
	2018-12-20 18:24:34.220028 PV     compress         [0.1, 0.2, 0.3]    
	2018-12-13 14:49:53.121188 PV     gov:HOSTNAME     otz.aps.anl.gov    
	2018-12-20 18:28:25.093941 PV     gov:IOC_CPU_LOAD 0.1501490058473918 
	2018-12-20 18:28:25.093943 PV     gov:SYS_CPU_LOAD 10.360270546421546 
	2018-12-20 18:28:28.817630 PV     gov:iso8601      2018-12-20T18:28:28
	2018-12-13 14:49:53.135016 PV     otz:HOSTNAME     otz.aps.anl.gov    
	2018-12-20 18:28:26.525208 PV     otz:IOC_CPU_LOAD 0.10009727705620367
	2018-12-20 18:28:26.525190 PV     otz:SYS_CPU_LOAD 12.937574161543873 
	2018-12-20 18:28:28.830285 PV     otz:iso8601      2018-12-20T18:28:28
	========================== ====== ================ ===================
	
	exit_status: success
	num_events: {'primary': 1}
	run_start: 7e77708e-9169-45ab-b2b6-4e31534d980a
	time: 1545352108.8656788
	uid: 0de0ec62-504e-4dbc-ad08-2507d4ed44f9
	


Source code documentation
+++++++++++++++++++++++++


.. automodule:: APS_BlueSky_tools.snapshot
    :members: 
