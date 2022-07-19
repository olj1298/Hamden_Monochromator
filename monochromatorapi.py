import codecs
import time
import serial
import pandas as pd
import numpy as np
import pyvisa as visa
import datetime
import os
import sys
import shutterapi as shapi
import picoapi as pico
from yaml import scan

"""
Module docstring
"""
def whereishome(): 
    """
    Returns the home wavelength for the monochrmator for use in movement.
    Inputs: 
        ::None
    Return: 
        ::Home wavelnegth(float)
    """
    return float(np.round(631.26,2))

def makescanarray(wlstart,wlend,wlstep,exposuretimes):
    """
    Creates scan array input for advance scan pixis function for given start wavelenghts, stop wavelenths and wavelength step size, and exposure times. 
    Inputs: 
        :wlstart: Start wavelength for advanced scan
        :wlstop: Stop wavelength for advanced scan
        :wlstep: Wavelenght step for the scan
        :exposuretimes: A float exposure time or a 1d numpy array listing the exposure times in increaseing order of wavelength.  
    Returns:
        ::Array for values
        ::ValueError message if exception occurs
    """
    wavelist=np.arange(wlstart,wlend+wlstep,wlstep,format=float)
    if type(exposuretimes)==float: 
        explist=float(exposuretimes*np.ones(len(wavelist)))
        return np.column_stack((wavelist,explist))
    elif type(exposuretimes)==np.ndarray:
        if len(exposuretimes)!=len(wavelist):
            raise ValueError("Length of exposure time list and wavelength range list does not match.")
        return np.column_stack((wavelist,explist))
    else: 
        raise ValueError("Incorrect data type. Expecting float or Numpy Array")
    # wl_list = np.arange(start_wl,end_wl+step_wl,step_wl)
    #wl_list=np.array([450,550,650])
    #exp_list=np.array([5,10,12])
    # for idx,wl in enumerate(wl_list):
    #     if idx==0:
    #         start=wl_list[idx]
    #         mcapi.go_to_fromhome(MCport,start)
    #         #time.sleep(3)
    #         #time.sleep(exp_list[idx])
    #         input("Press any key continue")
    #     else: 
    #         from_wl = wl_list[idx-1]
    #         to_wl=wl_list[idx]
    #         mcapi.go_to_from(MCport,from_wl,to_wl)
    #         #time.sleep(3)
    #         #time.sleep(exp_list[idx])
    #         input("Press any key continue")

def getports():
    """
    Lists all connected serial ports used on computer so user doesn't need to open DeviceManager.
    Returns:
        ::Names of ports
    """
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    #readable port information
    portslist=[]
    for port, desc, hwid in sorted(ports):
        portslist.append("{}: {} [{}]".format(port, desc, hwid))
        print("{}: {} [{}]".format(port, desc, hwid))
    return portslist

def initial(MCport):
    """
    Tests if scan controller serial parameters are correct and if port to scan controller is closed or open. 
    Inputs:
        :MCport(string): Serial port connection
    Returns:
        ::Confirmation that connection is working
        ::Error message if exception occured
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
        ser.write(b' \r'); #ascii intput for pressing enter on keyboard
        ser.read_until(size=None) #reads out feedback from scan controller until no data is left
        ser.close()
        msg = f"Program communication initialized, Run the exit command before closing out of window!"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not establish communication, check serial connection Error: {ex}"
        print(msg)
        return

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
    # finally:       


def movestat(MCport,waittime=1):
    """
    Checks if scan controller is moving or not. Used in movement functions so once a movement is stopped the code moves to the next line in the function.
        Inputs:
            :MCport(string): Serial Port connection
            :waittime(float): Pause for full readout from serial
        Returns:
            ::0 No motion
            ::1 Moving
            ::2 High constant velocity
            ::16 slewing ramping complete
            ::33 Moving
            ::Error message if exception occurs
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
        time.sleep(waittime)
        ser.open()
        ser.write(b'^ \r'); #read moving status input
        s=ser.read_until(size=None)
        ser.close()
        read = codecs.decode(s)
        movenow = int(str(read[4:])) #should slice output to only be the interger, not ^    0 as previous
        msg =f"moving status: {movenow}"
        return movenow,msg
    except Exception as ex:
        movenow=int(999) 
        msg =f"Move Status Could Not Be Read. Error Code: {ex}"
        print(msg)
        return movenow,msg

