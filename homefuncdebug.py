import codecs
import time
import serial
import pandas as pd
import pyvisa as visa
import datetime
import os
import sys
import shutterapi as shapi
import picoapi as pico
from yaml import scan
MCport ='COM4'

def checkstatus(MCport,waittime=1):
    """
    Gives value of limit switch to determine if the scan controller is at a wavelength greater than or less than home wavelength. (our home is 631.26nm)
    Inputs:
        :MCport(string): Serial Port Connection
        :waittime(float): Pause for full readout from serial
    Returns:
        :: 0 Scan controller above home
        :: 2 Scan controller above home and moving
        :: 32 Scan controller below home
        :: 34 Scan controller below home and moving
        :: Error message due to improper connection
    """
    try:
        ser = serial.Serial(port=MCport, 
                            baudrate = 9600, 
                            timeout = None,
                            xonxoff = True,
                            parity = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE,
                            bytesize = serial.EIGHTBITS,
                            )
        ser.close()
        time.sleep(waittime) #gives time to readout full message from serial reciever
        ser.open()
        ser.write(b'] \r'); #ascii keyboard input for checking limit status
        s = ser.read_until(size=None)
        ser.close()
        statnow = codecs.decode(s) #decodes info from serial to confirm movement
        statnow = int(str(statnow[4:])) #should slice output to only be the interger, not ]    0 as previous testing
        msg =f"Limits status is:{statnow}"
        return statnow,msg
    except Exception as ex:
        statnow = int(999) 
        tempmsg =f"Limit Status Could Not Be Read. Error Code: {ex}"
        return statnow,tempmsg

def stop(MCport):
    """
    Immediate stop of scan controller. VERY useful for writing code.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Error message if exception occurs.
    """
    try:
        ser = serial.Serial(port=MCport, 
                                    baudrate = 9600, 
                                    timeout = None,
                                    xonxoff = True,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    )
        ser.close()
        ser.open()
        ser.write(b'@ \r'); #soft stop
        ser.read_until(size=None)
        ser.close()
        msg =f"scan controller stopped"
        print(msg)
        return
    except Exception as ex:
        msg =f"Error, could not stop scan. Error: {ex}"
        print(msg)
        return

def home(MCport):
    """
    Moves the scan controller from any wavelength to home. Important for conducting other movement functions that assume you begin at home.
    Inputs:
        :MCport(string): Serial Port connection
    Returns:
        ::Initial location of the controller
        ::Movement status messages
        ::Error message and code when exception occurs
    """
    try:
        ser = serial.Serial(port=MCport, 
                                baudrate = 9600, 
                                timeout = None,
                                xonxoff = True,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                )
        ser.close()
        ser.open()
        ser.write(b'A8 \r'); #enables home circuit to configure to home wavelength
        ser.close()
        print("home circuit enabled, prepared to home")
        statnow,msg = checkstatus(MCport,waittime=1)
        if statnow < 32: #above home statnow=0, above home and moving statnow=2
            print("scanner is above home so moving down to home")
            ser.open()
            ser.write(b'm-23000 \r'); #move at constant vel. of 23KHz decreasing wavelength
            ser.read_until(size=None)
            ser.close()
            print("decreasing wavelength at 23KHz")
            while statnow < 32: #once scan passes home statnow should switch to 34
                statnow,msg = checkstatus(MCport,waittime=1)
                print(msg)
                if statnow==999:
                    print(msg)
                    return 
                if statnow > 32: #below home statnow=32, below home and moving statnow=34
                    stop(MCport)
                    #removes backlash
                    time.sleep(0.8)
                    ser.open()
                    ser.write(b'-108000 \r'); #turns motor for 3 rev., subtracts 12nm
                    ser.read_until(size=None)
                    ser.close()
                    print("decreasing wavelength for 3 revolutions")
                    time.sleep(4)
                    ser.open()
                    ser.write(b'+72000 \r'); #turns motor for 2 rev., adds 8nm
                    ser.read_until(size=None)
                    ser.close()
                    print("increasing wavelength for 2 revolutions")
                    time.sleep(3)
                    ser.open()
                    ser.write(b'A24 \r'); #enable high accuracy circuit for fine movement
                    ser.read_until(size=None)
                    ser.close()
                    print("high accuracy circuit enabled")
                    ser.open()
                    ser.write(b'F4500,0 \r'); #find edge of home flag at 1000 steps/sec
                    ser.read_until(size=None)
                    ser.close()
                    print("finding edge of home flag at 4500KHz this will take about 15 seconds")
                    time.sleep(15) #time it takes to complete F4500,0 movement

                    stop(MCport)
                    ser.open()
                    ser.write(b'A0 \r'); #disable home circuit
                    ser.read_until(size=None)
                    ser.close()
                    print(f"disabled home circuit")
                    print("homing successful")
                    return
        if statnow > 0: #below home wavelength statnow=32, below home and moving statnow=34
            print("scanner is below home so moving up to home")
            ser.open()
            ser.write(b'm+23000 \r') #move at constant vel. of 23KHz increasing wavelength
            ser.read_until(size=None)
            ser.close()
            print("increasing wavelength at a rate of 23KHz")
            while statnow > 2: #once scan passes home statnow should switch to 2
                statnow,msg = checkstatus(MCport,waittime=1)
                print(msg)
                if statnow==999:
                    print(f"home switch stat ={msg},Error code ={statnow}") 
                    return
                if statnow < 32: #above home wavelength statnow=0, above home and moving statnow=2
                    stop(MCport)

                    #removes backlash
                    time.sleep(0.8)    
                    ser.open()
                    ser.write(b'-108000 \r'); #decreasing wavelength for 3 motor revolutions
                    ser.read_until(size=None)
                    ser.close()
                    print(f"decrease wavelength for 3 revolutions")
                    time.sleep(3)
                    ser.open()
                    ser.write(b'+72000 \r'); #increase wavelength for 2 motor revolutions
                    ser.read_until(size=None)
                    ser.close()
                    print(f"increase wavelength for 2 revolutions")
                    time.sleep(2)
                    ser.open()
                    ser.write(b'A24 \r'); #enable high accuracy circuit
                    ser.read_until(size=None)
                    ser.close()
                    print(f"high accuracy circuit enabled")
                    ser.open()
                    ser.write(b'F4500,0 \r'); #find edge of home flag at 4500 steps/sec
                    ser.read_until(size=None)
                    ser.close()
                    print(f"finding edge of home flag at 4500KHz, this will take about 12 seconds")
                    time.sleep(10)

                    stop(MCport)
                    print("homing movement successful")
                    ser.open()
                    ser.write(b'A0 \r'); #disable home circuit
                    ser.read_until(size=None)
                    ser.close()
                    print(f"disabled home circuit")
                    print("homing successful")
                    return
    except Exception as ex:
        msg =f"Limit Status Could Not Be Read. Error: {ex}"
        print(msg)
        return
    
    home(MCport)