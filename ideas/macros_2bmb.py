#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:57:05 2015

@author: xhxiao
"""

import time
import epics
import numpy as np
import os
import Tkinter
import tkMessageBox as mbox
#from caputRecorder import _getGlobals

# The function "_abort" is special: it's used by caputRecorder.py to abort an
# executing macro



def _initFilepath():
    epics.caput("2bmb:caputRecorderGbl_filepath.VAL", "S:/2015_07/John/test_Slag_dry_test_10x_dimax_75mm_36DegPerSec_180Deg_2msecExpTime_600proj_Rolling_100umLuAG_1mmC_2mmGlass_pink_2.657mrad_AHutch/",  wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_filename.VAL", "proj",  wait=True, timeout=1000.0)                

def setDefaultFolderStructure():    
    epics.caput("2bmb:caputRecorderGbl_1.DESC",'prefix', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_2.DESC",'prefix #', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_3.DESC",'auto-increase #', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_4.DESC",'sample name', wait=True, timeout=1000.0)    
    epics.caput("2bmb:caputRecorderGbl_5.DESC",'lens mag', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_6.DESC",'sam-det dist(mm)', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_7.DESC",'scinThickness(um)', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_8.DESC",'scinType', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_9.DESC",'filter', wait=True, timeout=1000.0)                
    epics.caput("2bmb:caputRecorderGbl_10.DESC",'proj #', wait=True, timeout=1000.0)                

    epics.caput("2bmb:caputRecorderGbl_filename.VAL",'proj', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_1.VAL",'Exp', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_2.VAL",'1', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_3.VAL",'Yes', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_4.VAL",'S1', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_5.VAL",'10', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_6.VAL",'50', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_7.VAL",'10', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_8.VAL",'LuAG', wait=True, timeout=1000.0)
    epics.caput("2bmb:caputRecorderGbl_9.VAL",'1mmC1mmGlass', wait=True, timeout=1000.0)                    
    epics.caput("2bmb:caputRecorderGbl_10.VAL",'1', wait=True, timeout=1000.0)                                    
                                
def change2White():
    shutter = "2bma:A_shutter"    
    BL = '2bma'
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#    epics.caput(BL+":m33.VAL",107.8, wait=False, timeout=1000.0)                
    epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)                
    epics.caput(BL+":M1angl.VAL",0, wait=True, timeout=1000.0)
    time.sleep(1)                
    epics.caput(BL+":M1avg.VAL",-4, wait=True, timeout=1000.0)
    time.sleep(1)                
    epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
    epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
    time.sleep(3)                
    epics.caput(BL+":m26.VAL",-16, wait=False, timeout=1000.0)    
    epics.caput(BL+":m27.VAL",-16, wait=False, timeout=1000.0)    
    epics.caput(BL+":m29.VAL",-16, wait=True, timeout=1000.0)                
    time.sleep(3)                
    epics.caput(BL+":Slit1Hcenter.VAL",4.8, wait=True, timeout=1000.0)
    epics.caput(BL+":m7.VAL",11.8, wait=True, timeout=1000.0)                
                


def change2Mono():
    shutter = "2bma:A_shutter"    
    BL = '2bma'
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#    epics.caput(BL+":m33.VAL",121, wait=False, timeout=1000.0)                    
    epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
    epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
    time.sleep(1)                    
    epics.caput(BL+":M1angl.VAL",2.657, wait=True, timeout=1000.0)
    time.sleep(1)                                            
    epics.caput(BL+":m26.VAL",-0.1, wait=False, timeout=1000.0)    
    epics.caput(BL+":m27.VAL",-0.1, wait=False, timeout=1000.0)    
    epics.caput(BL+":m29.VAL",-0.1, wait=True, timeout=1000.0)                
    time.sleep(3)
    epics.caput(BL+":m25.VAL",81.5, wait=False, timeout=1000.0)    
    epics.caput(BL+":m28.VAL",81.5, wait=True, timeout=1000.0)
    time.sleep(3)                
    epics.caput(BL+":Slit1Hcenter.VAL",5, wait=True, timeout=1000.0)    
    epics.caput(BL+":m7.VAL",46.55, wait=True, timeout=1000.0)                
                
                


def change2Pink(ang=2.657):
    if ang == 2.657:
        shutter = "2bma:A_shutter"    
        BL = '2bma'
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    #    epics.caput(BL+":m33.VAL",-70.1, wait=False, timeout=1000.0)     
    #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                
        epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
        epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
        time.sleep(1)                    
        epics.caput(BL+":M1angl.VAL",2.657, wait=True, timeout=1000.0)
        time.sleep(1)
        epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
        epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
        time.sleep(3)                                            
        epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
        time.sleep(3)                
        epics.caput(BL+":Slit1Hcenter.VAL",6.6, wait=True, timeout=1000.0)    
        epics.caput(BL+":m7.VAL",28.75, wait=True, timeout=1000.0) 
    elif ang == 2.0:
        shutter = "2bma:A_shutter"    
        BL = '2bma'
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    #    epics.caput(BL+":m33.VAL",-75.6, wait=False, timeout=1000.0) 
    #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                    
        epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
        epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
        time.sleep(1)                    
        epics.caput(BL+":M1angl.VAL",2.0, wait=True, timeout=1000.0)
        time.sleep(1)
        epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
        epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
        time.sleep(3)                                            
        epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
        time.sleep(3)                
        epics.caput(BL+":Slit1Hcenter.VAL",4.85, wait=True, timeout=1000.0)    
        epics.caput(BL+":m7.VAL",23.25, wait=True, timeout=1000.0) 
    elif ang == 1.8:
        shutter = "2bma:A_shutter"    
        BL = '2bma'
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    #    epics.caput(BL+":m33.VAL",-77.1, wait=False, timeout=1000.0)    
    #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                 
        epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
        epics.caput(BL+":M1avg.VAL",0, wait=True, timeout=1000.0)
        time.sleep(1)                    
        epics.caput(BL+":M1angl.VAL",1.8, wait=True, timeout=1000.0)
        time.sleep(1)
        epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
        epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
        time.sleep(3)                                            
        epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
        time.sleep(3)                
        epics.caput(BL+":Slit1Hcenter.VAL",4.85, wait=True, timeout=1000.0)    
        epics.caput(BL+":m7.VAL",21.75, wait=True, timeout=1000.0)   
    elif ang == 1.5:
        shutter = "2bma:A_shutter"    
        BL = '2bma'
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    #    epics.caput(BL+":m33.VAL",-79.8, wait=False, timeout=1000.0)    
    #    epics.caput(BL+":m21.VAL",1306.0, wait=False, timeout=1000.0)                 
        epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
        epics.caput(BL+":M1avg.VAL",-0.1, wait=True, timeout=1000.0)
        time.sleep(1)                    
        epics.caput(BL+":M1angl.VAL",1.5, wait=True, timeout=1000.0)
        time.sleep(1)
        epics.caput(BL+":m25.VAL",50, wait=False, timeout=1000.0)    
        epics.caput(BL+":m28.VAL",50, wait=True, timeout=1000.0)
        time.sleep(3)                                            
        epics.caput(BL+":m26.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m27.VAL",-10., wait=False, timeout=1000.0)    
        epics.caput(BL+":m29.VAL",-10., wait=True, timeout=1000.0)                
        time.sleep(3)                
        epics.caput(BL+":Slit1Hcenter.VAL",4.85, wait=True, timeout=1000.0)    
        epics.caput(BL+":m7.VAL",18.75, wait=True, timeout=1000.0)               
                
                
                
def change2MonoDummy():
    print 'Caution!!! You are running wrong routine ...'
    pass

def changeDMMEng(eng = 24.9):
    shutter = "2bma:A_shutter"    
    BL = '2bma'
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    change2Mono()                
    if eng < 20.0:
        epics.caput(BL+":fltr1:select.VAL",4, wait=True, timeout=1000.0)
    else:                                
        epics.caput(BL+":fltr1:select.VAL",0, wait=True, timeout=1000.0)
#    if epics.caget(BL+":M1angl.VAL") is not 2.657:
#        print 'mirror angle is wrong. quit!'
#        return 0
    caliEng_list = np.array([40.0,35.0,31.0,27.4,24.9,22.7,21.1,20.2,18.9,17.6,16.8,16.0,15.0,14.4])
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

    idx = np.where(caliEng_list==eng)                
    if idx[0].size == 0:
        print 'there is no specified energy in the energy lookup table. please choose a calibrated energy.'
        return    0                            
    USArm = USArm_list[idx[0]]                
    DSArm = DSArm_list[idx[0]]
    M2Y = M2Y_list[idx[0]]
    
    DMM_USX = DMM_USX_list[idx[0]]
    DMM_DSX = DMM_DSX_list[idx[0]]
    DMM_USY_OB = DMM_USY_OB_list[idx[0]] 
    DMM_USY_IB = DMM_USY_IB_list[idx[0]]
    DMM_DSY = DMM_DSY_list[idx[0]
    ]
    Mirr_Ang = Mirr_Ang_list[idx[0]] 
    Mirr_YAvg = Mirr_YAvg_list[idx[0]]
    XIASlit = XIASlit_list[idx[0]]          

    epics.caput(BL+":M1angl.VAL",Mirr_Ang, wait=False, timeout=1000.0) 
    epics.caput(BL+":M1avg.VAL",Mirr_YAvg, wait=False, timeout=1000.0) 
    
    epics.caput(BL+":m26.VAL",DMM_USY_OB, wait=False, timeout=1000.0) 
    epics.caput(BL+":m27.VAL",DMM_USY_IB, wait=False, timeout=1000.0) 
    epics.caput(BL+":m29.VAL",DMM_DSY, wait=False, timeout=1000.0) 
    epics.caput(BL+":m30.VAL",USArm, wait=False, timeout=1000.0)    
    epics.caput(BL+":m31.VAL",DSArm, wait=True, timeout=1000.0)
    time.sleep(3)                                            
    epics.caput(BL+":m32.VAL",M2Y, wait=True, timeout=1000.0)
    epics.caput(BL+":m25.VAL",DMM_USX, wait=False, timeout=1000.0)
    epics.caput(BL+":m28.VAL",DMM_DSX, wait=True, timeout=1000.0)
    epics.caput(BL+":m7.VAL",XIASlit, wait=True, timeout=1000.0)                
    print 'DMM energy is set to ', eng, 'keV.'                
                
                


def centerAxis(axisShift = 12.5,refYofX0 = 14.976):
    """ 
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
      this is the case in which the rotation axis move toward right side (larger 'center' in reconstruction)
      when the sample stage moves up.                                                        
    """
    posRefPos = refYofX0 
                                
##### AHutch tomo configurations -- start                           
#### for LAT                
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
                
### for SAT                
#    samStage = "2bma:m49"
#    posStage = "2bma:m46"                        
               
##### AHutch tomo configurations -- end                    

####### BHutch tomo configurations -- start              
#### for SAT                
#    samStage = "2bmb:m63"
#    posStage = "2bmb:m57"
#                
#### for LAT
##    samStage = "2bmb:m58"
##    posStage = "2bmb:m4"              
####### BHutch tomo configurations -- end                   

    posCurr = epics.caget(posStage + ".VAL")    
    samStageOffset = axisShift * (posCurr - posRefPos)/1000.0  
    print samStageOffset                                               
    epics.caput(samStage + ".VAL",str(samStageOffset), wait=True, timeout=1000.0) 
    print 'done'                
               
             
                            
                

def initDimax(samInPos = 0, hutch='A'):
    camPrefix = "PCOIOC2" 
    epics.caput(camPrefix+":HDF1:EnableCallbacks.VAL","Enable", wait=True, timeout=1000.0)  
    epics.caput(camPrefix + ":cam1:ArrayCallbacks.VAL","Enable", wait=True, timeout=1000.0)  
    
#    if epics.caget(camPrefix+":HDF1:XMLFileName_RBV.VAL") != "DynaMCTHDFLayout.xml":        
#        epics.caput(camPrefix+":HDF1:XMLFileName.VAL","DynaMCTHDFLayout.xml", wait=True, timeout=1000.0)                 
#
#    if epics.caget(camPrefix+":cam1:NDAttributesFile.VAL") != "DynaMCTDetectorAttributes.xml":     
#        epics.caput(camPrefix+":cam1:NDAttributesFile.VAL","DynaMCTDetectorAttributes.xml", wait=True, timeout=1000.0)

    if hutch == 'A' or hutch == 'a':                                       
        shutter = "2bma:A_shutter"
    #    samStage = "2bma:m49"
    #    rotStage = "2bmb:m100"    
                    
        samStage = "2bmb:m49"                
        rotStage = "2bmb:m82" 
        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_cancel_dump.VAL","1", wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(rotStage+".CNEN","Enable", wait=True, timeout=1000.0)
    #    epics.caput("2bmb:tableFly2:sseq2.PROC", 1, wait=True, timeout=1000.0)                
        epics.caput(rotStage+".VELO","180", wait=True, timeout=1000.0)
        epics.caput(rotStage+".ACCL","3", wait=True, timeout=1000.0)                
        epics.caput(rotStage+".VAL","0", wait=True, timeout=1000.0)                                
        epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    elif hutch == 'B' or hutch == 'b':                               
        shutter = "2bma:B_shutter"
        samStage = "2bmb:m63"                
        rotStage = "2bmb:m100"     
                    
#        samStage = "2bmb:m58"                
#        rotStage = "2bmb:m82"                 
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_cancel_dump.VAL","1", wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(rotStage+".CNEN","Enable", wait=True, timeout=1000.0)
    #    epics.caput("2bmb:tableFly2:sseq2.PROC", 1, wait=True, timeout=1000.0)                
        epics.caput(rotStage+".VELO","360", wait=True, timeout=1000.0)
        epics.caput(rotStage+".ACCL","3", wait=True, timeout=1000.0)                
        epics.caput(rotStage+".VAL","0", wait=True, timeout=1000.0)                                
        epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)                    
    print "Dimax is reset!"                




def initEdge(samInPos = 0,samStage=None,rotStage=None):
    camPrefix = "PCOIOC3"                            
    shutter = "2bma:A_shutter"
#    samStage = "2bmb:m63"
    if samStage is None:
        samStage = "2bma:m49"  
    if rotStage is None:              
        rotStage = "2bmb:m82"
    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:EnableCallbacks.VAL",1, wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0) 

    if epics.caget(camPrefix+":HDF1:XMLFileName_RBV.VAL") != "DynaMCTHDFLayout.xml":        
        epics.caput(camPrefix+":HDF1:XMLFileName.VAL","DynaMCTHDFLayout.xml", wait=True, timeout=1000.0)                 

    if epics.caget(camPrefix+":cam1:NDAttributesFile.VAL") != "DynaMCTDetectorAttributes.xml":     
        epics.caput(camPrefix+":cam1:NDAttributesFile.VAL","DynaMCTDetectorAttributes.xml", wait=True, timeout=1000.0)

    epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_is_frame_rate_mode.VAL",0, wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:AcquireTime.VAL",0.2, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:SizeX.VAL","2560", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:SizeY.VAL","1400", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":image1:EnableCallbacks.VAL","Enable", wait=True, timeout=1000.0)
#    epics.caput("2bmb:tableFly2:sseq2.PROC", 1, wait=True, timeout=1000.0)                                
    epics.caput(rotStage+".STOP",1, wait=True, timeout=1000.0)
    epics.caput(rotStage+".SET","Set", wait=True, timeout=1000.0) 
    epics.caput(rotStage+".VAL",epics.caget(rotStage+".VAL")%360.0, wait=True, timeout=1000.0) 
    epics.caput(rotStage+".SET","Use", wait=True, timeout=1000.0) 
    epics.caput(rotStage+".VELO","30", wait=True, timeout=1000.0)    
    epics.caput(rotStage+".ACCL","3", wait=True, timeout=1000.0)                
    epics.caput(rotStage+".VAL","0", wait=True, timeout=1000.0)
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)  
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)               
    print "Edge is reset!"





def _DimaxSingleScanTempTrigger(exposureTime=0.01, slewSpeed=10,angEnd = 180,
                numProjPerSweep=1024,
                samInPos=0, samOutPos=-4,
                roiSizeX = 1200, roiSizeY = 800,trigTemp = 550,
                accl = 90.0):
    """
        Customize for Brian Patterson in situ loading experiments.
    """
                
    # tomo configurations -- start
    initDimax()    
    shutter = "2bma:A_shutter"
    samStage = "2bma:m49"
    rotStage = "2bmb:m100"
    PSO = "2bmb:PSOFly1"
    BL = "2bmb"                
    camPrefix = "PCOIOC2"                
    camShutterMode = 'Rolling'                
    # tomo configurations -- end                    

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
                '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                

    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
    
    scanDelta = 1.0*angEnd/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 20)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    print "Scan starts ..."                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
    filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep
    
    # test camera -- start
    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    # test camera -- end
    
    # set scan parameters -- start
    _dimaxSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
    _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)
    # set scan parameters -- end
                
    print "start sample scan ... "    
    preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")
    while ((epics.caget(BL+":ET2k:1:Temperature.VAL")-trigTemp)*(preTemp-trigTemp)>0):    
        preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")            
        time.sleep(0.5)
        
    _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)                        
    
    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
    print "sample scan is done!"                          
    # scan sample -- end
    
    # set for white field -- start
    print "Acquiring flat images ..."     
    _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
    print "flat is done!"                
    # set for white field -- end
    
    # set for dark field -- start
    print "Acquiring dark images ..."                
    _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
    print "dark is done!"  

    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
    # set for new scans -- end
    print "Scan is done."    









#def DimaxSingleScan(exposureTime=0.0004, slewSpeed=360,angEnd = 180,
#                numProjPerSweep=1000,
#                samInPos=0, samOutPos=12,
#                roiSizeX = 2016, roiSizeY = 600,
#                hutch = 'A',
#                accl = 180.0):
def DimaxSingleScan(exposureTime=0.05, slewSpeed=2,angEnd = 180,
                numProjPerSweep=1501,
                samInPos=0, samOutPos=4,
                roiSizeX = 2016, roiSizeY = 1300,
                hutch = 'A',
                accl = 2.0):    
    """
        Customize for Brian Patterson in situ loading experiments.
    """
                
    # tomo configurations -- start
    if hutch == 'A' or hutch == 'a':                
        initDimax()    
        shutter = "2bma:A_shutter"
        samStage = "2bma:m49"
        rotStage = "2bmb:m82"
        PSO = "2bmb:PSOFly2"
        BL = "2bmb"                
        camPrefix = "PCOIOC2"
        camShutterMode = 'Rolling'                
        # tomo configurations -- end                    
    
        if camPrefix == 'PCOIOC3':
            cam = 'edge'
        elif camPrefix == 'PCOIOC2':
            cam = 'dimax'    
    
        if samStage.split(':')[0] == '2bma':
            station = 'AHutch'
        elif samStage.split(':')[0] == '2bmb':    
            station = 'BHutch'                                
        filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
        filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                    epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                    epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                    cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                    epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                    str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                    camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                    epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                    epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                    str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
                    '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
                    
        epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
                    
        epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
        
        scanDelta = 1.0*angEnd/numProjPerSweep
        acclTime = 1.0*slewSpeed/accl
        frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 20)                
    
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                    
        print "Scan starts ..."                
    #    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                    
        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
        pathSep =  filepath.rsplit('/')
        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
    
        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)
                            
        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
                
        logFile = open(logFileName,'w')
        logFile.close()                
        print "Your scan is logged in ", logFileName
        
        numImage = numProjPerSweep
        
        # test camera -- start
        _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
        # test camera -- end
        
        # set scan parameters -- start
        _dimaxSet(numImage, exposureTime, frate)                            
        _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                 
        # set scan parameters -- end
                    
        print "start sample scan ... "    
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(2)        
        _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,filepath,filename,PSO = PSO,rotStage=rotStage)                        
        epics.caput('PCOIOC2:HDF1:Capture.VAL','Done',wait=True,timeout=1000.0)
        
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
        # set for white field -- start
        print "Acquiring flat images ..."    
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(5)                
        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput('PCOIOC2:HDF1:Capture.VAL','Done',wait=True,timeout=1000.0)
        print "flat is done!"                
        # set for white field -- end
        
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput('PCOIOC2:HDF1:Capture.VAL','Done',wait=True,timeout=1000.0)              
        print "dark is done!"  
    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
        
        # set for new scans -- start
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)    
    elif hutch == 'B' or hutch == 'b':                
        initDimax()    
        shutter = "2bma:B_shutter"
        samStage = "2bmb:m63"
        rotStage = "2bmb:m100"
        PSO = "2bmb:PSOFly2"
        BL = "2bmb"                
        camPrefix = "PCOIOC2"
        camShutterMode = 'Rolling'                
        # tomo configurations -- end                    
    
        if camPrefix == 'PCOIOC3':
            cam = 'edge'
        elif camPrefix == 'PCOIOC2':
            cam = 'dimax'    
    
        if samStage.split(':')[0] == '2bma':
            station = 'AHutch'
        elif samStage.split(':')[0] == '2bmb':    
            station = 'BHutch'                                
        filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
        filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                    epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                    epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                    cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                    epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                    str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                    camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                    epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                    epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                    str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
                    '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
                    
        epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
                    
        epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
        
        scanDelta = 1.0*angEnd/numProjPerSweep
        acclTime = 1.0*slewSpeed/accl
        frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 20)                
    
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                    
        print "Scan starts ..."                
    #    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                    
        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
        pathSep =  filepath.rsplit('/')
        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
    
        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)
                            
        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
                
        logFile = open(logFileName,'w')
        logFile.close()                
        print "Your scan is logged in ", logFileName
        
        numImage = numProjPerSweep
        
        # test camera -- start
        _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
        # test camera -- end
        
        # set scan parameters -- start
        _dimaxSet(numImage, exposureTime, frate)                            
        _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                 
        # set scan parameters -- end
                    
        print "start sample scan ... "    
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(2)        
        _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,filepath,filename,PSO = PSO,rotStage=rotStage)                        
        
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
        # set for white field -- start
        print "Acquiring flat images ..."    
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(5)                
        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
        print "flat is done!"                
        # set for white field -- end
        
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
        print "dark is done!"  
    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
        
        # set for new scans -- start
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                                    
    # set for new scans -- end
    print "Scan is done."    












def DimaxMultiScan(exposureTime=0.003, slewSpeed=90,angEnd = 180,
                numProjPerSweep=600, repeats = 21,
                samInPos=0, samOutPos=3,
                roiSizeX = 1584, roiSizeY = 2016,
                hutch = 'A',
                delay=0, accl = 90.0, timeFile=0, clShutter=1):
    """
        Customize for Brian Patterson in situ loading experiments.
    """
                
    # tomo configurations -- start
    if hutch == 'A' or hutch == 'a':                
        initDimax()    
        shutter = "2bma:A_shutter"
        posStage = "2bma:m20" 
        samStage = "2bma:m49"
        rotStage = "2bmb:m82"
        PSO = "2bmb:PSOFly2"
        BL = "2bmb"                
        camPrefix = "PCOIOC2"
        camShutterMode = 'Rolling'                
        # tomo configurations -- end                    
    
        if camPrefix == 'PCOIOC3':
            cam = 'edge'
        elif camPrefix == 'PCOIOC2':
            cam = 'dimax'    
    
        if samStage.split(':')[0] == '2bma':
            station = 'AHutch'
        elif samStage.split(':')[0] == '2bmb':    
            station = 'BHutch'                        
                                
        filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#        filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                    epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#                    epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#                    cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                    epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                    str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#                    camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                    epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                    epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                    str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
#                    '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
                    
        epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
        epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
        
        scanDelta = 1.0*angEnd/numProjPerSweep
        acclTime = 1.0*slewSpeed/accl
        frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 100)                
    
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                    
        print "Scan starts ..."                
    #    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                    
        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#        pathSep =  filepath.rsplit('/')
#        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])    
#        if not os.path.exists(logFilePath):
#            os.makedirs(logFilePath)                    
#                            
#        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#                
#        logFile = open(logFileName,'w')
#        logFile.close()                
#        print "Your scan is logged in ", logFileName
        
#        numImage = (numProjPerSweep+1)*repeats + 3
        numImage = (numProjPerSweep+1)*repeats
        
        # test camera -- start
        _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
        # test camera -- end
        
        # set scan parameters -- start
        _dimaxSet(numImage, exposureTime, frate)                            
        _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)        
        # set scan parameters -- end

        if timeFile == 1:
            tf = open('/local/user2bmb/timeSeq.txt')                    
            timeSeq = tf.readlines()
            tf.close()   
                  
        print "start sample scan ... "    
        cnt = 0  
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        for ii in range(repeats): 
#            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
#            time.sleep(2) 
            if timeFile == 1:
                delay = float(timeSeq[ii]) 
            timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
                         
            filepath = os.path.join(filepath_top, \
               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
                              
            _dimaxAcquisitionWODump(samInPos,samStage,numImage,shutter,PSO = PSO,rotStage=rotStage)                            
#            logFile = open(logFileName,'a')                                
#            logFile.write("Scan #" + str(cnt-1) + " was done at time: " + time.asctime() + '\n')                                    
#            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
            cnt += 1                    
#            logFile.close()                                
            print "scan #: ", str(ii+1), " is done at" + time.asctime() + "!"            
            if cnt != repeats:
                time.sleep(delay)                                                            
    
        print "Saving sample data ..."  
        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                    
        _dimaxDump(filepath, filename)                                             
        while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):
    #    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:NumImagesCounter_RBV.VAL")):                    
            time.sleep(1)    
        
#        logFile = open(logFileName,'a')
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')
#        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
        # set for white field -- start
        print "Acquiring flat images ..."     
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(2)                
        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
        print "flat is done!"                
        # set for white field -- end
        
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
        print "dark is done!"  
    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
        
        # set for new scans -- start
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
        # set for new scans -- end
    elif hutch == 'B' or hutch == 'b':                
        initDimax()    
        shutter = "2bma:B_shutter"
        samStage = "2bmb:m63"
        rotStage = "2bmb:m100"
        PSO = "2bmb:PSOFly2"
        BL = "2bmb"                
        camPrefix = "PCOIOC2"
        camShutterMode = 'Rolling'                
        # tomo configurations -- end                    
    
        if camPrefix == 'PCOIOC3':
            cam = 'edge'
        elif camPrefix == 'PCOIOC2':
            cam = 'dimax'    
    
        if samStage.split(':')[0] == '2bma':
            station = 'AHutch'
        elif samStage.split(':')[0] == '2bmb':    
            station = 'BHutch'                                
        filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
        filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                    epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                    epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                    cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                    epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                    str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                    camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                    epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                    epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                    str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
                    '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
                    
        epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
        epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
        
        scanDelta = 1.0*angEnd/numProjPerSweep
        acclTime = 1.0*slewSpeed/accl
        frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 100)                
    
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                    
        print "Scan starts ..."                
    #    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                    
        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
        pathSep =  filepath.rsplit('/')
        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])    
        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)        
                            
        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
                
        logFile = open(logFileName,'w')
        logFile.close()                
        print "Your scan is logged in ", logFileName
        
        numImage = (numProjPerSweep+1)*repeats
        
        # test camera -- start
        _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
        # test camera -- end
        
        # set scan parameters -- start
        _dimaxSet(numImage, exposureTime, frate)                            
        _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)        
        # set scan parameters -- end
                    
        print "start sample scan ... "    
        cnt = 0    
        for ii in range(repeats): 
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
            time.sleep(2)                                
            _dimaxAcquisitionWODump(samInPos,samStage,numImage,shutter,PSO = PSO,rotStage=rotStage)                            
            logFile = open(logFileName,'a')                                
            logFile.write("Scan #" + str(cnt-1) + " was done at time: " + time.asctime() + '\n')                                    
            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
            cnt += 1                    
            logFile.close()                                
            print "scan #: ", str(ii+1), " is done!"            
            if cnt != repeats:
                time.sleep(delay-2)                                                            
    
        print "Saving sample data ..."  
        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                    
        _dimaxDump(filepath, filename)                                             
        while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):
    #    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:NumImagesCounter_RBV.VAL")):                    
            time.sleep(1)    
        
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
        # set for white field -- start
        print "Acquiring flat images ..."     
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(2)                
        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
        print "flat is done!"                
        # set for white field -- end
        
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
        print "dark is done!"  
    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
        
        # set for new scans -- start
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
        # set for new scans -- end                                    
    print "Scan is done."    







#def DimaxMultiPosStopGoScan(exposureTime=0.004, slewSpeed=30,angEnd = 180,
#                      numProjPerSweep=1201,samInPos=0, samOutPos=10,
#                      roiSizeX = 2016, roiSizeY = 1008,posInit = 9.3, 
#                      posStep = -2, posNum = 1, delay = 0,accl = 30, 
#                      timeFile=0, clShutter=1,dumpPerScan=0):    
#    """ Multiple poistion scans along vertical direction with dimax camera
#                
#      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
#              it assumes rotation axis is at image center at posInit.
#                    
#      refYofX0: Y where rotation axis coincide to the image center
#    """
#                
#    # tomo configurations -- start
#    initDimax()    
#    shutter = "2bma:A_shutter"
#    samStage = "2bma:m49"
#    posStage = "2bma:m20"
#    rotStage = "2bmb:m82"
#    PSO = "2bmb:PSOFly2"
#    BL = "2bmb"                
#    camPrefix = "PCOIOC2"                
#    camShutterMode = 'Rolling'              
#    # tomo configurations -- end                                                     
#
#    if camPrefix == 'PCOIOC3':
#        cam = 'edge'
#    elif camPrefix == 'PCOIOC2':
#        cam = 'dimax'    
#
#    if samStage.split(':')[0] == '2bma':
#        station = 'AHutch'
#    elif samStage.split(':')[0] == '2bmb':    
#        station = 'BHutch'                                
#    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#                
#    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                
#
#    posInit = epics.caget(posStage+".VAL")
#    epics.caput(BL+":caputRecorderArg9Value.VAL",str(posInit),wait=True,timeout=1000.0)                
#    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
#    
#    scanDelta = 1.0*angEnd/numProjPerSweep
#    acclTime = 1.0*slewSpeed/accl
##    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 200)    
#    frate = int(1.1/exposureTime+2000)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#                
#    print "Scan starts ..."                
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
#    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
#    
##    numImage = numProjPerSweep + 20
##    numImage = numProjPerSweep 
#    if dumpPerScan == 1:
#        numImage = numProjPerSweep
#    elif dumpPerScan == 0:    
#        numImage = numProjPerSweep*posNum
#    
#    # test camera -- start
#    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#    # test camera -- end
#                
#    print "start sample scan ... "
#
#    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numImage), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
#    time.sleep(2) 
#
#
#    if dumpPerScan == 1:               
#        for ii in range(posNum):
#            print "scan at position #", ii+1, " starts at "+time.asctime()+"!"
#            timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
#                   
#            filepath = os.path.join(filepath_top, \
#                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ str(ii).zfill(2)+'_'+\
#                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
#                   
#    
#                   
#            filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#            pathSep =  filepath.rsplit('/')
#            logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#        
#            if not os.path.exists(logFilePath):
#                os.makedirs(logFilePath)
#                                
#            logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#                    
#            logFile = open(logFileName,'w')
#            logFile.close()                
#            print "Your scan is logged in ", logFileName
#                                                
#            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
#            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)         
#            _dimaxSet(numImage, exposureTime, frate)
#            _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage) 
#            _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,filepath,filename,PSO = PSO,rotStage=rotStage)                                                          
#    #
#            print "Acquiring flat images ..."    
#            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
#            time.sleep(2)                
#            _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
#            epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#            print "flat is done!"                
#            # set for white field -- end
#            
#            # set for dark field -- start
#            print "Acquiring dark images ..."                    
#            _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
#            epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
#            print "dark is done!" 
#            
#    #        _dimaxAcquisitionWODump(samInPos,samStage,numImage,shutter,PSO = PSO,rotStage=rotStage)
#            time.sleep(1)                                                            
#            print "scan at position #", ii+1, " is done at "+time.asctime()+"!"
#            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
#            if ii != (posNum-1):
#                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#                time.sleep(delay)  
#    
#        logFile = open(logFileName,'a')
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')
#        logFile.close()                                                                    
#        print "sample scan is done!"                          
#        # scan sample -- end
#
#    
#    elif dumpPerScan == 0:
#        _dimaxSet(numImage, exposureTime, frate)
#        timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
#                   
#        filepath = os.path.join(filepath_top, \
#                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ str(0).zfill(2)+'_'+\
#                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
#        for ii in range(posNum):
#            print "scan at position #", ii+1, " starts at "+time.asctime()+"!"              
#                                   
#            filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#            pathSep =  filepath.rsplit('/')
#            logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#        
#            if not os.path.exists(logFilePath):
#                os.makedirs(logFilePath)
#                                
#            logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#                    
#            logFile = open(logFileName,'w')
#            logFile.close()                
#            print "Your scan is logged in ", logFileName
#                                                
#            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
#            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                     
#            _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)  
#            _dimaxAcquisitionWODump(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
#
#            time.sleep(1)                                                            
#            print "scan at position #", ii+1, " is done at "+time.asctime()+"!"
#            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
#            if ii != (posNum-1):
#                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#                time.sleep(delay)
#    
#    # this section is for _dimaxAcquisitionWODump -- start
#        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
#        print "Saving sample data ..."                 
#        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                    
#        _dimaxDump(filepath, filename)                 
#                
#                                                    
#        while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):
#            time.sleep(1)    
#    # this section is for _dimaxAcquisitionWODump -- end    
#    
#        logFile = open(logFileName,'a')
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')
#        logFile.close()                                                                    
#        print "sample scan is done!"                          
#        # scan sample -- end
#    
#        print "Acquiring flat images ..."    
#        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
#        time.sleep(2)                
#        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
#        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#        print "flat is done!"                
#        # set for white field -- end
#        
#        # set for dark field -- start
#        print "Acquiring dark images ..."                    
#        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
#        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
#        print "dark is done!" 
#    
#
#    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end
#    
#    # set for new scans -- start
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
##    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)                        
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
#    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
#        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#
##    posCurr = epics.caget(posStage + ".VAL")    
##    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
##    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
##    epics.caput(BL + ":caputRecorderArg13Value.VAL",str(posCurr), wait=True, timeout=1000.0)    
#    # set for new scans -- end
#    print "Scan is done." 






