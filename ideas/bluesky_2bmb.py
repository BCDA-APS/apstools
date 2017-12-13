
"""
2-BM-B tomography macros for BlueSky
"""

import time
from ophyd import SingleTrigger, AreaDetector, PcoDetectorCam
from ophyd import Component, Device, EpicsMotor, EpicsSignal, EpicsSignalWithRBV
from ophyd import HDF5Plugin, ImagePlugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite


class ServoRotationStage(EpicsMotor):
    """extend basic motor support to enable/disable the servo loop controls"""
    servo = Component(EpicsSignal, ".CNEN", string=True)        # values: "Enable" or "Disable"


class Mirror1_A(Device):
    """
	Mirror 1 in the 2BM-A station
	
	A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
	A_mirror1.angle.put(Mirr_Ang)
	A_mirror1.average.put(Mirr_YAvg)
	"""
	angle = Component(EpicsSignal, "ang1")
    average = Component(EpicsSignal, "avg")


class AB_Shutter(Device):
    """
    A or B station shutter (PSS item)
    
    USAGE::

        A_shutter = AB_Shutter("2bma:A_shutter", "A_shutter")
        A_shutter.open()
        A_shutter.close()

        B_shutter = AB_Shutter("2bma:B_shutter", "B_shutter")
        B_shutter.close()

    """
    pss_open = Component(Signal, ":open")
    pss_close = Component(Signal, ":close")
    
    def open(self):
        """tells PSS to open the shutter"""
        self.pss_open.put(1)
    
    def close(self):
        """tells PSS to close the shutter"""
        self.pss_close.put(1)


class Motor_Shutter(Device):
    """
    a shutter, implemented with a motor
    
    USAGE::

        tomo_shutter = Motor_Shutter("2bma:m23", "tomo_shutter")
        tomo_shutter.open()
        tomo_shutter.close()

    """
    motor = Component(EpicsMotor, "")
    closed_position = 1.0
    open_position = 0.0
    
    def open(self):
        """move motor to BEAM NOT BLOCKED position"""
        self.motor.move(self.open_position)
    
    def close(self):
        """move motor to BEAM BLOCKED position"""
        self.motor.move(self.closed_position)


class PSO_Device(Device):
    # TODO: this might fit the ophyd "Flyer" API
    slew_speed = Component(EpicsSignal, "slewSpeed.VAL")
    scan_control = Component(EpicsSignal, "scanControl.VAL", string=True)
    start_pos = Component(EpicsSignal, "startPos.VAL")
    end_pos = Component(EpicsSignal, "endPos.VAL")
    scan_delta = Component(EpicsSignal, "scanDelta.VAL")
    pso_taxi = Component(EpicsSignal, "taxi.VAL")
    pso_fly = Component(EpicsSignal, "fly.VAL")
    
    def taxi(self):
        self.pso_taxi.put("Taxi")
    
    def fly(self):
        self.pso_fly.put("Fly")


class MyPcoCam(PcoDetectorCam):    # TODO: check this
    array_callbacks = Component(EpicsSignal, "ArrayCallbacks")
	pco_cancel_dump = Component(EpicsSignal, "pco_cancel_dump")
	pco_live_view = Component(EpicsSignal, "pco_live_view")
	pco_trigger_mode = Component(EpicsSignal, "pco_trigger_mode")
	pco_edge_fastscan = Component(EpicsSignal, "pco_edge_fastscan")
	pco_is_frame_rate_mode = Component(EpicsSignal, "pco_is_frame_rate_mode")
	pco_imgs2dump = Component(EpicsSignalWithRBV, "pco_imgs2dump")
	pco_dump_counter = Component(EpicsSignal, "pco_dump_counter")
	pco_dump_camera_memory = Component(EpicsSignal, "pco_dump_camera_memory")


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    """adapt HDF5 plugin for AD 2.5+"""
    
    file_number_sync = None
	xml_layout_file = Component(EpicsSignalWithRBV, "XMLFileName")
    
    def get_frames_per_point(self):
        return self.parent.cam.num_images.get()
    

class MyPcoDetector(SingleTrigger, AreaDetector):
    """PCO detectors as used by 2-BM tomography"""
    # TODO: configure the "root" and "write_path_template" attributes
    
    cam = Component(MyPcoCam, "cam1:")
    image = Component(ImagePlugin, "image1:")
    hdf1 = Component(
        MyHDF5Plugin, 
        "HDF1:", 
        root="/",                   # root path for HDF5 files (for databroker filestore)
        write_path_template="/tmp", # path for HDF5 files (for EPICS area detector)
        )


