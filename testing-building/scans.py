import codecs
import time
import serial
import numpy as np
from icecream import ic

from Home.py import connect
from Home.py import home

connect()
home()
#scan to one certain wavelength, within range and input by user, converted to revolutions
def GoTo():
    try:
        ser = serial.Serial('COM5', 
                                baudrate = 9600, 
                                timeout = None,
                                xonxoff = True,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                )
        ser.close()

        ser.open()                            
        ser.write(b' \r'); 
        ser.read_until(size=None) 
        ser.close()
        print("communication initialized")

        #enable home circuit to configure to home wavelength
        ser.open()
        ser.write(b'A8 \r'); 
        ser.read_until(size=None)
        ser.close()
        print("home circuit enabled")
        
        #user input
        try:
            wavelength = float(input("Enter the wavelength you want to scan to: "))
            uplim = 999.9 #nm
            lowlim = 0.1 #nm
            home = 631.26 #nm
            rev = 9000 #steps
            if wavelength > uplim: #monochromator upper limit 
                print("please enter a number lower than 999.9")
            if wavelength < lowlim: #monochromator lower limit
                print("please enter a number higher than 0.1")
            #equation to find difference between home position and new wavelength desired
            difference = wavelength - home 
            #eq for number of motor steps from home to desired wavelength, 9000 steps = 1 nm
            steps = difference * rev
            #take off fraction of a step for mechanical movement
            serialsteps = round(steps,0)
            #convert to string
            str = f'{serialsteps}' + ' \r'
            #convert string to byte for serial command for monochromator to read
            str_2_bytes = bytes(str, 'utf-8')
            if lowlim < wavelength < uplim:
                ser = serial.Serial('COM3', 
                                    baudrate = 9600, 
                                    timeout = None,
                                    xonxoff = True,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    )
                ser.close()
                ser.open()                            
                ser.write(b' \r'); 
                ser.read_until(size=None) 
                ser.close()
                print("communication initialized")
                
                ser.open()
                ser.write(str_2_bytes); 
                ser.read_until(size=None)
                ser.close()
                print('scan controller is moving for', serialsteps,'revolutions')
                
                #wait command

                ser.open()
                ser.write(b'@ \r'); #soft stop
                ser.read_until(size=None)
                ser.close()
                print("scan controller stopped")

                #wait command, exposure time?
                
                ser.open()
                ser.write(b'P \r'); #exit program
                ser.read_until(size=None)
                ser.close()
                print("exited program")
        except: 
            print("Could not complete move command")
    except:
        print("Error establishing connection.")

def scanbasic():
    try:
        ser = serial.Serial('COM5', 
                                baudrate = 9600, 
                                timeout = None,
                                xonxoff = True,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                )
        ser.close()
        
        ser.open()                            
        ser.write(b' \r'); 
        ser.read_until(size=None) 
        ser.close()
        print("communication initialized")

        #this function takes wl range and interval from user and scans the monochromator for a given hold time for each wl 
        #user input for start and end wavelength of monochromator scan from any given wavelength within limits
        try:
            wavelength_start = float(input("Enter the wavelength you want to scan to: "))
            wavelength_end = float(input("Enter the wavelength you want to scan to: "))
            #upper wavelength limit of mechanical step motor on monochromator
            uplim = 999.9 #nm
            #lower wavelength limit of mechanical step motor on monochromator
            lowlim = 0.1 #nm
            #home wavelength for monochromator
            home = 631.26 #nm
            #wavelength to mechanical step motor conversion 9000 step = 1 nm
            rev = 9000.0 #steps
            if wavelength_start > uplim: #monochromator upper limit error
                print("please enter a number lower than 999.9")
            if wavelength_start < lowlim: #monochromator lower limit error
                print("please enter a number higher than 0.1")
            if wavelength_end >  uplim: #monochromator upper limit error
                print("please enter a number lower than 999.9")
            if wavelength_end < lowlim: #monochromator lower limit error
                print("please enter a number higher than 0.1")
            #equation to find difference between home position and new wavelength desired
            difference_start = wavelength_start - home
            difference_end = wavelength_end - wavelength_start
            #conversion eq for number of steps from home to new desired wavelength, 9000 steps = 1 nm
            steps_start = difference_start * rev
            steps_end = difference_end * rev
            #take off fraction of a step for mechanical movement
            serialstart = round(steps_start,0)
            serialend = round(steps_end,0)
            #first wavelength convert to string and then convert string to byte for serial command
            if serialstart > 0:
                start = str('+' f'{serialstart}' + ' \r')
                str_2_bytestart = bytes(start, 'utf-8')
            if serialstart <= 0:
                start = str(f'{serialstart}' + ' \r')
                str_2_bytestart = bytes(start, 'utf-8')
            #second wavelength convert to string and then convert to byte for serial command
            if serialend > 0:
                end = str('+' f'{serialend}' + ' \r')
                str_2_byteend = bytes(end, 'utf-8')
            if serialend <= 0:
                end = str(f'{serialend}' + ' \r')
                str_2_byteend = bytes(end, 'utf-8')
            #if statement when input wavelength within limits that completes monochromator initial movement
            if lowlim < wavelength_start <  uplim:
                ser = serial.Serial('COM3', 
                                    baudrate = 9600, 
                                    timeout = None,
                                    xonxoff = True,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    )
                ser.close()
                ser.open()                            
                ser.write(b' \r'); #initialize communication between monochromator and serial
                ser.read_until(size=None) 
                ser.close()
                print("communication initialized")
                
                ser.open()
                ser.write(str_2_bytestart); #value of steps to scan 
                ser.read_until(size=None)
                ser.close()
                print('scan controller is moving for', serialstart,'steps')

                #wait command, exposure time?

                ser.open()
                ser.write(b'@ \r'); #soft stop
                ser.read_until(size=None)
                ser.close()
                print("scan controller stopped")

                #wait command, exposure time?

            #if statement when input wavelength within limits that completes monochromator ending movement
            if lowlim < wavelength_end <  uplim:
                ser = serial.Serial('COM5', 
                                    baudrate = 9600, 
                                    timeout = None,
                                    xonxoff = True,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    )
                ser.close()
                ser.open()                            
                ser.write(b' \r'); 
                ser.read_until(size=None) 
                ser.close()
                print("communication initialized")

                ser.open()
                ser.write(str_2_byteend); 
                ser.read_until(size=None)
                ser.close()
                print('scan controller is moving for', serialend, 'steps')

                #wait command

                ser.open()
                ser.write(b'@ \r'); #soft stop
                ser.read_until(size=None)
                ser.close()
                print("scan controller stopped")

                #wait command, exposure time?
                
                ser.open()
                ser.write(b'P \r'); #exit program
                ser.read_until(size=None)
                ser.close()
                print("exited program")
        except:
            print("Error completing beginning or end scan")
    except:
        print("Error establishing connection.")

