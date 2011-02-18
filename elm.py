#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       elm.py
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

import re
import time
import sys
import logging
import os
import ConfigParser

import myOBDclasses
import elm_data
import elm_decoder


class Elm:
    def __init__(self):

        self.MODES = [
            '-C',
            '-D',
            '-E',
            '-S'
        ]

        self.record = elm_data.ELM_Data()
        self.port = None
        self.keep_going = True
        self.total_steps = 30
        self.current_step = 0
        self.status = 'Idle'
        self.observers = {'status': [], 'progress': [], 'logger': []}

    def register_observer(self, callback, event = 'status'):
        self.observers[event].append(callback)

    def notify_observer(self, event):
        for callback in self.observers[event]:
            callback(self)

    def do_cancel(self):
        self.keep_going = False

    def create_connection(self):
        self.record = elm_data.ELM_Data()
        self.Processor = myOBDclasses.OBD_Connector(self.record) #TODO: if there is not response from ECU to atz command, the app remains freezed here
        self.serial = self.Processor.initCommunication()
        if (self.serial != 1):
            self.set_status('Connection error...')
        return

    def do_connect(self):
        self.keep_going = True
        self.set_status('Creating data structures...')
        self.set_status('Connecting...')
        self.create_connection()
        self.set_status('Connected')
        return

    def do_disconnect(self):
        self.set_status('Disconnecting...')
        time.sleep(0.5)
        self.set_status('Disconnected')
        #print self.record.popup_statistics()
        #self.record.do_lookup('prueba.txt')
        return

    def do_test(self, option):
        if option not in self.MODES:
            self.set_status('App mode selected unsupported')
            self.set_logger('App mode selected unsupported, shutting down app')
            raise
        self.set_status('Working...')

        self.option = option
        self.record.do_init(option)


        if self.option == '-C':
            self.check_mode(self.Processor)
        elif self.option == '-D':
            self.delete_mode(self.Processor)
        elif self.option == '-E':
            self.expert_mode(self.Processor)
        elif self.option == '-S':
            try:
                self.sampler_mode(self.Processor)
            except KeyboardInterrupt:
                self.set_logger('>>> Polling aborted by user, finishing...')
            self.Processor.run_OBD_command('END', self.option)
        self.set_status('Work finished')
        return

    def set_progress(self, current_step):
        self.current_step = current_step
        self.notify_observer('progress')

    def get_progress(self):
        return int(100.0 * self.current_step / self.total_steps)

    def set_status(self, status):
        self.status = status
        self.notify_observer('status')

    def get_status(self):
        return self.status

    def set_logger(self, logger):
        self.logger = logger
        self.notify_observer('logger')

    def get_logger(self):
        return self.logger

    def check_mode(self, Processor):
        self.mnemonics, self.commands =  self.record.GetOBD_DBInfo(self.option)
        self.total_steps = len(self.commands)
        current_step = 1
        total = len(self.commands)
        for i in range(len(self.commands)):
            self.set_logger(' > Getting OBD polling parameter (%d/%d)...' %(current_step, total))
            if self.keep_going == False:
                self.set_progress(self.total_steps)
                self.set_status('Cancelled by user')
                #time.sleep(1)
                return
            self.set_progress(current_step)
            #time.sleep(0.1)
            Processor.run_OBD_command(self.commands[i], self.option)
            #time.sleep(.1)
            current_step += 1
        Processor.run_OBD_command('END', self.option)
        self.set_status('Succesfully tested')
        return

    def delete_mode(self, Processor):
        self.set_logger(' > Executing CLEAR status command...')
        SERVICE_CLEAR = '04'
        result, validation = Processor.run_OBD_command(SERVICE_CLEAR, self.option)
        if validation == 'Y':
            self.set_logger(' > Done! Try again Check mode to take a new snapshot of system status...')
        else:
            self.set_logger(' > Fail! ECU busy, try again in a few later...')
        Processor.run_OBD_command('END', self.option)
        return

    def expert_mode(self, Processor):
        self.set_logger(' > Launching Expert Mode console...')
        choice = ''
        valid_answers = ['Y','N']
        while choice not in valid_answers:
            choice = raw_input('WARNING: You are enabling EXPERT mode.\n\
It allows to perform any OBD command against Electronic Control Units.\n\
May lead to harm in your car if not used wisely. Do you wish to proceed? (Y/N)')
        if choice == 'Y':
            self.set_logger(' *** DISCLAIMER: There is absolutely no warranty for any action performed by the user from here on ***')
            self.set_logger('Type quit to exit')
            while self.keep_going == True:
                try:
                    user_command = raw_input('ROOT@KT-OBD>').upper()
                    if re.search('\AAT', user_command):
                        self.set_logger('Wrong command, ELM configuration is not allowed')
                    elif re.search('QUIT', user_command):
                        raise KeyboardInterrupt
                    elif user_command == '':
                        pass
                    else:
                        result, validation = Processor.run_OBD_command(user_command, self.option)
                        if re.search('ERROR', result) or re.search('DATA', result):
                            self.set_logger('ERROR: Wrong command or not supported, type another one')
                        elif re.search('BUSY', result):
                            self.set_logger('ERROR: Bus busy, try again')
                        elif re.search('UNABLE', result):
                            self.set_logger('ERROR: Communication lost, shutting down app!')
                            break
                        else:
                            print result
                except KeyboardInterrupt:
                        break
        self.set_logger(' >>> Expert mode aborted by user, finishing...')
        Processor.run_OBD_command('END', self.option)
        return

    def sampler_mode(self, Processor):
        self.poll_mnemonics, self.poll_commands = self.record.GetOBD_DBInfo(self.option)
        round = 1
        total = len(self.poll_commands)
        available_pids = []
        for i in range(len(self.poll_commands)):
            available_pids.append(1)

        """ Poll every single PID once, then only those wich respond """

        while self.keep_going == True:
            self.set_logger(' > Polling parameters: round %i' %round)
            k = 1
            self.total_steps = len(self.poll_commands)
            for i in range(len(self.poll_commands)):
                self.set_logger(' > Getting OBD polling parameter (%d/%d)...' %(k,total))
                if available_pids[i] == 1:
                    data, validation = Processor.run_OBD_command(self.poll_commands[i], self.option)
                    time.sleep(.1)
                    if re.search('NO DATA',data) or validation == 'N':
                        available_pids[i] = 0
                self.set_progress(i)
                k += 1
            round += 1