def DimaxMultiPosScan(exposureTime=0.5, slewSpeed=0.1,angEnd = 360,
                      numProjPerSweep=3602,samInPos=0, samOutPos=3,
                      roiSizeX = 2016, roiSizeY = 2016,posInit = 9.3, 
                      posStep = 1, posNum = 1, delay = 0,accl = 0.1, 
                      timeFile=0, clShutter=1,dumpPerScan=1):    
    """ Multiple poistion scans along vertical direction with dimax camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
                    
      refYofX0: Y where rotation axis coincide to the image center
    """
                
    # tomo configurations -- start
    initDimax()    
    shutter = "2bma:A_shutter"
    samStage = "2bma:m49"
    posStage = "2bma:m20"
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"
    BL = "2bmb"                
    camPrefix = "PCOIOC2"                
    camShutterMode = 'Rolling'              
    # tomo configurations -- end                                                     

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                

    posInit = epics.caget(posStage+".VAL")
    epics.caput(BL+":caputRecorderArg9Value.VAL",str(posInit),wait=True,timeout=1000.0)                
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
    
    scanDelta = 1.0*angEnd/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
#    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 200)    
    frate = int(1.1/exposureTime+2000)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    print "Scan starts ..."                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
#    numImage = numProjPerSweep + 20
#    numImage = numProjPerSweep 
    if dumpPerScan == 1:
        numImage = numProjPerSweep
    elif dumpPerScan == 0:    
        numImage = numProjPerSweep*posNum
    
    # test camera -- start
    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    # test camera -- end
                
    print "start sample scan ... "

    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numImage), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
    time.sleep(2) 


    if dumpPerScan == 1:               
        for ii in range(posNum):
            print "scan at position #", ii+1, " starts at "+time.asctime()+"!"
            timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
                   
            filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ str(ii).zfill(2)+'_'+\
                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
                   
    
                   
            filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
            pathSep =  filepath.rsplit('/')
            logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
        
            if not os.path.exists(logFilePath):
                os.makedirs(logFilePath)
                                
            logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
                    
            logFile = open(logFileName,'w')
            logFile.close()                
            print "Your scan is logged in ", logFileName
                                                
            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)         
            _dimaxSet(numImage, exposureTime, frate)
            _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage) 
            _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,filepath,filename,PSO = PSO,rotStage=rotStage) 
                                                          
    
    #        global ansCritical
    #        ansCritical = 'no'                
    #        top = Tkinter.Tk()
    #        def confirm():
    #            global ansCritical
    #            ans = mbox.askquestion('Action','Have you manually remove the sample?',icon='warning')
    #            if ans != 'yes':
    #                print  'Please remove the sample from tomo stage first to proceed reference image acquisition...'
    #            else:
    #                print 'Very good. You need to close the Action Box'
    #                ansCritical = ans
    #                
    #        B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
    #        B1.pack()
    #        top.mainloop() 
    #        
    #        print ansCritical
    #        if ansCritical != ('yes' or 'Yes'):
    #            print ansCritical
    #            print 'I cannot take reference images with the sample in the beam!!!'
    #            return False
    #        else:
    #            print 'Good to go ...'  
    #
            print "Acquiring flat images ..."    
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
            time.sleep(2)                
            _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
            epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
            print "flat is done!"                
            # set for white field -- end
            
            # set for dark field -- start
            print "Acquiring dark images ..."                    
            _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
            epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
            print "dark is done!" 
            
    #        _dimaxAcquisitionWODump(samInPos,samStage,numImage,shutter,PSO = PSO,rotStage=rotStage)
            time.sleep(1)                                                            
            print "scan at position #", ii+1, " is done at "+time.asctime()+"!"
            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
            if ii != (posNum-1):
                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
                time.sleep(delay)  
    
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
    #    global ansCritical
    #    ansCritical = 'no'                
    #    top = Tkinter.Tk()
    #    def confirm():
    #        global ansCritical
    #        ans = mbox.askquestion('Action','Have you manually remove the sample?',icon='warning')
    #        if ans != 'yes':
    #            print  'Please remove the sample from tomo stage first to proceed reference image acquisition...'
    #        else:
    #            print 'Very good. You need to close the Action Box'
    #            ansCritical = ans
    #            
    #    B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
    #    B1.pack()
    #    top.mainloop() 
    #    
    #    print ansCritical
    #    if ansCritical != ('yes' or 'Yes'):
    #        print ansCritical
    #        print 'I cannot take reference images with the sample in the beam!!!'
    #        return False
    #    else:
    #        print 'Good to go ...'   
    
    elif dumpPerScan == 0:
        _dimaxSet(numImage, exposureTime, frate)
        timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
                   
        filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ str(0).zfill(2)+'_'+\
                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
        for ii in range(posNum):
            print "scan at position #", ii+1, " starts at "+time.asctime()+"!"
#            timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
#                   
#            filepath = os.path.join(filepath_top, \
#                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ str(ii).zfill(1+1)+'_'+\
#                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
                   
    
                   
            filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
            pathSep =  filepath.rsplit('/')
            logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
        
            if not os.path.exists(logFilePath):
                os.makedirs(logFilePath)
                                
            logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
                    
            logFile = open(logFileName,'w')
            logFile.close()                
            print "Your scan is logged in ", logFileName
                                                
            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                     
            _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage)  
            _dimaxAcquisitionWODump(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
                                                          
    
    #        global ansCritical
    #        ansCritical = 'no'                
    #        top = Tkinter.Tk()
    #        def confirm():
    #            global ansCritical
    #            ans = mbox.askquestion('Action','Have you manually remove the sample?',icon='warning')
    #            if ans != 'yes':
    #                print  'Please remove the sample from tomo stage first to proceed reference image acquisition...'
    #            else:
    #                print 'Very good. You need to close the Action Box'
    #                ansCritical = ans
    #                
    #        B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
    #        B1.pack()
    #        top.mainloop() 
    #        
    #        print ansCritical
    #        if ansCritical != ('yes' or 'Yes'):
    #            print ansCritical
    #            print 'I cannot take reference images with the sample in the beam!!!'
    #            return False
    #        else:
    #            print 'Good to go ...'  

            time.sleep(1)                                                            
            print "scan at position #", ii+1, " is done at "+time.asctime()+"!"
            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
            if ii != (posNum-1):
                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
                time.sleep(delay)
    
    # this section is for _dimaxAcquisitionWODump -- start
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
        print "Saving sample data ..."                 
        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                    
        _dimaxDump(filepath, filename)                 
                
                                                    
        while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):
            time.sleep(1)    
    # this section is for _dimaxAcquisitionWODump -- end    
    
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
    #    global ansCritical
    #    ansCritical = 'no'                
    #    top = Tkinter.Tk()
    #    def confirm():
    #        global ansCritical
    #        ans = mbox.askquestion('Action','Have you manually remove the sample?',icon='warning')
    #        if ans != 'yes':
    #            print  'Please remove the sample from tomo stage first to proceed reference image acquisition...'
    #        else:
    #            print 'Very good. You need to close the Action Box'
    #            ansCritical = ans
    #            
    #    B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
    #    B1.pack()
    #    top.mainloop() 
    #    
    #    print ansCritical
    #    if ansCritical != ('yes' or 'Yes'):
    #        print ansCritical
    #        print 'I cannot take reference images with the sample in the beam!!!'
    #        return False
    #    else:
    #        print 'Good to go ...'  
    
        print "Acquiring flat images ..."    
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        time.sleep(2)                
        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
        print "flat is done!"                
        # set for white field -- end
        
        # set for dark field -- start
        print "Acquiring dark images ..."                    
        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
        print "dark is done!" 
    

    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)                        
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                

#    posCurr = epics.caget(posStage + ".VAL")    
#    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
#    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
#    epics.caput(BL + ":caputRecorderArg13Value.VAL",str(posCurr), wait=True, timeout=1000.0)    
    # set for new scans -- end
    print "Scan is done." 





