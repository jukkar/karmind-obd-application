#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       myOBDclasses.py
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

""" myOBDclasses module for KarmindOBD.py - Automotive tool based on OBD-II protocol """

import os
import re
import sys
import ConfigParser
import logging

import obd_link

class OBD_Connector():

    def __init__(self, record):
        self.record = record
        config = ConfigParser.RawConfigParser()
        if sys.platform == 'win32':
            configfilepath="karmind.ini"
        else:
            configfilepath=os.environ['HOME']+'/.karmind' #TODO: Change filename for Unix OS

        if config.read(configfilepath) == []:
            # Defaults
            self.COMPORT        = "/dev/ttyACM0"
            self.RECONNATTEMPTS = 5
            self.SERTIMEOUT     = 2
        else:
            self.COMPORT        = config.get("elm","COMPORT")
            self.RECONNATTEMPTS = config.getint("elm","RECONNATTEMPTS")
            self.SERTIMEOUT     = config.getint("elm","SERTIMEOUT")

        return

    def initCommunication(self):

        global OBD_Interface

        OBD_Interface = obd_link.OBDPort(
            self.COMPORT,
            self.SERTIMEOUT,
            self.RECONNATTEMPTS,
            self.record
        )

        if OBD_Interface.State==0: #serial port can not be opened
            logging.warning('No init interface %s... shutting down app!' %(OBD_Interface.portnum))
            return 0
        else:
            logging.debug('Interface %s initialized successfully' %(OBD_Interface.portnum))
            return 1

    def run_OBD_command(self, obd_command, option):

        if (OBD_Interface.State==1):  #Caution, if UNABLE TO CONNECT is received, OBD_Interface remains set to 1

            if obd_command == 'END':
                OBD_Interface.close()
                return
            OBD_Interface.send_command(obd_command)
            bus_data = ''
            bus_data, validation_test = OBD_Interface.get_result(obd_command)
            if bus_data:
                if (re.search('UNABLE', bus_data) or re.search('BUSY', bus_data) or re.search('ERROR', bus_data)) and option!='-E':
                    logging.warning('Unable to connect to OBD socket while getting parameters, shutting down app... \
Please check port configuration, connectivity between laptop and OBD socket, and turn the ignition on in the car!')
                    OBD_Interface.close()
                    sys.exit(1)
                return bus_data, validation_test
            else:
                return 'ERROR', validation_test
        else:
            return 'OBD PORT CLOSED'