#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       utils.py
#
#       Copyright 2010 miguel <enoelrocotiv@gmail.com>
#       Copyright 2010 oscar  <osc.iglesias@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


""" Utils module for KarmindOBD.py - Automotive tool based on OBD-II protocol """

import serial
   
def serial_test():
    
    """scan for available ports. return a list of serial names"""

    available = []

    for i in range(256):
      try: #scan standart ttyS*
        s = serial.Serial(i)
        available.append(s.portstr)
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    for i in range(256):
      try: #scan USB ttyACM
        s = serial.Serial("/dev/ttyACM"+str(i))
        available.append(s.portstr)
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    for i in range(256):
      try:
        s = serial.Serial("/dev/ttyUSB"+str(i))
        available.append( (i, s.portstr))
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    for i in range(256):
      try:
        s = serial.Serial("/dev/ttyd"+str(i))
        available.append( (i, s.portstr))
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    
    return available
    
    
def hex_to_bin(var):

        h2b = {
            '0':'0000',
            '1':'0001',
            '2':'0010',
            '3':'0011',
            '4':'0100',
            '5':'0101',
            '6':'0110',
            '7':'0111',
            '8':'1000',
            '9':'1001',
            'A':'1010',
            'B':'1011',
            'C':'1100',
            'D':'1101',
            'E':'1110',
            'F':'1111'
        }

        return h2b[var]
        
def hex_to_int(str):
    i = eval("0x" + str, {}, {})
    return i