#
#def DimaxMultiPosScan(exposureTime=0.004, slewSpeed=30,angEnd = 180,
#                numProjPerSweep=1201,
#                samInPos=0, samOutPos=10,
#                roiSizeX = 2016, roiSizeY = 1008,
#                posInit = 9.3, posStep = -2, posNum = 1, axisShift = 0.0, refYofX0 = 23.46925,
#                delay = 0,accl = 30, timeFile=0, clShutter=1):    
#    """ Multiple poistion scans along vertical direction with dimax camera
#                
#      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
#              it assumes rotation axis is at image center at posInit.
#                    
#      refYofX0: Y where rotation axis coincide to the image center
#    """
#                
#    # tomo configurations -- start
#    initDimax()    
#    shutter = "2bma:A_shutter"
#    samStage = "2bma:m49"
#    posStage = "2bma:m20"
#    rotStage = "2bmb:m82"
#    PSO = "2bmb:PSOFly2"
#    BL = "2bmb"                
#    camPrefix = "PCOIOC2"                
#    camShutterMode = 'Rolling'
#    samInInitPos = samInPos                
#    # tomo configurations -- end    
#
#    posCurr = epics.caget(posStage + ".VAL")    
#    posStageOffset = axisShift * (posCurr - refYofX0)/1000.0
#    epics.caput(samStage + ".VAL",str(posStageOffset), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
#    epics.caput(BL + ":caputRecorderArg13Value.VAL",str(posCurr), wait=True, timeout=1000.0)                    
#                
#    if posStep > 0:
#        axisShift = np.abs(axisShift)    
#    elif posStep < 0:    
#        axisShift = -np.abs(axisShift)                                
#
#    if camPrefix == 'PCOIOC3':
#        cam = 'edge'
#    elif camPrefix == 'PCOIOC2':
#        cam = 'dimax'    
#
#    if samStage.split(':')[0] == '2bma':
#        station = 'AHutch'
#    elif samStage.split(':')[0] == '2bmb':    
#        station = 'BHutch'                                
#    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#                
#    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                
#
#    posInit = epics.caget(posStage+".VAL")
#    epics.caput(BL+":caputRecorderArg9Value.VAL",str(posInit),wait=True,timeout=1000.0)                
#    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
#    
#    scanDelta = 1.0*angEnd/numProjPerSweep
#    acclTime = 1.0*slewSpeed/accl
##    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 200)    
#    frate = int(1.1/exposureTime+2000)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#                
#    print "Scan starts ..."                
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
#    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
#    
##    numImage = numProjPerSweep + 20
##    numImage = numProjPerSweep  
#    numImage = numProjPerSweep*posNum
#    
#    # test camera -- start
#    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#    # test camera -- end
#                
#    print "start sample scan ... "
#
#    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numImage), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
#    time.sleep(2)                
#    for ii in range(posNum):
#        print "scan at position #", ii+1, " starts at "+time.asctime()+"!"
#        timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
##        filepath = os.path.join(filepath_top, \
##               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
##               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
##               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
##               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
##               '0DegPos'+str(int(epics.caget("2bmS1:m2.RBV")*1000)/1000.0)+'mm_'+\
##               '90DegPos'+str(int(epics.caget("2bmS1:m1.RBV")*1000)/1000.0)+'mm_'+\
##               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
##               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
##               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
##               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
##               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
##               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
##               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
#               
#        filepath = os.path.join(filepath_top, \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
#               
#
#               
#        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#        pathSep =  filepath.rsplit('/')
#        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    
#        if not os.path.exists(logFilePath):
#            os.makedirs(logFilePath)
#                            
#        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#                
#        logFile = open(logFileName,'w')
#        logFile.close()                
#        print "Your scan is logged in ", logFileName
#                                            
#        epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
#        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)         
##        samInPos = samInInitPos + ii*axisShift*posStep/1000.0 
#        _dimaxSet(numImage, exposureTime, frate)
#        _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage) 
#        _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,filepath,filename,PSO = PSO,rotStage=rotStage) 
##        _dimaxAcquisitionWODump(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
#                                                      
#
##        global ansCritical
##        ansCritical = 'no'                
##        top = Tkinter.Tk()
##        def confirm():
##            global ansCritical
##            ans = mbox.askquestion('Action','Have you manually remove the sample?',icon='warning')
##            if ans != 'yes':
##                print  'Please remove the sample from tomo stage first to proceed reference image acquisition...'
##            else:
##                print 'Very good. You need to close the Action Box'
##                ansCritical = ans
##                
##        B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
##        B1.pack()
##        top.mainloop() 
##        
##        print ansCritical
##        if ansCritical != ('yes' or 'Yes'):
##            print ansCritical
##            print 'I cannot take reference images with the sample in the beam!!!'
##            return False
##        else:
##            print 'Good to go ...'  
##
#        print "Acquiring flat images ..."    
#        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
#        time.sleep(2)                
#        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
#        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#        print "flat is done!"                
#        # set for white field -- end
#        
#        # set for dark field -- start
#        print "Acquiring dark images ..."                    
#        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
#        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
#        print "dark is done!" 
#        
##        _dimaxAcquisitionWODump(samInPos,samStage,numImage,shutter,PSO = PSO,rotStage=rotStage)
#        time.sleep(1)                                                            
#        print "scan at position #", ii+1, " is done at "+time.asctime()+"!"
#        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
#        if ii != (posNum-1):
#            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#            time.sleep(delay)
#
### this section is for _dimaxAcquisitionWODump -- start
##    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
##    print "Saving sample data ..."                 
##    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
##    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                    
##    _dimaxDump(filepath, filename)                 
##            
##                                                
##    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):
##        time.sleep(1)    
### this section is for _dimaxAcquisitionWODump -- end    
#
#    logFile = open(logFileName,'a')
#    logFile.write("Scan was done at time: " + time.asctime() + '\n')
#    logFile.close()                                                                    
#    print "sample scan is done!"                          
#    # scan sample -- end
#    
##    global ansCritical
##    ansCritical = 'no'                
##    top = Tkinter.Tk()
##    def confirm():
##        global ansCritical
##        ans = mbox.askquestion('Action','Have you manually remove the sample?',icon='warning')
##        if ans != 'yes':
##            print  'Please remove the sample from tomo stage first to proceed reference image acquisition...'
##        else:
##            print 'Very good. You need to close the Action Box'
##            ansCritical = ans
##            
##    B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
##    B1.pack()
##    top.mainloop() 
##    
##    print ansCritical
##    if ansCritical != ('yes' or 'Yes'):
##        print ansCritical
##        print 'I cannot take reference images with the sample in the beam!!!'
##        return False
##    else:
##        print 'Good to go ...'  
#
##    print "Acquiring flat images ..."    
##    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
##    time.sleep(2)                
##    _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
##    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
##    print "flat is done!"                
##    # set for white field -- end
##    
##    # set for dark field -- start
##    print "Acquiring dark images ..."                    
##    _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
##    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
##    print "dark is done!"  
#
#    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end
#    
#    # set for new scans -- start
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
##    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)                        
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
#    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
#        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#
##    posCurr = epics.caget(posStage + ".VAL")    
##    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
##    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
##    epics.caput(BL + ":caputRecorderArg13Value.VAL",str(posCurr), wait=True, timeout=1000.0)    
#    # set for new scans -- end
#    print "Scan is done."    






def DimaxBackforthScan(exposureTime=0.001, slewSpeed=180, angEnd=180, 
                numSweep = 20,numProjPerSweep=601,
                samInPos=0, samOutPos=17,
                roiSizeX = 2016, roiSizeY = 1008,
                delay = 0,accl = 180, timeFile=0, clShutter=1):    
    """ Multiple poistion scans along vertical direction with dimax camera with 
        backforth scan scheme                
    """
                
    # tomo configurations -- start
    initDimax()    
    shutter = "2bma:A_shutter"
    samStage = "2bma:m49"
    posStage = "2bma:m20"
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"
    BL = "2bmb"                
    camPrefix = "PCOIOC2"                
    camShutterMode = 'Rolling'                
    # tomo configurations -- end    
   
    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)                      
                               

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                
             
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
    
    scanDelta = 1.0*angEnd/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.1/exposureTime+2000)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    print "Scan starts ..."                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
     
    numImage = numProjPerSweep*numSweep
    
    # test camera -- start
    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    # test camera -- end
                
    print "Scan starts ... "

    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numImage), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
    time.sleep(2)                

    timestamp = [x for x in time.asctime().rsplit(' ') if x!=''] 
           
    filepath = os.path.join(filepath_top, \
           epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
           epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
           epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
           'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
           timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
           cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
           epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
           str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
           camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
           epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
           epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
           str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
           '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
           

           
    filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepath.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName

    _dimaxSet(numImage, exposureTime, frate)

#    print "Acquiring flat images ..."    
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
#    time.sleep(2)                
#    _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
#    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#    print "flat is done!"                
#    # set for white field -- end
#    
#    # set for dark field -- start
#    print "Acquiring dark images ..."                    
#    _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
#    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
#    print "dark is done!"  
#    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end

    print "Sample scan starts at "+time.asctime()+"!"                                        
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)         
#    _dimaxSet(numImage, exposureTime, frate)
    _setPSO(slewSpeed, scanDelta, acclTime, angEnd=angEnd, PSO=PSO,rotStage=rotStage) 
    _dimaxAcquisitionBackforthWODump(samInPos,samStage,numSweep,delay,shutter,rotStage=rotStage)
                                                          
    time.sleep(1)                                                            
    print "Sample scan is done at "+time.asctime()+"!"
    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    


# this section is for _dimaxAcquisitionWODump -- start
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    print "Saving sample data ..."                 
    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                    
    _dimaxDump(filepath, filename)                 
            
                                                
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):
        time.sleep(1)    
# this section is for _dimaxAcquisitionWODump -- end    

    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
    print "sample scan is done!"                          
    # scan sample -- end

    print "Acquiring flat images ..."    
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
    time.sleep(2)                
    _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
    print "flat is done!"                
    # set for white field -- end
    
    # set for dark field -- start
    print "Acquiring dark images ..."                    
    _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)             
    print "dark is done!"  

    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                                       
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
    # set for new scans -- end
        
    print "Scan is done." 






def _Dimax2D(exposureTime=0.0005,
                numImage=12000,
                samInPos=0, samOutPos=60,
                roiSizeX = 2016, roiSizeY = 1008):
    """
        Customize for Brian Patterson in situ loading experiments.
    """
                
    # tomo configurations -- start
    initDimax()    
    shutter = "2bma:B_shutter"    
    samStage = "2bmb:m12"                
    BL = "2bmb"                
    camPrefix = "PCOIOC2"                
    # tomo configurations -- end    

    frate = 1.0/exposureTime                        
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
                
    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                            
    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
    filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your measurement is logged in ", logFileName
    
    # test camera -- start
    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = "")

    camPrefix = "PCOIOC2"
    print "Set writer ..."                
    epics.caput(camPrefix + ":cam1:NumImages.VAL",str(numImage-0), wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL","0", wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:pco_is_frame_rate_mode.VAL","FrateExp", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    print "ready to take images ... "                
    while (epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")):    
        time.sleep(0.1)        
    #    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
                
    epics.caput(camPrefix + ":cam1:FrameType.VAL","Normal", wait=True, timeout=1000.0) 
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numImage), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    

    while epics.caget(camPrefix + ":cam1:DetectorState_RBV.VAL") != 0:
        time.sleep(1)
    epics.caput(shutter + ":close.VAL", 1, wait=True, timeout=1000.0)                                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory.VAL",1, wait=True, timeout=1000.0)                 
                                
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")):    
        time.sleep(1)    
    
    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
    print "sample scan is done!"                          
    # scan sample -- end
    
    # set for white field -- start
    print "Acquiring flat images ..."     
    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:FrameType.VAL","FlatField", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
    time.sleep(2)     
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(samStage + ".VAL","0", wait=True, timeout=1000.0)                
    print "flat is done!"                
    # set for white field -- end
    
    # set for dark field -- start
    print "Acquiring dark images ..."                
    time.sleep(2)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:FrameType.VAL","Background", wait=True, timeout=1000.0)             
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)               
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
    time.sleep(2)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    
    print "dark is done!"  

    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
    # set for new scans -- end
    print "Measurement is done."   











def _Edge2D(exposureTime=0.003, frameRate=30,
                numImage=12000,
                samInPos=0, samOutPos=-10,
                roiSizeX = 2400, roiSizeY = 600):
    """
        Customize for Brian Patterson in situ loading experiments.
    """
                
    # tomo configurations -- start
    initEdge()
#    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
    camScanSpeed = "Normal"
    camShutterMode = "Global"                
    shutter = "2bma:A_shutter"    
    samStage = "2bma:m49"                
    BL = "2bmb"                
    camPrefix = "PCOIOC3"
    PSO = "2bmb:PSOFly1"                
    # tomo configurations -- end    

    frate = frameRate                        
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
                
    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your measurement is logged in ", logFileName
    
    # test camera -- start
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)

    print "Set writer ..."                
    epics.caput(camPrefix + ":cam1:NumImages.VAL",str(numImage-0), wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL","0", wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:pco_is_frame_rate_mode.VAL","FrateExp", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate+1), wait=True, timeout=1000.0)
    time.sleep(1)                
    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)

    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
    time.sleep(2)                
    print "start to take images ... "                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
                                
    while epics.caget(camPrefix + ":cam1:NumImagesCounter_RBV.VAL") != numImage:
        time.sleep(1)
    epics.caput(shutter + ":close.VAL", 1, wait=True, timeout=1000.0)                                            
                                
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != numImage):    
        time.sleep(1)    
    
    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
    print "radiography recording is done!"                          
    # scan sample -- end
    
    # set for white field -- start
    print "Acquiring flat images ..."     
    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:FrameType.VAL","FlatField", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
    time.sleep(2)     
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(samStage + ".VAL","0", wait=True, timeout=1000.0)                
    print "flat is done!"                
    # set for white field -- end
    
    # set for dark field -- start
    print "Acquiring dark images ..."                
    time.sleep(2)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:FrameType.VAL","Background", wait=True, timeout=1000.0)             
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)               
    time.sleep(2)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    
    print "dark is done!"  

    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
    # set for new scans -- end
    print "Measurement is done."   


def _testEdgeDriver(repeat=20):
    camPrefix = "PCOIOC3"
    BL = "2bmb"                
    idx = epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True)
    idx = int(idx)-3
    epics.caput(BL + ":caputRecorderGbl_10.VAL", str(idx), wait=True, timeout=1000.0)
    for ii in range(repeat):
        EdgeSingleScan(exposureTime=0.1, slewSpeed=0.5,angEnd = 180,
                numProjPerSweep=1500,
                samInPos=-0.0, samOutPos=-4,
                roiSizeX = 2560, roiSizeY = 2160,
                accl = 1.0)
        idx = epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True)
        idx = int(idx)-3
        epics.caput(BL + ":caputRecorderGbl_10.VAL", str(idx), wait=True, timeout=1000.0)                                


def EdgeRadiography(exposureTime=0.1, frmRate = 9, acqPeroid = 30,
                    samInPos=0, samOutPos=5,
                    roiSizeX = 2560, roiSizeY = 1300,
                    repeat=1, delay=300,
                    scanMode=0):

    samStage = "2bma:m49"
    posStage = "2bma:m20"  
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"    
    BL = "2bmb"
    shutter = "2bma:A_shutter"                

    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                

    numImage = frmRate * acqPeroid
                
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit..."  
        return False
    camShutterMode = "Rolling"                
    camPrefix = "PCOIOC3"
    shutter = "2bma:A_shutter"    
                
    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ 'Radiography_' +\
#                epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#                      'YPos'+str(epics.caget('2bma:m20.VAL'))+'mm_'+\
#                cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+'DegPerSec_'+\
#                camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
#                '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)

    for ii in range(repeat):
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']
        filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ 'Radiography_'+\
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)     
        filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    
    
        epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
                    
        epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                            
        epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:ImageMode.VAL","Multiple", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:NumImages.VAL",numImage, wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL",camScanSpeed, wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_global_shutter.VAL",camShutterMode, wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:AcquirePeriod.VAL","0", wait=True, timeout=1000.0)   
        epics.caput(camPrefix+":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0)     
        epics.caput(camPrefix+":HDF1:EnableCallbacks.VAL",1, wait=True, timeout=1000.0)                  
        epics.caput(camPrefix+":HDF1:AutoIncrement.VAL","Yes", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":HDF1:NumCapture.VAL",str(numImage+20), wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":HDF1:NumCapture_RBV.VAL",str(numImage+20), wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
        epics.caput(camPrefix+":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)  
                  
        epics.caput(camPrefix+":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0) 
        time.sleep(2)  
                                    
        epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
        print 'data is done'    
    
        epics.caput(camPrefix+":cam1:NumImages.VAL",10, wait=True, timeout=1000.0)      
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
        print 'flat is done'           
             
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
        print 'dark is done'           
    
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)            
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)
                    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   

        print str(ii), 'th acquistion is done at ', time.asctime() 
        if ii != repeat-1:
            time.sleep(delay)
                 
                
    print 'Radiography acquisition finished!'    

def DimaxRadiography(exposureTime=0.1, frmRate = 9, acqPeroid = 30,
                    samInPos=0, samOutPos=7,
                    roiSizeX = 2016, roiSizeY = 2016,
                    repeat=1, delay=600,
                    scanMode=0):

    samStage = "2bma:m49"
    posStage = "2bma:m20"  
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"    
    BL = "2bmb"
    shutter = "2bma:A_shutter"                

    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)               

    numImage = frmRate * acqPeroid + 20
                
    camShutterMode = "Rolling"                
    camPrefix = "PCOIOC2"
    shutter = "2bma:A_shutter"    
                
    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ 'Radiography_' +\
#                epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#                      'YPos'+str(epics.caget('2bma:m20.VAL'))+'mm_'+\
#                cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+'DegPerSec_'+\
#                camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
#                '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)

#    if epics.caget(camPrefix+":HDF1:XMLFileName_RBV.VAL") != "DynaMCTHDFLayout.xml":        
#        epics.caput(camPrefix+":HDF1:XMLFileName.VAL","DynaMCTHDFLayout.xml", wait=True, timeout=1000.0)                 
#
#    if epics.caget(camPrefix+":cam1:NDAttributesFile.VAL") != "DynaMCTDetectorAttributes.xml":     
#        epics.caput(camPrefix+":cam1:NDAttributesFile.VAL","DynaMCTDetectorAttributes.xml", wait=True, timeout=1000.0)

    for ii in range(repeat):
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)        
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']
        filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ 'Radiography_'+\
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)     
        filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    
    
        epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
                            
        epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)                        
        epics.caput(camPrefix+":cam1:pco_live_view.VAL","No", wait=True, timeout=1000.0)               
        epics.caput(camPrefix+":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:AcquirePeriod.VAL","0", wait=True, timeout=1000.0)   
                    
        epics.caput(camPrefix+":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":HDF1:EnableCallbacks.VAL",1, wait=True, timeout=1000.0)                  
        epics.caput(camPrefix+":HDF1:AutoIncrement.VAL","Yes", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
        epics.caput(camPrefix+":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
        epics.caput(camPrefix+":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
        epics.caput(camPrefix+":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
        epics.caput(camPrefix+":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)                    
        epics.caput(camPrefix+":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0) 
        time.sleep(2)  

        epics.caput("2bma:m49.VAL",str(samInPos), wait=True, timeout=1000.0)
        epics.caput(camPrefix+":cam1:NumImages.VAL",str(numImage-20), wait=True, timeout=1000.0)         
        epics.caput(camPrefix+":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0)                                             
        epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_dump_counter.VAL",'0', wait=True, timeout=1000.0)        
        epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numImage-20), wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numImage-20), wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)        
        print 'data is done'    
    
        epics.caput(camPrefix+":cam1:NumImages.VAL",10, wait=True, timeout=1000.0) 
        epics.caput("2bma:m49.VAL",str(samOutPos), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:FrameType.VAL",'2', wait=True, timeout=1000.0) 
        epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0) 
        epics.caput(camPrefix + ":cam1:pco_dump_counter.VAL",'0', wait=True, timeout=1000.0)         
        epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",'10', wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",'10', wait=True, timeout=1000.0) 
        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)               
        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)                   
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0) 
        print 'flat is done'           
     
#        epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0) 
        epics.caput("2bma:m49.VAL",str(samInPos), wait=True, timeout=1000.0)         
        epics.caput(camPrefix + ":cam1:FrameType.VAL",'1', wait=True, timeout=1000.0) 
        epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0) 
        epics.caput(camPrefix + ":cam1:pco_dump_counter.VAL",'0', wait=True, timeout=1000.0)         
        epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",'10', wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",'10', wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)       
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0) 
        print 'dark is done'           
    
        epics.caput(camPrefix+":HDF1:Capture.VAL","Done", wait=False, timeout=1000.0)             
        epics.caput(camPrefix+":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)
                    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   

        print str(ii), 'th acquistion is done at ', time.asctime() 
        if ii != repeat-1:
            time.sleep(delay)

    epics.caput(camPrefix+":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0) 
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                  
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)                 
    print 'Radiography acquisition finished!'    

            

#
#
# 
#def EdgeMultiPosScan(exposureTime=0.1, slewSpeed=1., angStart=0, angEnd = 180,
#                numProjPerSweep=1500,
#                samInPos=0, samOutDist=10,
#                roiSizeX = 2560, roiSizeY = 2160,
#                posStep = 0, posNum = 1, 
#                delay = 0, flatPerScan = 1, darkPerScan = 1,
#                accl = 1, shutterMode=0, scanMode=0, timeFile=0, clShutter=1):      
#    """ Multiple poistion scans along vertical direction with edge camera
#                
#      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
#              it assumes rotation axis is at image center at posInit.
#    """
#
#    #### this is a dummy number
#    refYofX0 = 22.772
#    axisShift = 0.0  
#              
###### AHutch tomo configurations -- start
#    initEdge(samInPos = samInPos)
##    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)     
#    if shutterMode == 0:
#        camShutterMode = "Rolling"
#    elif shutterMode == 1:
#        camShutterMode = "Global"
#    else:
#        print "Wrong camera shutter mode! Quit ..."
#        return False
#        
#    if scanMode == 0:
#        camScanSpeed = 'Normal'
#    elif scanMode == 1:
#        camScanSpeed = 'Fast'
#    elif scanMode == 2:
#        camScanSpeed = 'Fastest'
#    else:
#        print "Wrong camera scan mode! Quit ..."  
#        return False                
#                                  
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:A_shutter"
#                
##### for LAT                
##    samStage = "2bma:m20"
#    samStage = "2bma:m49"
#    posStage = "2bma:m20"        
#    rotStage = "2bmb:m82"
#    PSO = "2bmb:PSOFly2"
#                
#### for SAT                
##    samStage = "2bma:m49"
##    posStage = "2bma:m46"        
##    rotStage = "2bmb:m100"
##    PSO = "2bmb:PSOFly2"                
#
##    samInInitPos = samInPos 
#    samInInitPos = epics.caget(samStage + ".VAL")                
#    BL = "2bmb"
#    posRefPos = refYofX0                 
###### AHutch tomo configurations -- end                    
#
######## BHutch tomo configurations -- start
##    initEdge()                
##    camScanSpeed = "Fastest"
##    camShutterMode = "Rolling"                        
##    camPrefix = "PCOIOC3"                
##    shutter = "2bma:B_shutter"
##                
##### for SAT                
##    samStage = "2bmb:m63"
##    posStage = "2bmb:m57"
##    rotStage = "2bmb:m100"    
##    PSO = "2bmb:PSOFly2"
##                
##### for LAT
###    samStage = "2bmb:m58"
###    posStage = "2bmb:m4"
###    rotStage = "2bmb:m82"    
###    PSO = "2bmb:PSOFly1"                
##                
##    samInInitPos = samInPos                
##    BL = "2bmb"
######## BHutch tomo configurations -- end    
#
#
##    posCurr = epics.caget(posStage + ".VAL")    
##    posStageOffset = axisShift * (posCurr - refYofX0)/1000.0
##    epics.caput(samStage + ".VAL",str(posStageOffset), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
##    epics.caput(BL + ":caputRecorderArg14Value.VAL",str(posCurr), wait=True, timeout=1000.0)                
#                
##    ''' 
##     this is the case in which the rotation axis move toward left side (smaller 'center' in reconstruction)
##     when the sample stage moves up.                                                                
##    '''
##    if posStep > 0:
##        axisShift = np.abs(axisShift)    
##    elif posStep < 0:    
##        axisShift = -np.abs(axisShift)    
#
##    ''' 
##       this is the case in which the rotation axis move toward right side (larger 'center' in reconstruction)
##       when the sample stage moves up.                            
##    '''
##
##    if posStep > 0:
##        axisShift = -np.abs(axisShift)    
##    elif posStep < 0:    
##        axisShift = np.abs(axisShift)                                
#
#    if camPrefix == 'PCOIOC3':
#        cam = 'edge'
#    elif camPrefix == 'PCOIOC2':
#        cam = 'dimax'    
#
#    if samStage.split(':')[0] == '2bma':
#        station = 'AHutch'
#    elif samStage.split(':')[0] == '2bmb':    
#        station = 'BHutch'                                
#    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#           
#    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
#               
#    posInit = epics.caget(posStage+".VAL")
#    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
#    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
#    acclTime = 1.0*slewSpeed/accl
#    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#            
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
##    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
#    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    
#
#    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
#    pathSep =  filepathString.rsplit('/')
#    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    
#    if not os.path.exists(logFilePath):
#        os.makedirs(logFilePath)
#                        
#    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#            
#    logFile = open(logFileName,'w')
#    logFile.close()                
#    print "Your scan is logged in ", logFileName
#    
#    numImage = numProjPerSweep+20
#    
#    # test camera -- start
#    print roiSizeX,roiSizeY    
#    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#    
#                
#    # sample scan -- start
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)     
#    if timeFile == 1:
#        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
#        timeSeq = tf.readlines()
#        tf.close() 
#        posNum = len(timeSeq)            
#    print "start sample scan ... "
#    for ii in range(posNum):    
#    # set scan parameters -- start 
#        if timeFile == 1:
#            delay = float(timeSeq[ii]) 
#            
#        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
# 
#        epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
##        posCurr = epics.caget(posStage + ".VAL")    
##        samStageOffset = axisShift * (posCurr - posRefPos)/1000.0                                                 
##        samInPos = samInInitPos + samStageOffset 
#        samInPos = samInInitPos
#
###### heating with Eurotherm2K:3                                            
##        filepath = os.path.join(filepath_top, \
##               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
##               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
##               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
##               str(int(epics.caget("2bma:ET2k:3:Temperature.VAL")))+'C_'+ str(ii).zfill(1) + '_' + \
##               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
##               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
##               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
##               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
##               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
##               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
##               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
##               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
#
###### tension with 2bma:m58
##        epics.caput("2bmS1:D1done_read.VAL",1,wait=True,timeout=1000.0) 
##        filepath = os.path.join(filepath_top, \
##               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
##               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
##               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
##               str('{:5.5f}'.format(epics.caget("2bmS1:D1Dmm_calc.VAL")))+'N_'+ str(ii).zfill(2) + '_' + \
##               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
##               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
##               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
##               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
##               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
##               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
##               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
##               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
#
##        filepath = os.path.join(filepath_top, \
##               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
##               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
##               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
##               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
##               '0DegPos'+str(int(epics.caget("2bmS1:m2.RBV")*1000)/1000.0)+'mm_'+\
##               '90DegPos'+str(int(epics.caget("2bmS1:m1.RBV")*1000)/1000.0)+'mm_'+\
##               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
##               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
##               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
##               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
##               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
##               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
##               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
#
##### normal filename
#        filepath = os.path.join(filepath_top, \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ 
#               str(int(epics.caget("2bma:ET2k:2:Temperature.VAL")))+'C_'+ str(ii).zfill(1+1)+'_'\
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
#                   
#
###### tension with 2bma:m6                   
##        filepath = os.path.join(filepath_top, \
##               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
##               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
##               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
##               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
##               'TensionDist'+str(int(epics.caget("2bma:m6.RBV")*1000)/1000.0)+'mm_'+\
##               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
##               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
##               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
##               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
##               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
##               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
##               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
##               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)
#                   
#        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#        _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
#        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
#        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
#        time.sleep(3)                                                            
#        _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
#        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        print "scan at position #",ii+1," is done!"
#
#        samOutPos = samInPos + samOutDist
#        
#        if flatPerScan == 1:
#        # set for white field -- start                   
#            print "Acquiring flat images ..."                   
#            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)       
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)               
#            print "flat for position #", ii+1, " is done!"                
#        # set for white field -- end                                            
#                                
#        if darkPerScan == 1:
#            # set for dark field -- start
#            print "Acquiring dark images ..."                
#            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)             
#            print "dark is done!"  
#        if  posNum!=1 and darkPerScan!=0 and flatPerScan!=0 and ii!=(posNum-1):       
#            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#        # set for dark field -- end
#                                
#        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
#            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   
#        
#        if ii != (posNum-1):
#            time.sleep(delay)
#
#    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
#    print "sample scan is done!"          
#                                
#
#
#    logFile = open(logFileName,'a')
#    logFile.write("Scan was done at time: " + time.asctime() + '\n')
#    logFile.close()                                                                    
#                         
#    # sample scan -- end
#
#    if clShutter==1:
#        if flatPerScan == 0:    
#            # set for white field -- start                   
#            print "Acquiring flat images ..."    
#            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
#            time.sleep(3)                
#            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
#            print "flat is done!"                
#            # set for white field -- end
#    
#        if darkPerScan == 0:    
#            # set for dark field -- start
#            print "Acquiring dark images ..."                
#            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
#            print "dark is done!"  
#
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end
#    
#    # set for new scans -- start
#    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                                                                               
#    # set for new scans -- end
#    print "Scan finished!" 
#    epics.caput(posStage + ".VAL",str(posInit), wait=True, timeout=1000.0)
#    
#                


 
def EdgeMultiPosScan(exposureTime=0.2, slewSpeed=0.5, angStart=0, angEnd = 180,
                numProjPerSweep=1500,
                samInPos=0, samOutDist=7,
                roiSizeX = 2560, roiSizeY = 2160,
                posStep = 0, posNum = 1, 
                delay = 0, flatPerScan = 1, darkPerScan = 1,
                accl = 1, shutterMode=0, scanMode=0, timeFile=0, clShutter=1):      
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
              
