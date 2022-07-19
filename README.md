$UV Monochromator API
========

$UV Monochromator API will send commands to the McPherson 798-A Scan Controller for movements and homing.

Use main.py to enter and run commands, all libraries should be imported at the beginnng of the file.
To test that RS232 connection is working for communication between your computer and the Scan Controller, run mcapi.initial(port). You will need to check the serial ports on your computer for the correct port number the Scan Controller is connected to.

Features
--------
This software can home, check the limit status, movement status, set scanning parameters, stop and move the controller at user given range and interval with pauses for exposure times. Written for integration with PIXIS 1024B camera and Keithly 6482 Picoammeter.

Installation
------------
Download 798-A Scan Controller Application and drivers from McPherson.com
pyserial library
pyvisa library
Lightfield software

Contribute
----------

- Issue Tracker: https://github.com/aafaquerk/UV-Monochromator-control/issues
- Source Code: https://github.com/aafaquerk/UV-Monochromator-control

Support
-------

If you are having issues, please let us know.
olj1298@gmail.com

License
-------

The project is licensed under the BSD license.