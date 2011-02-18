#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Karmind app - Automotive tool based on OBD-II protocol 
#       Check www.karmind.com for further details
#
#       karmind_app.py
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

LICENSE_TEXT = (
"This program is free software; you can redistribute it and/or modify "
"it under the terms of the GNU General Public License as published by "
"the Free Software Foundation; either version 2 of the License, or "
"(at your option) any later version.\n"
"\n"
"This program is distributed in the hope that it will be useful, "
"but WITHOUT ANY WARRANTY; without even the implied warranty of "
"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
"GNU General Public License for more details.\n"
"\n"
"You should have received a copy of the GNU General Public License "
"along with this program; if not, write to the Free Software "
"Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, "
"MA 02110-1301, USA.\n"
)

import os
import thread
import time

#import  wx
import  wx.lib.newevent
from wx.lib.wordwrap import wordwrap

import elm
import elm_decoder

import icon

(UpdateStatusBarEvent, EVT_UPDATE_STATUSBAR) = wx.lib.newevent.NewEvent()
(UpdateGaugeEvent, EVT_UPDATE_GAUGE) = wx.lib.newevent.NewEvent()
(UpdateLogEvent, EVT_UPDATE_LOG) = wx.lib.newevent.NewEvent()
(EndEvent, EVT_END) = wx.lib.newevent.NewEvent()

OPTIONS = [
    ('-C', 'Check'),
    ('-D', 'Clear'),
    ('-S', 'Sampler'),
    #('-E', 'Expert'),
]

ELMCONTROLLER_OK = 0
ELMCONTROLLER_ERROR = 1
ELMCONTROLLER_CONNECTIONERROR = 2
ELMCONTROLLER_OPERATIONERROR = 3

class ElmController:
    def __init__(self, win):
        self.set_option(0)
        self.win = win
        self.running = False
        self.result = {}
        self.elm = elm.Elm()
        self.elm.register_observer(self.refresh_status, 'status')
        self.elm.register_observer(self.refresh_progress, 'progress')
        self.elm.register_observer(self.refresh_log, 'logger')
        self.refresh_status(self.elm)

    def set_option(self, option_id):
        self.option = OPTIONS[option_id][0]

    def get_result(self):
        return self.result

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False
        try:
            self.elm.do_cancel()
        except:
            evt = EndEvent(exit_code = ELMCONTROLLER_ERROR)
            wx.PostEvent(self.win, evt)

    def IsRunning(self):
        return self.running

    def Run(self):
        try:
            self.elm.do_connect()
        except:
            evt = EndEvent(exit_code = ELMCONTROLLER_CONNECTIONERROR)
            wx.PostEvent(self.win, evt)

        try:
            self.elm.do_test(self.option)
        except:
            evt = EndEvent(exit_code = ELMCONTROLLER_OPERATIONERROR)
            wx.PostEvent(self.win, evt)

        self.elm.do_disconnect()

        record = self.elm.record

        decoder = elm_decoder.ELM_Decoder(record)
        #decoder.do_translate_answers() #FIX: Not used now
        self.result = decoder.show_answers_translated()

        self.running = False
        if self.keepGoing == True: # Triggers end event if not cancelled by user...
            evt = EndEvent(exit_code = ELMCONTROLLER_OK)
            wx.PostEvent(self.win, evt)
        elif self.option == '-S':
            evt = EndEvent(exit_code = ELMCONTROLLER_OK) # ... or is sample mode ...
            wx.PostEvent(self.win, evt)
        else:
            evt = EndEvent(exit_code = ELMCONTROLLER_ERROR) # ... ERROR otherwise.
            wx.PostEvent(self.win, evt)


    def refresh_status(self, elm):
        evt = UpdateStatusBarEvent(text = elm.get_status())
        wx.PostEvent(self.win, evt)

    def refresh_progress(self, elm):
        evt = UpdateGaugeEvent(progress = elm.get_progress())
        wx.PostEvent(self.win, evt)

    def refresh_log(self, elm):
        evt = UpdateLogEvent(text = elm.get_logger())
        wx.PostEvent(self.win, evt)

    def save_result(self, path):
        my_file = open(path,'w')
        record = self.elm.record
        my_file.write('%s;%s;\n' %(record.mode, record.completed))
        for i in record.record:
            my_file.write('%s;%s;%s;%s;\n' %(str(i[0]),str(i[1]),str(i[2]),str(i[3])))
        my_file.close()


class Command:
    def __init__(self, frame):
        self.frame = frame
        self()

class RunningCommand(Command):
    def __call__(self):
        self.frame.Gauge.SetValue(0)
        self.frame.SetStatusText('Running')
        self.frame.Button.Disable()
        self.frame.thread.Start()
        self.frame.Button.SetLabel('Stop')
        self.frame.Button.Enable()

class StopCommand(Command):
    def __call__(self):
        self.frame.Button.SetLabel('Start')
        self.frame.Button.Enable()
        self.frame.SetStatusText('Idle')
        self.frame.Gauge.SetValue(0)

class State:
    def __init__(self, frame):
        self.frame = frame
    def start_stop(self):
        pass
    def finish_successfully(self):
        pass
    def finish_errors(self):
        pass

class IdleState(State):
    def start_stop(self):
        RunningCommand(self.frame)
        self.frame.state = self.frame.running_state

class RunningState(State):
    def start_stop(self):
        self.frame.SetStatusText('Stopping...')
        self.frame.Button.Disable()
        self.frame.thread.Stop()
        self.frame.wait_for_threads()
