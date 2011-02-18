#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       obd_link.py
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

import serial
import string
import time
import re
import logging

import utils



class OBDPort:
    """ OBDPort allows to abstract the communication with ELM-327"""

    def __init__(self, portnum, serial_timeout, max_retries, record):

        baud     = 9600
        databits = 8
        par      = serial.PARITY_NONE
        sb       = 1
        to       = serial_timeout
        self.ELMver = "Unknown"
        self.State = 1 #state SERIAL is 1 connected, 0 disconnected (connection failed)
        self.portnum = portnum
        self.record = record
        self.max_retries = max_retries

        pre_connect_commands = [
            'ate0',
            'ati',
            'ath1',
            'atsp0'
        ]

        post_connect_commands = [
            'atdp',
            'atdpn',
            'atstff'
        ]


        logging.debug('Opening interface (serial port)')
        self.record.set_info('Opening interface (serial port)')

        available_ports = utils.serial_test()
        ELM_found = 0

        for i in range(len(available_ports)):
            try:
                self.State = 1
                logging.debug('Trying to open %s (serial port)' %available_ports[i])
                self.record.set_info('Trying to open '+str(available_ports[i])+' (serial port)')
                self.port = serial.Serial(available_ports[i], baud, \
                parity = par, stopbits = sb, bytesize = databits,timeout = to)
            except serial.SerialException:
                logging.debug('Port %s could not be opened' %available_ports[i])
                self.State = 0
            else:
                logging.debug('Port %s opened successfully, trying to connect ...' %available_ports[i])
                self.send_command("ati")
                data, validation_test = self.get_result("ati")
                if re.search('ELM', data):
                    logging.debug('Found ELM device in port %s !!!' %available_ports[i])
                    ELM_found = 1
                    self.portnum = available_ports[i]
                    self.port.close()
                    break
                else:
                    logging.debug('ELM device not found in port %s ...' %available_ports[i])

        if not(ELM_found):
            logging.debug('ELM device could not be found. Trying with port from .ini file...')

        """ Now the connection will be made from COM detected earlier, or in case was not, with that from elm.ini """

        self.State = 1
        try:
            logging.debug('Trying to open designed port %s (serial port)' %self.portnum)
            self.record.set_info('Trying to open designed port'+ str(self.portnum)+' (serial port)')
            self.port = serial.Serial(self.portnum, baud, \
            parity = par, stopbits = sb, bytesize = databits,timeout = to)

        except serial.SerialException:
            self.State = 0
            return None

        logging.debug('Interface '+ str(self.port.portstr) +' scanned successfully')
        self.record.set_info('Interface '+ str(self.port.portstr) +' scanned successfully')
        logging.debug('Connecting to ECU...')
        self.record.set_info('Connecting to ECU...')

        ready = "ERROR"
        count=0

        while ready == "ERROR": #until error is returned try to connect
            try:
                self.send_command('atz')   # initialize
            except serial.SerialException:
                self.State = 0
                return None

            self.ELMver, validation_test = self.get_result('atz')
            if not(re.search('ELM',self.ELMver) or re.search('OK', self.ELMver)):
                logging.warning('Aborted execution: unable to connect to ELM device')
                self.record.set_info('Aborted execution: unable to connect to ELM device')
                self.close()
                self.State = 0
                return None

            for i in pre_connect_commands:
                self.send_command(i)
                got, validation_test = self.get_result(i)

            self.send_command("0100")   # ping/PID request
            ready, validation_test = self.get_result("0100")

            if re.search("[0-9]",ready) or re.search("OK", ready):
                for i in post_connect_commands:
                    self.send_command(i)
                    got, validation_test = self.get_result(i)
            else:
                logging.debug('Connection attempt failed: '+ready)
                self.record.set_info('Connection attempt failed: '+str(ready))
                ready='ERROR' #Expecting error message: BUSINIT:.ERROR
                time.sleep(5)
                logging.debug('Connection attempt: '+str(count))
                self.record.set_info('Connection attempt: '+str(count))
                count+=1
                if count == self.max_retries:
                    logging.warning('EXECUTION ABORTED: unable to connect after max_retries')
                    self.record.set_info('EXECUTION ABORTED: unable to connect after max_retries')
                    self.close()
                    self.State = 0
                    return None


    def send_command(self, cmd):
        """Internal use only: not a public interface"""
        if self.port:
            self.port.flushOutput()
            self.port.flushInput()
            for c in cmd:
                self.port.write(c)
            self.port.write("\r\n")
        return

    def get_result(self, cmd):
        """Internal use only: not a public interface"""
        if self.port:
            buffer = ""
            ini_t = time.time()
            cur_t = time.time()
            while (cur_t-ini_t < 5):
                c = self.port.read(1)
                cur_t = time.time()
                if c == '>' and len(buffer) > 0:
                    break
                else:
                    if (buffer != "" or c != ">"):
                        if (c=="\r" or c=="\n" or c==':'):
                            buffer = buffer + ' '
                        else:
                            buffer = buffer + c

            if re.search('at|AT|At|aT',cmd):
                valid_response = 'SETUP'
            else:
                valid_response = 'N'
                test_pattern = string.replace(buffer,' ','')
                check = '4' + cmd[1:]
                if re.search(check,test_pattern):
                    valid_response = 'Y'


            logging.info('Output of '+str(cmd)+': '+str(string.strip(buffer)))
            if valid_response != 'SETUP':
                self.record.set_value(str(cmd),str(string.strip(buffer)))
            else:
                self.record.set_info(str(cmd),'SETUP')

            return buffer, valid_response
        return None, None

    def close(self):
        """ Resets device and closes all associated filehandles"""

        if (self.port!= None) and self.State==1:
            self.send_command("atz")
            self.port.close()

        self.port = None
        self.ELMver = "Unknown"

        self.record.do_complete()
        return