def wait(MCport,t):
    """
    Converts value to milliseconds and pauses before next movement command is sent.
        Inputs:
            :MCport(string): Serial Port connection
            :t(float): Wait time in seconds
        Returns:
            ::Wait message
            ::Error message if exception occurs
    """
    wait = t/1000.0 #ms
    intwait = int(wait)
    strwait = (f'W{intwait}' + '\r')
    wait2bytes = bytes(strwait, 'ascii')
    try:
        msg = f"wait time is: {wait}"
        print(msg)
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
        ser.write(wait2bytes); #wait n milliseconds n = 0 to 65535
        ser.read_until(size=None)
        ser.close()
        return
    except Exception as ex:
        msg = f"could not insert wait command. Error: {ex}"
        print(msg)
        return

def go_to_fromhome(MCport,wl):
    """
    Moves scan controller to one wavelength starting from home wavelength. Movements converts wavelength to mechanical steps and revolutions, then to bytes sent to scan controller.
        Inputs:
            :MCport(string): Serial Port connection
            :wl(float): Desired wavelength to end movement at
        Returns
            ::Movement status. Completion of movement
            ::Error message if exception occurs
    """
    try:
        home(MCport)        
        uplim = 900.0 #nm
        lowlim = 100.0 #nm
        home_wl = 631.26 #nm
        rev = 9000 #steps
        #equation to find difference between home position and new wavelength desired
        difference = wl - home_wl
        rounddiff = round(difference,0) 
        #eq for number of motor steps from home to desired wavelength, 9000 steps = 1 nm
        steps = difference * rev
        #take off fraction of a step for mechanical movement
        serialsteps = round(steps,0)
        intsteps=int(serialsteps)
        if intsteps > 0:
            tempstr = str('+' f'{intsteps}' + ' \r')
            gotostr = bytes(tempstr, 'ascii')
        if intsteps <= 0:
            tempstr = str(f'{intsteps}' + ' \r')
            gotostr = bytes(tempstr, 'ascii')
        if lowlim < wl < uplim:
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
            ser.write(gotostr); 
            ser.close()
            print(f"scan controller is moving for {rounddiff}nm")
            mvread,msg = movestat(MCport,waittime=1) #check the movement status
            if mvread ==999:
                print(msg)
                return msg
            while mvread > 0: #some type of motion
                mvread,msg = movestat(MCport,waittime=1)
                print(msg)
                if mvread ==999:
                    print(msg)
                    return msg               
                if mvread == 0: #no motion
                    stop(MCport)
                    msg = f"Movement completed"
                    # print(msg)
                    #shapi.shutopen(shutport)
                    # print(f"this exposure will take {exposuretime} seconds")
                    # wait(port,exposuretime)
                    #picrun(aslr,Ch1ON,Ch2ON,interval,nsamples)
                    #shapi.shutclose(shutport)
                    return msg
            print(f"Now at {wl} nm")
    except Exception as ex: 
        msg = f"Could not complete move command, Error: {ex}"
        print(msg)
        return

def go_to_from(MCport,wlstart,wlend):
    """
    Moves scan controller from wlstart to wlend wavelength. Movements converts wavelength to mechanical steps and revolutions, then to bytes sent to scan controller.
        Inputs:
            :MCport(string): Serial Port connection
            :wlstart(float): Start wavelength
            :wlend(float): End wavelength
            :exposuretime(float): Exposure time in seconds which is converted to ms
        Returns
            ::Movement status. Completion of movement
            ::Error message if exception occurs
    """
    try:       
        uplim = 900.0 #nm
        lowlim = 100.0 #nm
        current_wl = wlstart #nm
        print(f"Monochromator is at {current_wl}")
        rev = 9000 #steps
        #equation to find difference between home position and new wavelength desired
        difference = wlend - current_wl
        rounddiff = round(difference,0) 
        #eq for number of motor steps from home to desired wavelength, 9000 steps = 1 nm
        steps = difference * rev
        #take off fraction of a step for mechanical movement
        serialsteps = round(steps,0)
        intsteps=int(serialsteps)
        if intsteps > 0:
            tempstr = str('+' f'{intsteps}' + ' \r')
            gotostr = bytes(tempstr, 'ascii')
        if intsteps <= 0:
            tempstr = str(f'{intsteps}' + ' \r')
            gotostr = bytes(tempstr, 'ascii')
        if lowlim < wlend < uplim:
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
            ser.write(gotostr); 
            ser.close()
            print(f"scan controller is moving for {rounddiff} nm")
            mvread,msg = movestat(MCport,waittime=1) #check the movement status
            if mvread ==999:
                print(msg)
                return msg
            while mvread > 0: #some type of motion
                mvread,msg = movestat(MCport,waittime=1)
                print(msg)
                if mvread ==999:
                    print(msg)
                    return msg               
                if mvread == 0: #no motion
                    stop(MCport)
                    msg = f"Movement completed"
                    return msg
            print(f"Now at {wlend} nm")
    except Exception as ex: 
        msg = f"Could not complete move command, Error: {ex}"
        print(msg)
        return

