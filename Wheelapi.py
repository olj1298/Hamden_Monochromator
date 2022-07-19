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

def rollwheel(wheelport):
    """
    Tests if 747 filter wheel serial parameters are correct and if port is closed or open. 
    Inputs:
        :wheelport(string): Serial port connection
    Returns:
        ::Confirmation that connection is working
        ::Error message if exception occured
    """
    try:
        ser = serial.Serial(port=wheelport, 
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
        ser.read_until(size=None) #reads out feedback until no data is left
        ser.close()
        msg = f"Program communication initialized"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not establish communication, check serial connection Error: {ex}"
        print(msg)
        return

#ENQ
#HEX:4E2105 ASCII:N!<ENQ>
#ACK
#HEX:4E2106 ASCII:N!<ACK>
#NAK
#HEX:4E2115 ASCII:N!<NAK>