##### AHutch tomo configurations -- start
    
#    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)     
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False
        
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"
                
#### for LAT                
#    samStage = "2bma:m20"
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"
                
### for SAT                
#    samStage = "2bma:m49"
#    posStage = "2bma:m46"        
#    rotStage = "2bmb:m100"
#    PSO = "2bmb:PSOFly2"                
              
    BL = "2bmb"

    initEdge(samInPos = samInPos,samStage=samStage,rotStage=rotStage)            
##### AHutch tomo configurations -- end                    

####### BHutch tomo configurations -- start
#    initEdge()                
#    camScanSpeed = "Fastest"
#    camShutterMode = "Rolling"                        
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:B_shutter"
#                
#### for SAT                
#    samStage = "2bmb:m63"
#    posStage = "2bmb:m57"
#    rotStage = "2bmb:m100"    
#    PSO = "2bmb:PSOFly2"
#                
#### for LAT
##    samStage = "2bmb:m58"
##    posStage = "2bmb:m4"
##    rotStage = "2bmb:m82"    
##    PSO = "2bmb:PSOFly1"                
#                
#    samInInitPos = samInPos                
#    BL = "2bmb"
####### BHutch tomo configurations -- end    


#    posCurr = epics.caget(posStage + ".VAL")    
#    posStageOffset = axisShift * (posCurr - refYofX0)/1000.0
#    epics.caput(samStage + ".VAL",str(posStageOffset), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
#    epics.caput(BL + ":caputRecorderArg14Value.VAL",str(posCurr), wait=True, timeout=1000.0)                
                
#    ''' 
#     this is the case in which the rotation axis move toward left side (smaller 'center' in reconstruction)
#     when the sample stage moves up.                                                                
#    '''
#    if posStep > 0:
#        axisShift = np.abs(axisShift)    
#    elif posStep < 0:    
#        axisShift = -np.abs(axisShift)    

#    ''' 
#       this is the case in which the rotation axis move toward right side (larger 'center' in reconstruction)
#       when the sample stage moves up.                            
#    '''
#
#    if posStep > 0:
#        axisShift = -np.abs(axisShift)    
#    elif posStep < 0:    
#        axisShift = np.abs(axisShift)                                

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
           
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
               
    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
            
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
#    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
    
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print roiSizeX,roiSizeY    
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    
                
    # sample scan -- start
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)     
    if timeFile == 1:
        tf = open('~/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close() 
        posNum = len(timeSeq)            
    print "start sample scan ... "
    for ii in range(posNum):    
    # set scan parameters -- start 
        if timeFile == 1:
            delay = float(timeSeq[ii]) 
            
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
 
        epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)

##### heating with Eurotherm2K:3                                            
#        filepath = os.path.join(filepath_top, \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#               str(int(epics.caget("2bma:ET2k:3:Temperature.VAL")))+'C_'+ str(ii).zfill(1) + '_' + \
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 

##### tension with 2bma:m58
#        epics.caput("2bmS1:D1done_read.VAL",1,wait=True,timeout=1000.0) 
#        filepath = os.path.join(filepath_top, \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#               str('{:5.5f}'.format(epics.caget("2bmS1:D1Dmm_calc.VAL")))+'N_'+ str(ii).zfill(2) + '_' + \
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 

#        filepath = os.path.join(filepath_top, \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               '0DegPos'+str(int(epics.caget("2bmS1:m2.RBV")*1000)/1000.0)+'mm_'+\
#               '90DegPos'+str(int(epics.caget("2bmS1:m1.RBV")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 

#### normal filename
        filepath = os.path.join(filepath_top, \
               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+ 
               str(int(epics.caget("2bma:ET2k:2:Temperature.VAL")))+'C_'+ str(ii).zfill(1+1)+'_'\
               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
                   

##### tension with 2bma:m6                   
#        filepath = os.path.join(filepath_top, \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               'TensionDist'+str(int(epics.caget("2bma:m6.RBV")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
#               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)
                   
        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
        _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
        time.sleep(3)                                                            
        _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
        print "scan at position #",ii+1," is done!"

        samOutPos = samInPos + samOutDist
        
        if flatPerScan == 1:
        # set for white field -- start                   
            print "Acquiring flat images ..."                   
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)       
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)               
            print "flat for position #", ii+1, " is done!"                
        # set for white field -- end                                            
                                
        if darkPerScan == 1:
            # set for dark field -- start
            print "Acquiring dark images ..."                
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)             
            print "dark is done!"  
        if  posNum!=1 and darkPerScan!=0 and flatPerScan!=0 and ii!=(posNum-1):       
            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
                                
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   
        
        if ii != (posNum-1):
            time.sleep(delay)

    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
    print "sample scan is done!"          
                                


    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if clShutter==1:
        if flatPerScan == 0:    
            # set for white field -- start                   
            print "Acquiring flat images ..."    
            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
            time.sleep(3)                
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
            print "flat is done!"                
            # set for white field -- end
    
        if darkPerScan == 0:    
            # set for dark field -- start
            print "Acquiring dark images ..."                
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
            print "dark is done!"  

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                                                                               
    # set for new scans -- end
    print "Scan finished!" 
    epics.caput(posStage + ".VAL",str(posInit), wait=True, timeout=1000.0)
    
                



 
def EdgeTimeLoopMultiPosScan(exposureTime=0.15, slewSpeed=0.67, angStart=0, angEnd = 180,
                numProjPerSweep=1500,
                samInPos=0, samOutDist=5,
                roiSizeX = 2560, roiSizeY = 2160,
                posStep = 0, posNum = 1, 
                posDelay = 0, flatPerScan = 1, darkPerScan = 1,
                accl = 1, shutterMode=0, scanMode=0, timeFile=0, 
                timeNum = 1,timeDelay = 0, clShutter=1):      
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
              
##### AHutch tomo configurations -- start
    initEdge(samInPos = samInPos)
#    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)     
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False
        
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"
                
#### for LAT                
#    samStage = "2bma:m20"
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"
    BL = "2bmb" 
                
### for SAT                
#    samStage = "2bma:m49"
#    posStage = "2bma:m46"        
#    rotStage = "2bmb:m100"
#    PSO = "2bmb:PSOFly2"                
              
                  
##### AHutch tomo configurations -- end                    

####### BHutch tomo configurations -- start
#    initEdge()                
#    camScanSpeed = "Fastest"
#    camShutterMode = "Rolling"                        
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:B_shutter"
#                
#### for SAT                
#    samStage = "2bmb:m63"
#    posStage = "2bmb:m57"
#    rotStage = "2bmb:m100"    
#    PSO = "2bmb:PSOFly2"
#                
#### for LAT
##    samStage = "2bmb:m58"
##    posStage = "2bmb:m4"
##    rotStage = "2bmb:m82"    
##    PSO = "2bmb:PSOFly1"                
#                
#    samInInitPos = samInPos                
#    BL = "2bmb"
####### BHutch tomo configurations -- end    


#    posCurr = epics.caget(posStage + ".VAL")    
#    posStageOffset = axisShift * (posCurr - refYofX0)/1000.0
#    epics.caput(samStage + ".VAL",str(posStageOffset), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
#    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
#    epics.caput(BL + ":caputRecorderArg14Value.VAL",str(posCurr), wait=True, timeout=1000.0)                
                
#    ''' 
#     this is the case in which the rotation axis move toward left side (smaller 'center' in reconstruction)
#     when the sample stage moves up.                                                                
#    '''
#    if posStep > 0:
#        axisShift = np.abs(axisShift)    
#    elif posStep < 0:    
#        axisShift = -np.abs(axisShift)    

#    ''' 
#       this is the case in which the rotation axis move toward right side (larger 'center' in reconstruction)
#       when the sample stage moves up.                            
#    '''
#
#    if posStep > 0:
#        axisShift = -np.abs(axisShift)    
#    elif posStep < 0:    
#        axisShift = np.abs(axisShift)                                

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
           
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
               
    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
            
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
#    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
    
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print roiSizeX,roiSizeY    
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    
                
    # sample scan -- start
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)     
    if timeFile == 1:
        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close() 
        posNum = len(timeSeq)            
    print "start sample scan ... "
    for jj in range(timeNum):
        for ii in range(posNum):    
        # set scan parameters -- start 
            if timeFile == 1:
                posDelay = float(timeSeq[ii]) 
                
            timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
     
            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
    
    ##### heating with Eurotherm2K:3                                            
    #        filepath = os.path.join(filepath_top, \
    #               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
    #               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
    #               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
    #               str(int(epics.caget("2bma:ET2k:3:Temperature.VAL")))+'C_'+ str(ii).zfill(1) + '_' + \
    #               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
    #               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
    #               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
    #               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
    #               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
    #               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
    #               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
    #               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
    
    ##### tension with 2bma:m58
    #        epics.caput("2bmS1:D1done_read.VAL",1,wait=True,timeout=1000.0) 
    #        filepath = os.path.join(filepath_top, \
    #               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
    #               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
    #               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
    #               str('{:5.5f}'.format(epics.caget("2bmS1:D1Dmm_calc.VAL")))+'N_'+ str(ii).zfill(2) + '_' + \
    #               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
    #               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
    #               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
    #               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
    #               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
    #               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
    #               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
    #               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
    
    #        filepath = os.path.join(filepath_top, \
    #               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
    #               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
    #               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
    #               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
    #               '0DegPos'+str(int(epics.caget("2bmS1:m2.RBV")*1000)/1000.0)+'mm_'+\
    #               '90DegPos'+str(int(epics.caget("2bmS1:m1.RBV")*1000)/1000.0)+'mm_'+\
    #               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
    #               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
    #               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
    #               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
    #               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
    #               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
    #               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
    
    #### normal filename
            filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_pos'+ str(ii+1).zfill(2)+'_time'+ str(jj+1).zfill(2)+\
                   '_YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)                
                       
    
    ##### tension with 2bma:m6                   
    #        filepath = os.path.join(filepath_top, \
    #               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
    #               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
    #               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
    #               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
    #               'TensionDist'+str(int(epics.caget("2bma:m6.RBV")*1000)/1000.0)+'mm_'+\
    #               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
    #               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
    #               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
    #               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
    #               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
    #               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
    #               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
    #               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station)
                       
            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
            _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
            time.sleep(3)                                                            
            _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
            print "Sample scan at position #",ii+1, " at time point # ",str(jj+1)," is done!"
    
            samOutPos = samInPos + samOutDist
            
            if flatPerScan == 1:
            # set for white field -- start                   
                print "Acquiring flat images ..."                   
                _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)       
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)               
                print "Flat for position #", ii+1, " at time point # ",str(jj+1)," is done!"                
            # set for white field -- end                                            
                                    
            if darkPerScan == 1:
                # set for dark field -- start
                print "Acquiring dark images ..."                
                _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)             
                print "Dark for position #", ii+1, " at time point # ",str(jj+1)," is done!"
            if  posNum!=1 and darkPerScan!=0 and flatPerScan!=0 and ii!=(posNum-1):       
                epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
            epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
            # set for dark field -- end
                                    
            if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   
            
            if ii != (posNum-1):
                time.sleep(posDelay)
    
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
        print "Sample scans at time point # ",str(jj+1), "is done!"          
                                    
    
    
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
                             
        # sample scan -- end
    
        if clShutter==1:
            if flatPerScan == 0:    
                # set for white field -- start                   
                print "Acquiring flat images ..."    
                epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
                time.sleep(3)                
                _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
        #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
                print "flat is done!"                
                # set for white field -- end
        
            if darkPerScan == 0:    
                # set for dark field -- start
                print "Acquiring dark images ..."                
                _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
        #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
                print "dark is done!"  
    
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
        if jj != (timeNum-1):
            print timeNum,timeDelay
            time.sleep(timeDelay)    
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                                                                               
    # set for new scans -- end
    print "Scan finished!" 
    epics.caput(posStage + ".VAL",str(posInit), wait=True, timeout=1000.0)
    
                



 
def EdgeMultiPosScanJoseph(exposureTime=0.1, slewSpeed=1, angStart=0, angEnd = 180,
                numProjPerSweep=1501,
                samInPos=0, samOutPos=4.5,
                roiSizeX = 2560, roiSizeY = 2160,
                posStep = 0, posNum = 1, axisShift = 0.0,refYofX0 = 22.772,
                delay = 0, flatPerScan = 0, darkPerScan = 0,
                accl = 1, shutterMode=0, scanMode=0, timeFile=0, clShutter=1):      
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
                
##### AHutch tomo configurations -- start
    initEdge(samInPos = samInPos)
#    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)     
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False
        
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"
                
#### for LAT                
#    samStage = "2bma:m49"
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bmb:m82"
    furnaceY = "2bma:m55"
    PSO = "2bmb:PSOFly2"
                
### for SAT                
#    samStage = "2bma:m49"
#    posStage = "2bma:m46"        
#    rotStage = "2bmb:m100"
#    PSO = "2bmb:PSOFly2"                

#    samInInitPos = samInPos 
    samInInitPos = epics.caget(samStage + ".VAL")                
    BL = "2bmb"
    posRefPos = refYofX0                   
##### AHutch tomo configurations -- end                                                 

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
                
    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
#    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    print 2
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print roiSizeX,roiSizeY    
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    
                
    # sample scan -- start
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)     
    if timeFile == 1:
        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close() 
        posNum = len(timeSeq)            
    print "start sample scan ... "
    for ii in range(posNum):    
    # set scan parameters -- start 
        if timeFile == 1:
            delay = float(timeSeq[ii]) 

        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
 
        epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
        posCurr = epics.caget(posStage + ".VAL")    
        samStageOffset = axisShift * (posCurr - posRefPos)/1000.0                                                 
        samInPos = samInInitPos + samStageOffset 

#### heating with Eurotherm2K:1                                            
        filepath = os.path.join(filepath_top, \
               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
               str(int(epics.caget("2bma:ET2k:1:Temperature.VAL")))+'C_'+ str(ii).zfill(2) + '_' + \
               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
                                  
        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
        _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
        time.sleep(3)                                                            
        _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
        print "scan at position #",ii+1," is done!"

#        samOutPos = samInPos + samOutPos
        samOutPos = samInInitPos + samOutPos
        
        if flatPerScan == 1 or ii==0:
        # set for white field -- start   
            epics.caput(furnaceY+".VAL",90, wait=True, timeout=1000.0)                 
            print "Acquiring flat images ..."                   
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)           
            print "flat for position #", ii+1, " is done!"                
        # set for white field -- end                                            
                                
        if darkPerScan == 1 or ii==0:
            # set for dark field -- start
            epics.caput(furnaceY+".VAL",90, wait=True, timeout=1000.0) 
            print "Acquiring dark images ..."                
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                
            print "dark is done!" 
        # set for dark field -- end    

        epics.caput(furnaceY+".VAL",0, wait=True, timeout=1000.0)
        if ii != (posNum-1):
            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
            
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
                                        
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   
        
        if ii != (posNum-1) and ii!=0:
            time.sleep(delay)

    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0) 
    epics.caput(furnaceY+".VAL",90, wait=True, timeout=1000.0)                                             
    print "sample scan is done!"          
                                


    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if flatPerScan == 0:    
        # set for white field -- start                   
        print "Acquiring flat images ..."    
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
        time.sleep(3)                
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
        print "flat is done!"                
        # set for white field -- end

    if darkPerScan == 0:    
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO) 
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
        print "dark is done!"  

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".VAL",str(samInInitPos), wait=True, timeout=1000.0)
#    epics.caput(posStage + ".VAL",str(posInit), wait=False, timeout=1000.0)                                                                
    # set for new scans -- end
    print "Scan finished!" 
    epics.caput(posStage + ".VAL",str(posInit), wait=True, timeout=1000.0)
    
                


 
def EdgeMultiPosScanFreeRun(exposureTime=0.1, slewSpeed=1, angStart=0, angEnd = 180,
                numProjPerSweep=1501,
                samInPos=0, samOutPos=8,
                roiSizeX = 2560, roiSizeY = 2160,
                posStep = 0, posNum = 1, axisShift = 0.0,refYofX0 = 22.772,
                delay = 0, flatPerScan = 1, darkPerScan = 1,
                accl = 1, shutterMode=0, scanMode=0, timeFile=0, clShutter=1):      
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
                
##### AHutch tomo configurations -- start
    initEdge(samInPos = samInPos)
#    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)     
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False
        
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"
                
#### for LAT                
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"
                
### for SAT                
#    samStage = "2bma:m49"
#    posStage = "2bma:m46"        
#    rotStage = "2bmb:m100"
#    PSO = "2bmb:PSOFly2"                