# def scanbasicpixis(MCport,firstwl,endwl,t):
#     """
#     Moves controller from home to a desired wavelength, pauses for an exposure time, then moves to a final wavelength. Assumes that controller begins at home.
#         Inputs:
#             :MCport(string): Serial Port connection
#             :firstwl(float): Desired wavelength
#             :endwl(float): Desired final wavelength
#             :t(float): Exposure time between wavelengths
#         Returns
#             ::Movement status, Exposure status, Movement completion
#             ::Error message if exception occurs
#     """
#     try:
#         ser = serial.Serial(port=MCport, 
#                             baudrate = 9600, 
#                             timeout = None,
#                             xonxoff = True,
#                             parity = serial.PARITY_NONE,
#                             stopbits = serial.STOPBITS_ONE,
#                             bytesize = serial.EIGHTBITS,
#                             )
#         ser.close()
#         uplim = 900.0 #nm
#         lowlim = 185.0 #nm
#         home_wl = 631.26 #nm
#         rev = 9000.0 #steps
#         #equation to find difference between home position and new wavelength desired
#         diffstart = firstwl - home_wl
#         diffend = endwl - firstwl
#         #conversion eq for number of steps from home to new desired wavelength, 9000 steps = 1 nm
#         stepsstart = diffstart * rev
#         stepsend = diffend * rev
#         #take off fraction of a step for mechanical movement
#         serialstart = round(stepsstart,0)
#         serialend = round(stepsend,0)
#         intstart=int(serialstart)
#         intend=int(serialend)
#         #first wavelength convert to string and then convert string to byte for serial command
#         if serialstart > 0:
#             start = str('+' f'{intstart}' + ' \r')
#             str2bytestart = bytes(start, 'ascii')
#         if serialstart <= 0:
#             start = str(f'{intstart}' + ' \r')
#             str2bytestart = bytes(start, 'ascii')
#         #second wavelength convert to string and then convert to byte for serial command
#         if serialend > 0:
#             end = str('+' f'{intend}' + ' \r')
#             str2byteend = bytes(end, 'ascii')
#         if serialend <= 0:
#             end = str(f'{intend}' + ' \r')
#             str2byteend = bytes(end, 'ascii')
#         #if statement when input wavelength within limits that completes monochromator initial movement
#         if lowlim < firstwl <  uplim:
#             ser = serial.Serial(port=MCport, 
#                                 baudrate = 9600, 
#                                 timeout = None,
#                                 xonxoff = True,
#                                 parity = serial.PARITY_NONE,
#                                 stopbits = serial.STOPBITS_ONE,
#                                 bytesize = serial.EIGHTBITS,
#                                 )
#             ser.close()
#             ser.open()
#             ser.write(str2bytestart); #value of steps to scan 
#             ser.read_until(size=None)
#             ser.close()
#             print(f"scan controller is moving for {serialstart} steps")
#             #check the limit status before starting movement, so the loop knows to scan up or down
#             mvread,msg = movestat(port,waittime=1)
#             if mvread ==999:
#                 print(msg)
#                 return msg
#             while mvread > 0: #some type of motion
#                 mvread,msg = movestat(port,waittime=1)
#                 print(msg)
#                 if mvread ==999: #error code defined in mv read function
#                     print(msg)
#                     return msg   
#                 if mvread == 0: #no motion
#                     stop(MCport)
#                     msg = f"First Movement completed"
#                     print(msg)
#         print("Running pixis subroutine")
#         pixis_get_dark(t)
#         pixis_get_exposure(t)
#         print("Continuing to the next wavelength")
#         if lowlim < endwl <  uplim:
#             ser = serial.Serial(port=MCport, 
#                                 baudrate = 9600, 
#                                 timeout = None,
#                                 xonxoff = True,
#                                 parity = serial.PARITY_NONE,
#                                 stopbits = serial.STOPBITS_ONE,
#                                 bytesize = serial.EIGHTBITS,
#                                 )
#             ser.close()
#             ser.open()
#             ser.write(str2byteend); 
#             ser.read_until(size=None)
#             ser.close()
#             print(f"scan controller is moving for {serialend} steps")
#             #check the limit status before starting movement, so the loop knows to scan up or down
#             mvread,msg = movestat(MCport,waittime=1)
#             if mvread ==999:
#                 print(msg)
#                 return msg
#             while mvread > 0: #some type of motion
#                 mvread,msg = movestat(MCport,waittime=1)
#                 print(msg)
#                 if mvread ==999:
#                     print(msg)
#                     return msg             
#                 if mvread == 0: #no motion
#                     stop(MCport)
#                     msg = f"Second Movement completed"
#                     print(msg)
#     except Exception as ex: 
#         msg = f"Could not complete move command, Error: {ex}"
#         print(msg)
#         return

