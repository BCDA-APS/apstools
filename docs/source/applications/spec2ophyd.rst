

.. index:: !spec2ophyd

.. _spec2ophyd:

spec2ophyd
----------

Read SPEC config file and convert to ophyd setup commands.

This is a tool to help migration from SPEC to bluesky.  It reads
a SPEC configuration file named `config` 
*in the present working directory* 
and converts the lines it recognizes into ophyd
commands which create ophyd objects.  These commands are printed
to `sys.stdout`.  The output can be copied into a setup file for ophyd.

Example
++++++++++++++++++++++

SPEC config file
~~~~~~~~~~~~~~~~

.. code-block:: text

	# ID @(#)getinfo.c	6.6  01/15/16 CSS
	# Device nodes
	SDEV_0	 = /dev/ttyUSB0 19200 raw
	SDEV_1	 = /dev/ttyUSB2 19200 raw
	#SDEV_2	 = /dev/ttyUSB2 19200 raw
	VM_EPICS_M1	 = 9idcLAX:m58:c0: 8
	VM_EPICS_M1	 = 9idcLAX:m58:c1: 8
	VM_EPICS_M1	 = 9idcLAX:m58:c2: 8
	VM_EPICS_M1	 = 9idcLAX:mxv:c0: 8
	VM_EPICS_M1	 = 9idcLAX:pi:c0: 4
	VM_EPICS_M1	 = 9idcLAX:xps:c0: 8
	VM_EPICS_M1	 = 9idcLAX:aero:c0: 1
	VM_EPICS_M1	 = 9idcLAX:mxv:c1: 8
	VM_EPICS_M1	 = 9idcLAX:aero:c1: 1
	VM_EPICS_M1	 = 9idcLAX:aero:c2: 1
	PSE_MAC_MOT	 = kohzuE 1
	VM_EPICS_M1	 = 9ida: 60
	VM_EPICS_M1	 = 9idcLAX:aero:c3: 1
	VM_EPICS_SC	 = 9idcLAX:vsc:c0 16
	# CAMAC Slot Assignments
	#  CA_name_unit = slot [crate_number]
	# Motor    cntrl steps sign slew base backl accel nada  flags   mne  name
	MOT000 = EPICS_M2:0/2   2000  1  2000  200   50  125    0 0x003       mx  mx
	MOT001 = EPICS_M2:0/3   2000  1  2000  200   50  125    0 0x003       my  my
	MOT002 = EPICS_M2:1/1   2000  1  2000  200   50  125    0 0x003      msx  msx
	MOT003 = EPICS_M2:1/2   2000  1  2000  200   50  125    0 0x003      msy  msy
	MOT004 = EPICS_M2:1/3   2000  1  2000  200   50  125    0 0x003      art  ART50-100
	MOT005 = EPICS_M2:2/5   2000  1  2000  200   50  125    0 0x003  uslvcen  uslitvercen
	MOT006 = EPICS_M2:2/6   2000  1  2000  200   50  125    0 0x003  uslhcen  uslithorcen
	MOT007 = EPICS_M2:3/3   2000  1  2000  200   50  125    0 0x003   gslout  GSlit_outb
	MOTPAR:read_mode = 7
	MOT008 = EPICS_M2:3/4   2000  1  2000  200   50  125    0 0x003   gslinb  GSlit_inb
	MOTPAR:read_mode = 7
	MOT009 = EPICS_M2:3/5   2000  1  2000  200   50  125    0 0x003   gsltop  GSlit_top
	MOTPAR:read_mode = 7
	MOT010 = EPICS_M2:3/6   2000  1  2000  200   50  125    0 0x003   gslbot  GSlit_bot
	MOTPAR:read_mode = 7
	MOT011 = MAC_MOT:0/0   2000  1  2000  200   50  125    0 0x003        en  en
	MOTPAR:read_mode = 7
	MOT012 = EPICS_M2:10/43   2000  1  2000  200   50  125    0 0x003    InbMS  MonoSl_inb
	# Counter   ctrl unit chan scale flags    mne  name
	CNT000 = EPICS_SC  0  0 10000000 0x001      sec  seconds
	CNT001 = EPICS_SC  0  1      1 0x002       I0  I0
	CNT002 = EPICS_SC  0  2      1 0x000      I00  I00
	CNT003 = EPICS_SC  0  3      1 0x000     upd2  photodiode
	CNT004 = EPICS_SC  0  4      1 0x000      trd  TR_diode
	CNT005 = EPICS_SC  0  5      1 0x000     I000  I000