def scanadv():
    try:
        """This function assumes that the monochromator is already on the home position"""
        #user inputs for 8 wavelengths and exposures
        wavelist = np.array([input("Enter wavelength you want to scan to: ") for wave in range(8)])
        exposure = np.array([input("Enter exposure time for each wavelength: ") for exp in range(8)])
        #calibration wavelength for instrument
        home = 631.26 #nm
        rev = 9000 #steps = 1 nm conversion factor for wavelength to mechanical step, used for serial commands
        #indexes wavelist entry so first input can be used to find the difference between home wavelength and the first entry
        try:
            for idx,wave in enumerate(wavelist):  
                if idx == 0:
                    currentwave = home
                    diff_wave = float(wavelist[0])-currentwave
                    diff_step = diff_wave*rev
                    #for positive values of diff_step, add plus to value while converting to string and then bytes
                    if diff_step > 0:
                        diff_stepstr = str('+' f'{diff_step}' + ' \r')
                        diff_stepbyte = bytes(diff_stepstr, 'utf-8')
                    #for all other values of diff_step, keep value and convert to string and then bytes
                    if diff_step <= 0:
                        diff_stepstr = str(f'{diff_step}' + ' \r')
                        diff_stepbyte = bytes(diff_stepstr, 'utf-8')
                
                    #serial move command for diff_step to desired wavelength
                    ser = serial.Serial('COM5', 
                                    baudrate = 9600, 
                                    timeout = None,
                                    xonxoff = True,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    )
                    ser.close()
                    ser.open()                            
                    ser.write(b' \r'); 
                    ser.read_until(size=None) 
                    ser.close()
                    print("serial communication initialized")

                    ser.open()
                    ser.write(diff_step); 
                    ser.read_until(size=None)
                    ser.close(diff_stepbyte)
                    print('scan controller is moving by', diff_step, 'steps')
                    print(f"Moving scan controller {diff_wave}nm to {wavelist[0]}nm")
                    print(f"Holding for current exposure {exposure[idx]} seconds")
                    print(f"The exposure for {wavelist[0]}nm was taken")

                    ser.open()
                    ser.write(b'@ \r'); #soft stop
                    ser.read_until(size=None)
                    ser.close()
                    print("scan controller stopped")
                    #update list and go to the next input in the list
                    currentwave = wavelist[idx+1]
                else:
                    #for other inputs in wavelist index find difference between the current wavelength and the previous input in the list
                    diff_wave = float(currentwave)-float(wavelist[idx-1])
                    diff_step = diff_wave*rev
                    #for positive values of diff_step, add plus sign and convert from string to bytes
                    if diff_step > 0:
                        diff_stepstr = str('+' f'{diff_step}' + ' \r')
                        diff_stepbyte = bytes(diff_stepstr, 'utf-8')
                    #for all other values of diff_step, keep the same, convert to string and then bytes
                    if diff_step <= 0:
                        diff_stepstr = str(f'{diff_step}' + ' \r')
                        diff_stepbyte = bytes(diff_stepstr, 'utf-8')
                    #serial move command for diff_step to desired wavelength
                    ser = serial.Serial('COM3', 
                                    baudrate = 9600, 
                                    timeout = None,
                                    xonxoff = True,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    )
                    ser.close()
                    ser.open()                            
                    ser.write(b' \r'); 
                    ser.read_until(size=None) 
                    ser.close()
                    print("serial communication initialized")

                    ser.open()
                    ser.write(diff_step); 
                    ser.read_until(size=None)
                    ser.close()
                    print('scan controller is moving by', diff_step, 'steps')
                    print(f"Moving scan controller {diff_wave}nm to {wavelist[0]}nm")
                    #check or wait to reach next wavelength
                    print(f"Holding for current exposure {exposure[idx]} seconds")
                    #take exposure/hold time for exposure
                    print(f"The exposure for {currentwave}nm was taken")
                    
                    ser.open()
                    ser.write(b'@ \r'); #soft stop
                    ser.read_until(size=None)
                    ser.close()
                    print("scan controller stopped")
                    #update
                    if idx < len(wavelist)-1:
                        currentwave = wavelist[idx+1]
        except:
            print("Error with serial communication or movement.")
    except:
        print("Error with user input.")
    finally:
        ser.open()
        ser.write(b'P \r'); #exit program
        ser.read_until(size=None)
        ser.close()
        print("exited program")