# def scanadvancedpixis(MCport,scanarray,pixisfunc,at_home=False):
#     """
#     Scans from sequentially through a list of wavelenght L passed as Lx2 and exposure times. By default assumes that scan controller is not at home (home=False). 
#         Inputs:
#             :MCport(string): Serial Port connection for monochromator scan controller
#             :scanarray(numpy array): LX2 numpy array with L waveleghts and corresponding exposure time.
#             :pixisfunc(funciton): pixis subroutine takes exposure time t as input to run a custom pixis subroutine 
#             :at_home(boolean): Defualt values is False, 
#         Returns:
#             ::Movement status, exposure status, movement completion
#             ::Error message if exception occurs
#     """
#     print("start")
#     try:
#         if at_home==False: 
#             home(port)
#             print("at home")
#         else: 
#             print("At home flag is True. Assuming that the monochormator is at home.") 

#         home_wl = 631.26 #nm
#         rev = 9000 #steps = 1 nm 
#         currentwave=home_wl
#         print("here")
#         # print(scanarray)
#         #indexes wavelist entry so first input can be used to find the difference between home wavelength and the first entry
#         # for wl, exp in scanarray:  
#         wl_list=scanarray[:,0]
#         print(wl_list)
#         exp_list=scanarray[:,1]
#         for idx,wl in enumerate(wl_list):
#             diffwave = wl-currentwave
#             diffstep = diffwave*rev
#             roundstep = round(diffstep,0)
#             intstep = int(roundstep)
#             #for positive values of diff_step, add plus to value while converting to string and then bytes
#             if diffstep > 0:
#                 diffstepstr = str('+' f'{intstep}' + ' \r')
#             #for all other values of diff_step, keep value and convert to string and then bytes
#             else:
#                 diffstepstr = str(f'{intstep}' + ' \r')
#             diffstepbyte = bytes(diffstepstr, 'ascii')
#             #serial settings and move command to desired wavelength
#             ser = serial.Serial(port=MCport, 
#                                     baudrate = 9600, 
#                                     timeout = None,
#                                     xonxoff = True,
#                                     parity = serial.PARITY_NONE,
#                                     stopbits = serial.STOPBITS_ONE,
#                                     bytesize = serial.EIGHTBITS,
#                                     )
#             ser.close()
#             ser.open()
#             ser.write(diffstepbyte); 
#             ser.read_until(size=None)
#             ser.close()
#             print(f"scan controller is moving by {diffstep} steps")
#             print(f"Moving scan controller {diffwave}nm to {float(wl)}nm. Taking {float(exp_list[idx])} millisecond exposure")
#             #check the limit status before starting movement, so the loop knows to scan up or down
#             mvread,msg = movestat(MCport,waittime=1)
#             if mvread == 999: #error code defined in mvread function
#                 print(msg)
#                 return
#             while mvread > 0: #some type of motion
#                 mvread,msg = movestat(MCport,waittime=1)
#                 print(msg)
#                 if mvread == 999: #connection error 
#                     print(msg)
#                     return              
#                 if mvread == 0: #no motion
#                     stop(MCport)
#                     msg = f"Movement completed"
#                     print(msg)
#                     msg=f"Running PIXIS subroutine"
#                     print(msg)
#                     time.sleep(exp)
#                     # pixisfunc(exp_list[idx])
#                     msg=f"The exposure for {currentwave}nm was taken"
#                     print(msg)
#                     #update list and go to the next input in the list
#                     currentwave = wl
#         print("Scan complete! Goiming back to home")
#         home(MCport)
#     except Exception as ex:
#         msg = f"Could not complete the command, Error: {ex}"
#         print(msg)
#         return