#    samInInitPos = samInPos 
    samInInitPos = epics.caget(samStage + ".VAL")                
    BL = "2bmb"
    posRefPos = refYofX0                   
##### AHutch tomo configurations -- end                    

####### BHutch tomo configurations -- start
#    initEdge()                
#    camScanSpeed = "Fastest"
#    camShutterMode = "Rolling"                        
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:B_shutter"
#                
#### for SAT                
#    samStage = "2bmb:m63"
#    posStage = "2bmb:m57"
#    rotStage = "2bmb:m100"    
#    PSO = "2bmb:PSOFly2"
#                
#### for LAT
##    samStage = "2bmb:m58"
##    posStage = "2bmb:m4"
##    rotStage = "2bmb:m82"    
##    PSO = "2bmb:PSOFly1"                
#                
#    samInInitPos = samInPos                
#    BL = "2bmb"
####### BHutch tomo configurations -- end                                  

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
                
    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
#    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    print 2
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print roiSizeX,roiSizeY    
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    
                
    # sample scan -- start
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)     
    if timeFile == 1:
        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close()             
    print "start sample scan ... "
    for ii in range(posNum):    
    # set scan parameters -- start 
        if timeFile == 1:
            delay = float(timeSeq[ii]) 
            
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
 
        epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
        posCurr = epics.caget(posStage + ".VAL")    
        samStageOffset = axisShift * (posCurr - posRefPos)/1000.0                                                 
        samInPos = samInInitPos + samStageOffset 

        filepath = os.path.join(filepath_top, \
               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
                   
        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
        _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
        time.sleep(3)                                                            
        _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
        print "scan at position #",ii+1," is done!"

        samOutPos = samInPos + samOutPos
        
        if flatPerScan == 1:
        # set for white field -- start                   
            print "Acquiring flat images ..."                   
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)            
            print "flat for position #", ii+1, " is done!"                
        # set for white field -- end                                            
                                
        if darkPerScan == 1:
            # set for dark field -- start
            print "Acquiring dark images ..."                
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)             
            print "dark is done!"  

        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
                                
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   
        
        if ii != (posNum-1):
            time.sleep(delay)

    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
    print "sample scan is done!"          
                                


    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if flatPerScan == 0:    
        # set for white field -- start                   
        print "Acquiring flat images ..."    
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
        time.sleep(3)                
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
        print "flat is done!"                
        # set for white field -- end

    if darkPerScan == 0:    
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
        print "dark is done!"  

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".VAL",str(samInInitPos), wait=True, timeout=1000.0)
#    epics.caput(posStage + ".VAL",str(posInit), wait=False, timeout=1000.0)                                                                
    # set for new scans -- end
    print "Scan finished!" 
    
                



def EdgeMultiPosScanArjun(exposureTime=0.1, slewSpeed=1, angStart=0, angEnd = 180,
                numProjPerSweep=1501,
                samInPos=0, samOutPos=8.53,
                roiSizeX = 2560, roiSizeY = 1500,
                posStep = 0, posNum = 1, axisShift = 0.0,refYofX0 = 22.772,
                delay = 2380, flatPerScan = 1, darkPerScan = 1,
                accl = 2, shutterMode=0, scanMode=0, timeFile=0, clShutter=1):    
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
                
##### AHutch tomo configurations -- start
    initEdge(samInPos = samInPos)  
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False
        
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"
                
#### for LAT                
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bmb:m82"
    top0Deg = "2bmS1:m2"
    top90Deg = "2bmS1:m1"    
    PSO = "2bmb:PSOFly2"
                
    samInInitPos = epics.caget(samStage + ".VAL")                
    BL = "2bmb"
    posRefPos = refYofX0                   
##### AHutch tomo configurations -- end                                                 

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
                
    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    print 2
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print roiSizeX,roiSizeY    
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    
                
    # sample scan -- start    
    if timeFile == 1:
        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close()             
    print "start sample scan ... "
    
    samInPosList = [0.038, -0.026, -0.191]
    samOutPosList = [8.52, 8.87, 8.7]
    yPosList = [12.282, 16.482, 27.182]
    top0DegList = [-8.175, -8.505, -8.585]
    top90DegList = [9.162, 9.392, 9.492]
    for ii in range(posNum):    
    # set scan parameters -- start 
        if timeFile == 1:
            delay = float(timeSeq[ii]) 

        for jj in range(3):            
            timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
     
            samInPos = samInPosList[jj]
            samOutPos = samOutPosList[jj] 
            epics.caput(posStage, str(yPosList[jj]),wait=True,timeout=1000.0)
            epics.caput(top0Deg, str(top0DegList[jj]),wait=True,timeout=1000.0)
            epics.caput(top90Deg, str(top90DegList[jj]),wait=True,timeout=1000.0)            
    
            filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
                       
            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
            _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
            time.sleep(3)                                                            
            _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
            print "scan at position #",ii+1," is done!"
    
#            samOutPos = samInPos + samOutPos
            
            if flatPerScan == 1:
            # set for white field -- start                   
                print "Acquiring flat images ..."                   
                _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)            
                print "flat for position #", ii+1, " is done!"                
            # set for white field -- end                                            
                                    
            if darkPerScan == 1:
                # set for dark field -- start
                print "Acquiring dark images ..."                
                _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)             
                print "dark is done!"  
    
            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
            epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
            # set for dark field -- end
                                    
            if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   

        epics.caput(posStage, str(yPosList[0]),wait=False,timeout=1000.0)                
        if ii != (posNum-1):
            time.sleep(delay)

    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
    print "sample scan is done!"          
                                


    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if flatPerScan == 0:    
        # set for white field -- start                   
        print "Acquiring flat images ..."    
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
        time.sleep(3)                
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
        print "flat is done!"                
        # set for white field -- end

    if darkPerScan == 0:    
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
        print "dark is done!"  

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".VAL",str(samInInitPos), wait=True, timeout=1000.0)
#    epics.caput(posStage + ".VAL",str(posInit), wait=False, timeout=1000.0)                                                                
    # set for new scans -- end
    print "Scan finished!" 
    
                






#def EdgeMultiPosTimeLoopScan(exposureTime=0.03, slewSpeed=3, angStart=0, angEnd = 180,
#                numProjPerSweep=901,
#                samInPos=0, samOutPos=1.5,
#                roiSizeX = 1600, roiSizeY = 2160,
#                posInit = 0, posStep = 0, posNum = 1, axisShift = 0,refYofX0 = 13.34, 
#                timeNum=1, 
#                posDelay=0, timeDelay = 0,timeFile = 0,
#                accl = 2, scanMode=0):
#    """ Multiple poistion scans along vertical direction with edge camera
#                
#      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
#              it assumes rotation axis is at image center at posInit.
#    """
#                
###### AHutch tomo configurations -- start
#    initEdge()
#    if scanMode == 0:
#        camScanSpeed = 'Normal'
#    elif scanMode == 1:
#        camScanSpeed = 'Fast'
#    elif scanMode == 2:
#        camScanSpeed = 'Fastest'
#    else:
#        print "Wrong camera scan mode! Quit..."  
#        return False                
#    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
#    camShutterMode = "Global"                    
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:A_shutter"
#                
##### for LAT                
#    samStage = "2bma:m49"
#    posStage = "2bma:m20"        
#    rotStage = "2bmb:m82"
#    PSO = "2bmb:PSOFly1"
#                
#### for SAT                
##    samStage = "2bma:m49"
##    posStage = "2bma:m46"        
##    rotStage = "2bmb:m100"
##    PSO = "2bmb:PSOFly2"                
#
#    samInInitPos = samInPos                
#    BL = "2bmb"
#    posRefPos = refYofX0                
###### AHutch tomo configurations -- end                    
#
######## BHutch tomo configurations -- start
##    initEdge()                
##    camScanSpeed = "Fastest"
##    camShutterMode = "Rolling"                        
##    camPrefix = "PCOIOC3"                
##    shutter = "2bma:B_shutter"
##                
##### for SAT                
##    samStage = "2bmb:m63"
##    posStage = "2bmb:m57"
##    rotStage = "2bmb:m100"    
##    PSO = "2bmb:PSOFly2"
##                
##### for LAT
###    samStage = "2bmb:m58"
###    posStage = "2bmb:m4"
###    rotStage = "2bmb:m82"    
###    PSO = "2bmb:PSOFly1"                
##                
##    samInInitPos = samInPos                
##    BL = "2bmb"
######## BHutch tomo configurations -- end    
#
#
##    posCurr = epics.caget(posStage + ".VAL")    
##    posStageOffset = axisShift * (posCurr - refYofX0)/1000.0
##    epics.caput(samStage + ".VAL",str(posStageOffset), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(1), wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".VAL",'0', wait=True, timeout=1000.0)    
##    epics.caput(samStage + ".SET",str(0), wait=True, timeout=1000.0)    
##    epics.caput(BL + ":caputRecorderArg14Value.VAL",str(posCurr), wait=True, timeout=1000.0)                
#                
##    ''' 
##     this is the case in which the rotation axis move toward left side (smaller 'center' in reconstruction)
##     when the sample stage moves up..
##    '''
##    if posStep > 0:
##        axisShift = np.abs(axisShift)    
##    elif posStep < 0:    
##        axisShift = -np.abs(axisShift)    
#
##    ''' 
##       this is the case in which the rotation axis move toward right side (larger 'center' in reconstruction)
##       when the sample stage moves up.
##    '''
##
##    if posStep > 0:
##        axisShift = -np.abs(axisShift)    
##    elif posStep < 0:    
##        axisShift = np.abs(axisShift)                                
#
#    if camPrefix == 'PCOIOC3':
#        cam = 'edge'
#    elif camPrefix == 'PCOIOC2':
#        cam = 'dimax'    
#
#    if samStage.split(':')[0] == '2bma':
#        station = 'AHutch'
#    elif samStage.split(':')[0] == '2bmb':    
#        station = 'BHutch'                                
#    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
##    filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
##                epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
##                epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
##                'YPos'+str(int(epics.caget('2bma:m20.VAL')*1000)/1000.0)+'mm_'+\
##                cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
##                epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
##                str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
##                camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
##                epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
##                epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
##                str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
##                '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
#                
#    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
#                
#    posInit = epics.caget(posStage+".VAL")
#    posCurr = posInit                
#    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
#    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
#    acclTime = 1.0*slewSpeed/accl
#    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#                
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
##    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
#    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    
#
#    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
#    pathSep =  filepathString.rsplit('/')
#    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
##    print 2
#    if not os.path.exists(logFilePath):
#        os.makedirs(logFilePath)
#                        
#    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#            
#    logFile = open(logFileName,'w')
#    logFile.close()                
#    print "Your scan is logged in ", logFileName
#    
#    numImage = numProjPerSweep+20
#    
#    # test camera -- start
#    print roiSizeX,roiSizeY    
#    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#    
#                
#    # sample scan -- start
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)   
#    if timeFile == 1:
#        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
#        timeSeq = tf.readlines()
#        tf.close()                                                                
#    print "start sample scan ... "
#    for jj in range(timeNum): 
#        if timeFile == 1:
#            timeDelay = float(timeSeq[jj])  
#          
#        for ii in range(posNum):    
#        # set scan parameters -- start  
#            timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                   
#
#            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
#            posCurr = epics.caget(posStage + ".VAL")    
#            samStageOffset = axisShift * (posCurr - posRefPos)/1000.0                                                 
#            samInPos = samInInitPos + samStageOffset                                                 
#            filepath = os.path.join(filepath_top + epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True), \
#               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
#               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
#               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#               str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
#               '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)                                                                                                
#            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#            _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)  
#                            
#            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
#           
#            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                 
#            time.sleep(3)                                                            
#            _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
##            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#            print "scan at position #",ii+1," is done!"
#    
#            # set for white field -- start
#            epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#            epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#            epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                    
#            print "Acquiring flat images ..."                    
#            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#            print "flat at position #", ii+1, " is done!"                
#            # set for white field -- end
#                                    
#            epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)                                
#            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
#            # set for dark field -- start         
#            print "Acquiring dark images ..."                
#            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)   
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#            print "dark at position #", ii+1, " is done!"                                             
#            if ii != (posNum-1):
#                time.sleep(posDelay)
#    
#  
#            # sample scan -- end    
#
#            if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
#                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)  
#
#            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#            epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)                                                                
#        print 'Time point ', jj, ' is finished ...' 
#        epics.caput(posStage + ".VAL",str(posInit))                    
#        if jj != (timeNum-1):
#            time.sleep(timeDelay)                                
#
#    print "sample scan is done!"     
#    
#    logFile = open(logFileName,'a')
#    logFile.write("Scan was done at time: " + time.asctime() + '\n')
#    logFile.close()                                                                    
#                             
##    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end
#    
#    # set for new scans -- start
#    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
##    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
##    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    print "Scan finished!" 
#    
#                
#






#
#
#
#
#
#
#def _EdgeMultiPosTimeLoopScan(exposureTime=0.01, slewSpeed=7.2, angStart=0, angEnd = 180,
#                numProjPerSweep=750,
#                samInPos=0, samOutPos=3,
#                roiSizeX = 2560, roiSizeY = 2160,
#                posInit = 0, posStep = 3.5, posNum = 1, axisShift = 5.2,refYofX0 = 21.604, 
#                timeNum=5, 
#                posDelay=0, timeDelay = 300,
#                accl = 2, scanMode=0):
#    """ Multiple poistion scans along vertical direction with edge camera
#      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
#              it assumes rotation axis is at image center at posInit.
#    """
#                
####### AHutch tomo configurations -- start
##    initEdge()
##    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
##    camScanSpeed = "Normal"
##    camShutterMode = "Rolling"                    
##    camPrefix = "PCOIOC3"                
##    shutter = "2bma:A_shutter"
##    samStage = "2bma:m49"
##    posStage = "2bma:m49"
##    samInInitPos = samInPos            
##    rotStage = "2bmb:m82"
##    PSO = "2bmb:PSOFly1"
##    BL = "2bmb"
####### AHutch tomo configurations -- end                    
#
####### BHutch tomo configurations -- start
#    initEdge()                
#    camScanSpeed = "Fastest"
#    camShutterMode = "Rolling"                        
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:B_shutter"
#                
#### for SAT                
#    samStage = "2bmb:m63"
#    posStage = "2bmb:m57"
#    rotStage = "2bmb:m100"    
#    PSO = "2bmb:PSOFly2"
#                
#### for LAT
##    samStage = "2bmb:m58"
##    posStage = "2bmb:m4"
##    rotStage = "2bmb:m82"    
##    PSO = "2bmb:PSOFly1"                
#                
#    samInInitPos = samInPos                
#    BL = "2bmb"
####### BHutch tomo configurations -- end
#    if camPrefix == 'PCOIOC3':
#        cam = 'edge'
#    elif camPrefix == 'PCOIOC2':
#        cam = 'dimax'    
#
#    if samStage.split(':')[0] == '2bma':
#        station = 'AHutch'
#    elif samStage.split(':')[0] == '2bmb':    
#        station = 'BHutch'                                
#    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#                epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#                cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#                camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
#                '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
#                
#    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
#                
#    posInit = epics.caget(posStage+".VAL")
#    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
#    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
#    acclTime = 1.0*slewSpeed/accl
#    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#                
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
#    filepath = epics.caget(BL + ":caputRecorderGbl_filepath.VAL")
#    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    
#
#    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
#    pathSep =  filepathString.rsplit('/')
#    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
##    print 2
#    if not os.path.exists(logFilePath):
#        os.makedirs(logFilePath)
#                        
#    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#            
#    logFile = open(logFileName,'w')
#    logFile.close()                
#    print "Your scan is logged in ", logFileName
#    
#    numImage = numProjPerSweep
#    
#    # test camera -- start
#    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#    
#                
#    # sample scan -- start
##    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)                
#    print "start sample scan ... "
#    for jj in range(timeNum):
#        print 'Time point ', jj, ' starts ...'
#        for ii in range(posNum):    
#        # set scan parameters -- start                    
#            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#            _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)
#            epics.caput(posStage + ".VAL",str(posInit+ii*posStep), wait=True, timeout=1000.0)
#            samInPos = samInInitPos + ii*axisShift*posStep/1000.0                                
#            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
##            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
#            time.sleep(3)                                                            
#            _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
#            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#            print "scan at position #",ii+1," is done!"
#            epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)                                
##            epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)    
#            if ii != (posNum-1):
#                time.sleep(posDelay)
#
#        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
##        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
#        print 'sample scan of time point ', jj, ' is done!'          
#                                    
#    
#    
#        logFile = open(logFileName,'a')
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')
#        logFile.close()                                                                    
#                             
#        # sample scan -- end
#        
#        # set for white field -- start
##        epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)    
##        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
##        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                    
#        print "Acquiring flat images ..."    
#    #    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
#    #    time.sleep(5)                
#        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
#        print "flat is done!"                
#        # set for white field -- end
#        
#        # set for dark field -- start
#        print "Acquiring dark images ..."                
#        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
#        print "dark is done!"  
#                    
#        print 'Time point ', jj, ' is finished ...'                    
#        if jj != (timeNum-1):
#            time.sleep(timeDelay)    
#                    
#    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end
#    
#    # set for new scans -- start
#    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
#    epics.caput(posStage + ".VAL",str(posInit), wait=False, timeout=1000.0)
#    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
#        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#    # set for new scans -- end
#    print "Scan finished!"    
#
#
#
#




#
#def _EdgeTimeLoopScan(exposureTime=0.1, slewSpeed=1,angEnd = 180,
#                numProjPerSweep=1500, numTomoSweeps=10,
#                samInPos=0, samOutPos=-3,
#                roiSizeX = 1280, roiSizeY = 2160,
#                delay=390, accl = 1.0):
#    """
#        this routine allows users to do loop scan with same delay; 
#    """
######## AHutch tomo configurations -- start                
##    initEdge()
##    camScanSpeed = "Normal"
##    camShutterMode = "Rolling"                
##    camPrefix = "PCOIOC3"                
##    shutter = "2bma:A_shutter"
##    samStage = "2bma:m49"
##    rotStage = "2bmb:m82"
##    PSO = "2bmb:PSOFly1"
##    BL = "2bmb"
######## AHutch tomo configurations -- start    
#                
####### BHutch tomo configurations -- start                
#    initEdge()
#    camScanSpeed = "Normal"
#    camShutterMode = "Rolling"                
#    camPrefix = "PCOIOC3"                
#    shutter = "2bma:B_shutter"
#
#### for SAT                
##    samStage = "2bmb:m63"
##    rotStage = "2bmb:m82"
##    PSO = "2bmb:PSOFly1"
#                
#### for SAT                
#    samStage = "2bmb:m63"
#    rotStage = "2bmb:m100"
#    PSO = "2bmb:PSOFly2"
#    BL = "2bmb"
####### BHutch tomo configurations -- start    
#    if camPrefix == 'PCOIOC3':
#        cam = 'edge'
#    elif camPrefix == 'PCOIOC2':
#        cam = 'dimax'    
#
#    if samStage.split(':')[0] == '2bma':
#        station = 'AHutch'
#    elif samStage.split(':')[0] == '2bmb':    
#        station = 'BHutch'                                
#    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
#    filepath = os.path.join(filepath_top, epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
#                epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
#                epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
#                cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
#                str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
#                camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
#                epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
#                epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
#                str(epics.caget('2bma:M1angl.VAL'))+'mrad_USArm'+str(epics.caget('2bma:m30.VAL'))+\
#                '_monoY_'+str(epics.caget('2bma:m26.VAL'))+'_'+station)
#                
#    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
#                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
#    scanDelta = 1.0*angEnd/numProjPerSweep
#    acclTime = 1.0*slewSpeed/accl
#    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 5)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)            
#                
#    filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
#    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
#
#    filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
#    filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#    pathSep =  filepathString.rsplit('/')
#    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])    
#                
#    samFolderName = os.path.basename(filepathString)
#    dirUpLevel = os.path.dirname(filepathString)                
#    folderIdx = int(samFolderName.split('_')[0].strip('Exp'))                    
#
#    if not os.path.exists(logFilePath):
#        os.makedirs(logFilePath)
#                        
#    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#            
#    logFile = open(logFileName,'w')
#    logFile.close()                
#    print "Your scan is logged in ", logFileName
#                
#    numImage = numProjPerSweep
#    
#    cnt = 0                
#    for ii in range(numTomoSweeps):
#        filepathString = os.path.join(dirUpLevel,samFolderName.replace(samFolderName.split('_')[0],'Exp'+'{:03}'.format(ii+folderIdx)))
#        epics.caput(BL+":caputRecorderGbl_filepath.VAL",filepathString, wait=True, timeout=1000.)    
#        filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")                                
#        _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
#        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#        _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)                    
#                    
#        print "start acquire #: ", str(ii+1)
#                    
#        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
#        time.sleep(2)
#
#        logFile = open(logFileName,'a')
#        logFile.write("Scan #" + str(cnt) + " started at time: " + time.asctime() + '\n')        
#        _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)                            
#        epics.caput(rotStage + ".VELO","10.00000", wait=True, timeout=1000.0)
#        epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)
#                    
#        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')                                                                    
#
#        print "Acquiring flat images ..."    
#        epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
#        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
#        print "flat is done!"                
#        
#        print "Acquiring dark images ..."                
#        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
#        print "dark is done!"  
#    
#        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)        
#
#        cnt += 1                    
#        logFile.write("Scan #" + str(cnt-1) + " was done at time: " + time.asctime() + '\n')    
#        logFile.close()                                
#        print "scan #: ", str(ii+1), " is done!"            
#        if cnt != numTomoSweeps:
#            time.sleep(delay)
#
#    logFile.close()
#                    
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#    # scan sample -- end
# 
#    # set for new scans -- start
#    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
#    if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
#        epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)                
#    # set for new scans -- end
#    print "Scan is completed!!! Ready for the next scan ..."
#
#