command line
~~~~~~~~~~~~

.. code-block:: bash

   spec2ophyd


output
~~~~~~

.. code-block:: text

	mx = EpicsMotor('9idcLAX:m58:c0:m2', name='mx', labels=('motor',))
	my = EpicsMotor('9idcLAX:m58:c0:m3', name='my', labels=('motor',))
	msx = EpicsMotor('9idcLAX:m58:c1:m1', name='msx', labels=('motor',))
	msy = EpicsMotor('9idcLAX:m58:c1:m2', name='msy', labels=('motor',))
	art = EpicsMotor('9idcLAX:m58:c1:m3', name='art', labels=('motor',))  # ART50-100
	uslvcen = EpicsMotor('9idcLAX:m58:c2:m5', name='uslvcen', labels=('motor',))  # uslitvercen
	uslhcen = EpicsMotor('9idcLAX:m58:c2:m6', name='uslhcen', labels=('motor',))  # uslithorcen
	gslout = EpicsMotor('9idcLAX:mxv:c0:m3', name='gslout', labels=('motor',))  # GSlit_outb # read_mode=7
	gslinb = EpicsMotor('9idcLAX:mxv:c0:m4', name='gslinb', labels=('motor',))  # GSlit_inb # read_mode=7
	gsltop = EpicsMotor('9idcLAX:mxv:c0:m5', name='gsltop', labels=('motor',))  # GSlit_top # read_mode=7
	gslbot = EpicsMotor('9idcLAX:mxv:c0:m6', name='gslbot', labels=('motor',))  # GSlit_bot # read_mode=7
	# Macro Motor: SpecMotor(mne='en', config_line='11', macro_prefix='kohzuE') # read_mode=7
	InbMS = EpicsMotor('9ida:m43', name='InbMS', labels=('motor',))  # MonoSl_inb
	c0 = ScalerCH('9idcLAX:vsc:c0', name='c0', labels=('detectors',))
	# counter: sec = SpecCounter(mne='sec', config_line='0', name='seconds', unit='0', chan='0', pvname=9idcLAX:vsc:c0.S1)
	# counter: I0 = SpecCounter(mne='I0', config_line='1', unit='0', chan='1', pvname=9idcLAX:vsc:c0.S2)
	# counter: I00 = SpecCounter(mne='I00', config_line='2', unit='0', chan='2', pvname=9idcLAX:vsc:c0.S3)
	# counter: upd2 = SpecCounter(mne='upd2', config_line='3', name='photodiode', unit='0', chan='3', pvname=9idcLAX:vsc:c0.S4)
	# counter: trd = SpecCounter(mne='trd', config_line='4', name='TR_diode', unit='0', chan='4', pvname=9idcLAX:vsc:c0.S5)
	# counter: I000 = SpecCounter(mne='I000', config_line='5', unit='0', chan='5', pvname=9idcLAX:vsc:c0.S6)

Cautions
++++++++++++++++++++++

* *spec2ophyd* is a work-in-progress.
* *spec2ophyd* does not rely on any libraries of *apstools*
* It is not necessarily robust
* There is no command line help for this utility.  
* It is not packaged or installed with the apstools.  
* It is only available from the source code repository.
* It may be refactored or removed at any time.
* Check the *apstools* Change History for more updates (https://github.com/BCDA-APS/apstools/blob/master/CHANGES.rst)
