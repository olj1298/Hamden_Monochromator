import codecs
import time
import serial
import numpy as np
from icecream import ic

ser = serial.Serial('COM5', 
                                baudrate = 9600, 
                                timeout = None,
                                xonxoff = True,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                )
ser.close()
print("Remember to close the connection before exiting the program!")
def param(event):
    try:
        ser.open()
        ser.write(b'X \r'); #X=K(ramp speed),I(starting velocity),V(scanning velocity)
        s = ser.read_until(size=None) #reads the data coming from the serial until there is no data left
        param = codecs.decode(s)   
        print("ramp speed, start vel., scan vel. : ", param)
        ser.close()
    except:
        print("Error, could not return parameters.")

def exep(event):
    try:
        ser.open()
        ser.write(b'G \r'); #exectues program stored in non-volitile memory
        s=ser.read_until(size=None)
        print("executing program")
        #add user putting in their program's address
        #address = [input("Enter your stored program's address")]
        ser.close()
    except:
        print("Error, could not execute program")

def wait(event):
    try:
        ser.open
        ser.write(b'W \r'); #wait n milliseconds n= 0 to 65535
        ser.read_until(size=None)
        print("wait n millisecods for next command")
        ser.close()
    except:
        print("Error, could not insert wait command.")

def movestat(event):
    try:
        ser.open()
        ser.write(b'^ \r'); #read moving status 0=no motion, 1=moving, 2=High const. vel., 16=slewing ramping complete
        s=ser.read_until(size=None)
        read = codecs.decode(s)
        print("moving status: ", read)
        ser.close()
    except:
        print("Error, could not read moving status.")

def status(event):
    try:
        ser.open()
        ser.write(b'] \r'); #read limit switch status 0=no limit, 32=home limit, 64=high limit, 128=low limit
        s=ser.read_until(size=None)
        stat = codecs.decode(s)
        stat = int(float(str(stat[4:])))
        print("limit status is: ", stat)
        ser.close()
    except:
        print("Error, could not read limit status.")

def eprg(event):
    try:
        ser.open()
        s=ser.write(b'P \r'); #enter and exit program mode. P0 thru P1000 sets scanner in internal program mode
        s=ser.read_until(size=None)
        print("exited program")
        ser.close()
    except:
        print("Error, could not exit program. Please exit manually.")

def edge(event):
    try:
        ser.open()
        ser.write(b'F4500,0 \r'); #find edge. home swtich must be blocked. motor moves upward 4500steps/sec
        s=ser.read_until(size=None)
        print("finding edge of home flag")
        ser.close()
    except:
        print("Error, could not execute home flag finding function.")

def hcircuit(event):
    try:
        ser.open()
        ser.write(b'A8 \r'); #enable home circuit
        s=ser.read_until(size=None)
        print("home circuit enabled")
        ser.close()
    except:
        print("Error, could not enable home circuit.")

def dcircuit(event):
    try:
        ser.open()
        ser.write(b'A0 \r'); #Disable Home Circuit
        s=ser.read_until(size=None)
        print("disabled home circuit")
        ser.close()
    except:
        print("Error, could not disable home circuit. Check serial connection.")

def acircuit(event):
    try:
        ser.open()
        ser.write(b'A24 \r'); #home accuracy circut enabled
        s=ser.read_until(size=None)
        print("high accuracy circuit enabled")
        ser.close()
    except:
        print("Error, could not enable high accuracy circuit.")

def store(event):
    try:
        ser.open()
        ser.write(b'S \r'); #store parameters to non-volitile memory
        ser.read_until(size=None)
        print("storing parameters to memory")
        ser.close()
    except:
        print("Error, could not store new parameters to memory.")

def init(event):
    try:
        ser.open()                            
        ser.write(b' \r'); 
        ser.read_until(size=None) 
        ser.close()
        print("communication initialized")
    except:
        print("Error, could not initialize communication, check serial connection.")

def clear(event):
    try:
        ser.open()
        ser.write(b'C1 \r'); #clear; erases pre-programmed parameters. only use when unexplainable scanning error has occured
        s=ser.read_until(size=None)
        print("cleared pre-programmed parameters")
        ser.close()
    except:
        print("Error, could not clear parameters.")

def reset(event):
    try:
        ser.open()
        ser.write(b'^C \r'); #Reset; stops motion, sets counter to 0 assumes idle state
        s=ser.read_until(size=None)
        print("reset, stopping motion, becoming idle")
        ser.close()
    except:
        print("Error, could not reset. Could not stop motion.")

def stop(event):
    try:
        ser.open()
        ser.write(b'@ \r'); #soft stop
        s=ser.read_until(size=None)
        print("stopping scan controller")
        ser.close()
    except:
        print("Error, could not stop scan. Check if serial is opened or closed.")