def dimaxResetCrash():
    """
        Customize for Brian Patterson in situ loading experiments.
    """    
    exposureTime=0.0002
    slewSpeed=50
    angEnd = 10
    numProjPerSweep=15
    samInPos=0 
    roiSizeX = 1200 
    roiSizeY = 800    
                
    # tomo configurations -- start
    initDimax()    
    shutter = "2bma:A_shutter"
    samStage = "2bma:m49"
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly1"
    BL = "2bmb"        
    camPrefix = "PCOIOC2"    
    print "Reseting software ..."            
    # tomo configurations -- end                    

    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 20)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
            
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
    filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
    filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
    numImage = numProjPerSweep
    
    # test camera -- start
    _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = "2bmb:PSOFly1")    
    _dimaxSet(filepath, filename, numImage, exposureTime, frate, PSO = "2bmb:PSOFly1")
    epics.caput(camPrefix + ":cam1:FrameType.VAL","Normal", wait=True, timeout=1000.0) 
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numProjPerSweep), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numProjPerSweep), wait=True, timeout=1000.0)    
    epics.caput(samStage+".VAL",str(samInPos), wait=False, timeout=1000.0)
    epics.caput(PSO+":startPos.VAL","0", wait=False, timeout=1000.0)
    epics.caput(PSO+":endPos.VAL","15", wait=False, timeout=1000.0)
    epics.caput(PSO+":slewSpeed.VAL","50", wait=False, timeout=1000.0)
    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=1000.0)                    
#    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)    
    print "Saving sample data ..."     
                    
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)            

    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)                    

    time.sleep(2)
                    
    epics.caput(camPrefix + ":cam1:pco_cancel_dump",1, wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
    # set for new scans -- end
    print "Dimax is reset! Good to go."     


#
#
#def _InterlaceScan(exposureTime=0.006, 
#                samInPos=0, samOutPos=-4,
#                roiSizeX = 2560, roiSizeY = 800, trigTemp = 550, delay = 0, 
#                 repeat = 1, interval = 60,
#                accl = 1.0):
#    cam = "edge" 
#    shutter = "2bma:A_shutter"
#    samStage = "2bma:m20"
#    rotStage = "2bmb:m82"
#    PSO = "2bmb:PSOFly1"
#    BL = "2bmb"
#    epics.caput(PSO + ":scanControl.VAL","Custom", wait=True, timeout=1000.0) 
#    epics.caput(BL + ":iFly:interlaceFlySub.PROC",1, wait=True, timeout=1000.0) 
#    slewSpeed = epics.caget(PSO+":slewSpeed.VAL")
#    if cam == "edge":
#        initEdge()
#        camScanSpeed = "Fastest"
#        camShutterMode = "Rolling"                
#        camPrefix = "PCOIOC3"                                       
#
#        imgPerSubCycle = 1.0*epics.caget(BL + ":iFly:interlaceFlySub.A")/epics.caget(BL + ":iFly:interlaceFlySub.B")
#        secPerSubCycle = 180.0/epics.caget(BL + ":PSOFly1:slewSpeed.VAL")
#        frate = int(imgPerSubCycle/secPerSubCycle + 5)                          
#        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#        epics.caput(BL+":saveData_scanNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#
#        print "Scan starts ..."                
##        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                    
#        filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
#        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
#    
#        filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
#        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#        pathSep =  filepathString.rsplit('/')
#        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    
#        if not os.path.exists(logFilePath):
#            os.makedirs(logFilePath)
#                            
#        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#                
#        logFile = open(logFileName,'w')
#        logFile.close()                
#        print "Your scan is logged in ", logFileName
#        
#        numImage = epics.caget(BL+":iFly:interlaceFlySub.VALE")
#        
#        # test camera -- start
#        _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#        
#        # set scan parameters -- start
##        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
##        _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)
#            
#        # sample scan -- start  
#        print "start sample scan ... "
#        
#        
#        preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")
#        while ((epics.caget(BL+":ET2k:1:Temperature.VAL")-trigTemp)*(preTemp-trigTemp)>0):    
#            preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")            
#            time.sleep(0.5)
#        
#        time.sleep(delay) 
#        for ii in range(repeat):
#            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#            epics.caput(rotStage+".VELO","200", wait=True, timeout=1000.0)
#            epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0) 
#            _edgeInterlaceAcquisition(samInPos,samStage,numImage,shutter,InterlacePSO = PSO,rotStage=rotStage)                                       
#            if ii < (repeat-1):
#                print "repeat #", str(ii), " is done! next scan will be started in ", str(interval), " seconds ..." 
#                time.sleep(interval)  
#                
#
#        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
#        logFile = open(logFileName,'a')
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')
#        logFile.close()                                                                    
#        print "sample scan is done!"                          
#        # scan sample -- end                                                      
#        
#        # set for white field -- start
#        print "Acquiring flat images ..."    
#        
#        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
#        print "flat is done!"                
#        # set for white field -- end
#        
#        # set for dark field -- start
#        print "Acquiring dark images ..."                
#        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
#        print "dark is done!"  
#    
#        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#        # set for dark field -- end
#        
#        # set for new scans -- start        
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
#        # set for new scans -- end
#        print "Scan is done."
#    elif cam == "dimax":
#        initDimax(samInPos=samInPos)    
#        camPrefix = "PCOIOC2"        
#        # tomo configurations -- end                    
#    
##        scanDelta = 1.0*angEnd/numProjPerSweep
##        acclTime = 1.0*slewSpeed/accl
#        imgPerSubCycle = 1.0*epics.caget(BL + ":iFly:interlaceFlySub.A")/epics.caget(BL + ":iFly:interlaceFlySub.B")
#        secPerSubCycle = 180.0/epics.caget(BL + ":PSOFly1:slewSpeed.VAL")
#        frate = int(imgPerSubCycle/secPerSubCycle + 100)                          
#        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#        epics.caput(BL + ":saveData_scanNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
##        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":userCalc3.CALC",as_string=True), wait=True, timeout=1000.0)
#        print "Scan starts ..."                
##        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                    
#        filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
#        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
#    
#        filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
#        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
#        pathSep =  filepathString.rsplit('/')
#        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    
#        if not os.path.exists(logFilePath):
#            os.makedirs(logFilePath)
#                            
#        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#                
#        logFile = open(logFileName,'w')
#        logFile.close()                
#        print "Your scan is logged in ", logFileName
#        
#        numImage = epics.caget(BL+":iFly:interlaceFlySub.VALE")
##        numImage = epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")
#        
#        # test camera -- start
#        _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
#        # test camera -- end
#        
#        # set scan parameters -- start
#        _dimaxSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
##        _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)
#        # set scan parameters -- end
#                    
#        print "start sample scan ... "
#        epics.caput(rotStage+".VELO","200", wait=True, timeout=1000.0)
#        epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#        
#        preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")
#        while ((epics.caget(BL+":ET2k:1:Temperature.VAL")-trigTemp)*(preTemp-trigTemp)>0):    
#            preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")            
#            time.sleep(0.5)
#        
#        time.sleep(delay)                
#        _dimaxInterlaceAcquisition(samInPos,samStage,numImage,shutter,InterlacePSO = PSO,rotStage=rotStage)                        
#        
#        logFile = open(logFileName,'a')
#        logFile.write("Scan was done at time: " + time.asctime() + '\n')
#        logFile.close()                                                                    
#        print "sample scan is done!"                          
#        # scan sample -- end
#        
#        # set for white field -- start
#        print "Acquiring flat images ..."     
#        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
#        print "flat is done!"                
#        # set for white field -- end
#        
#        # set for dark field -- start
#        print "Acquiring dark images ..."                
#        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
#        print "dark is done!"  
#    
#        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#        # set for dark field -- end
#        
#        # set for new scans -- start        
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
#        # set for new scans -- end
#        print "Scan is done." 
#    epics.caput(PSO+":slewSpeed.VAL", slewSpeed, wait=True, timeout=1000.0)
#





def InterlaceScan(exposureTime=0.006, 
                samInPos=0, samOutPos=-4,
                roiSizeX = 2560, roiSizeY = 800, trigTemp = 550, delay = 0, 
                 repeat = 1, interval = 60,
                flatPerScan = 0, darkPerScan = 0,																	
                accl = 60.0):
    cam = "edge" 
    shutter = "2bma:A_shutter"
    samStage = "2bma:m20"
    posStage = "2bma:m20"				
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly2"
    BL = "2bmb"
    epics.caput(PSO + ":scanControl.VAL","Custom", wait=True, timeout=1000.0) 
    epics.caput(BL + ":iFly:interlaceFlySub.PROC",1, wait=True, timeout=1000.0) 
    slewSpeed = epics.caget(PSO+":slewSpeed.VAL")
    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch' 
								
    if cam == "edge":
        initEdge()
        camScanSpeed = "Fastest"
        camShutterMode = "Rolling"                
        camPrefix = "PCOIOC3"                                       

        imgPerSubCycle = 1.0*epics.caget(BL + ":iFly:interlaceFlySub.A")/epics.caget(BL + ":iFly:interlaceFlySub.B")
        secPerSubCycle = 180.0/epics.caget(BL + ":PSOFly1:slewSpeed.VAL")
        frate = int(imgPerSubCycle/secPerSubCycle + 5)                          
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
        epics.caput(BL+":saveData_scanNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)

        print "Scan starts ..."                

        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                    
        filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)                
        epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
        filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    
        filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
        filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
        pathSep =  filepathString.rsplit('/')
        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)
                        
        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                                    
        logFile = open(logFileName,'w')
        logFile.close()                 
        print "Your scan is logged in ", logFileName
        
        timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
                                                
        samInPos = epics.caget(samStage + ".VAL") 
        samOutPos = samInPos + samOutPos								
                                            
        filepath = os.path.join(filepath_top, \
               epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
               epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
               epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
               'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
               timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
               cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
               epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
               str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
               camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
               epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
               epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
               str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
               '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 

        numImage = epics.caget(BL+":iFly:interlaceFlySub.VALE")
        
        # test camera -- start
        _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
        
        # set scan parameters -- start
#        _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#        _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)
            
        # sample scan -- start  
        print "start sample scan ... "
        
        
        preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")
        while ((epics.caget(BL+":ET2k:1:Temperature.VAL")-trigTemp)*(preTemp-trigTemp)>0):    
            preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")            
            time.sleep(0.5)
        
        time.sleep(delay) 
        for ii in range(repeat):
            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
            epics.caput(rotStage+".VELO","200", wait=True, timeout=1000.0)
            epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0) 
            _edgeInterlaceAcquisition(samInPos,samStage,numImage,shutter,InterlacePSO = PSO,rotStage=rotStage)                                       
            if ii < (repeat-1):
                print "repeat #", str(ii), " is done! next scan will be started in ", str(interval), " seconds ..." 
                time.sleep(interval)  
                

        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end                                                      
        
        # set for white field -- start
        if flatPerScan == 0: 								
            print "Acquiring flat images ..."            
            _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
            print "flat is done!"                
        # set for white field -- end
        
#        # set for dark field -- start
        if darkPerScan == 0:								
            print "Acquiring dark images ..."                
            _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)            
            print "dark is done!"  
    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
            epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0) 								
        # set for dark field -- end
        
        # set for new scans -- start        
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
        # set for new scans -- end
        print "Scan is done."
    elif cam == "dimax":
        initDimax(samInPos=samInPos)    
        camPrefix = "PCOIOC2"        
        # tomo configurations -- end                    
    
#        scanDelta = 1.0*angEnd/numProjPerSweep
#        acclTime = 1.0*slewSpeed/accl
        imgPerSubCycle = 1.0*epics.caget(BL + ":iFly:interlaceFlySub.A")/epics.caget(BL + ":iFly:interlaceFlySub.B")
        secPerSubCycle = 180.0/epics.caget(BL + ":PSOFly1:slewSpeed.VAL")
        frate = int(imgPerSubCycle/secPerSubCycle + 100)                          
        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
        epics.caput(BL + ":saveData_scanNumber.VAL",epics.caget(BL+":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#        epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL+":userCalc3.CALC",as_string=True), wait=True, timeout=1000.0)
        print "Scan starts ..."                
#        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
        epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                    
        filepath = epics.caget(BL+":caputRecorderGbl_filepath.VAL")
        filename = epics.caget(BL+":caputRecorderGbl_filename.VAL")    
    
        filepathString = epics.caget(BL+":caputRecorderGbl_filepath.VAL",as_string=True)
        filenameString = epics.caget(BL+":caputRecorderGbl_filename.VAL",as_string=True)
        pathSep =  filepathString.rsplit('/')
        logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
    
        if not os.path.exists(logFilePath):
            os.makedirs(logFilePath)
                            
        logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
                
        logFile = open(logFileName,'w')
        logFile.close()                
        print "Your scan is logged in ", logFileName
        
        numImage = epics.caget(BL+":iFly:interlaceFlySub.VALE")
#        numImage = epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")
        
        # test camera -- start
        _dimaxTest(roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
        # test camera -- end
        
        # set scan parameters -- start
        _dimaxSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
#        _setPSO(slewSpeed, scanDelta, acclTime, PSO=PSO,rotStage=rotStage)
        # set scan parameters -- end
                    
        print "start sample scan ... "
        epics.caput(rotStage+".VELO","200", wait=True, timeout=1000.0)
        epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
        
        preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")
        while ((epics.caget(BL+":ET2k:1:Temperature.VAL")-trigTemp)*(preTemp-trigTemp)>0):    
            preTemp = epics.caget(BL+":ET2k:1:Temperature.VAL")            
            time.sleep(0.5)
        
        time.sleep(delay)                
        _dimaxInterlaceAcquisition(samInPos,samStage,numImage,shutter,InterlacePSO = PSO,rotStage=rotStage)                        
        
        logFile = open(logFileName,'a')
        logFile.write("Scan was done at time: " + time.asctime() + '\n')
        logFile.close()                                                                    
        print "sample scan is done!"                          
        # scan sample -- end
        
        # set for white field -- start
        print "Acquiring flat images ..."     
        _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)        
        print "flat is done!"                
        # set for white field -- end
        
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)                
        print "dark is done!"  
    
        epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
        # set for dark field -- end
        
        # set for new scans -- start        
        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
        epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
        epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
        epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
        # set for new scans -- end
        print "Scan is done." 
    epics.caput(PSO+":slewSpeed.VAL", slewSpeed, wait=True, timeout=1000.0)





def PGMultiPosScan(exposureTime=0.1, slewSpeed=1, angStart=0, angEnd = 180,
                numProjPerSweep=1501,
                samInPos=0, samOutPos=8.53,
                roiSizeX = 2560, roiSizeY = 1500,
                posStep = 0, posNum = 1, axisShift = 0.0,refYofX0 = 22.772,
                delay = 2380, flatPerScan = 1, darkPerScan = 1,
                accl = 2, shutterMode=0, scanMode=0, timeFile=0, clShutter=1):    
    """ Multiple poistion scans along vertical direction with edge camera
                
      axisShift: rotation axis shift in unit um/mm. it is defined as the shift distance when the vertical stage moves up.
              it assumes rotation axis is at image center at posInit.
    """
                
##### AHutch tomo configurations -- start
    initEdge(samInPos = samInPos)  
    if shutterMode == 0:
        camShutterMode = "Rolling"
    elif shutterMode == 1:
        camShutterMode = "Global"
    else:
        print "Wrong camera shutter mode! Quit ..."
        return False
        
    if scanMode == 0:
        camScanSpeed = 'Normal'
    elif scanMode == 1:
        camScanSpeed = 'Fast'
    elif scanMode == 2:
        camScanSpeed = 'Fastest'
    else:
        print "Wrong camera scan mode! Quit ..."  
        return False                
                                  
    camPrefix = "PCOIOC3"                
    shutter = "2bma:A_shutter"
                
#### for LAT                
    samStage = "2bma:m49"
    posStage = "2bma:m20"        
    rotStage = "2bmb:m82"
    top0Deg = "2bmS1:m2"
    top90Deg = "2bmS1:m1"    
    PSO = "2bmb:PSOFly2"
                
    samInInitPos = epics.caget(samStage + ".VAL")                
    BL = "2bmb"
    posRefPos = refYofX0                   
##### AHutch tomo configurations -- end                                                 

    if camPrefix == 'PCOIOC3':
        cam = 'edge'
    elif camPrefix == 'PCOIOC2':
        cam = 'dimax'    

    if samStage.split(':')[0] == '2bma':
        station = 'AHutch'
    elif samStage.split(':')[0] == '2bmb':    
        station = 'BHutch'                                
    filepath_top = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
                
    epics.caput(camPrefix + ":HDF1:CreateDirectory.VAL", -5, wait=True, timeout=1000.0)
                
    posInit = epics.caget(posStage+".VAL")
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    scanDelta = 1.0*(angEnd-angStart)/numProjPerSweep
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*(angEnd-angStart)/slewSpeed) + 5)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget(BL + ":caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    filename = epics.caget(BL + ":caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget(BL + ":caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget(BL + ":caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#    print 2
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your scan is logged in ", logFileName
    
    numImage = numProjPerSweep+20
    
    # test camera -- start
    print roiSizeX,roiSizeY    
    _edgeTest(camScanSpeed,camShutterMode,roiSizeX=roiSizeX,roiSizeY=roiSizeY,PSO = PSO)
    
                
    # sample scan -- start    
    if timeFile == 1:
        tf = open('/local/user2bmb/2016_10/Qi/timeSeq.txt')                    
        timeSeq = tf.readlines()
        tf.close()             
    print "start sample scan ... "
    
    samInPosList = [0.038, -0.026, -0.191]
    samOutPosList = [8.52, 8.87, 8.7]
    yPosList = [12.282, 16.482, 27.182]
    top0DegList = [-8.175, -8.505, -8.585]
    top90DegList = [9.162, 9.392, 9.492]
    for ii in range(posNum):    
    # set scan parameters -- start 
        if timeFile == 1:
            delay = float(timeSeq[ii]) 

        for jj in range(3):            
            timestamp = [x for x in time.asctime().rsplit(' ') if x!='']                                 
     
            samInPos = samInPosList[jj]
            samOutPos = samOutPosList[jj] 
            epics.caput(posStage, str(yPosList[jj]),wait=True,timeout=1000.0)
            epics.caput(top0Deg, str(top0DegList[jj]),wait=True,timeout=1000.0)
            epics.caput(top90Deg, str(top90DegList[jj]),wait=True,timeout=1000.0)            
    
            filepath = os.path.join(filepath_top, \
                   epics.caget(BL + ":caputRecorderGbl_1.VAL",as_string=True)+ \
                   epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True).zfill(3)+'_'+ \
                   epics.caget(BL + ":caputRecorderGbl_4.VAL",as_string=True)+'_'+\
                   'YPos'+str(int(epics.caget(posStage + ".VAL")*1000)/1000.0)+'mm_'+\
                   timestamp[0] + timestamp[1] + timestamp[2] + '_' + timestamp[3].replace(':','_') + '_' + timestamp[4] + '_'+\
                   cam+'_'+epics.caget(BL + ":caputRecorderGbl_5.VAL",as_string=True)+'x'+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_6.VAL",as_string=True)+'mm'+'_'+\
                   str(exposureTime*1000)+'msecExpTime_'+str(slewSpeed)+'DegPerSec_'+\
                   camShutterMode+'_'+epics.caget(BL + ":caputRecorderGbl_7.VAL",as_string=True)+'um'+\
                   epics.caget(BL + ":caputRecorderGbl_8.VAL",as_string=True)+'_'+\
                   epics.caget(BL + ":caputRecorderGbl_9.VAL",as_string=True)+'_'+\
                   str(int(epics.caget('2bma:M1angl.VAL')*1000)/1000.0)+'mrad_USArm'+str(int(epics.caget('2bma:m30.VAL')*1000)/1000.0)+\
                   '_monoY_'+str(int(epics.caget('2bma:m26.VAL')*1000)/1000.0)+'_'+station) 
                       
            _edgeSet(filepath, filename, numImage, exposureTime, frate, PSO = PSO)
            _setPSO(slewSpeed, scanDelta, acclTime, angStart=angStart, angEnd=angEnd, PSO=PSO,rotStage=rotStage)                              
            epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
            epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                    
            time.sleep(3)                                                            
            _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,PSO = PSO,rotStage=rotStage)
            epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
            print "scan at position #",ii+1," is done!"
    
#            samOutPos = samInPos + samOutPos
            
            if flatPerScan == 1:
            # set for white field -- start                   
                print "Acquiring flat images ..."                   
                _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)            
                print "flat for position #", ii+1, " is done!"                
            # set for white field -- end                                            
                                    
            if darkPerScan == 1:
                # set for dark field -- start
                print "Acquiring dark images ..."                
                _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)    
                epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    #            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)             
                print "dark is done!"  
    
            epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
            epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
            # set for dark field -- end
                                    
            if epics.caget(BL + ":caputRecorderGbl_3.VAL",as_string=True) == 'Yes':
                epics.caput(BL + ":caputRecorderGbl_2.VAL", str(int(epics.caget(BL + ":caputRecorderGbl_2.VAL",as_string=True))+1), wait=True, timeout=1000.0)   

        epics.caput(posStage, str(yPosList[0]),wait=False,timeout=1000.0)                
        if ii != (posNum-1):
            time.sleep(delay)

    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)      
    epics.caput("2bma:m23.VAL","1", wait=True, timeout=1000.0)                                            
    print "sample scan is done!"          
                                


    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()                                                                    
                         
    # sample scan -- end

    if flatPerScan == 0:    
        # set for white field -- start                   
        print "Acquiring flat images ..."    
        epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)    
        time.sleep(3)                
        _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)         
        print "flat is done!"                
        # set for white field -- end

    if darkPerScan == 0:    
        # set for dark field -- start
        print "Acquiring dark images ..."                
        _edgeAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = PSO)  
        epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#        epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)           
        print "dark is done!"  

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(BL+":caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL","Normal", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode.VAL","Continuous", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".VAL",str(samInInitPos), wait=True, timeout=1000.0)
#    epics.caput(posStage + ".VAL",str(posInit), wait=False, timeout=1000.0)                                                                
    # set for new scans -- end
    print "Scan finished!" 
    
                






def _setPSO(slewSpeed, scanDelta, acclTime,angStart=0, angEnd=180, PSO="2bmb:PSOFly1",rotStage="2bmb:m82"):
    epics.caput(PSO+":startPos.VAL",str(angStart), wait=True, timeout=1000.0)                
    epics.caput(PSO+":endPos.VAL",str(angEnd), wait=True, timeout=1000.0)
    epics.caput(rotStage+".VELO",str(slewSpeed), wait=True, timeout=1000.0)
    epics.caput(PSO+":slewSpeed.VAL",str(slewSpeed), wait=True, timeout=1000.0)
    epics.caput(rotStage+".ACCL",str(acclTime), wait=True, timeout=1000.0)
    epics.caput(PSO+":scanDelta.VAL",str(scanDelta), wait=True, timeout=1000.0)    



def _edgeTest(camScanSpeed,camShutterMode,roiSizeX=2560,roiSizeY=2160,PSO = "2bmb:PSOFly1"):
    camPrefix = "PCOIOC3"
#    epics.caput(camPrefix+":cam1:scanControl.VAL","Standard", wait=True, timeout=1000.0)            
    epics.caput(camPrefix+":cam1:ArrayCallbacks.VAL","Enable", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:ImageMode.VAL","Multiple", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_global_shutter.VAL",camShutterMode, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_edge_fastscan.VAL",camScanSpeed, wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":cam1:AcquireTime.VAL","0.001000", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
    print "camera passes test!"
                
def _edgeSet(filepath, filename, numImage, exposureTime, frate,
          PSO = "2bmb:PSOFly1"):    
    camPrefix = "PCOIOC3"
    epics.caput(camPrefix+":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:AcquirePeriod.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_set_frame_rate.VAL",str(frate+1), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)                    
    epics.caput(camPrefix+":HDF1:AutoIncrement.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)  
    epics.caput(camPrefix+":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
    epics.caput(camPrefix+":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
    epics.caput(camPrefix+":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix+":cam1:NumImages.VAL",str(numImage), wait=True, timeout=1000.0)                                
    epics.caput(camPrefix+":cam1:ImageMode.VAL","Multiple", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Soft/Ext", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)            
            
def _edgeAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1, PSO = "2bmb:PSOFly1",rotStage="2bmb:m82"):
    camPrefix = "PCOIOC3"    
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)                
#    epics.caput(camPrefix+":cam1:FrameType.VAL",'Normal', wait=True, timeout=1000.0) 
    epics.caput(camPrefix+":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0)     
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)                    
    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=1000.0) 
    if epics.caget(PSO+":fly.VAL") == 0 & clShutter == 1:               
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)     
    rotCurrPos = epics.caget(rotStage + ".VAL")
    epics.caput(rotStage + ".SET",str(1), wait=True, timeout=1000.0)       
    epics.caput(rotStage + ".VAL",str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0) 
    epics.caput(rotStage + ".SET",str(0), wait=True, timeout=1000.0)              
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    time.sleep(1)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)   
#    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)                  
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != numProjPerSweep):    
        time.sleep(1)                    
            
def _edgeInterlaceAcquisition(samInPos,samStage,numProjPerSweep,shutter,clShutter=1,InterlacePSO = "2bmb:PSOFly1",rotStage="2bmb:m82"):
    camPrefix = "PCOIOC3"    
    epics.caput(camPrefix+":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0) 
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    epics.caput(InterlacePSO+":fly.VAL","Fly", wait=True, timeout=1000.0)                    
#    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)    
#    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    if clShutter == 1:               
        epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0) 
    rotCurrPos = epics.caget(rotStage + ".VAL")
    epics.caput(rotStage + ".SET",str(1), wait=True, timeout=1000.0)     
    epics.caput(rotStage + ".VAL",str(1.0*rotCurrPos%360.0), wait=True, timeout=1000.0)	
    epics.caput(rotStage + ".SET",str(0), wait=True, timeout=1000.0)     
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)    
    numProjPerSweep = epics.caget(camPrefix+":cam1:NumImagesCounter_RBV.VAL")
    print "Saving sample data ..."                
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != numProjPerSweep):    
        time.sleep(1)                    
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    
                        
