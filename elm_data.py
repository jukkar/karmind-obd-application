#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       elm_data.py
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

import time
import string
import re

import utils
import elm_decoder

class ELM_Data:
    def __init__(self):

        # record will contain two type of messages:
        # [pid, answer, boolean, time.time()] or
        # [message, info_level, None, time.time()]

        self.record = []
        self.mode = 'unknown'
        self.completed = False

        self.OBD_database = [

            ['PING','0100'],
            ['OBDSUP','011C'],
            ['TESTS','0101'],
            ['MIL','0101'],
            ['NUM_DTCS','0101'],
            ['DTCFRZF','0102'],
            ['FUELSYS','0103'],
            ['LOAD_PCT','0104'],
            ['ECT','0105'],
            ['SHRTFT1and3','0106'],
            ['LONGFT1and3','0107'],
            ['SHRTFT2and4','0108'],
            ['LONGFT2and4','0109'],
            ['FRP','010A'],
            ['MAP','010B'],
            ['RPM','010C'],
            ['VSS','010D'],
            ['SPARKADV','010E'],
            ['IAT','010F'],
            ['MAF','0110'],
            ['TP','0111'],
            ['ATR_STAT','0112'],
            ['O2SLOC','0113'],
            ['BNK1SEN1','0114'],
            ['BNK1SEN2','0115'],
            ['BNK1SEN3','0116'],
            ['BNK1SEN4','0117'],
            ['BNK2SEN1','0118'],
            ['BNK2SEN2','0119'],
            ['BNK2SEN3','011A'],
            ['BNK2SEN4','011B'],
            ['O2SLOC2','011D'],
            ['AUXINPST','011E'],
            ['RUNTM','011F'],
            ['MIL_DST','0121'],
            ['FLI','012F'],
            ['CLR_DIST','0131'],
            ['MIL_TIME','014D'],
            ['CLR_TIME','014E'],
            ['FUEL_TYP','0151'],
            ['ALCH_PCT','0152'],
            ['VIN_COUNT','0901'],
            ['VIN','0902'],
            ['CALID_COUNT','0903'],
            ['CALID','0904'],
            ['CVN_COUNT','0905'],
            ['CVN','0906'],
            ['ECUNAME','0909'],
            ['ECUNAME_COUNT','090A'],
            ['GET_STORED_DTCs','03'],
            ['GET_PENDING_DTCs','07']
            #['CLEAR_DTCs','04']
        ]

        self.OBD_description = {
            'PING':'0100 --> OBD-II Ping/keepalive + Request available PIDs',
            'TESTS':'0101 --> Status Since DTC Cleared',
            'MIL':'0101 --> Malfunction Indicator Lamp',
            'NUM_DTCS':'0101 --> Number of Diagnosic Trouble Codes',
            'DTCFRZF':'0102 --> DTC Causing Freeze Frame',
            'FUELSYS':'0103 --> Fuel System Status',
            'LOAD_PCT':'0104 --> Calculated Load Value',
            'ECT':'0105 --> Coolant Temperature',
            'SHRTFT1and3':'0106 --> Short Term Fuel Trim',
            'LONGFT1and3':'0107 --> Long Term Fuel Trim',
            'SHRTFT2and4':'0108 --> Short Term Fuel Trim',
            'LONGFT2and4':'0109 --> Long Term Fuel Trim',
            'FRP':'010A --> Fuel Rail Pressure',
            'MAP':'010B --> Intake Manifold Pressure',
            'RPM':'010C --> Engine RPM',
            'VSS':'010D --> Vehicle Speed',
            'SPARKADV':'010E --> Timing Advance',
            'IAT':'010F --> Intake Air Temp',
            'MAF':'0110 --> Air Flow Rate (MAF)',
            'TP':'0111 --> Throttle Position',
            'ATR_STAT':'0112 --> Secondary Air Status',
            'O2SLOC':'0113 --> Location of O2 sensors',
            'BNK1SEN1':'0114 --> O2 Sensor: 1 - 1',
            'BNK1SEN2':'0115 --> O2 Sensor: 1 - 2',
            'BNK1SEN3':'0116 --> O2 Sensor: 1 - 3',
            'BNK1SEN4':'0117 --> O2 Sensor: 1 - 4',
            'BNK2SEN1':'0118 --> O2 Sensor: 2 - 1',
            'BNK2SEN2':'0119 --> O2 Sensor: 2 - 2',
            'BNK2SEN3':'011A --> O2 Sensor: 2 - 3',
            'BNK2SEN4':'011B --> O2 Sensor: 2 - 4',
            'OBDSUP':'011C --> OBD Designation',
            'O2SLOC2':'011D --> Location of O2 sensors',
            'AUXINPST':'011E --> Aux input status',
            'RUNTM':'011F --> Time Since Engine Start',
            'MIL_DST':'0121 --> Engine Run with MIL on',
            'FLI':'012F --> Fuel Level Input',
            'CLR_DIST':'0131 --> Distance since DTCs cleared',
            'MIL_TIME':'014D --> Time run by the engine while MIL is activated',
            'CLR_TIME':'014E --> Time since DTCs cleared',
            'FUEL_TYP':'0151 --> Type of fuel being utilized',
            'ALCH_PCT':'0152 --> Alcohol fuel percentage',
            'VIN_COUNT':'0901 --> Vehicle id number message count',
            'VIN':'0902 --> Vehicle id number',
            'CALID_COUNT':'0903 --> Calibration id message count',
            'CALID':'0904 --> Calibration IDs (SW version ECU)',
            'CVN_COUNT':'0905 --> Calibration verification numbers message count',
            'CVN':'0906 --> Calibration Verification Numbers',
            'ECUNAME_COUNT':'0909 --> ECU name  message count',
            'ECUNAME':'090A --> ECU name',
            'GET_STORED_DTCs':'03 --> Service $03, get stored DTCs',
            'GET_PENDING_DTCs':'07 --> Service $07, get pending DTCs',
            #'CLEAR_DTCs':'04 --> Service $04, clear DTCs'
        }

        self.OBD_polling_database = [

            ['ECT','0105'],
            ['FRP','010A'],
            ['MAP','010B'],
            ['RPM','010C'],
            ['VSS','010D'],
            ['IAT','010F'],
            ['MAF','0110'],
            ['TP','0111'],
            ['RUNTM','011F'],
            ['FLI','012F']

        ]

        self.OBD_polling_description = {

            'ECT':'0105 --> Coolant Temperature',
            'FRP':'010A --> Fuel Rail Pressure',
            'MAP':'010B --> Intake Manifold Pressure',
            'RPM':'010C --> Engine RPM',
            'VSS':'010D --> Vehicle Speed',
            'IAT':'010F --> Intake Air Temp',
            'MAF':'0110 --> Air Flow Rate (MAF)',
            'TP':'0111 --> Throttle Position',
            'RUNTM':'011F --> Time Since Engine Start',
            'FLI':'012F --> Fuel Level Input'

        }

    def GetOBD_DBInfo(self, param = '-C'):

        mnemonics = []
        commands = []

        if param == '-C':
            for i in range(len(self.OBD_database)):
                mnemonics.append(self.OBD_database[i][0])
                commands.append(self.OBD_database[i][1])
        elif param == '-S':
            for i in range(len(self.OBD_polling_database)):
                mnemonics.append(self.OBD_polling_database[i][0])
                commands.append(self.OBD_polling_database[i][1])

        return mnemonics, commands


    def do_init(self, mode):
        self.mode = mode

    def do_complete(self):
        self.completed = True

    def test_if_valid(self, pid, answer):
        valid_response = False
        pattern = '4' + pid[1:]
        value_to_test = string.replace(answer,' ','')
        if re.search(pattern, value_to_test):
            valid_response = True
        return valid_response

    def set_value(self, pid, answer):

        # Insert parameter validation here before storing

        boolean = self.test_if_valid(pid, answer)
        self.record.append([pid, answer, boolean, time.time()])
        return

    def set_info(self, message, info_level = 'INFO'):

        # Insert parameter validation here before storing

        self.record.append([message, info_level, None, time.time()])
        return

    def get_value(self, position):
        if len(self.record) >= position:
            return self.record[position]
        else:
            return None

    def popup_statistics(self):

        MODES = {
            'unknown' : 'unknown',
            '-C': 'Check',
            '-D': 'Clear',
            '-S': 'Sampler',
            '-E': 'Expert'
        }

        def look_for_issues_check_mode():

            def extract_payload(answer):
                #Delete headers and checksum. Rework for multiple response messages
                test_pattern = string.replace(answer,' ','')
                index = string.find(test_pattern, '4101')
                position = index+len('4101')
                return test_pattern[position:-2]

            mil_state = []
            num_dtcs = []
            for i in range(len(self.record)):
                array = self.get_value(i)
                if array[0] == '0101':
                    payload = extract_payload(array[1])
                    while 1:
                        if len(payload) >= 8:
                            #index = string.find(test_pattern,'4101')
                            payload_databyte_1A = payload[0]
                            payload_databyte_2A = payload[1]
                            code = utils.hex_to_bin(payload_databyte_1A)[0]
                            if code:
                                mil_state.append('ON')
                            else:
                                mil_state.append('OFF')
                            partial1 = str(utils.hex_to_bin(payload_databyte_1A[0]))
                            partial2 = str(utils.hex_to_bin(payload_databyte_2A))
                            num_dtcs.append(str(int(partial1[1:]+partial2,2)))
                        try:
                            payload = payload[16:]  #jump ahead checksum and headers of next frame
                            if payload[0:4]!='4101':   #verify answer of next frame
                                break
                            else:
                                payload = payload[4:]
                        except IndexError:
                            break
                    break
            return mil_state, num_dtcs


        def add(message, line):
            message = message + line + '\n'
            return message

        def get_general_stats():
            info = 0
            commands = 0
            valid = 0
            invalid = 0
            for i in range(len(self.record)):
                record = self.get_value(i)
                if record[2] == None:
                    info += 1
                else:
                    commands += 1
                    if record[2]:
                        valid += 1
                    else:
                        invalid += 1
            return info, commands, valid, invalid

        """ Statistics retrieval starts here """

        message = ''
        message = add(message, '*** Statistics ***')

        message = add(message, 'Mode: %s' %MODES[self.mode])
        message = add(message, 'Task completed: %s' %self.completed)

        if self.completed == False:
            message = add(message, 'The job either hasn\'t finished correctly or was aborted. Perhaps you wanna try again...')
        if self.completed == True:
            info,commands, valid, invalid = get_general_stats()
            message = add(message, 'Total messages: %s' %str(int(info+commands)))
            message = add(message, 'Info messages: %s (%s%s)' %(info, str(float(info*100/(info+commands))), '%'))
            message = add(message, 'Command messages: %s (%s%s)' %(commands, str(100 - float(info*100/(info+commands))), '%'))
            message = add(message, 'Valid OBD answers received: %s' %valid)
            message = add(message, 'Invalid OBD answers received: %s' %invalid)
            message = add(message, 'OBD compliant level: %s%s' %(str(float(valid*100/(valid+invalid))), '%'))
            if self.mode in ['-S','-D']:
                message = add(message, 'No issues detected')
            else:
                mil, dtcs = look_for_issues_check_mode()
                if len(mil) == 0 and len(dtcs) == 0:
                    message = add(message, 'Issues detected: None')
                else:
                    message = add(message, 'Issues detected: DTCs detected in your car... Check them out in karmind.com!')
                    message = add(message, 'MIL state: %s' %mil[0])
                    message = add(message, 'Number of DTCs found: %s' %dtcs[0])

            message = add(message, 'Upload the output file to your personal space on karmind.com to have it available whenever you want.')
        return message

    def do_lookup(self, file = None):
        if file != None:
            f = open(file,'w')
        if self.completed:
            print 'Modo: ', self.mode
            for i in range(len(self.record)):
                array = self.get_value(i)
                print '\nPosition %s: ' %i
                if file != None:
                    f.write('\nPosition %s: ' %i)
                for j in range(len(array)):
                    print array[j]
                    if file != None:
                        f.write(str(array[j]))
            print self.popup_statistics()





def test():

    record = ELM_Data()

    record.do_init('-C')
    record.set_value('0100','48 6B 10 41 00 BE 3E A8 11 B9')
    record.set_value('011C','48 6B 10 41 1C 06 26')
    record.set_info('Testing the functionality','INFO')
    record.do_complete()
    record.do_lookup('prueba.txt')

    decoder = elm_decoder.ELM_Decoder(record)
    decoder.do_translate_answers()
    print decoder.show_answers_translated()
    print decoder.get_statistics()

if __name__ == '__main__':
    test()