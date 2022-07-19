import serial

def shutopen(shutport):
    """
    Tests if VCM D1 shutter controller serial parameters are correct and if port is closed or open. Opens shutter if connection is working properly. 
    Inputs:
        :port(string): Serial port connection
    Returns:
        ::Shutter open message
        ::error message due to improper connection
    """
    try:
        #serial communication settings. port variable may be changed depending on computer connected, but other settings must stay the same
        ser = serial.Serial(port=shutport, 
                            baudrate = 9600, 
                            timeout = None,
                            xonxoff = True,
                            parity = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE,
                            bytesize = serial.EIGHTBITS,
                            )
        ser.close()
        ser.open()
        ser.write(b'@'); #ASCII command to open shutter
        msg = f"Shutter opened"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not establish communication, check serial connection Error: {ex}"
        print(msg)
        
def shutclose(shutport):
    """
    Tests if VCM D1 shutter controller serial parameters are correct and if port is closed or open. Closes shutter if connection is working properly
    Inputs:
        :port(string): Serial port connection
    Returns:
        ::Shutter close message
        ::error message due to improper connection
    """
    try:
        #serial communication settings. port variable may be changed depending on computer connected, but other settings must stay the same
        ser = serial.Serial(port=shutport, 
                            baudrate = 9600, 
                            timeout = None,
                            xonxoff = True,
                            parity = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE,
                            bytesize = serial.EIGHTBITS,
                            )
        ser.close()
        ser.open()
        ser.write(b'A'); #ASCII command to close shutter
        msg = f"Shutter closed"
        print(msg)
        return
    except Exception as ex:
        msg = f"Error, could not establish communication, check serial connection Error: {ex}"
        print(msg)