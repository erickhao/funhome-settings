# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team FunHomeTV (https://funhometv.tv)

import os
import socket
import threading

import xbmc
import time

import syspath
import dbus_utils
import log
import oe


class Service_Thread(threading.Thread):

    SOCKET = '/var/run/service.funhometv.settings.sock'

    def __init__(self):
        threading.Thread.__init__(self)
        self.init()

    @log.log_function()
    def init(self):
        try:
            log.log("FunHomeTV-settings-init::enter",log.INFO)
            if os.path.exists(self.SOCKET):
                os.remove(self.SOCKET)
            self.daemon = True
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.setblocking(1)
            self.sock.bind(self.SOCKET)
            self.sock.listen(1)
            self.stopped = False
            log.log("FunHomeTV-settings-init::exit after listen",log.INFO)
        except Exception as e:
            log.log("FunHomeTV-settings-init::except :"+repr(e),log.INFO)


    @log.log_function()
    def run(self):
        log.log(f'FunHomeTV-settings-run::enter', log.INFO)
        if oe.read_setting('funhometv', 'wizard_completed') == None:
            log.log("FunHomeTV-settings-run::wizard not completed , new thread to start wizard",log.INFO)
            threading.Thread(target=oe.openWizard).start()
        while self.stopped == False:
            try:
                log.log(f'FunHomeTV-settings-run::Waiting-notstoped', log.INFO)
                conn, addr = self.sock.accept()
                message = (conn.recv(1024)).decode('utf-8')
                conn.close()
                log.log(f'FunHomeTV-settings-run::Received {message}', log.INFO)
                if message == 'openConfigurationWindow':
                    if not hasattr(oe, 'winOeMain'):
                        log.log("FunHomeTV-settings-run::no winOeMain , new thread to start",log.INFO)
                        threading.Thread(target=oe.openConfigurationWindow).start()
                        log.log("FunHomeTV-settings-run::no winOeMain , after thread start",log.INFO)
                    else:
                        log.log("FunHomeTV-settings-run::have winOeMain ",log.INFO)
                        if oe.winOeMain.visible != True:
                            log.log("FunHomeTV-settings-run::have winOeMain not visiable, start new thread",log.INFO)
                            threading.Thread(target=oe.openConfigurationWindow).start()
                            log.log("FunHomeTV-settings-run::have winOeMain not visiable, after new thread",log.INFO)
                        else:
                            log.log("FunHomeTV-settings-run::maybe something wrong,still want open configuration windows with it visible?",log.INFO)
                elif message == 'exit':
                    log.log("FunHomeTV-settings-run::receive exit",log.INFO)
                    self.stopped = True
                elif message == 'certapplied':   #in reloadcmd add a message send .
                    log.log("FunHomeTV-settings-run::receive message certapplied", log.INFO)
                    threading.Thread(target=oe.certapplied).start()
                    log.log("FunHomeTV-settings-run::after new thread of certapplied", log.INFO)
                elif message == 'mounted':  #in vm , user specify the shared folder , and we mounted the folder for nextcloud or immich.
                    log.log("FunHomeTV-settings-run::receive message mounted", log.INFO)
                    threading.Thread(target=oe.foldermounted).start()
                    log.log("FunHomeTV-settings-run::after start thread foldermounted", log.INFO)

                log.log("FunHomeTV-settings-run::in loop-waiting",log.INFO)
            except Exception as e:
                log.log("FunHomeTV-settings-run::except:"+repr(e),log.DEBUG)

        log.log("FunHomeTV-settings-run::exit run",log.INFO)


    @log.log_function()
    def stop(self):
        try:
            log.log("FunHomeTV-settings-stop::enter",log.DEBUG)
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.SOCKET)
            sock.send(bytes('exit', 'utf-8'))
            sock.close()
            self.join()
            self.sock.close()
            log.log("FunHomeTV-settings-stop::exit",log.DEBUG)
        except Exception as e:
            log.log("FunHomeTV-settings-stop::except:"+repr(e),log.DEBUG)