def _edgeAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage, shutter, PSO = "2bmb:PSOFly1"):    
    camPrefix = "PCOIOC3"
    epics.caput(samStage+".VAL",str(samOutPos), wait=True, timeout=1000.0)                
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)                
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(camPrefix+":cam1:FrameType.VAL",'2', wait=True, timeout=1000.0)     
    epics.caput(camPrefix+":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)   
    
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)   
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)  
        
#    epics.caput(PSO+":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO+":endPos.VAL","6.0000", wait=True, timeout=1000.0)
#    epics.caput(PSO+":scanDelta.VAL","0.3", wait=True, timeout=1000.0)
#    epics.caput(PSO+":slewSpeed.VAL","1", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".VELO","3", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".ACCL","1.", wait=True, timeout=1000.0)                
#    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".VAL","0.00000", wait=True, timeout=1000.0)
    
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)            
#    while (epics.caget(camPrefix+":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)                
    epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)                    
    # set for white field -- end

def _edgeAcquireDark(samInPos,filepath,samStage,rotStage, shutter, PSO = "2bmb:PSOFly1"):    
    camPrefix = "PCOIOC3"    
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)
    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
            
    epics.caput(camPrefix+":cam1:FrameType.VAL",'1', wait=True, timeout=1000.0)             
    epics.caput(camPrefix+":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)

    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)            
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
        
        
#    epics.caput(PSO+":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO+":endPos.VAL","6.0000", wait=True, timeout=1000.0)
#    epics.caput(PSO+":scanDelta.VAL","0.3", wait=True, timeout=1000.0)
#    epics.caput(PSO+":slewSpeed.VAL","1", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".VELO","3", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".ACCL","1.", wait=True, timeout=1000.0)                
#    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage+".VAL","0.00000", wait=True, timeout=1000.0)   
             
#    while (epics.caget(camPrefix+":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)                
    epics.caput(camPrefix+":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)    




def _dimaxTest(roiSizeX=2560,roiSizeY=2160,PSO = "2bmb:PSOFly1"):
    camPrefix = "PCOIOC2"
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","No", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_global_shutter.VAL","Global", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL","0.001000", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    print "test camera ..."
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
#    print 'to stop'
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    print "camera passes test!"
                
def _dimaxSet(numImage, exposureTime, frate):    
    camPrefix = "PCOIOC2"
    print "Set writer ..."                
    epics.caput(camPrefix + ":cam1:NumImages.VAL",str(numImage-0), wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL","0", wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate+.1), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Soft/Ext", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoIncrement.VAL",'Yes', wait=True, timeout=1000.0) 
    epics.caput(camPrefix + ":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                  
#    time.sleep(2)    
    #    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage), wait=True, timeout=1000.0)    
                
def _dimaxDump(filepath, filename):    
    camPrefix = "PCOIOC2"    
    print filepath  
         
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)

    time.sleep(5)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0) 
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)  
#    while epics.caget(camPrefix + ":HDF1:Capture_RBV.VAL") != 'Capturing':
#         epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)   
#         time.sleep(1)
    time.sleep(5)     
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)                                
    
    
            
def _dimaxAcquisition(samInPos,samStage,numProjPerSweep,shutter,filepath,filename,PSO = "2bmb:PSOFly1",rotStage="2bmb:m82"):
    camPrefix = "PCOIOC2"
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0) 
    epics.caput(camPrefix + ":cam1:pco_dump_counter.VAL",str(0), wait=True, timeout=1000.0)       
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numProjPerSweep), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numProjPerSweep), wait=True, timeout=1000.0)    
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)                
    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=10000.0)                    
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".ACCL","1.00000", wait=True, timeout=1000.0)                
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput("2bma:m23.VAL","0", wait=True, timeout=1000.0)                
    print "Saving sample data ..."                 
    _dimaxDump(filepath, filename)                                
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_imgs2dump_RBV.VAL")):   
#    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_num_imgs_seg0_RBV.VAL")):     
        time.sleep(1)                    
    
            
def _dimaxAcquisitionWODump(samInPos,samStage,numProjPerSweep,shutter,PSO = "2bmb:PSOFly1",rotStage="2bmb:m82"):
    camPrefix = "PCOIOC2"    
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(2)
    epics.caput(camPrefix + ":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0)                 
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","60.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)                
    epics.caput(PSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO+":fly.VAL","Fly", wait=True, timeout=1000.0)                    
#    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","60.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)            


def _dimaxAcquisitionBackforthWODump(samInPos,samStage,numSweep,delay,shutter,rotStage="2bmb:m82"):
    """
      PSO is hard coded in the userStringSeq record as PSOFly2
    """
    camPrefix = "PCOIOC2"    
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(2)
    epics.caput(camPrefix + ":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0)                 
    epics.caput(samStage+".VAL",str(samInPos), wait=True, timeout=1000.0)
    for ii in range(numSweep):
        epics.caput("2bmb:userStringSeq3.PROC",1, wait=True, timeout=1000.0)
        print ii
        time.sleep(delay)
    epics.caput(rotStage + ".VELO","60.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","90.00000", wait=False, timeout=1000.0)   
 


                
def _dimaxInterlaceAcquisition(samInPos,samStage,numProjPerSweep,shutter,InterlacePSO = "2bmb:PSOFly1",rotStage="2bmb:m82"):
    camPrefix = "PCOIOC2"
    epics.caput(camPrefix + ":cam1:FrameType.VAL",'0', wait=True, timeout=1000.0) 
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(numProjPerSweep), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(numProjPerSweep), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_dump_counter.VAL",str(0), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")), wait=True, timeout=1000.0)
    epics.caput(samStage+".VAL",str(samInPos), wait=False, timeout=1000.0)
#    epics.caput(InterlacePSO+":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(InterlacePSO+":fly.VAL","Fly", wait=True, timeout=1000.0)                    
#    epics.caput(shutter+":close.VAL",1, wait=True, timeout=1000.0)
    epics.caput(shutter+":open.VAL",1, wait=True, timeout=1000.0)
    epics.caput("2bmb:tableFly2:sseq2.PROC", 1, wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)    
    print "Saving sample data ..."                 
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)        
    
#    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != (numProjPerSweep-0)):
    while (epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL") != epics.caget(camPrefix+":cam1:pco_max_imgs_seg0_RBV.VAL")):    
        time.sleep(1)
#        print numProjPerSweep-20
#        print epics.caget(camPrefix+":HDF1:NumCaptured_RBV.VAL")
                                
def _dimaxAcquireFlat(samInPos,samOutPos,filepath,samStage,rotStage,shutter, PSO = "2bmb:PSOFly1"):    
    camPrefix = "PCOIOC2"
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)
    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)                
    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:FrameType.VAL",'2', wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
#    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":endPos.VAL","6", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":slewSpeed.VAL","3.0", wait=True, timeout=1000.0)
#    epics.caput(PSO+":scanDelta.VAL","0.3", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","3.0", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)        
#    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":fly.VAL","Fly", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)   
    
    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)   
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)  
    
    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)
    time.sleep(2)     
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(samStage + ".VAL","0", wait=True, timeout=1000.0)



def _dimaxAcquireDark(samInPos,filepath,samStage,rotStage,shutter, PSO = "2bmb:PSOFly1"):    
    camPrefix = "PCOIOC2"
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0) 
    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:FrameType.VAL",'1', wait=True, timeout=1000.0)             
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
#    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":endPos.VAL","6", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":slewSpeed.VAL","3.0", wait=True, timeout=1000.0)
#    epics.caput(PSO+":scanDelta.VAL","0.3", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","3.0", wait=True, timeout=1000.0)    
#    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)                
#    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":fly.VAL","Fly", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)

    epics.caput(camPrefix+":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)   
    epics.caput(camPrefix+":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)  
    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)
    time.sleep(2)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)    

def _readCounterFFT(readCounter="32idcTXM:SG_RdCntr:", readFreq=1000, arrayCalc="32idcTXM:SG_RdCntr:fft", acqTime_s=10):
    if readFreq > 10000:  readFreq = 10000
    source = arrayCalc+".AA"
    dest = arrayCalc+".BB"
    t = arrayCalc+".CC"
    trig = readCounter+"acquire"
    oneshot = readCounter+"oneshot"
    softGlue = "32idcTXM:softGlue:"
    # save state of "oneshot" switch
    save_oneshot = epics.caget(oneshot)
    # make sure softGlue is triggering interrupts
    epics.caput(softGlue+"In_17IntEdge", "None")
    epics.caput(softGlue+"In_17IntEdge", "Rising")
    # set encoder-read frequency
    epics.caput(softGlue+"DivByN-3_N", 8.e6/readFreq)
    # set plot-update rate
    epics.caput("32idcTXM:SG_RdCntr:cVals.SCAN", "1 second")
    # set readCounter to "oneshot" mode
    epics.caput(oneshot, "oneshot", wait=True, timeout=100)
    # set number of points to acquire
    maxN = epics.caget("32idcTXM:SG_RdCntr:cVals.NELM")
    n = min(maxN, acqTime_s*readFreq)
    epics.caput("32idcTXM:SG_RdCntr:cVals.NUSE", n)
    epics.caput(trig, "Busy", wait=True, timeout=10000)
    epics.caput(arrayCalc+".PROC", 1, wait=True)
    d = epics.caget(source)
    n = epics.caget(arrayCalc+".NUSE")
    d = d[0:n]
    f = np.fft.rfft(d-np.average(d))
    ticksPerSample = epics.caget("32idcTXM:softGlue:DivByN-3_N")
    dt = 125e-9 * ticksPerSample
    freq = np.fft.fftfreq(len(d), d=dt)
    epics.caput(dest, abs(f.real))
    epics.caput(t, freq[0:len(freq)/2])
    # restore "oneshot" mode
    #epics.caput(oneshot, save_oneshot)

                                        








#### setting used in 2015_08
#def BrianLoadScan(exposureTime=0.0002, slewSpeed=720,angEnd = 3960,
#                numProjPerSweep=19826,
#                samInPos=0, samOutPos=14,
#                roiSizeX = 2016, roiSizeY = 600, 
#                loadStageDis=-0.7, loadStageVelo=0.1, acqDelay=0,
#                accl = 10.0):

#### setting used in 2016_04 for 5x lens configuration
#def BrianLoadScan(exposureTime=0.0002, slewSpeed=720,angEnd = 3780,
#                numProjPerSweep=12622,
#                samInPos=0, samOutPos=10,
#                roiSizeX = 1392, roiSizeY = 1400, 
#                loadStageDis=-1.0, loadStageVelo=0.3, acqDelay=0,
#                accl = 72):
#### setting used in 2016_04 for 2x lens configuration 1
#def BrianLoadScan(exposureTime=0.0002, slewSpeed=720,angEnd = 6300,
#                numProjPerSweep=21038,
#                samInPos=0, samOutPos=10,
#                roiSizeX = 2016, roiSizeY = 600, 
#                loadStageDis=-1.0, loadStageVelo=0.3, acqDelay=0,
#                accl = 72):    
### setting used in 2016_04 for 2x lens configuration 2
# for 601proj/scan, 2016x600 frame size, the combination of number of images vs total scan time has
# 3sec : 7213
# 4sec : 9617
# 5sec : 12021
# 6sec : 14426
# 7sec : 16830
# 8sec : 19235
# 8.5sec : 20437
def BrianLoadScan(exposureTime=0.0002, slewSpeed=720,angEnd = 4680,
                numProjPerSweep=15628,
                samInPos=0, samOutPos=10,
                roiSizeX = 2016, roiSizeY = 600, 
                loadStageDis=-1.0, loadStageVelo=0.5, acqDelay=0,
                accl = 72):                        
#def BrianLoadScan(exposureTime=0.0002, slewSpeed=20,angEnd = 60,
#                numProjPerSweep=20,
#                samInPos=0, samOutPos=0,
#                roiSizeX = 1392, roiSizeY = 1400, 
#                loadStageDis=-0.7, loadStageVelo=0.1, acqDelay=0,
#                accl = 10.0):
    """
        Customize for Brian Patterson in situ loading experiments.
    """
                
    # tomo configurations -- start
    initDimax()    
    epics.caput("2bmb:scaler3.CONT","OneShot", wait=True, timeout=1000.0)
    epics.caput("2bmb:m82.CNEN","Enable", wait=True, timeout=1000.0)
    epics.caput("2bmb:setModuloPos.PROC", 1, wait=True, timeout=1000.0)                
    DimaxSingleScan(exposureTime=3*exposureTime, slewSpeed=30.0,angEnd = 180,
                numProjPerSweep=1500,
                samInPos=samInPos, samOutPos=samOutPos,
                roiSizeX = roiSizeX, roiSizeY = roiSizeY,
                accl = 15.0)
            
    camPrefix = "PCOIOC2"                
    shutter = "2bma:A_shutter"
    samStage = "2bma:m49"
    rotStage = "2bmb:m82"
    PSO = "2bmb:PSOFly1"
    # tomo configurations -- end                    