def moveit(MCport,move):
    """
    Continous scanning movement at given speed. Must run stop command to stop. VERY useful when creating code for scan contoller.
        Inputs:
            :MCport(string): Serial Port connection
            :move(float): Movement speed, units are steps
        Returns:
            ::Message if controller passed home wavelength
            ::Error message if exception occurs
    """
    try:
        strmove = str(f'M{move}' + '\r')
        move2bytes = bytes(strmove, 'ascii')
        print(f"MUST RUN mcapi.stop(port) TO STOP CONTINUOUS MOTION!")
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
        ser.write(move2bytes); #continuous move
        ser.read_until(size=None)
        ser.close()
        statnow,msg = checkstatus(MCport,waittime=1)
        if statnow < 32:
            while statnow < 32:
                statnow,msg = checkstatus(MCport,waittime=1)
                if statnow > 32:
                    print(f"scanner has passed home of 631.26nm")
        if statnow > 0:
            while statnow > 2:
                statnow,msg = checkstatus(MCport,waittime=1)
                if statnow < 32:
                    print(f"scanner has passed home of 631.26nm")
    except Exception as ex:
        msg = f"Error, could interpret move command. Error:{ex}"
        print(msg)
        return

def param(MCport):
    """
    Parameters for scan controller. Lists values of ramp speed, starting velocity, scanning velocity respectively.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Values for scanning parameters
            ::Error message if exception occurs
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
        ser.write(b'X \r'); #X=K(ramp speed),I(starting velocity),V(scanning velocity)
        s = ser.read_until(size=None) #reads the data coming from the serial until there is no data left
        param = codecs.decode(s)   
        ser.close()
        msg = f"ramp speed, start vel. , scan vel. (steps per second) : {param}"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not return parameters, Error:{ex}"
        print(msg)
        return

def rspeed(MCport,Rspeed):
    """
    Scanning ramp speed.
        Inputs:
            :MCport(string): Serial Port connection
            :Rspeed(int): Ramping speed for scan controller
        Returns:
            ::Ramp speed Value
            ::Error message if exception occurs
    """
    try:
        stringRspeed = (f'K{Rspeed}' + '\r')
        speed2bytes = bytes(stringRspeed, 'ascii')
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
        ser.write(speed2bytes); #ramp speed
        s = ser.read_until(size=None) #reads the data coming from the serial until there is no data left
        rs = codecs.decode(s)   
        ser.close()
        msg = f"ramp speed: {rs}"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not return parameters, Error:{ex}"
        print(msg)
        return

def startvel(MCport,Startvel):
    """
    Starting velocity of scan controller.
        Inputs:
            :MCport(string): Serial Port connection
            :Startvel(int): Starting velocity for scan controller in steps per second
        Returns:
            ::starting velocity value
            ::Error message if exception occurs
    """
    try:
        stringStartvel = (f'I{Startvel}' + '\r')
        Startvel2bytes = bytes(stringStartvel, 'ascii')
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
        ser.write(Startvel2bytes); #starting velocity
        s = ser.read_until(size=None) #reads the data coming from the serial until there is no data left
        startv = codecs.decode(s)   
        ser.close()
        msg = f"ramp speed: {startv}"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not return parameters, Error:{ex}"
        print(msg)
        return

def scanvel(MCport,Scanvel):
    """
    Scanning velocity.
        Inputs:
            :MCport(string): Serial Port connection
            :Scanvel(int): 
        Returns:
            ::scanning velocity value
            ::Error message if exception occurs
    """
    try:
        stringScanvel = (f'G{Scanvel}' + '\r')
        Scanvel2bytes = bytes(stringScanvel, 'ascii')
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
        ser.write(Scanvel2bytes); #scanning velocity
        s = ser.read_until(size=None) #reads the data coming from the serial until there is no data left
        svelocity = codecs.decode(s)   
        ser.close()
        msg = f"ramp speed: {svelocity}"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not return parameters, Error:{ex}"
        print(msg)
        return

def edge(MCport):
    """
    Finds edge of limit switch when scan controller is close to home. Slow scanning speed of 4500 steps/rev. Must run hcircuit and acircuit functions before running this command.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Movement has begun
            ::Exception if error occurs
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
        ser.write(b'F4500,0 \r'); #find edge. home swtich must be blocked. motor moves upward 4500steps/sec
        ser.read_until(size=None)
        ser.close()
        msg = f"finding edge of home flag"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not execute home flag finding function. Error: {ex}"
        print(msg)
        return