##        self.frame.OnSuccess()
##        StopCommand(self.frame)
##        self.frame.state = self.frame.idle_state

    def finish_successfully(self):
        self.frame.SetStatusText('Finished successfully')
        self.frame.OnSuccess()
        self.frame.SaveAs()
        StopCommand(self.frame)
        self.frame.state = self.frame.idle_state

    def finish_errors(self):
        self.frame.SetStatusText('Finished with errors')
        self.frame.OnError()
        StopCommand(self.frame)
        self.frame.state = self.frame.idle_state



class KarmindFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.idle_state = IdleState(self)
        self.running_state = RunningState(self)
        self.state = self.idle_state

        self.SetIcon(icon.GetIcon())

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        # Build the menu bar
        MenuBar = wx.MenuBar()
        FileMenu = wx.Menu()
        item = FileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, item)
        item2 = FileMenu.Append(wx.ID_ABOUT, text="&About...")
        self.Bind(wx.EVT_MENU, self.OnAbout, item2)
        MenuBar.Append(FileMenu, "&File")
        self.SetMenuBar(MenuBar)

        # Build the status bar
        StatusBar = wx.StatusBar(self)
        self.SetStatusBar(StatusBar)
        self.Bind(EVT_UPDATE_STATUSBAR, self.OnUpdate)

        self.Bind(EVT_END, self.OnEnd)

        #Build the panel
        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        optionsList = []
        for mode, label in OPTIONS:
            optionsList.append(label)


        rb = wx.RadioBox(
                panel, pos=wx.DefaultPosition, size=wx.DefaultSize,
                choices=optionsList, majorDimension=len(optionsList), style=wx.RA_SPECIFY_ROWS
                )
        self.Bind(wx.EVT_RADIOBOX, self.OnOptionSelected, rb)


        self.Button = wx.Button(panel, -1, "Start")
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.Button)

        self.Gauge = wx.Gauge(panel, -1, 100, (110, 50), (-1, 25))
        self.Bind(EVT_UPDATE_GAUGE, self.OnProgress)

        self.Log = wx.TextCtrl(panel, -1, size=(255, 100),
                              style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        self.Bind(EVT_UPDATE_LOG, self.OnLog)


        hbox.Add((50, 0), 0)
        hbox.Add(rb, wx.ALIGN_CENTRE)
        hbox.Add((50, 0), 0)
        hbox.Add(self.Button, 0, wx.ALIGN_CENTRE)
        hbox.Add((50, 0), 0)

        vbox.Add((0, 50), 0)
        #~ vbox.Add(rb, 0, wx.ALIGN_CENTRE)
        #~ vbox.Add(self.Button, 0, wx.ALIGN_CENTRE)
        vbox.Add(hbox, 0, wx.ALIGN_CENTRE)
        vbox.Add((0, 50), 0)
        vbox.Add(self.Gauge, 0, wx.ALIGN_CENTRE)
        vbox.Add((0, 50), 0)
        vbox.Add(self.Log, 0, wx.ALIGN_CENTRE)
        vbox.Add((0, 50), 0)

        panel.SetSizer(vbox)
        vbox.Fit(panel)



        self.Fit()

        self.thread = ElmController(self)

        # Add the Widget Panel

    def OnEnd(self, evt):
        exit_code = evt.exit_code
        if exit_code == ELMCONTROLLER_OK:
            self.state.finish_successfully()
        else:
            self.state.finish_errors()


    def OnOptionSelected(self, event):
        option_id = event.GetInt()
        self.thread.set_option(option_id)

    def OnProgress(self, evt):
        self.Gauge.SetValue(evt.progress)

    def OnUpdate(self, evt):
        self.SetStatusText("%s"%(evt.text))

    def OnLog(self, evt):
        self.Log.AppendText(evt.text + '\n')

    def OnButton(self, evt):
        self.state.start_stop()
##        self.thread.Start()
##        self.Button.Disable()

    def wait_for_threads(self):
        running = 1
        while running:
            running = 0
            running = self.thread.IsRunning()
            time.sleep(0.3)

    def OnCloseWindow(self, evt):
        wx.BusyInfo("One moment please, waiting for device")
        wx.Yield()
        self.thread.Stop()
        self.wait_for_threads()
        #~ for t in self.threads:
            #~ t.Stop()
        self.Destroy()

    def OnSuccess(self):
        dlg = wx.MessageDialog(self, self.thread.elm.record.popup_statistics(),
                               'Finished',
                               wx.OK | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()

    def SaveAs(self):
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(),
            defaultFile="", wildcard="All files (*.*)|*.*", style=wx.SAVE
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.thread.save_result(path)
        dlg.Destroy()

    def OnError(self):
        dlg = wx.MessageDialog(self, 'Error',
                               'Finished',
                               wx.OK | wx.ICON_ERROR
                               )
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, evt):
        info = wx.AboutDialogInfo()
        info.Name = "karmind app"
        info.Version = "1.0.0"
        info.Copyright = "(C) 2011 karmind.com"
        info.Description = wordwrap(
            "The karmind application is the ELM327 interface "
            "developed to generate files in order to be imported "
            "on karmind.com's site.",
            350, wx.ClientDC(self))
        info.WebSite = (
            "http://www.karmind.com/about.html?app",
            "http://www.karmind.com"
        )
        info.License = LICENSE_TEXT #wordwrap(LICENSE_TEXT, 500, wx.ClientDC(self))
        wx.AboutBox(info)



class KarmindApp(wx.App):
    def OnInit(self):
        frame = KarmindFrame(None, -1, 'Karmind app')
        frame.Show(True)
        return True


if __name__ == '__main__':
    elm.build_logging()
    app = KarmindApp(0)
    app.MainLoop()
