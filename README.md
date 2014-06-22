CCLib
=====

An arduino and a python library that implements a CC.Debugger for Texas Instruments' CCxxxx chips. 
The python library targets specifically the CC2540 SoC which is used by BlueGiga's BLE112 & BLE113 modules.
The arduino library on the other hand is just a low-level debug protocol implementation that can be used 
with any CCxxxx chip.

Wiring
------

The arduino library is tailored for 5V Teensy/Arduino chips, and therefore provide two separate DD pins, for use with voltage dividers (since the BLE112/3 chips operate on 3.3V).

Start with the **CCLib_proxy** example from CCLib and change the pin configuration in order to match your setup. For your reference, here is the wiring diagram with voltage dividers.

    For the DD Pin:
    
     <CC_DD_O> --[ 100k ]-- <CC_DD_I> --[ 200k ]-- <GND>
                                |
                               {DD}
     
    For the DC Pin:
    
     <CC_DC> --[ 100k ]-- {DC} --[ 200k ]-- <GND>
     
    For the RST Pin:
     
     <CC_DC> --[ 100k ]-- {RST} --[ 200k ]-- <GND>

Where {DD},{DC} and {RST} are the pins on the CCxxxx chip.

Usage
-----

1. Open the CCLib_proxy example.
2. Change the `LED`, `CC_RST`, `CC_DC`, `CC_DD_I` and `CC_DD_O` constants to match your configuration.
3. Flash it to your Teensy/Arduino
4. Connect it to your CCxxxx chip
5. Use the python scripts from the Python/ directory to read/flash your chip.

Disclaimer
----------

I have successfully managed to flash various BLE112 modules using the scripts provided with this project, however I DO NOT GURANTEE THAT THIS WILL WORK IN YOUR CASE. **YOU ARE USING THIS CODE SOLELY AT YOUR OWN RISK!**

License
-------

Copyright (C) 2014 Ioannis Charalampidis

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


