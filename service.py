# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team FunHomeTV (https://funhometv.tv)

import os
import socket
import threading

import xbmc

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
                            threading.Thread(
                                target=oe.openConfigurationWindow).start()
                            log.log("FunHomeTV-settings-run::have winOeMain not visiable, after new thread",log.INFO)
                if message == 'exit':
                    log.log("FunHomeTV-settings-run::receive exit",log.INFO)
                    self.stopped = True
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


class Monitor(xbmc.Monitor):

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
            log.log("FunHomeTV-settings-monitor::enter",log.DEBUG)
            dbus_utils.LOOP_THREAD.start()
            oe.load_modules()
            oe.start_service()
            service_thread = Service_Thread()
            service_thread.start()
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
            if hasattr(oe, 'winOeMain') and hasattr(oe.winOeMain, 'visible'):
                if oe.winOeMain.visible == True:
                    oe.winOeMain.close()
            oe.stop_service()
            service_thread.stop()
            dbus_utils.LOOP_THREAD.stop()
            log.log("FunHomeTV-settings-monitor::exit",log.DEBUG)
        except Exception as e:
            log.log("FunHomeTV-settings-monitor::exception:"+repr(e),log.DEBUG)



if __name__ == '__main__':
    log.log("FunHomeTV-settings-main-monitor::enter",log.DEBUG)
    Monitor().run()
    log.log("FunHomeTV-settings-main-monitor::exit",log.DEBUG)
