import codecs
import time
import serial
import pandas as pd
import numpy as np
import pyvisa as visa
import datetime
import os
import sys
import monochromatorapi as mcapi
import shutterapi as shapi
import picoapi as pico
import pixisapi as pix
import clr # Import the .NET class library
import sys # Import python sys module
import os # Import os module
from System.IO import * # Import System.IO for saving and opening files
# Import C compatible List and String
from System import String
from System.Collections.Generic import List
# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')
# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import SensorTemperatureStatus
from PrincetonInstruments.LightField.AddIns import TriggerResponse
import PrincetonInstruments.LightField.AddIns as AddIns

MCport = 'COM4' #Serial port to monochromator scan controller
shutport = 'COM3' #serial port to shutter controller
t = 5.0 #s #wait variable for seconds ot be converted to ms for scanner to stop (useful for goto and scanbasic commands if used)
#gotofromhome function wavelength value
wl = 600.0 #nm 
#gotofrom function wavelength values
wlbegin= 550.0 #nm
wllast= 600.0 #nm
#makescanarray function values
wlstart=550.0 #nm
wlend=600.0 #nm
wlstep=10 # interval nm
exposuretimes=10 #s can be array
#picoammeter function settings
interval = .1 #s time between consecutive writes of selected channel readings to datalog
nsamples = 51  # number of readings total written to datalog
Ch1ON = 1  # 0 = channel off, 1 = channel on
Ch2ON = 0  # 0 = channel off, 1 = channel on
asrl = "asrl5::instr" #instrument address for picoammeter
#PIXIS experiment function settings
MC_lamp = 'Xe'
Traget_spectral_bandpass = 0.62 #nm
Experiment_PIXIS_default='PIXIS_MC_Default' 
exp_filenames_basename='exp_Xe_500ms'
exp_folder_name=exp_filenames_basename+'_180to700nm_10C'
start_wl=180.0 #nm 
end_wl=700.0 #nm 
wl_step=10.0 #nm 
exp_time=1000.0 #ms
n_bias=10 #number of bias frames

#when writing a command, write mcapi.Commandname(variables)
#you must run mcapi.home(port) in between two movement commands
#mcapi.getports()
#mcapi.initial(port)
#mcapi.home(port)
#mcapi.go_to_fromhome(port,600)
#mcapi.go_to_from(port,600,620)
#mcapi.stop(port)
#mcapi.makescanarray(wlstart,wlend,wlstep,exposuretimes)