#### setting used in 2016_04 for 5x lens configuration
#    scanDelta = 1.0*angEnd/(numProjPerSweep-1)
#### setting used in 2016_04 for 2x lens configuration 1
#    scanDelta = 1.0*angEnd/(numProjPerSweep-3)
### setting used in 2016_04 for 2x lens configuration 2
    scanDelta = 1.0*angEnd/(numProjPerSweep-2)
    acclTime = 1.0*slewSpeed/accl
    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 20)                

    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget("2bmb:caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
                
    print "in situ Scan starts ..."                
    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
                
    filepath = epics.caget("2bmb:caputRecorderGbl_filepath.VAL")
    filename = epics.caget("2bmb:caputRecorderGbl_filename.VAL")    

    filepathString = epics.caget("2bmb:caputRecorderGbl_filepath.VAL",as_string=True)
    filenameString = epics.caget("2bmb:caputRecorderGbl_filename.VAL",as_string=True)
    pathSep =  filepathString.rsplit('/')
    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            

    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath)
                        
    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
            
    logFile = open(logFileName,'w')
    logFile.close()                
    print "Your log file is save in ", logFileName
    
    numImage = numProjPerSweep
    
    # test camera -- start
    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ArrayCallbacks.VAL","Enable", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","No", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_global_shutter.VAL","Global", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL","0.001000", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    print "test camera ..."
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
    print "camera passes test!"
    # test camera -- end

    # set for white field -- start
    print "start acquire in situ flat ..."
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)                
    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
    epics.caput(PSO + ":endPos.VAL",str(30*scanDelta), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","5.0", wait=True, timeout=1000.0)
    epics.caput(PSO + ":slewSpeed.VAL","5.0", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)                
    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO + ":fly.VAL","Fly", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)
    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
    time.sleep(5)
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
        time.sleep(1)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)        
    print "in situ flat acquire is done!"                
    # set for white field -- end
    
    # set for dark field -- start
    print "start acquire in situ dark ..."                
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
                
    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
    epics.caput(PSO + ":endPos.VAL",str(30*scanDelta), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","5.0", wait=True, timeout=1000.0)
    epics.caput(PSO + ":slewSpeed.VAL","5.0", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(PSO + ":fly.VAL","Fly", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
        time.sleep(1)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    print "in situ dark acquire is done!"  

    
    # set scan parameters -- start
    print "Set writer for in situ ..."                
#    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage-5), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage-5), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
    epics.caput(samStage + ".VAL","0.00000", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:NumImages.VAL",str(numImage), wait=True, timeout=1000.0)                
    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
    epics.caput(PSO + ":endPos.VAL", str(angEnd), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VELO",str(slewSpeed), wait=True, timeout=1000.0)
    epics.caput(PSO + ":slewSpeed.VAL",str(slewSpeed), wait=True, timeout=1000.0)
    epics.caput(rotStage + ".ACCL",str(acclTime), wait=True, timeout=1000.0)
    epics.caput(PSO + ":scanDelta.VAL",str(scanDelta), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL","0", wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Soft/Ext", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)                    
    epics.caput("2bmb:loadDist.VAL",loadStageDis, wait=True, timeout=1000.0)                
    epics.caput("2bmb:loadSpeed.VAL",loadStageVelo, wait=True, timeout=1000.0)                
    epics.caput("2bmb:tomo_load_time.VAL",acqDelay, wait=True, timeout=1000.0)                    
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)            
    # set scan parameters -- end
                
    # scan sample -- start
#    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
#    time.sleep(5)
                
    print "start in situ acquisition ... "        
    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)                
    print "start in situ fly"
    _loadCellAfterTaxi(PSOFly="2bmb:PSOFly1:", loadMotor="2bma:m58", MCS="2bmb:mcs:", loadIOpin=20, tomoIOpin=21)
    print 0                
    epics.caput("2bmb:loadCellStartMeasurement.PROC", 1, wait=True, timeout=1000.0)                    
    print "in situ fly done"
                
    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
    epics.caput("2bmb:setModuloPos.PROC", 1, wait=True, timeout=1000.0)                            
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)            
    print "in situ acquisition is done! Saving images now ..."          

#            while (epics.caget(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL") != epics.caget(camPrefix + ":cam1:pco_max_imgs_seg0_RBV.VAL")):    
#                time.sleep(1)
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    nImages = np.int(epics.caget("PCOIOC2:cam1:pco_num_imgs_seg0_RBV.VAL"))
    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(nImages), wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(nImages), wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage-5), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage-5), wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)    
    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
        time.sleep(1)
                    

    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)

    logFile = open(logFileName,'a')
    logFile.write("Scan was done at time: " + time.asctime() + '\n')
    logFile.close()    
                                                                
    print "in situ scan is done!"                          
    # scan sample -- end
    
    # reset rotation stage position -- start                
    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)
    print "stop acquire"
    # reset rotation stage position -- end
    

    epics.caput("2bmb:caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
    # set for dark field -- end
    
    # set for new scans -- start
    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
    epics.caput("2bmb:scaler3.CONT","AutoCount", wait=True, timeout=1000.0)                
    # set for new scans -- end
    print "Scan is completed!!! Ready for the next scan ..."    







#
#
#
#
#
##### setting used in 2015_08
##def BrianLoadScan(exposureTime=0.0002, slewSpeed=720,angEnd = 3960,
##                numProjPerSweep=19826,
##                samInPos=0, samOutPos=14,
##                roiSizeX = 1392, roiSizeY = 1400, 
##                loadStageDis=-0.7, loadStageVelo=0.1, acqDelay=0,
##                accl = 10.0):
#
#### setting used in 2016_04
#def BrianLoadScan(exposureTime=0.0002, slewSpeed=720,angEnd = 3780,
#                numProjPerSweep=12622,
#                samInPos=0, samOutPos=4,
#                roiSizeX = 1392, roiSizeY = 1400, 
#                loadStageDis=1.0, loadStageVelo=0.1, acqDelay=0,
#                accl = 72):
##def BrianLoadScan(exposureTime=0.0002, slewSpeed=20,angEnd = 60,
##                numProjPerSweep=20,
##                samInPos=0, samOutPos=0,
##                roiSizeX = 1392, roiSizeY = 1400, 
##                loadStageDis=-0.7, loadStageVelo=0.1, acqDelay=0,
##                accl = 10.0):
#    """
#        Customize for Brian Patterson in situ loading experiments.
#    """
#                
#    # tomo configurations -- start
#    initDimax()    
#    epics.caput("2bmb:scaler3.CONT","OneShot", wait=True, timeout=1000.0)
#    epics.caput("2bmb:m82.CNEN","Enable", wait=True, timeout=1000.0)
#    epics.caput("2bmb:setModuloPos.PROC", 1, wait=True, timeout=1000.0)                
#    DimaxSingleScan(exposureTime=3*exposureTime, slewSpeed=30.0,angEnd = 180,
#                numProjPerSweep=1500,
#                samInPos=samInPos, samOutPos=samOutPos,
#                roiSizeX = roiSizeX, roiSizeY = roiSizeY,
#                accl = 15.0)
#            
#    camPrefix = "PCOIOC2"                
#    shutter = "2bma:A_shutter"
#    samStage = "2bma:m49"
#    rotStage = "2bmb:m82"
#    PSO = "2bmb:PSOFly1"
#    # tomo configurations -- end                    
#
#    scanDelta = 1.0*angEnd/(numProjPerSweep-1)
#    acclTime = 1.0*slewSpeed/accl
#    frate = int(1.0*numProjPerSweep/(1.0*angEnd/slewSpeed) + 20)                
#
#    epics.caput(camPrefix + ":HDF1:FileNumber.VAL",epics.caget("2bmb:caputRecorderGbl_10.VAL",as_string=True), wait=True, timeout=1000.0)
#                
#    print "Scan starts ..."                
#    epics.caput(shutter + ":open.VAL", 1, wait=True, timeout=1000.0)
#                
#    filepath = epics.caget("2bmb:caputRecorderGbl_filepath.VAL")
#    filename = epics.caget("2bmb:caputRecorderGbl_filename.VAL")    
#
#    filepathString = epics.caget("2bmb:caputRecorderGbl_filepath.VAL",as_string=True)
#    filenameString = epics.caget("2bmb:caputRecorderGbl_filename.VAL",as_string=True)
#    pathSep =  filepathString.rsplit('/')
#    logFilePath = os.path.join('/local/user2bmb', pathSep[-3],pathSep[-2],pathSep[-1])            
#
#    if not os.path.exists(logFilePath):
#        os.makedirs(logFilePath)
#                        
#    logFileName = os.path.join(logFilePath, filenameString+ "_" + "%(index)03d"%{"index":int(epics.caget(camPrefix + ":HDF1:FileNumber.VAL"))} + ".log")                                                                                                        
#            
#    logFile = open(logFileName,'w')
#    logFile.close()                
#    print "Your log file is save in ", logFileName
#    
#    numImage = numProjPerSweep
#    
#    # test camera -- start
#    epics.caput(PSO + ":scanControl.VAL","Standard", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:ArrayCallbacks.VAL","Enable", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","No", wait=True, timeout=1000.0)
##    epics.caput(camPrefix + ":cam1:pco_global_shutter.VAL","Global", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:AcquireTime.VAL","0.001000", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    print "test camera ..."
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=True, timeout=1000.0)
#    print "camera passes test!"
#    # test camera -- end
#    
#    # set scan parameters -- start
#    print "Set writer ..."                
##    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage-5), wait=True, timeout=1000.0)    
##    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage-5), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCaptured_RBV.VAL","0", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:FileName.VAL",filename, wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:FileTemplate.VAL","%s%s_%4.4d.hdf", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
#    epics.caput(samStage + ".VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:NumImages.VAL",str(numImage), wait=True, timeout=1000.0)                
#    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":endPos.VAL", str(angEnd), wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO",str(slewSpeed), wait=True, timeout=1000.0)
#    epics.caput(PSO + ":slewSpeed.VAL",str(slewSpeed), wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".ACCL",str(acclTime), wait=True, timeout=1000.0)
#    epics.caput(PSO + ":scanDelta.VAL",str(scanDelta), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL","0", wait=True, timeout=1000.0)                    
#    epics.caput(camPrefix + ":cam1:pco_is_frame_rate_mode.VAL","DelayExp", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_set_frame_rate.VAL",str(frate), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:AcquireTime.VAL",str(exposureTime), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Soft/Ext", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)                    
#    epics.caput("2bmb:loadDist.VAL",loadStageDis, wait=True, timeout=1000.0)                
#    epics.caput("2bmb:loadSpeed.VAL",loadStageVelo, wait=True, timeout=1000.0)                
#    epics.caput("2bmb:tomo_load_time.VAL",acqDelay, wait=True, timeout=1000.0)                    
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)            
#    # set scan parameters -- end
#                
#    # scan sample -- start
##    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
##    time.sleep(5)
#                
#    print "start acquisition ... "        
#    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)                
#    print "start fly"
#    _loadCellAfterTaxi(PSOFly="2bmb:PSOFly1:", loadMotor="2bma:m58", MCS="2bmb:mcs:", loadIOpin=20, tomoIOpin=21)
#    print 0                
#    epics.caput("2bmb:loadCellStartMeasurement.PROC", 1, wait=True, timeout=1000.0)                    
#    print "fly done"
#                
#    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
#    epics.caput("2bmb:setModuloPos.PROC", 1, wait=True, timeout=1000.0)                            
#    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VAL","0.00000", wait=False, timeout=1000.0)            
#    print "acquisition is done!"          
#
##            while (epics.caget(camPrefix + ":cam1:pco_num_imgs_seg0_RBV.VAL") != epics.caget(camPrefix + ":cam1:pco_max_imgs_seg0_RBV.VAL")):    
##                time.sleep(1)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    nImages = np.int(epics.caget("PCOIOC2:cam1:pco_num_imgs_seg0_RBV.VAL"))
#    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(nImages), wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(nImages), wait=True, timeout=1000.0)                
##    epics.caput(camPrefix + ":HDF1:NumCapture.VAL",str(numImage-5), wait=True, timeout=1000.0)    
##    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL",str(numImage-5), wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)    
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)
#                    
#
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)
#
#    logFile = open(logFileName,'a')
#    logFile.write("Scan was done at time: " + time.asctime() + '\n')
#    logFile.close()    
#                                                                
#    print "scan is done!"                          
#    # scan sample -- end
#    
#    # reset rotation stage position -- start                
#    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)
#    print "stop acquire"
#    # reset rotation stage position -- end
#    
#    # set for white field -- start
#    print "start acquire flat ..."                
#    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
#    time.sleep(5)
#    epics.caput(samStage + ".VAL",str(samOutPos), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
#    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
#    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":endPos.VAL",str(30*scanDelta), wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","5.0", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":slewSpeed.VAL","5.0", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
#    epics.caput(shutter + ":open.VAL",1, wait=True, timeout=1000.0)
#    time.sleep(5)                
#    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":fly.VAL","Fly", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(shutter + ":close.VAL",1, wait=True, timeout=1000.0)
#    time.sleep(5)
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)        
#    print "flat acquire is done!"                
#    # set for white field -- end
#    
#    # set for dark field -- start
#    print "start acquire dark ..."                
#    epics.caput(camPrefix + ":HDF1:NumCapture.VAL","10", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:NumCapture_RBV.VAL","10", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":HDF1:FilePath.VAL",filepath, wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:AutoSave.VAL","Yes", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:FileWriteMode.VAL","Stream", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Capture", wait=False, timeout=1000.0)
#                
#    epics.caput(camPrefix + ":cam1:NumImages.VAL","10", wait=True, timeout=1000.0)            
#    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Acquire", wait=False, timeout=1000.0)
#    epics.caput(PSO + ":startPos.VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":endPos.VAL",str(30*scanDelta), wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","5.0", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":slewSpeed.VAL","5.0", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".ACCL","1.", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_ready2acquire.VAL","0", wait=True, timeout=1000.0)                
#    epics.caput(PSO + ":taxi.VAL","Taxi", wait=True, timeout=1000.0)
#    epics.caput(PSO + ":fly.VAL","Fly", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VELO","50.00000", wait=True, timeout=1000.0)
#    epics.caput(rotStage + ".VAL","0.00000", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump.VAL","10", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:pco_imgs2dump_RBV.VAL","10", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:pco_dump_camera_memory",1, wait=True, timeout=1000.0)
#    while (epics.caget(camPrefix + ":HDF1:NumCapture_RBV.VAL") != epics.caget(camPrefix + ":HDF1:NumCaptured_RBV.VAL")):    
#        time.sleep(1)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    print "dark acquire is done!"  
#
#    epics.caput("2bmb:caputRecorderGbl_10.VAL",epics.caget(camPrefix + ":HDF1:FileNumber.VAL",as_string=True), wait=True, timeout=1000.0)
#    # set for dark field -- end
#    
#    # set for new scans -- start
#    epics.caput(camPrefix + ":HDF1:Capture.VAL","Done", wait=True, timeout=1000.0)                
#    epics.caput(camPrefix + ":cam1:Acquire.VAL","Done", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_trigger_mode.VAL","Auto", wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:pco_live_view.VAL","Yes", wait=True, timeout=1000.0)    
#    epics.caput(camPrefix + ":cam1:SizeX.VAL",str(roiSizeX), wait=True, timeout=1000.0)
#    epics.caput(camPrefix + ":cam1:SizeY.VAL",str(roiSizeY), wait=True, timeout=1000.0)                
#    epics.caput(samStage + ".VAL",str(samInPos), wait=True, timeout=1000.0)
#    epics.caput("2bmb:scaler3.CONT","AutoCount", wait=True, timeout=1000.0)                
#    # set for new scans -- end
#    print "Scan is completed!!! Ready for the next scan ..."    
#
#
#










def _loadCellAfterTaxi(PSOFly="2bmb:PSOFly1:", loadMotor="2bma:m58",
                MCS="2bmb:mcs:", loadIOpin=20, tomoIOpin=21):

    """    
    Arrange for load stage and tomography scan to start at specified
    relative time, 'loadTime_s' ("2bmb:tomo_load_time").  Assume the motor
    is in the PSOFly "taxi" position, which (PSOFly ensures) is greater than
    the distance required to accelerate to slewSpeed.
    """

    recordDate = "Fri Aug  7 13:39:10 2015"
    softGlue = "2bmb:softGlue:"
    motor = epics.caget(PSOFly+"motorName")

    # Calculate timeToFirstTrigger: time from pressing "Fly" button to first
    # data-acquisition trigger
    accelTime = epics.caget(motor+".ACCL")
    currPos = epics.caget(motor+".VAL")
    startPos = epics.caget(PSOFly+"startPos")
    startDistance = abs(startPos-currPos)
    speed = epics.caget(PSOFly+"slewSpeed")
    if (speed <= 0): print "invalid slewSpeed"
    accelDist = accelTime*speed/2
    tomoProgramTime = .0118 # time (s) from softGlue "tomo" signal to tomo motor start
    timeToFirstTrigger = tomoProgramTime + accelTime + (startDistance - accelDist) / speed
    #print "timeToFirstTrigger=%f" % timeToFirstTrigger

    # program softGlue circuit to start load stage and press the "Fly" button
#    print '000'
    loadTime_s = epics.caget("2bmb:tomo_load_time")
    if (loadTime_s < -timeToFirstTrigger):
        # start load stage first
        loadStartTime = 0
        tomoStartTime = (-loadTime_s) - timeToFirstTrigger
    else:
        tomoStartTime = 0
        loadStartTime = timeToFirstTrigger + loadTime_s
    loadStartTime += .002
    tomoStartTime += .002
    #print "tomoStart=%f, loadStart=%f" % (tomoStartTime, loadStartTime)
    # Program loadStart time
#    print '001'
    clockFreq = 1000
    pulseTime = .002
    epics.caput(softGlue+"DnCntr-1_PRESET",loadStartTime*clockFreq, wait=True, timeout=1000000.0)
    epics.caput(softGlue+"DivByN-1_N",pulseTime*clockFreq, wait=True, timeout=1000000.0)
    # Program tomoStart time
    epics.caput(softGlue+"DnCntr-2_PRESET",tomoStartTime*clockFreq, wait=True, timeout=1000000.0)
    epics.caput(softGlue+"DivByN-2_N",pulseTime*clockFreq, wait=True, timeout=1000000.0)

#    print '002'
    # Program Sseqs to start user actions, and clear busy records when done
    loadSseq = "2bmb:loadSseq"
    epics.caput(loadSseq+".DOL1", loadMotor+".VELO") #save old speed
    epics.caput(loadSseq+".DOL2", loadMotor+".VAL") #save old position

#    print '003'
    epics.caput(loadSseq+".DOL3", "2bmb:loadSpeed")
    epics.caput(loadSseq+".LNK3", loadMotor+".VELO CA", wait=True,timeout=10)
    epics.caput(loadSseq+".WAIT3", "NoWait")

#    print '004'
    epics.caput(loadSseq+".DOL4", "2bmb:loadDist")
    epics.caput(loadSseq+".LNK4", loadMotor+".RLV CA", wait=True,timeout=10)
    epics.caput(loadSseq+".WAIT4", "Wait")

#    print '005'
    epics.caput(loadSseq+".STR5", "Done")
    epics.caput(loadSseq+".LNK5", "2bmb:loadBusy CA")

    # move motor back to ore-scan position
    #epics.caput(loadSseq+".DOL6", loadSseq+".DO2")
    #epics.caput(loadSseq+".LNK6", loadMotor+".VAL CA", wait=True,timeout=10)
    #epics.caput(loadSseq+".WAIT6", "NoWait")

#    print '006'
    epics.caput(loadSseq+".DOL7", loadSseq+".DO1")
    epics.caput(loadSseq+".LNK7", loadMotor+".VELO CA", wait=True,timeout=10)
    epics.caput(loadSseq+".WAIT7", "NoWait")

#    print '007'
    tomoSseq = "2bmb:tomoSseq"
    epics.caput(tomoSseq+".STR1", "Fly")
    epics.caput(tomoSseq+".LNK1", PSOFly+"fly CA", wait=True,timeout=10)
    epics.caput(tomoSseq+".WAIT1", "Wait")
    epics.caput(tomoSseq+".STR2", "Done")
    epics.caput(tomoSseq+".LNK2", "2bmb:tomoBusy CA")

#    print '008'
    # Program softGlue interrupt to start load stage and tomo
    epics.caput(softGlue+"In_%dDo.OUT"%loadIOpin, loadSseq+".PROC PP")
    epics.caput(softGlue+"In_%dIntEdge"%loadIOpin, "Rising")
    epics.caput(softGlue+"In_%dDo.OUT"%tomoIOpin, tomoSseq+".PROC PP")
    epics.caput(softGlue+"In_%dIntEdge"%tomoIOpin, "Rising")

#    print '009'
    # Program Sseq record to do premeasurement: save loadStage position
    epics.caput("2bmb:loadCellStartMeasurement.DOL1", loadMotor+".VAL")
    epics.caput("2bmb:loadCellStartMeasurement.LNK1", "2bmb:loadStart PP")
    epics.caput("2bmb:loadCellStartMeasurement.WAIT1", "NoWait")

#    print '010'
    # Program Sseq record to do measurement
    epics.caput("2bmb:loadCellStartMeasurement1.STR1", "Start")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK1", MCS+"StartAll PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT1", "NoWait")

#    print '011'
    # start MCS clock
    epics.caput("2bmb:loadCellStartMeasurement1.STR2", "1")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK2", softGlue+"BUFFER-2_IN_Signal PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT2", "NoWait")

#    print '012'
    epics.caput("2bmb:loadCellStartMeasurement1.STR3", "Busy")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK3", "2bmb:loadBusy CA")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT3", "After7")

#    print '013'
    epics.caput("2bmb:loadCellStartMeasurement1.STR4", "Busy")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK4", "2bmb:tomoBusy CA")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT4", "After7")

#    print '014'
    epics.caput("2bmb:loadCellStartMeasurement1.STR5", "0")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK5", softGlue+"BUFFER-1_IN_Signal PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT5", "NoWait")

#    print '015'
    epics.caput("2bmb:loadCellStartMeasurement1.STR6", "1")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK6", softGlue+"BUFFER-1_IN_Signal PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT6", "NoWait")

#    print '016'
    epics.caput("2bmb:loadCellStartMeasurement1.STR7", "0")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK7", softGlue+"BUFFER-1_IN_Signal PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT7", "NoWait")

    epics.caput("2bmb:loadCellStartMeasurement1.STR8", "Done")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK8", MCS+"StopAll PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT8", "NoWait")

#    print '017'
    # stop MCS clock
    epics.caput("2bmb:loadCellStartMeasurement1.STR9", "0")
    epics.caput("2bmb:loadCellStartMeasurement1.LNK9", softGlue+"BUFFER-2_IN_Signal PP")
    epics.caput("2bmb:loadCellStartMeasurement1.WAIT9", "NoWait")

#    print '018'
    epics.caput("2bmb:loadCellStartMeasurement1.DLYA", 3)
    epics.caput("2bmb:loadCellStartMeasurement1.DOA", 1)
#    epics.caput("2bmb:saveData_baseName","proj_"+epics.caget("2bmb:caputRecorderGbl_10.VAL",as_string=True)+"_")
#    print '0181'    
    epics.caput("2bmb:saveData_baseName","proj_"+"%(index)04d"%{"index":int(epics.caget("2bmb:caputRecorderGbl_10.VAL",as_string=True))}+"_")
#    print '0182'    
    epics.caput("2bmb:loadCellStartMeasurement1.LNKA", "2bmb:scanAux1.EXSC CA")
    epics.caput("2bmb:loadCellStartMeasurement1.WAITA", "Wait")

    # done programming records to stuff that will happen later

    # erase MCS
#    print '019'
    epics.caput(MCS+"EraseAll", "Erase")
    time.sleep(0.1)

#    print '020'
    # start MCS clock
    epics.caput(softGlue+"BUFFER-2_IN_Signal", "1")
#    print '021'    

def _rock_m55():
    recordDate = "Tue Aug 11 17:26:30 2015"
    epics.caput("2bma:m55.TWF","1", wait=True, timeout=10000.0)
    epics.caput("2bma:m55.TWR","1", wait=True, timeout=10000.0)
    time.sleep(1)
    

def _rock_motor(motor="2bma:m58", step=1):
    recordDate = "Tue Aug 18 11:07:44 2015"
    epics.caput(motor+".RLV",step, wait=True, timeout=10000.0)
    epics.caput(motor+".RLV",-step, wait=True, timeout=10000.0)


#
#def StripTool():
    

# for Sarah loading experiment: recording loading and displacement
def record_loading(exposureTime=0.5):
    camPrefix = "2bmbPG3" 
        
    epics.caput(camPrefix + ":TIFF1:CreateDirectory", -5,wait=True,timeout=1000.0) 
    epics.caput(camPrefix + ":TIFF1:FilePath", "/local/user2bmb/data/2017_10/Sarah/"+epics.caget('2bmb:caputRecorderGbl_1',as_string=True)+\
                                               epics.caget('2bmb:caputRecorderGbl_2',as_string=True).zfill(3)+'_loading_history')
    epics.caput(camPrefix + ":TIFF1:FileName", epics.caget('2bmb:caputRecorderGbl_1',as_string=True)+\
                                          epics.caget('2bmb:caputRecorderGbl_2',as_string=True).zfill(3)+'_DIC_images'\
                                          ,wait=True,timeout=1000.0)
                                     
    epics.caput(camPrefix + ":TIFF1:AutoIncrement", 'Yes',wait=True,timeout=1000.0)                                      
    epics.caput(camPrefix + ":TIFF1:FileTemplate", '%s%s_%4.4d.tif',wait=True,timeout=1000.0) 
    epics.caput(camPrefix + ":TIFF1:AutoSave", 'Yes',wait=True,timeout=1000.0) 
    epics.caput(camPrefix + ":TIFF1:FileWriteMode", 'Single',wait=True,timeout=1000.0) 
    
    epics.caput(camPrefix + ":cam1:FrameRateOnOff", 'On',wait=True,timeout=1000.0)
    epics.caput(camPrefix + ":cam1:Acquire", 'Done',wait=True,timeout=1000.0) 
    epics.caput(camPrefix + ":cam1:AcquireTime", exposureTime,wait=True,timeout=1000.0) 
    epics.caput(camPrefix + ":cam1:FrameRateValAbs", 1.0,wait=True,timeout=1000.0)
    epics.caput(camPrefix + ":cam1:ImageMode", 'Continuous',wait=True,timeout=1000.0)   

    logFilePath = epics.caget(camPrefix + ":TIFF1:FilePath",as_string=True) 
 
    if not os.path.exists(logFilePath):
        os.makedirs(logFilePath) 
             
    logFileName = os.path.join(logFilePath, epics.caget('2bmb:caputRecorderGbl_1',as_string=True)+\
                                          epics.caget('2bmb:caputRecorderGbl_2',as_string=True).zfill(3)+'_loading_history.log') 
                                          
    print 'Your log file is saved at ',logFileName    
    
    epics.caput(camPrefix + ":cam1:Acquire", 'Acquire',wait=False,timeout=1000.0)
    
    global ansCritical
    ansCritical = 'no'                
    top = Tkinter.Tk()
    def confirm():
        global ansCritical
        ans = mbox.askquestion('Action','Please ctrl+C to stop load history recording if you have done manual loading',icon='warning')
        if ans != 'yes':
            print  'Please stop the load history recording first...'
        else:
            print 'Very good. You need to close this Action Box'
            ansCritical = ans
            
    B1 = Tkinter.Button(top, text = ".....Action.....", command = confirm)
    B1.pack()
    top.mainloop() 
    
    print ansCritical
    if ansCritical != ('yes' or 'Yes'):
        print ansCritical
        print 'I wont proceed if the load history recording is still going!!!'
        return False
    else:
        print 'Good to go ...'    
            
    epics.caput(camPrefix + ":cam1:Acquire", 'Done',wait=True,timeout=1000.0) 
    epics.caput(camPrefix + ":TIFF1:FileWriteMode", 'Stream',wait=True,timeout=1000.0)   
    epics.caput("2bmb:caputRecorderMacros1", 'EdgeMultiPosScan',wait=False,timeout=1000.0)             
      
    
    
    
    
    
    
    
    
    
    
    