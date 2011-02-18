#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       elm_decoder.py
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


import string
import binascii
from re import search

import utils

class ELM_Decoder:
    def __init__(self, record):
        # record format: list of lists
        # [pid, answer, boolean, time.time()]
        # or
        # [message, info_level, None, time.time()]
        # decoded record format: list of lists
        # [pid, answer, value, unit, time.time()] in case answer is not valid, value and unit are set to None

        self.available_models = [
            '-C',
            '-D',
            '-S',
            '-E'
        ]

        self.record = record.record
        self.mode = record.mode
        self.completed = record.completed
        self.decoded_record = []

        self.cmd2mnemonic = {
            '0100':'PING',
            '011C':'OBDSUP',
            '0101':'TESTS',
            '0101':'MIL',
            '0101':'NUM_DTCS',
            '0102':'DTCFRZF',
            '0103':'FUELSYS',
            '0104':'LOAD_PCT',
            '0105':'ECT',
            '0106':'SHRTFT1and3',
            '0107':'LONGFT1and3',
            '0108':'SHRTFT2and4',
            '0109':'LONGFT2and4',
            '010A':'FRP',
            '010B':'MAP',
            '010C':'RPM',
            '010D':'VSS',
            '010E':'SPARKADV',
            '010F':'IAT',
            '0110':'MAF',
            '0111':'TP',
            '0112':'ATR_STAT',
            '0113':'O2SLOC',
            '0114':'BNK1SEN1',
            '0115':'BNK1SEN2',
            '0116':'BNK1SEN3',
            '0117':'BNK1SEN4',
            '0118':'BNK2SEN1',
            '0119':'BNK2SEN2',
            '011A':'BNK2SEN3',
            '011B':'BNK2SEN4',
            '011D':'O2SLOC2',
            '011E':'AUXINPST',
            '011F':'RUNTM',
            '0121':'MIL_DST',
            '012F':'FLI',
            '0131':'CLR_DIST',
            '014D':'MIL_TIME',
            '014E':'CLR_TIME',
            '0151':'FUEL_TYP',
            '0152':'ALCH_PCT',
            '0901':'VIN_COUNT',
            '0902':'VIN',
            '0903':'CALID_COUNT',
            '0904':'CALID',
            '0905':'CVN_COUNT',
            '0906':'CVN',
            '0909':'ECUNAME',
            '090A':'ECUNAME_COUNT',
            '03':'GET_STORED_DTCs',
            '07':'GET_PENDING_DTCs',
            '04':'CLEAR_DTCs'
        }

        self.mnemonic2desc = {
            'PING':'0100 --> Keepalive + available PIDs',
            'TESTS':'0101 --> MIL, Number of DTCs and [00-20] available PIDs',
            'MIL':'0101 --> MIL, Number of DTCs and [00-20] available PIDs',
            'NUM_DTCS':'0101 --> MIL, Number of DTCs and [00-20] available PIDs',
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
            'CLEAR_DTCs':'04 --> Service $04, clear DTCs'
        }

    def set_value(self, pid, answer, value, unit, timestamp):
        self.decoded_record.append([pid, answer, value, unit, timestamp])
        return

    def get_value(self, position):
        if len(self.decoded_record) > position:
            return self.decoded_record[position]
        else:
            return None

    def get_value_rec(self, position):
        if len(self.record) >= position:
            return self.record[position]
        else:
            return None

    def extract_payload(self, cmd, answer):
        #Delete headers and checksum. Rework for multiple response messages
        test_pattern = string.replace(answer,' ','')
        if cmd=='04' and search('44', test_pattern):
            return '44'
        valid_code_answer = '4'+cmd[1:]
        index = string.find(test_pattern, valid_code_answer)
        position = index+len(valid_code_answer)
        return test_pattern[position:-2]

    def decode_dtc(self, frame):
        if frame == '0000' or len(frame)!=4:
            return None
        else:
            description = {
                '00':'P',
                '01':'C',
                '10':'B',
                '11':'U'
            }
            nibble = frame[0]
            pre_symbol = utils.hex_to_bin(nibble)
            symbol = description[pre_symbol[0:2]]
            first_char = hex(int(pre_symbol[2:],2))[2:]
            return symbol+first_char+frame[1:]

    def decode_answer(self, cmd, answer):
        # this will receive only valid answers
        value = None
        unit = None
        payload = self.extract_payload(cmd, answer)
        if cmd == '0100':
            value = payload

        elif cmd == '0101':
            mil_state = []
            num_dtcs = []
            supported_tests = []
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
                    tests = ''
                    for i in range(2,6):
                        tests = tests + utils.hex_to_bin(payload[i])
                    supported_tests.append(tests)
                try:
                    payload = payload[16:]  #jump ahead checksum and headers of next frame
                    if payload[0:4]!='4101':   #verify answer of next frame
                        break
                    else:
                        payload = payload[4:]
                except IndexError:
                    break

            value = [mil_state, num_dtcs, supported_tests]

        elif cmd == '0102':
            value = self.decode_dtc(payload)


        elif cmd == '0103':
            #OL: open loop. CL: closed loop.
            description = {
                '00000000':'Wrong state',
                '00000001':'OL',
                '00000010':'CL',
                '00000100':'OL-Drive',
                '00001000':'OL-Fault',
                '00010000':'CL-Fault',
                '0010000':'ISO Reserved',
                '01000000':'ISO Reserved',
                '10000000':'ISO Reserved'
            }
            fuel_system1_status = utils.hex_to_bin(payload[0]) + utils.hex_to_bin(payload[1])
            fuel_system2_status = utils.hex_to_bin(payload[2]) + utils.hex_to_bin(payload[3])
            try:
                value = [description[fuel_system1_status], description[fuel_system2_status]]
            except KeyError:
                value = 'Unknown'

        elif cmd in ['0104','012F','0152']:
            code = utils.hex_to_int(payload)
            value = code * 100.0 / 255.0
            unit = 'Percent scale'

        elif cmd == '0105' or cmd == '010F':
            code = utils.hex_to_int(payload)
            value = code - 40
            unit = 'Degrees Celsius'

        elif cmd in ['0106', '0107', '0108', '0109']:
            code = utils.hex_to_int(payload)
            value = (code - 128.0) * 100.0 / 128
            unit = 'Percent scale'

        elif cmd == '010A':
            code = utils.hex_to_int(payload)
            value = code * 3
            unit = 'KPa'

        elif cmd == '010B':
            value = utils.hex_to_int(payload)
            unit = 'KPa'

        elif cmd == '010C':
            code = utils.hex_to_int(payload)
            value = code / 4
            unit = 'RPM'

        elif cmd == '010D':
            value = utils.hex_to_int(payload)
            unit = 'Km/h'

        elif cmd == '010E':
            code = utils.hex_to_int(payload)
            value = (code - 128) / 2.0
            unit = 'Degrees'

        elif cmd == '0110':
            code = utils.hex_to_int(payload)
            value = code * 0.01
            unit = 'g/s'

        elif cmd == '0111':
            code = utils.hex_to_int(payload)
            value = code * 0.01
            unit = 'Percent scale'

        elif cmd == '0112':
            description = {
                '00000000':'Wrong state',
                '00000001':'UPS',
                '00000010':'DNS',
                '00000100':'OFF',
                '00001000':'ISO Reserved',
                '00010000':'ISO Reserved',
                '0010000':'ISO Reserved',
                '01000000':'ISO Reserved',
                '10000000':'ISO Reserved'
            }
            air_status = utils.hex_to_bin(payload[0]) + utils.hex_to_bin(payload[1])
            try:
                value = description[air_status]
            except KeyError:
                value = 'Unknown'

        elif cmd in ['0113','011D']:
            value = utils.hex_to_bin(payload[0]) + utils.hex_to_bin(payload[1])

        elif cmd in ['0114', '0115', '0116', '0117', '0118', '0119', '011A', '011B']:
            code = utils.hex_to_int(payload[0:2])
            voltage = code * 0.005
            code2 = utils.hex_to_int(payload[2:4])
            stft = (code2 - 128.0) * 100.0 / 128
            value= [voltage, stft]
            unit = ['V', 'Percent scale']

        elif cmd == '011C':
            description = {
                '01':'OBD-II',
                '02':'OBD',
                '03':'OBD and OBD-II',
                '04':'OBD-I',
                '05':'NO OBD',
                '06':'EOBD',
                '07':'EOBD and OBD-II',
                '08':'EOBD and OBD',
                '09':'EOBD, OBD and OBD-II',
                '0A':'JOBD',
                '0B':'JOBD and OBD-II',
                '0C':'JOBD and OBD',
                '0D':'JOBD, EOBD and OBD-II',
                '0E':'EURO IV B1',
                '0F':'EURO V B2',
                '10':'EURO C',
                '11':'EMD'
            }
            try:
                value = description[payload]
            except KeyError:
                value = 'Unknown'

        elif cmd == '011E':
            code = utils.hex_to_bin(payload[1])[3]
            if code:
                value = 'ON'
            else:
                value = 'OFF'

        elif cmd == '011F':
            code = utils.hex_to_int(payload)
            value = code / 60
            unit = 'min'

        elif cmd in ['0121','0131']:
            value = utils.hex_to_int(payload)
            unit = 'Km'

        elif cmd in ['014D','014E']:
            value = utils.hex_to_int(payload)
            unit = 'min'

        elif cmd == '0151':
            description = {
                '01':'GAS',
                '02':'METH',
                '03':'ETH',
                '04':'DSL',
                '05':'LPG',
                '06':'CNG',
                '07':'PROP',
                '08':'ELEC',
                '09':'BI_GAS',
                '0A':'BI_METH',
                '0B':'BI_ETH',
                '0C':'BI_LPG',
                '0D':'BI_CNG',
                '0E':'BI_PROP',
                '0F':'BI_ELEC',
            }
            try:
                value = description[payload]
            except KeyError:
                value = 'Unknown'

        elif cmd in ['0901','0903','0905','0909']:
            value = utils.hex_to_int(payload)
            unit = 'Messages'

        elif cmd in ['0902','0904','0906','090A']:
            matrix = []
            while 1:
                if len(payload)>=9:    #if there is a compliant frame of response
                    index = utils.hex_to_int(payload[0:2])
                    frame = binascii.unhexlify(payload[2:10])
                    matrix.append([index,frame])
                else:
                    break
                try:
                    payload = payload[18:]  #jump ahead checksum and headers of next frame
                    if payload[0:4] not in ['4902','4904','4906','490A']:   #verify answer of next frame
                        break
                    else:
                        payload = payload[4:]
                except IndexError:
                    break
            #now, order the values gotten
            if len(matrix) > 0:
                value = ''
                for i in range(len(matrix)):
                    if matrix[i][0] == i:
                        value = value + matrix[i][1]

        elif cmd in ['03','07']:
            value = []
            while 1:
                if len(payload)>=12:    #if there is a compliant frame of dtcs
                    k = 0
                    while k != 12:
                        value_k = self.decode_dtc(payload[k:k+4])
                        if value_k != None:
                            value.append(value_k)
                        k += 4
                else:
                    break
                try:
                    payload = payload[20:]  #jump ahead checksum and headers of next frame
                    if payload[0:2] not in ['43','47']: #verify answer of next frame
                        break
                    else:
                        payload = payload[2:]
                except IndexError:
                    break

        elif cmd == '04':
            if payload == '44':
                value = True
            else:
                value = False
        return value, unit


    def do_translate_answers(self):
        if self.mode in self.available_models and self.completed:
            for i in range(len(self.record)):
                record = self.get_value_rec(i)
                if record[2] != None:   #if not info message
                    cmd = record[0]
                    answer = record[1]
                    timestamp = record[3]
                    if record[2] == True:   #if obd answer was valid
                        value, unit = self.decode_answer(cmd, answer)
                        self.set_value(cmd, answer, value, unit,timestamp)
                    if record[2] == False:
                        self.set_value(cmd, answer, None, None, timestamp)
        return


    def show_answers_translated(self):
        answers = []
        for i in range(len(self.decoded_record)):
            cmd, answer, value, unit, timestamp = self.get_value(i)
            description = self.mnemonic2desc[self.cmd2mnemonic[cmd]]
            answers += [{'description': description, 'answer': answer, 'value': value, 'unit': unit, 'timestamp': timestamp}]
        return answers


    def get_statistics(self):

        MODES = {
            'unknown' : 'unknown',
            '-C': 'Check',
            '-D': 'Clear',
            '-S': 'Sampler',
            '-E': 'Expert'
        }

        def add(message, line):
            message = message + line + '\n'
            return message

        def get_general_stats():
            commands = 0
            valid = 0
            invalid = 0
            for i in range(len(self.decoded_record)):
                commands += 1
                record = self.get_value(i)
                if record[2] == None:
                    invalid += 1
                else:
                    valid += 1

            return commands, valid, invalid

        """ Statistics retrieval starts here """

        message = ''
        message = add(message, '*** Statistics ***')

        message = add(message, 'Mode: %s' %MODES[self.mode])
        message = add(message, 'Task completed: %s' %self.completed)

        if self.completed == False:
            message = add(message, 'The job either hadn\'t finished correctly or it was aborted. Perhaps you wanna try again with the app...')
        if self.completed == True:
            commands, valid, invalid = get_general_stats()
            message = add(message, 'Total command messages: %s' %str(int(commands)))
            message = add(message, 'Valid OBD answers received: %s' %valid)
            message = add(message, 'Invalid OBD answers received: %s' %invalid)
            message = add(message, 'OBD compliant level: %s%s' %(str(float(valid*100/(valid+invalid))), '%'))
            if self.mode in ['-S','-D']:
                message = add(message, 'No issues detected')
            else:
                iter = 0
                issue = False
                for i in range(len(self.decoded_record)):
                    array = self.get_value(i)
                    if array[0]=='0101' and iter == 0: #format: pid, answer, value composed by MIL and num DTCs, and unit
                        iter += 1
                        message = add(message, 'MIL state: %s' %array[2][0][0])
                        message = add(message, 'Number of Diagnostic Trouble Codes detected: %s' %array[2][1][0])
                        if int(array[2][1][0])>0:
                            issue = True
                    if array[0]=='03' and len(array[2])>0:
                        message = add(message, 'Stored DTCs: %s' %array[2])
                    if array[0]=='07' and len(array[2])>0:
                        message = add(message, 'Pending DTCs: %s' %array[2])
                if issue:
                    message = add(message, 'Issues were detected regarding Diagnostic Trouble Codes. Check them out on DTC-Lookup!')
            return message
        else:
            return None