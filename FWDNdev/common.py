class ControlCodes:
    ENQ = b'\x05'  # Enquiry - initiate request
    ACK = b'\x06'  # Acknowledge - the communication was received without error
    NAK = b'\x15'  # Negative Acknowledge - there was a problem with the communication
    SOH = b'\x01'  # Start of Header - beginning of header
    ETB = b'\x17'  # End of Transmission Block - end of intermediate block
    STX = b'\x02'  # Start of Text - beginning of data block
    ETX = b'\x03'  # End of Text - End of last data block
    EOT = b'\x04'  # End of Transmission - the request is complete.
    """Header"""
    CAD = b'\x30' + b'\x31' #Controller Address (default)
    OPW = b'\x38' #Operation Write
    OPR = b'\x30' #Operation Read
    DAT = b'\x31' #Data Type (V Memory)
    MSBWrite = b'\x34'+ b'\x31' #Starting Memory Address (MSB) Write
    MSBRead = b'\x30' + b'\x34' #Starting Memory Address (MSB) Read
    LSBWrite = b'\x38' + b'\x31' #Starting Memory Address (LSB) Write
    LSBRead = b'\x41' + b'\x31' #Starting Memory Address (LSB) Read
    CDB = b'\x30' + b'\x30' #Complete Data Blocks (None)
    PDB = b'\x30' + b'\x34' #Partial Data Block (Four Bytes)
    HCA = b'\x30' + b'\x30' #Host Computer Address
    LRCWrite = b'\x30' + b'\x31' #Checksum (LRC) Write
    LRCRead = b'\x37' + b'\x31' #Checksum (LRC) Read
    """Data"""
    DT3 = b'\x30' #Data -ASCII Byte 3
    DT4 = b'\x31' #Data -ASCII Byte 4
    DT1 = b'\x30' #Data - ASCII Byte 1
    DT2 = b'\x30' #Data - ASCII Byte 2