def hcircuit(MCport):
    """
    Switches home circuit to on. Used for fine, slow movements.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Circuit enabled
            ::Error message if exception occurs
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
        ser.write(b'A8 \r'); #enable home circuit
        ser.close()
        msg = f"home circuit enabled"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not enable home circuit. Error:{ex}"
        print(msg)
        return

def dcircuit(MCport):
    """
    Switches home circuit to off. Used for fine, slow movements.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Circuit disabled
            ::Error message if exception occurs
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
        ser.write(b'A0 \r'); #Disable Home Circuit
        ser.close()
        msg = f"disabled home circuit"
        print(msg)
        return msg
    except Exception as ex:
        msg =f"Error, could not disable home circuit. Error:{ex}"
        print(msg)
        return

def acircuit(MCport):
    """
    Switches home accuracy circuit to on. Used for fine, slow movements.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Accuracy circuit enabled
            ::Error message if exception occurs
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
        ser.write(b'A24 \r'); #home accuracy circuit enabled
        ser.close()
        msg = f"high accuracy circuit enabled"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not enable high accuracy circuit. Error: {ex}"
        print(msg)
        return

def exep(MCport,progname):
    """
    Runs user's premade scan controller movement program from files.
        Inputs:
            :MCport(string): Serial Port connection
            :progname(string): File path to user made program file
        Returns:
            ::Execution of program
            ::Error message if exception occurs
    """
    try:
        strprog = (f'G{progname}' + '\r')
        prog2bytes = bytes(strprog, 'ascii')
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
        ser.write(prog2bytes); #exectues program 
        ser.read_until(size=None)
        ser.close()
        msg = f"executing {progname}"
        print(msg)
        return
    except Exception as ex:
        msg = f"could not execute program. Error:{ex}"
        print(msg)
        return

def store(MCport):
    """
    Saves current scan controller parameters to non-volitile memory.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Storing completion
            ::Error message if exception occurs
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
        ser.write(b'S \r'); #store parameters 
        ser.read_until(size=None)
        ser.close()
        msg = f"storing parameters to memory"
        print(msg)
        return
    except Exception as ex:
        msg = f"could not store new parameters to memory. Error:{ex}"
        print(msg)
        return

def clear(MCport):
    """
    Erases current scan controller parameters.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Cleared message
            ::Error message if exception occurs
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
        ser.write(b'C1 \r'); #clear
        ser.read_until(size=None)
        ser.close()
        msg = f"cleared pre-programmed parameters"
        print(msg)
        return
    except Exception as ex:
        msg =f"could not clear parameters. Error: {ex}"
        print(msg)
        return

def reset(MCport):
    """
    Stops movement of scan controller. Assumes idle state.
        Inputs:
            :MCport(string):
        Returns:
            ::Reset message
            ::Error message if exception occurs
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
        ser.write(b'^C \r'); #Reset
        ser.read_until(size=None)
        ser.close()
        msg = f"reset,stopping motion,becoming idle"
        print(msg)
        return
    except Exception as ex:
        msg = f"could not reset. Could not stop motion.Error:{ex}"
        print(msg)  
        return

def exit(MCport):
    """
    Exit program mode. Run before closing code window.
        Inputs:
            :MCport(string): Serial Port connection
        Returns:
            ::Exit message
            ::Error message if exception occurs
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
        ser.write(b'P \r'); #enter or exit
        ser.read_until(size=None)
        ser.close()
        msg = f"exited program"
        print(msg)
        return
    except Exception as ex:
        msg = f"could not exit program. Please exit manually. Error:{ex}"
        print(msg)
        return