class ztstatus_thread(threading.Thread):

    def __init__(self, oeMain):
        try:
            oeMain.dbg_log('ztstatus::__init__', 'enter_function', 4)
            self.oe = oeMain
            self.stopped = False
            threading.Thread.__init__(self)
            self.daemon = True
            self.oe.dbg_log('ztstatus::__init__', 'exit_function', 4)
        except Exception as e:
            self.oe.dbg_log('ztstatus::__init__', 'ERROR: (' + repr(e) + ')')

    def stop(self):
        try:
            self.oe.dbg_log('ztstatus::stop', 'enter_function', 0)
            self.stopped = True
            self.oe.dbg_log('ztstatus::stop', 'exit_function', 0)
        except Exception as e:
            self.oe.dbg_log('ztstatus::stop', 'ERROR: (' + repr(e) + ')')

    def run(self):
        try:
            self.oe.dbg_log('ztstatus::run', 'enter_function', 0)
            while self.stopped == False:
                self.oe.dbg_log('ztstatus::run', 'call ztStatusRefresh', 1)
                threading.Thread(target=self.oe.ztStatusRefresh).start()
                self.oe.dbg_log('ztstatus::run', 'start sleep 60 seconds' , 1)
                sleepcount = 0
                while self.stopped == False and sleepcount < 60:
                    time.sleep(1)
                    sleepcount = sleepcount + 1
                    if(sleepcount % 10 == 0):   
                        threading.Thread(target=self.oe.check_host_share).start()
            self.oe.dbg_log('ztstatus::run', 'exit_function', 0)
        except Exception as e:
            self.oe.dbg_log('ztstatus::run', 'ERROR: (' + repr(e) + ')')
        



class bMonitor(xbmc.Monitor):

    @log.log_function()
    def onScreensaverActivated(self):
        if oe.read_setting('bluetooth', 'standby'):
            threading.Thread(target=oe.standby_devices).start()

    @log.log_function()
    def onDPMSActivated(self):
        if oe.read_setting('bluetooth', 'standby'):
            threading.Thread(target=oe.standby_devices).start()

    @log.log_function()
    def run(self):
        try:
            while not self.abortRequested():
                if self.waitForAbort(60):
                    break
                if not oe.read_setting('bluetooth', 'standby'):
                    continue
                timeout = oe.read_setting('bluetooth', 'idle_timeout')
                if not timeout:
                    continue
                try:
                    timeout = int(timeout)
                except:
                    continue
                if timeout < 1:
                    continue
                if xbmc.getGlobalIdleTime() / 60 >= timeout:
                    log.log(f'Idle timeout reached', log.DEBUG)
                    oe.standby_devices()
        except Exception as e:
            log.log("FunHomeTV-settings-monitor::exception:"+repr(e),log.DEBUG)



if __name__ == '__main__':
    log.log("FunHomeTV-settings-main-monitor::enter",log.DEBUG)
    #        log.log("FunHomeTV-settings-monitor::enter",log.DEBUG)
    
    oe.__oe__.dbg_log('FUNHOMETV service.py 1/6', 'ready to dbusthreadstart load-modules and start_service and monitor start', 0)

    dbus_utils.LOOP_THREAD.start()
    oe.load_modules()
    oe.__oe__.dbg_log('FUNHOMETV service.py 2/6', 'after load_modules', 0)
    oe.start_service()
    oe.__oe__.dbg_log('FUNHOMETV service.py 3/6', 'after start_service,next bmonitor construct and xbmcm.run with service_thread', 0)
    service_thread = Service_Thread()
    service_thread.start()

    #add a zerotier monitor thread for refresh every minute
    ztmonitor = ztstatus_thread(oe.__oe__)
    ztmonitor.start()

    oe.__oe__.dbg_log('FUNHOMETV service.py 4/6','after start ztstatus',0)
    xbmcm = bMonitor()
    xbmcm.run()
    #oe.__oe__.dbg_log('service.py 3.5/5', 'after xbmcm.run--bMonitor run,next xbmcm.waitForAbort', 0)
    #xbmcm.start()
    #xbmcm.waitForAbort()



    oe.__oe__.dbg_log('FUNHOMETV service.py 5/6', 'after xbmcm.waitForAbort aka. xbmcm.run', 0)
    if hasattr(oe, 'winOeMain') and hasattr(oe.winOeMain, 'visible'):
        if oe.winOeMain.visible == True:
            oe.winOeMain.close()

    ztmonitor.stop()
    oe.stop_service()
    service_thread.stop()
    dbus_utils.LOOP_THREAD.stop()
    log.log("FUNHOMETV service.py 6/6  main-thread end",log.DEBUG)

    log.log("FunHomeTV-settings-main-monitor::exit",log.DEBUG)