def build_logging():

    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

    config = ConfigParser.RawConfigParser()

    if sys.platform == 'win32':
        configfilepath = "karmind.ini"
    else:
        configfilepath=os.environ['HOME']+'/.karmind'
    config.read("karmind.ini")
    logging_level = config.get("logging","level")
    event_log = config.get("logging","event_log")

    if event_log == 'yes':
        LOG_FILENAME = time.strftime("%Y%m%dT%H%M%S.log")
        logging.basicConfig(
            format = '%(asctime)s;%(message)s;%(levelname)s',
            datefmt = '%a %d %b %Y %H:%M:%S',
            filename = LOG_FILENAME,
            filemode = 'a',
            level = LEVELS.get(logging_level, logging.NOTSET)
            )
        f = open(LOG_FILENAME,'a')
        f.write('TIMESTAMP;MESSAGE;LOG_LEVEL\n')
        f.close()
        return True
    else:
        return False


def test(option = '-S'):

    def _test_status_observer(elm):
        print "Status: ", elm.get_status()

    def _test_progress_observer(elm):
        print "Progress: ", elm.get_progress()


    def _test_logger_observer(elm):
        print "App message: ", elm.get_logger()

    build_logging()
    elm = Elm()

    elm.register_observer(_test_status_observer, 'status')
    elm.register_observer(_test_progress_observer, 'progress')
    elm.register_observer(_test_logger_observer, 'logger')

    elm.do_connect()
    elm.do_test(option)
    elm.do_disconnect()

    record = elm.record

    FILENAME = time.strftime("%Y%m%dT%H%M%S_"+option[1]+"_output.csv")
    my_file = open(FILENAME,'w')
    my_file.write('%s;%s;\n' %(record.mode, record.completed))
    for i in record.record:
        my_file.write('%s;%s;%s;%s;\n' %(str(i[0]),str(i[1]),str(i[2]),str(i[3])))
    my_file.close()

    print elm.record.popup_statistics()
    decoder = elm_decoder.ELM_Decoder(record)
    decoder.do_translate_answers()
    print decoder.show_answers_translated()
    print decoder.get_statistics()

if __name__ == '__main__':
    test()