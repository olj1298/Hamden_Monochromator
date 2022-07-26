import serial
import six
from codecs import encode, decode

memory_map = {
    'V': 1,
}

class ControlCodes:
    ENQ = b'\x05'  # Enquiry - initiate request
    ACK = b'\x06'  # Acknowledge - the communication was received without error
    NAK = b'\x15'  # Negative Acknowledge - there was a problem with the communication
    SOH = b'\x01'  # Start of Header - beginning of header
    ETB = b'\x17'  # End of Transmission Block - end of intermediate block
    STX = b'\x02'  # Start of Text - beginning of data block
    ETX = b'\x03'  # End of Text - End of last data block
    EOT = b'\x04'  # End of Transmission - the request is complete.

class DNClient(object):
    """
    Client for accessing serial port using DirectNET protocol
    @type serial: serial.Serial
    """

    ENQUIRY_ID = b'N'

    def __init__(self, port):
        self.serial = serial.serial_for_url(port, baudrate=9600, timeout=1, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,xonxoff=False)
        self.client_id = 1

    def test_connection(self):
        self.enquiry()

    def disconnect(self):
        self.serial.close()

    def enquiry(self):
        self.serial.write(self.ENQUIRY_ID + chr(0x20 + self.client_id).encode() + ControlCodes.ENQ)
        ack = self.serial.read(size=3)
        assert ack == self.ENQUIRY_ID + chr(0x20 + self.client_id).encode() + ControlCodes.ACK, "ACK not received. Instead got: "+repr(ack)


    def read_header(self):
        read=1
        # Start of transmission
        header = ControlCodes.SOH

        # Controller Address (default)
        header += self.to_hex()

        # Client ID
        header += self.to_hex(3031, 2)

        # Operation Read/Write 0/8
        header += self.to_hex(0 if read else 8, 1)

        # Data type
        memory_type = address[0]
        header += self.to_hex(memory_map[memory_type], 1)

        # Address
        address = address[1:]
        header += self.to_hex(int(address, base=8)+1, 4)

        # No of blocks, bytes in last block
        header += self.to_hex(size / 256, 2)
        header += self.to_hex(size % 256, 2)

        # master id = 0
        header += self.to_hex(0, 2)

        header += ControlCodes.ETB

        # Checksum
        header += self.calc_csum(header[1:15])

        return header

    def get_request_header(self, read, address, size):
        # Header
        header = ControlCodes.SOH

        # Client ID
        header += self.to_hex(self.client_id, 2)

        # Operation Read/Write 0/8
        header += self.to_hex(0 if read else 8, 1)

        # Data type
        memory_type = address[0]
        header += self.to_hex(memory_map[memory_type], 1)

        # Address
        address = address[1:]
        header += self.to_hex(int(address, base=8)+1, 4)

        # No of blocks, bytes in last block
        header += self.to_hex(size / 256, 2)
        header += self.to_hex(size % 256, 2)

        # master id = 0
        header += self.to_hex(0, 2)

        header += ControlCodes.ETB

        # Checksum
        header += self.calc_csum(header[1:15])

        return header

    def read_value(self, header):
        self.enquiry()

        self.serial.write(header)

        self.read_ack()

        # data = self.parse_data(16)
        data=self.serial.readlines()

        self.write_ack()

        self.end_transaction()

        return data

    def read_int(self, address):
        data = self.read_value(address, 2)
        return int(encode(data[::-1], 'hex'))

    def read_ack(self):
        ack = self.serial.read(1)
        assert ack == ControlCodes.ACK, repr(ack) + ' != ACK'

    def read_end_of_text(self):
        etx = self.serial.read(1)
        assert etx == ControlCodes.ETX, repr(etx) + ' != ETX'

    def write_ack(self):
        self.serial.write(ControlCodes.ACK)

    def end_transaction(self):
        eot = self.serial.read(1)
        assert eot == ControlCodes.EOT, 'Not received EOT: '+repr(eot)
        self.serial.write(ControlCodes.EOT)

    def parse_data(self, size):
        data = self.serial.read(1 + size + 2)  # STX + DATA + ETX + CSUM
        return data[1:size+1]

    def calc_csum(self, data):
        csum = 0

        for item in data:
            csum ^= self.to_int(item)

        return self.to_bytes(csum)

    def to_hex(self, number, size):
        hex_chars = hex(number)[2:].upper()
        return ('0' * (size - len(hex_chars))) + hex_chars

    def to_int(self, value):
        if isinstance(value, int):
            return value
        return ord(value)

    def to_bytes(self, value):
        if six.PY3:
            return bytes((value,))
        return chr(value)