A_shutter = AB_Shutter("2bma:A_shutter, "A_shutter")
B_shutter = AB_Shutter("2bma:B_shutter, "B_shutter")
A_filter = EpicsSignal("2bma:fltr1:select.VAL", name="A_filter")
A_mirror1 = Mirror1_A("2bma:M1", name="A_mirror1")
A_slit1_h_center = EpicsSignal("2bma:Slit1Hcenter", name="A_slit1_h_center")

tomo_shutter = Motor_Shutter("2bma:m23", "tomo_shutter")
#m23 = EpicsMotor("2bma:m23", name="m23")   # this is a shutter.  Use the shutter device instead.

m7 = EpicsMotor("2bma:m7", name="m7")    # ? XIASLIT
m25 = EpicsMotor("2bma:m25", name="m25")    # ? DMM_USX
m26 = EpicsMotor("2bma:m26", name="m26")    # ? DMM_USY_OB
m27 = EpicsMotor("2bma:m27", name="m27")    # ? DMM_USY_IB
m28 = EpicsMotor("2bma:m28", name="m28")    # ? DMM_DSX
m29 = EpicsMotor("2bma:m29", name="m29")    # ? DMM_DSY
m30 = EpicsMotor("2bma:m30", name="m30")    # ? USArm
m31 = EpicsMotor("2bma:m31", name="m31")    # ? DSArm
m32 = EpicsMotor("2bma:m32", name="m32")    # ? M2Y


am20     = EpicsMotor("2bma:m20", name="am20")			    # posStage in A LAT
am46     = EpicsMotor("2bma:m46", name="am46")			    # posStage in A SAT
am49     = EpicsMotor("2bma:m49", name="am49")              # sample stage in A
bm82     = ServoRotationStage("2bmb:m82", name="bm82")      # rotation stage in A
bm63     = EpicsMotor("2bmb:m63", name="bm63")              # sample stage in B
bm100    = ServoRotationStage("2bmb:m100", name="bm100")    # rotation stage in B
furnaceY = EpicsMotor("2bma:m55", name="furnaceY")
bm4      = EpicsMotor("2bmb:m4",  name="bm4")			    # posStage in B LAT
bm57     = EpicsMotor("2bmb:m57", name="bm57")			    # posStage in B SAT

pso1     = PSO_Device("2bmb:PSOFly1:", name="pso1")
pso2     = PSO_Device("2bmb:PSOFly2:", name="pso2")
tableFly2_sseq_PROC = EpicsSignal(
          "2bmb:tableFly2:sseq2.PROC", name="tableFly2_sseq_PROC")

pco_dimax = MyPcoDetector("PCOIOC2:", name="pco_dimax")  # TODO: check PV prefix
pco_edge = MyPcoDetector("PCOIOC3:", name="pco_edge")  # TODO: check PV prefix

caputRecorder1 = EpicsSignal("2bmb:caputRecorderGbl_1", name="caputRecorder1", string=True)
caputRecorder2 = EpicsSignal("2bmb:caputRecorderGbl_2", name="caputRecorder2", string=True)
caputRecorder3 = EpicsSignal("2bmb:caputRecorderGbl_3", name="caputRecorder3", string=True)
caputRecorder4 = EpicsSignal("2bmb:caputRecorderGbl_4", name="caputRecorder4", string=True)
caputRecorder5 = EpicsSignal("2bmb:caputRecorderGbl_5", name="caputRecorder5", string=True)
caputRecorder6 = EpicsSignal("2bmb:caputRecorderGbl_6", name="caputRecorder6", string=True)
caputRecorder7 = EpicsSignal("2bmb:caputRecorderGbl_7", name="caputRecorder7", string=True)
caputRecorder8 = EpicsSignal("2bmb:caputRecorderGbl_8", name="caputRecorder8", string=True)
caputRecorder9 = EpicsSignal("2bmb:caputRecorderGbl_9", name="caputRecorder9", string=True)
caputRecorder10 = EpicsSignal("2bmb:caputRecorderGbl_10", name="caputRecorder10", string=True)
caputRecorder_filename = EpicsSignal("2bmb:caputRecorderGbl_filename", name="caputRecorder_filename", string=True)
caputRecorder_filepath = EpicsSignal("2bmb:caputRecorderGbl_filepath", name="caputRecorder_filepath", string=True)


def process_tableFly2_sseq_record():
    tableFly2_sseq_PROC.put(1)


def initDimax(samInPos=0, hutch='A'):
    """
    I want a comment here
    """
    if hutch.lower() == ('a'):
        shutter = A_shutter
        samStage = am49
        rotStage = bm82
    else:
        shutter = B_shutter
        samStage = bm63
        rotStage = bm100

    det = pco_dimax
    det.cam.array_callbacks.put("Enable")

    # det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")

    tomo_shutter.open()
    shutter.open()
    det.cam.pco_cancel_dump.put(1)
    det.cam.acquire.put("Done")
    det.cam.pco_trigger_mode.put("Auto")
    det.cam.pco_live_view.put("Yes")
    if hasattr(det, "hdf1"):
        det.hdf1.enable.put("Enable")
        # det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")
        det.hdf1.capture.put("Done")
        det.hdf1.num_captured.put(0)
    rotStage.servo.put("Enable")
	process_tableFly2_sseq_record()
    rotStage.velocity.put(180)
    rotStage.acceleration.put(3)
    rotStage.move(0)
    samStage.move(samInPos)
    print("Dimax is reset!")


def initEdge(samInPos=0, samStage=None, rotStage=None):
    """
    I want a comment here
    """
    samStage = samStage or am49
    rotStage = rotStage or bm82

    tomo_shutter.open()
    A_shutter.open()

    det = pco_edge

    det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")

    det.cam.acquire.put("Done")
    # det.cam.acquire.put("Done")  
    det.cam.pco_trigger_mode.put("Auto")
	det.cam.image_mode.put("Continuous")
	det.cam.pco_edge_fastscan.put("Normal")
	det.cam.pco_is_frame_rate_mode.put(0)
	det.cam.acquire_time.put(0.2)
	det.cam.size.size_x.put(2560)
	det.cam.size.size_y.put(1400)
    if hasattr(det, "hdf1"):
        det.hdf1.enable.put("Enable")
        det.hdf1.capture.put("Done")
        det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")
        det.hdf1.num_captured.put(0)
	det.image.enable.put("Enable")
	process_tableFly2_sseq_record()
    rotStage.stop()
    rotStage.set_use_switch.put("Set")
    rotStage.user_setpoint.put(rotStage.position % 360.0)
    rotStage.set_use_switch.put("Use")
    rotStage.velocity.put(30)
    rotStage.acceleration.put(3)
    rotStage.move(0)
    samStage.move(samInPos)
    tomo_shutter.close()
    print("Edge is reset!")


def change2White():
    shutter = "2bma:A_shutter"    
    BL = '2bma'
	A_shutter.close()
	# am33.move(107.8, wait=False)
    A_filter.put(0)
    A_mirror1.angle.put(0)
    time.sleep(1)                

    A_mirror1.average.put(-4)
    time.sleep(1)                

    am25.move(50, wait=False)
    am28.move(50, wait=True)
    time.sleep(3)                

    am26.move(-16, wait=False)
    am27.move(-16, wait=False)
    am29.move(-16, wait=True)
    time.sleep(3)                

    A_slit1_h_center.put(4.8)
    am7.move(11.8, wait=True)


def change2Mono():
	A_shutter.close()
	# am33.move(121)
    A_filter.put(0)
    A_mirror1.average.put(0)
    time.sleep(1) 
	
    A_mirror1.angle.put(2.657)
    time.sleep(1)

    am26.move(-0.1, wait=False)
    am27.move(-0.1, wait=False)
    am29.move(-0.1)
    time.sleep(3)

    am25.move(81.5, wait=False)
    am28.move(81.5)
    time.sleep(3)

    A_slit1_h_center.put(5)
    am7.move(46.55)


def changeDMMEng(energy=24.9):
    BL = '2bma'
    A_shutter.close()
    change2Mono()
    if energy < 20.0:
        A_filter.put(4)
    else:
        A_filter.put(0)

#    if A_mirror1.angle.get() is not 2.657:
#        print('mirror angle is wrong. quit!')
#        return 0                 # TODO: could raise ValueError instead!

    caliEnergy_list = np.array([40.0,35.0,31.0,27.4,24.9,22.7,21.1,20.2,18.9,17.6,16.8,16.0,15.0,14.4])
    XIASlit_list = np.array([37.35,41.35,42.35,42.35,43.35,46.35,44.35,46.35,47.35,50.35,52.35,53.35,54.35,51.35])    
#    XIASlit_list = np.array([38.35,43.35,42.35,44.35,46.35,46.35,47.35,48.35,50.35,50.35,52.35,53.35,54.35,55.35]) 
#    FlagSlit_list = np.array([19.9,,19.47])    
#    GlobalY_list = np.array([-87.9,1.15,-79.8,1.25,-84.2,1.35,1.4,1.45,1.5,-79.8,1.6,1.65])                    
    USArm_list = np.array([1.10,1.25,1.10,1.15,1.20,1.25,1.30,1.35,1.40,1.45,1.50,1.55,1.60,1.65])    
    DSArm_list = np.array([1.123,1.2725,1.121,1.169,1.2235,1.271,1.3225,1.366,1.4165,1.4655,1.5165,1.568,1.6195,1.67])
    M2Y_list = np.array([13.82,15.87,12.07,13.11,14.37,15.07,15.67,16.87,17.67,18.47,19.47,20.57,21.27,22.27]) 

    DMM_USX_list = [27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5]
    DMM_DSX_list = [27.5,27.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5,82.5]
    DMM_USY_OB_list = [-5.7,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1] 
    DMM_USY_IB_list = [-5.7,-3.8,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1]   
    DMM_DSY_list = [-5.7,-3.8,-0.1,-0.1,-0.2,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1,-0.1] 
    
    Mirr_Ang_list = [1.500,2.000,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657,2.657]
    Mirr_YAvg_list = [0.1,-0.2,0.0,0.0,-0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

    energy_index = np.where(caliEnergy_list==energy)[0]
    if energy_index.size == 0:
        print('there is no specified energy in the energy lookup table. please choose a calibrated energy.')
        return    0                            # TODO: could raise KeyError instead!

    A_mirror1.angle.put(Mirr_Ang_list[energy_index])
    A_mirror1.average.put(Mirr_YAvg_list[energy_index])
    
	am26.move(DMM_USY_OB_list[energy_index], wait=False)
	am27.move(DMM_USY_IB_list[energy_index], wait=False)
	am29.move(DMM_DSY_list[energy_index], wait=False)
	am30.move(USArm_list[energy_index], wait=False)
	am31.move(DSArm_list[energy_index])
    time.sleep(3)

	am32.move(M2Y_list[energy_index], wait=False)
	am25.move(DMM_USX_list[energy_index], wait=False)
	am28.move(DMM_DSX_list[energy_index])
	am7.move(XIASlit_list[energy_index] )
    print('DMM energy is set to ', energy, 'keV.')


def centerAxis(axisShift=12.5, refYofX0=14.976):
    """
	function documentation
                
	axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
		  it assumes rotation axis is at image center at posInit.
	this is the case in which the rotation axis move toward right side (larger 'center' in reconstruction)
	when the sample stage moves up.                                                        
    """
    posRefPos = refYofX0 
                                
	##### AHutch tomo configurations -- start                           
	#### for LAT                
    samStage = am49
    posStage = am20      
                
	### for SAT                
	#    samStage = am49
	#    posStage = am46
               
	##### AHutch tomo configurations -- end                    

	####### BHutch tomo configurations -- start              
	#### for SAT                
	#    samStage = bm63
	#    posStage = bm57
	#                
	#### for LAT
	##    samStage = bm58
	##    posStage = bm4
	####### BHutch tomo configurations -- end                   

    samStageOffset = axisShift * (posStage.position - posRefPos)/1000.0  
    print(samStageOffset)
	samStage.move(samStageOffset)
    print('done')

 
def DimaxRadiography(exposureTime=0.1, frmRate=9, acqPeroid=30,   # FIXME: typo
                    samInPos=0, samOutPos=7,
                    roiSizeX=2016, roiSizeY=2016,
                    repeat=1, delay=600,
                    scanMode=0):

    samStage = am49; station = 'AHutch'
    #samStage = bm63; station = 'BHutch'
	cam = "dimax"; det = pco_dimax
	# cam = "edge"; det = pco_edge
    posStage = am20 
    rotStage = bm82

    A_shutter.open()
    numImage = frmRate * acqPeroid + 20
    camShutterMode = "Rolling"
    filepath_top = caputRecorder_filepath.value

#    filepath = os.path.join(filepath_top, caputRecorder1.value+ \
#                caputRecorder2.value.zfill(3)+'_'+ 'Radiography_' +\
#                caputRecorder4.value+'_'+\
#                      'YPos'+str(am20.position)+'mm_'+\
#                cam+'_'+caputRecorder5.value+'x'+'_'+\
#                caputRecorder6.value+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+'DegPerSec_'+\
#                camShutterMode+'_'+caputRecorder7.value+'um'+\
#                caputRecorder8.value+'_'+\
#                caputRecorder9.value+'_'+\
#                str(A_mirror1.angle.value)+'mrad_USArm'+str(am30.position)+\
#                '_monoY_'+str(am26.position)+'_'+station)

	# det.cam.nd_attributes_file.put("DynaMCTDetectorAttributes.xml")
	# if hasattr(det, "hdf1"):
	#     det.hdf1.xml_layout_file.put("DynaMCTHDFLayout.xml")

	for ii in range(repeat):
		tomo_shutter.close()
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']
		
        filepath = os.path.join(filepath_top, \
                   caputRecorder1.value+ \
                   caputRecorder2.value.zfill(3)+'_'+ 'Radiography_'+\
                   caputRecorder4.value+'_'+\
                   'YPos'+str(int(posStage.position*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+caputRecorder5.value+'x'+'_'+\
                   caputRecorder6.value+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+\
                   camShutterMode+'_'+caputRecorder7.value+'um'+\
                   caputRecorder8.value+'_'+\
                   caputRecorder9.value+'_'+\
                   str(int(A_mirror1.angle.value*1000)/1000.0)+'mrad_USArm'+str(int(am30.position*1000)/1000.0)+\
                   '_monoY_'+str(int(am26.position*1000)/1000.0)+'_'+station)     
        filename = caputRecorder_filename.value   
    
		det.cam.acquire.put("Done")

		det.cam.pco_trigger_mode.put("Auto")
		det.cam.pco_is_frame_rate_mode.put("DelayExp")
		det.cam.pco_live_view.put("No")
        det.cam.size.size_x.put(roiSizeX)
        det.cam.size.size_y.put(roiSizeY)
		det.cam.acquire_period.put(0)

        if hasattr(det, "hdf1"):
			det.hdf1.capture.put("Done")
			det.hdf1.create_directory.put(-5)	# TODO: Why -5?
			det.hdf1.file_number.put(caputRecorder10.value)
			det.hdf1.enable.put(1)
			det.hdf1.auto_increment.put("Yes")
			det.hdf1.num_capture.put(numImage)
			det.hdf1.num_captured.put(numImage)
			det.hdf1.file_path.put(filepath)
			det.hdf1.file_name.put(filename)
			det.hdf1.file_template.put("%s%s_%4.4d.hdf")
			det.hdf1.auto_save.put("Yes")
			det.hdf1.file_write_mode.put("Stream")
			det.hdf1.capture.put("Capture", wait=False)
			time.sleep(2)  

        samStage.move(samInPos)
		det.cam.num_images.put(numImage-20)
		det.cam.frame_type.put('0')
		det.cam.acquire.put("Acquire")
		det.cam.pco_dump_counter.put('0')
		det.cam.pco_imgs2dump.put(numImage-20)
		det.cam.pco_dump_camera_memory.put(1)
        print('data is done')

		det.cam.num_images.put(10)
        samStage.move(samOutPos)
		det.cam.frame_type.put('2')
		det.cam.acquire.put("Acquire")
		det.cam.pco_dump_counter.put('0')
		det.cam.pco_imgs2dump.put(10)
		tomo_shutter.open()
		det.cam.pco_dump_camera_memory.put(1)
		det.cam.acquire.put("Done")
        print('flat is done')

        # tomo_shutter.open()
        samStage.move(samInPos)
		det.cam.frame_type.put('1')
		det.cam.acquire.put("Acquire")
		det.cam.pco_dump_counter.put('0')
		det.cam.pco_imgs2dump.put(10)
		det.cam.pco_dump_camera_memory.put(1)
		det.cam.acquire.put("Done")
        print('dark is done')

        if hasattr(det, "hdf1"):
			det.hdf1.capture.put("Done", wait=False)
		det.cam.image_mode.put("Continuous")

		caputRecorder10.put(det.hdf1.file_number.value)
        if caputRecorder3.value == 'Yes':
            caputRecorder2.put(int(caputRecorder2.value)+1)

        print(str(ii), 'the acquisition is done at ', time.asctime())
        if ii != repeat-1:
            time.sleep(delay)

	det.cam.pco_live_view.put("Yes")
    tomo_shutter.close()
	A_shutter.close()
    print('Radiography acquisition finished!')

 