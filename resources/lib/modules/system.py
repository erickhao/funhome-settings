# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team FunHomeTV (https://libreelec.tv)

import glob
import os
import re
import subprocess
import tarfile
from xml.dom import minidom

import xbmc
import xbmcgui
import json
import hostname
import log
import modules
import oe
import oeWindows
import shutil
import urllib.request, urllib.error, urllib.parse
from datetime import datetime
import base64


from faker import Faker
fake = Faker()

import socket

def get_ip_address():
 ip_address = ''
 s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 s.connect(("www.taobao.com",80))
 ip_address = s.getsockname()[0]
 s.close()
 return str(ip_address)

xbmcDialog = xbmcgui.Dialog()

class system(modules.Module):

    ENABLED = False
    KERNEL_CMD = None
    XBMC_RESET_FILE = None
    FUNHOMETV_RESET_FILE = None
    KEYBOARD_INFO = None
    UDEV_KEYBOARD_INFO = None
    NOX_KEYBOARD_INFO = None
    BACKUP_DIRS = None
    BACKUP_FILTER = None
    BACKUP_DESTINATION = None
    RESTORE_DIR = None
    SET_CLOCK_CMD = None
    JOURNALD_CONFIG_FILE = None
    menu = {'1': {
        'name': 32002,	  #32002 #msgid "System"
        'menuLoader': 'load_menu',
        'listTyp': 'list',
        'InfoText': 700,   #700 #msgid "Configure a hostname, keyboard type, perform a reset, update, or backups and restores"
        }}

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.keyboard_layouts = False
        self.nox_keyboard_layouts = False
        self.backup_dlg = None
        self.backup_file = None
        self.total_backup_size = 0
        self.done_backup_size = 0
        self.arrVariants = {}
        self.struct = {
            'ident': {
                'order': 1,
                'name': 32189,           #32189 #msgid "Identification"
                'settings': {
                    'hostname': {
                        'order': 1,
                        'name': 32190,   #32190 #msgid "System Name"
                        'value': '',
                        'action': 'set_hostname',
                        'type': 'text',
                        'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$',
                        'InfoText': 710,   #710 #msgid "Configure the Hostname of your @DISTRONAME@ system. This will be used for the HTPC \\hostname in Windows and SMB server name in the Mac OS Finder"
                        },
                    'ipaddress': {
                        'order': 2,
                        'name': 32568 , #32568 need insert "IP address"ok
                        'value':'',
                        'action':'nonce',
                        'type':'text',
                        'InfoText': 32569    #32569 need insert "IPv4 address to contact the device"
                        },
                    'hostname6': {
                        'order': 3,
                        'name': 32570,   #32570 #msgid "System IPv6 Name"ok
                        'value': '',
                        'action': 'nonce',
                        'type': 'text',
                        'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$',
                        'InfoText': 32571,   #32571 #msgid "Hostname of your device only for IPv6."
                        },
                    'ip6address': {
                        'order': 4,
                        'name': 32572 , #32572 need insert "IPv6 address"
                        'value':'',
                        'action':'nonce',
                        'type':'text',
                        'InfoText': 32573     #32573 need insert "IPv6 address to contact the device"ok
                        },
                    'dnsreg':{
                        'order': 5,
                        'name': 32595 , #32595  "Domain Name Service Registered :"
                        'value':'',
                        'action':'nonce',
                        'type':'text',
                        'InfoText': 32592 ,   #32592  msgid "Whether Domain Name Service(DNS) have registered "
                        },
                    'certificatesupplier':{
                        'order': 6,
                        'name': 32594 , #32594 "Certificate Apply from :"
                        'value':'',
                        'action':'certificatesupplier',
                        'type':'textTriggerButton',
                        'InfoText': 32591 ,   #32591  msgid "Certificate supplier , press to switch from the 2 supplier"
                        },
                    'certificateapplydone':{
                        'order': 7,
                        'name': 32593 , #32593 msgid "Certificate Applied :"
                        'value':'',
                        'action':'nonce',
                        'type':'text',
                        'InfoText': 32590 ,   #32590  msgid "Whether the host certificate have applied ."
                        },
                    'displaynextcloudentry':{
                        'order': 8,
                        'name': 36602 , #36602  need msgid "Display Nextcloud link QRCode"
                        'value':'',
                        'action':'displaynextcloudentry',
                        'type':'button',
                        'InfoText': 36603 ,   #36603  msgid "Display the host's Nextcloud QRCode for mobile client to link with ."
                        },
                    'displayapplylog':{
                        'order': 9,
                        'name': 36604 , #36604  need msgid "Display certificate apply log"
                        'value':'',
                        'action':'displayapplylog',
                        'type':'button',
                        'InfoText': 36605 ,   #36605  msgid "Display the log of certificate apply to debug ."
                        },

                },	
		    },
            'keyboard': {
                'order': 2,
                'name': 32009,
                'settings': {
                    'KeyboardLayout1': {
                        'order': 1,
                        'name': 32010,
                        'value': 'us',
                        'action': 'set_keyboard_layout',
                        'type': 'multivalue',
                        'values': [],
                        'InfoText': 711,
                        },
                    'KeyboardVariant1': {
                        'order': 2,
                        'name': 32386,
                        'value': '',
                        'action': 'set_keyboard_layout',
                        'type': 'multivalue',
                        'values': [],
                        'InfoText': 753,
                        },
                    'KeyboardLayout2': {
                        'order': 3,
                        'name': 32010,
                        'value': 'us',
                        'action': 'set_keyboard_layout',
                        'type': 'multivalue',
                        'values': [],
                        'InfoText': 712,
                        },
                    'KeyboardVariant2': {
                        'order': 4,
                        'name': 32387,
                        'value': '',
                        'action': 'set_keyboard_layout',
                        'type': 'multivalue',
                        'values': [],
                        'InfoText': 754,
                        },
                    'KeyboardType': {
                        'order': 5,
                        'name': 32330,
                        'value': 'pc105',
                        'action': 'set_keyboard_layout',
                        'type': 'multivalue',
                        'values': [],
                        'InfoText': 713,
                        },
                    },
                },
            'pinlock': {
                'order': 3,
                'name': 32192,
                'settings': {
                    'pinlock_enable': {
                        'order': 1,
                        'name': 32193,
                        'value': '0',
                        'action': 'init_pinlock',
                        'type': 'bool',
                        'InfoText': 747,
                        },
                    'pinlock_pin': {
                        'order': 2,
                        'name': 32194,
                        'value': '',
                        'action': 'set_pinlock',
                        'type': 'button',
                        'InfoText': 748,
                        'parent': {
                            'entry': 'pinlock_enable',
                            'value': ['1'],
                            },
                        },
                    },
                },

            'backup': {
                'order': 7,
                'name': 32371,
                'settings': {
                    'backup': {
                        'name': 32372,
                        'value': '0',
                        'action': 'do_backup',
                        'type': 'button',
                        'InfoText': 722,
                        'order': 1,
                        },
                    'restore': {
                        'name': 32373,
                        'value': '0',
                        'action': 'do_restore',
                        'type': 'button',
                        'InfoText': 723,
                        'order': 2,
                        },
                    },
                },
            'reset': {
                'order': 8,
                'name': 32323,
                'settings': {
                    'xbmc_reset': {
                        'name': 32324,
                        'value': '0',
                        'action': 'reset_soft',
                        'type': 'button',
                        'InfoText': 724,
                        'order': 1,
                        },
                    'oe_reset': {
                        'name': 32325,
                        'value': '0',
                        'action': 'reset_hard',
                        'type': 'button',
                        'InfoText': 725,
                        'order': 2,
                        },
                    },
                },
            'debug': {
                'order': 9,
                'name': 32376,
                'settings': {
                    'paste_system': {
                        'name': 32377,
                        'value': '0',
                        'action': 'do_send_system_logs',
                        'type': 'button',
                        'InfoText': 718,
                        'order': 1,
                        },
                    'paste_crash': {
                        'name': 32378,
                        'value': '0',
                        'action': 'do_send_crash_logs',
                        'type': 'button',
                        'InfoText': 719,
                        'order': 2,
                        },
                    },
                },
            'journal': {
                'order': 10,
                'name': 32410,
                'settings': {
                    'journal_persistent': {
                        'order': 1,
                        'name': 32411,
                        'value': '0',
                        'action': 'do_journald',
                        'type': 'bool',
                        'InfoText': 32412,
                    },
                    'journal_size': {
                        'order': 2,
                        'name': 32413,
                        'value': '30 MiB',
                        'action': 'do_journald',
                        'type': 'multivalue',
                        'values': [
                            '30 MiB', '60 MiB', '100 MiB',
                            '150 MiB', '200 MiB', '300 MiB'
                        ],
                        'InfoText': 32414,
                        'parent': {
                            'entry': 'journal_persistent',
                            'value': ['1'],
                        },
                    },
                    'journal_rate_limit': {
                        'order': 2,
                        'name': 32415,
                        'value': '1',
                        'action': 'do_journald',
                        'type': 'bool',
                        'InfoText': 32416,
                        'parent': {
                            'entry': 'journal_persistent',
                            'value': ['1'],
                        },
                    },
                },
            },
        }

    @log.log_function()
    def start_service(self):
        self.is_service = True
        self.load_values()
        self.set_hostname()
        self.set_keyboard_layout()
        self.set_hw_clock()
        del self.is_service

    @log.log_function()
    def stop_service(self):
        if hasattr(self, 'update_thread'):
            self.update_thread.stop()

    @log.log_function()
    def load_values(self):
        # Keyboard Layout
        (
            arrLayouts,
            arrTypes,
            self.arrVariants,
            ) = self.get_keyboard_layouts()
        if not arrTypes is None:
            self.struct['keyboard']['settings']['KeyboardType']['values'] = arrTypes
            value = oe.read_setting('system', 'KeyboardType')
            if not value is None:
                self.struct['keyboard']['settings']['KeyboardType']['value'] = value
        if not arrLayouts is None:
            self.struct['keyboard']['settings']['KeyboardLayout1']['values'] = arrLayouts
            self.struct['keyboard']['settings']['KeyboardLayout2']['values'] = arrLayouts
            value = oe.read_setting('system', 'KeyboardLayout1')
            if not value is None:
                self.struct['keyboard']['settings']['KeyboardLayout1']['value'] = value
            value = oe.read_setting('system', 'KeyboardVariant1')
            if not value is None:
                self.struct['keyboard']['settings']['KeyboardVariant1']['value'] = value
            value = oe.read_setting('system', 'KeyboardLayout2')
            if not value is None:
                self.struct['keyboard']['settings']['KeyboardLayout2']['value'] = value
            value = oe.read_setting('system', 'KeyboardVariant2')
            if not value is None:
                self.struct['keyboard']['settings']['KeyboardVariant2']['value'] = value
            if not arrTypes == None:
                self.keyboard_layouts = True
        if not os.path.exists('/usr/bin/setxkbmap'):
            self.struct['keyboard']['settings']['KeyboardLayout2']['hidden'] = 'true'
            self.struct['keyboard']['settings']['KeyboardType']['hidden'] = 'true'
            self.struct['keyboard']['settings']['KeyboardVariant1']['hidden'] = 'true'
            self.struct['keyboard']['settings']['KeyboardVariant2']['hidden'] = 'true'
            self.nox_keyboard_layouts = True

        # Hostname 
        value = oe.read_setting('system', 'hostname')
        if not value is None:
            self.struct['ident']['settings']['hostname']['value'] = value
            oe.hostname_2_funhomenic = value
            oe.hostname6_2_funhomenic = value.split('.')[0].lower() + '6.funhome.tv'
        else:
            hostname_gen = fake.first_name().lower() 
            #date_s = (datetime.now().strftime('%Y%m%d%H%M%S%f'))
            nows=datetime.now()
            #nows=datetime(2182,7,10)
            t2002=datetime(2002,7,10)
            td =nows-t2002
            #print("td:"+ repr(td) +". td.totalseconds:"+ repr(td.total_seconds()))
            intse=td.total_seconds()*1000000
            #print ("total seconds in interge :"+repr(intse))
            ints=int(intse)
            strname=base64.b32encode(ints.to_bytes(8,byteorder='big'))
            #print("base32 in big is ",strname)
            strname1=strname[1:13].decode().lower()
            #print("we may use :",strname1)
            #print("hostname is :",hostname_gen+'-'+strname1+'.funhome.tv')
            oe.hostname_gen = hostname_gen+'-'+strname1
            #+ '-' + fake.first_name().encode('ascii').lower()
            oe.hostname_2_funhomenic = oe.hostname_gen + '.funhome.tv'
            oe.hostname6_2_funhomenic = oe.hostname_gen + '6.funhome.tv'
            self.struct['ident']['settings']['hostname']['value'] = oe.hostname_2_funhomenic
            #in order to avoid user accept the suggest and not set host name in wizard , and go over the wizard , but it it not recorded in settings. so we record it, for next reboot use . 
            oe.write_setting('system', 'hostname', self.struct['ident']['settings']['hostname']['value']) 
            
        #for display
        self.struct['ident']['settings']['hostname6']['value'] = oe.hostname6_2_funhomenic
        #get ip address and as if ipaddress from connman , because no matter wifi or ethernet, can be connected is needed.
        oe.ipv4address_local = get_ip_address()
        if (oe.ipaddress_from_zerotier == None):
            oe.ipv4address_2_funhomenic = oe.ipv4address_local
            oe.ipaddress_from_connman = True
        
        #get hostname for dns serial and ip address of the lasttime
        oe.last_hostname = oe.read_setting('system', 'last_hostname')
        oe.last_hostname6 = oe.read_setting('system', 'last_hostname6')            
        oe.last_ipv4a = oe.read_setting('system', 'last_ipv4a')
        oe.last_ipv6aaaa = oe.read_setting('system', 'last_ipv6aaaa')
        oe.funhomenic_serial = oe.read_setting('system', 'funhomenic_serial')
        #oe.write_setting('system', 'funhomenic_serial', oe.funhomenic_serial)

        ########### certificate supplier
        value = oe.read_setting('system', 'issuer_set')
        if not value is None:
            self.struct['ident']['settings']['certificatesupplier']['value'] = value
        else:
            self.struct['ident']['settings']['certificatesupplier']['value'] = "Let's Encrypt"
            #recorded in settings
            oe.write_setting('system', 'issuer_set', self.struct['ident']['settings']['certificatesupplier']['value']) 
        ### end of certificate supplier
        self.check_current_apply_status()

        ##### we use generated or user inputed . the default hostname should not used if only internet connection is ok.
        #self.struct['ident']['settings']['hostname']['value'] = hostname.get_hostname() 
        
        # PIN Lock
        self.struct['pinlock']['settings']['pinlock_enable']['value'] = '1' if oe.PIN.isEnabled() else '0'

        # Journal
        self.get_setting('journal', 'journal_persistent')
        self.get_setting('journal', 'journal_size')
        self.get_setting('journal', 'journal_rate_limit')

    @log.log_function()
    def load_menu(self, focusItem):
        oe.winOeMain.build_menu(self.struct)

    def get_setting(self, group, setting, allowEmpty=False):
        value = oe.read_setting('system', setting)
        if not value is None and not (allowEmpty == False and value == ''):
            self.struct[group]['settings'][setting]['value'] = value

    @log.log_function()
    def set_value(self, listItem):
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        oe.write_setting('system', listItem.getProperty('entry'), str(listItem.getProperty('value')))

    @log.log_function()
    def set_keyboard_layout(self, listItem=None):
        if not listItem == None:
            if listItem.getProperty('entry') == 'KeyboardLayout1':
                if self.struct['keyboard']['settings']['KeyboardLayout1']['value'] != listItem.getProperty('value'):
                    self.struct['keyboard']['settings']['KeyboardVariant1']['value'] = ''
            if listItem.getProperty('entry') == 'KeyboardLayout2':
                if self.struct['keyboard']['settings']['KeyboardLayout2']['value'] != listItem.getProperty('value'):
                    self.struct['keyboard']['settings']['KeyboardVariant2']['value'] = ''
            self.set_value(listItem)
        if self.keyboard_layouts == True:
            self.struct['keyboard']['settings']['KeyboardVariant1']['values'] = self.arrVariants[self.struct['keyboard']['settings'
                    ]['KeyboardLayout1']['value']]
            self.struct['keyboard']['settings']['KeyboardVariant2']['values'] = self.arrVariants[self.struct['keyboard']['settings'
                    ]['KeyboardLayout2']['value']]
            log.log(str(self.struct['keyboard']['settings']['KeyboardLayout1']['value']) + ','
                            + str(self.struct['keyboard']['settings']['KeyboardLayout2']['value']) + ' ' + '-model '
                            + str(self.struct['keyboard']['settings']['KeyboardType']['value']), log.INFO)
            if not os.path.exists(os.path.dirname(self.UDEV_KEYBOARD_INFO)):
                os.makedirs(os.path.dirname(self.UDEV_KEYBOARD_INFO))
            config_file = open(self.UDEV_KEYBOARD_INFO, 'w')
            config_file.write(f"XKBMODEL=\"{self.struct['keyboard']['settings']['KeyboardType']['value']}\"\n")
            config_file.write(f"XKBVARIANT=\"{self.struct['keyboard']['settings']['KeyboardVariant1']['value']}, \
                                             {self.struct['keyboard']['settings']['KeyboardVariant2']['value']}\"\n")
            config_file.write(f"XKBLAYOUT=\"{self.struct['keyboard']['settings']['KeyboardLayout1']['value']}, {self.struct['keyboard']['settings']['KeyboardLayout2']['value']}\"\n")
            config_file.write('XKBOPTIONS="grp:alt_shift_toggle"\n')
            config_file.close()
            parameters = [
                '-display ' + os.environ['DISPLAY'],
                '-layout ' + self.struct['keyboard']['settings']['KeyboardLayout1']['value'] + ',' + self.struct['keyboard']['settings'
                        ]['KeyboardLayout2']['value'],
                '-variant ' + self.struct['keyboard']['settings']['KeyboardVariant1']['value'] + ',' + self.struct['keyboard']['settings'
                        ]['KeyboardVariant2']['value'],
                '-model ' + str(self.struct['keyboard']['settings']['KeyboardType']['value']),
                '-option "grp:alt_shift_toggle"',
                ]
            oe.execute('setxkbmap ' + ' '.join(parameters))
        elif self.nox_keyboard_layouts == True:
            log.log(str(self.struct['keyboard']['settings']['KeyboardLayout1']['value']), log.INFO)
            parameter = self.struct['keyboard']['settings']['KeyboardLayout1']['value']
            command = f'loadkmap < `ls -1 {self.NOX_KEYBOARD_INFO}/*/{parameter}.bmap`'
            log.log(command, log.INFO)
            oe.execute(command)

    @log.log_function()
    def set_hostname(self, listItem=None):          #need check funhomenic() 
        if listItem is not None:
            self.set_value(listItem)
        value = self.struct['ident']['settings']['hostname']['value']
        if value is not None and value != '':
            hostname.set_hostname(value)

            #ready for nic
            oe.hostname_2_funhomenic = value
            #hostname6_2_funhomenic should be a first part of hostname_2_funhomenic  and add '6.funhome.tv' 
            oe.hostname6_2_funhomenic = value.split('.')[0].lower().strip() + '6.funhome.tv' 
            #for display
            self.struct['ident']['settings']['hostname6']['value'] = value

            #let funhomenic decide when to real update nic
            #need : 1 postreg ok , so that we get machine-id
            #       2 name defined (or random generated, user accept), here funhomenic post to nic
            #       3 acme.sh to apply certificate .
            self.funhomenic()

            #new name with new cert ; when not real update nic , new cert is gened.
            #self.gen_cert()
            #should restart apache. ; and restarted.
            #oe.execute('systemctl restart apache2')


    @log.log_function()
    def get_keyboard_layouts(self):
        arrLayouts = []
        arrVariants = {}
        arrTypes = []
        if os.path.exists(self.NOX_KEYBOARD_INFO):
            for layout in glob.glob(f'{self.NOX_KEYBOARD_INFO}/*/*.bmap'):
                if os.path.isfile(layout):
                    arrLayouts.append(layout.split('/')[-1].split('.')[0])
            arrLayouts.sort()
            arrTypes = None
        elif os.path.exists(self.KEYBOARD_INFO):
            objXmlFile = open(self.KEYBOARD_INFO, 'r', encoding='utf-8')
            strXmlText = objXmlFile.read()
            objXmlFile.close()
            xml_conf = minidom.parseString(strXmlText)
            for xml_layout in xml_conf.getElementsByTagName('layout'):
                for subnode_1 in xml_layout.childNodes:
                    if subnode_1.nodeName == 'configItem':
                        for subnode_2 in subnode_1.childNodes:
                            if subnode_2.nodeName == 'name':
                                if hasattr(subnode_2.firstChild, 'nodeValue'):
                                    value = subnode_2.firstChild.nodeValue
                            if subnode_2.nodeName == 'description':
                                if hasattr(subnode_2.firstChild, 'nodeValue'):
                                    arrLayouts.append(subnode_2.firstChild.nodeValue + ':' + value)
                    if subnode_1.nodeName == 'variantList':
                        arrVariants[value] = [':']
                        for subnode_vl in subnode_1.childNodes:
                            if subnode_vl.nodeName == 'variant':
                                for subnode_v in subnode_vl.childNodes:
                                    if subnode_v.nodeName == 'configItem':
                                        for subnode_ci in subnode_v.childNodes:
                                            if subnode_ci.nodeName == 'name':
                                                if hasattr(subnode_ci.firstChild, 'nodeValue'):
                                                    vvalue = subnode_ci.firstChild.nodeValue.replace(',', '')
                                            if subnode_ci.nodeName == 'description':
                                                if hasattr(subnode_ci.firstChild, 'nodeValue'):
                                                    try:
                                                        arrVariants[value].append(subnode_ci.firstChild.nodeValue + ':' + vvalue)
                                                    except:
                                                        pass
            for xml_layout in xml_conf.getElementsByTagName('model'):
                for subnode_1 in xml_layout.childNodes:
                    if subnode_1.nodeName == 'configItem':
                        for subnode_2 in subnode_1.childNodes:
                            if subnode_2.nodeName == 'name':
                                if hasattr(subnode_2.firstChild, 'nodeValue'):
                                    value = subnode_2.firstChild.nodeValue
                            if subnode_2.nodeName == 'description':
                                if hasattr(subnode_2.firstChild, 'nodeValue'):
                                    arrTypes.append(subnode_2.firstChild.nodeValue + ':' + value)
            arrLayouts.sort()
            arrTypes.sort()
        else:
            log.log('No keyboard layouts found)')
            return (None, None, None)
        return (
            arrLayouts,
            arrTypes,
            arrVariants,
            )

    @log.log_function()
    def set_hw_clock(self):
        oe.execute(f'{self.SET_CLOCK_CMD} 2>/dev/null')

    @log.log_function()
    def reset_soft(self, listItem=None):
        if self.ask_sure_reset('Soft') == 1:
            open(self.XBMC_RESET_FILE, 'a').close()
            oe.winOeMain.close()
            oe.xbmcm.waitForAbort(1)
            subprocess.call(['/usr/bin/systemctl', '--no-block', 'reboot'], close_fds=True)

    @log.log_function()
    def reset_hard(self, listItem=None):
        if self.ask_sure_reset('Hard') == 1:
            open(self.FUNHOMETV_RESET_FILE, 'a').close()
            oe.winOeMain.close()
            oe.xbmcm.waitForAbort(1)
            subprocess.call(['/usr/bin/systemctl', '--no-block', 'reboot'], close_fds=True)

    @log.log_function()
    def ask_sure_reset(self, part):
        answer = xbmcDialog.yesno(f'{part} Reset', f'{oe._(32326)}\n\n{oe._(32328)}')   #32326 #msgid "Are you sure?"   #32328 #msgid "The system must reboot."
        if answer == 1:
            if oe.reboot_counter(30, oe._(32323)) == 1:    #32323 #msgid "Reset to Defaults"
                return 1
            else:
                return 0

    @log.log_function()
    def do_backup(self, listItem=None):
        try:
            self.total_backup_size = 1
            self.done_backup_size = 1
            try:
                for directory in self.BACKUP_DIRS:
                    self.get_folder_size(directory)
                log.log(f'Uncompressed backup size: {self.total_backup_size}', log.DEBUG)
            except:
                pass
            bckDir = xbmcDialog.browse( 0,
                                        oe._(32371),    #32371 #msgid "Backup"
                                        'files',
                                        '',
                                        False,
                                        False,
                                        self.BACKUP_DESTINATION )
            log.log(f'Directory for backup: {bckDir}', log.INFO)

            if bckDir and os.path.exists(bckDir):
                # free space check
                try:
                    folder_stat = os.statvfs(bckDir)
                    free_space = folder_stat.f_frsize * folder_stat.f_bavail
                    log.log(f'Available free space for backup: {free_space}', log.DEBUG)
                    if self.total_backup_size > free_space:
                        txt = oe.split_dialog_text(oe._(32379))     #32379 #msgid "There is not enough free storage space to continue!"
                        answer = xbmcDialog.ok('Backup', f'{txt[0]}\n{txt[1]}\n{txt[2]}')
                        return 0
                except:
                    log.log('Unable to determine free space available for backup.', log.DEBUG)
                    pass
                self.backup_dlg = xbmcgui.DialogProgress()
                self.backup_dlg.create('FunHomeTV', oe._(32375))   #32375 #msgid "Backup Progress"
                if not os.path.exists(self.BACKUP_DESTINATION):
                    os.makedirs(self.BACKUP_DESTINATION)
                self.backup_file = f'{oe.timestamp()}.tar'
                log.log(f'Backup file: {bckDir + self.backup_file}', log.INFO)
                tar = tarfile.open(bckDir + self.backup_file, 'w', format=tarfile.GNU_FORMAT)
                for directory in self.BACKUP_DIRS:
                    self.tar_add_folder(tar, directory)
                    if self.backup_dlg is None or self.backup_dlg.iscanceled():
                        break
                tar.close()
                if self.backup_dlg is None or self.backup_dlg.iscanceled():
                    try:
                        os.remove(self.BACKUP_DESTINATION + self.backup_file)
                    except:
                        pass
                else:
                    self.backup_dlg.update(100, oe._(32401))
                os.sync()
        finally:
            # possibly already closed by tar_add_folder if an error occurred
            try:
                self.backup_dlg.close()
            except:
                pass
            self.backup_dlg = None

    @log.log_function()
    def do_restore(self, listItem=None):
            copy_success = 0
            restore_file_path = xbmcDialog.browse( 1,
                                                   oe._(32373),   #32373 #msgid "Restore Backup"
                                                   'files',
                                                   '??????????????.tar',
                                                   False,
                                                   False,
                                                   self.BACKUP_DESTINATION )
            # Do nothing if the dialog is cancelled - path will be the backup destination
            if not os.path.isfile(restore_file_path):
                return
            log.log(f'Restore file: {restore_file_path}', log.INFO)
            restore_file_name = restore_file_path.split('/')[-1]
            if os.path.exists(self.RESTORE_DIR):
                oe.execute(f'rm -rf {self.RESTORE_DIR}')
            os.makedirs(self.RESTORE_DIR)
            folder_stat = os.statvfs(self.RESTORE_DIR)
            file_size = os.path.getsize(restore_file_path)
            free_space = folder_stat.f_frsize * folder_stat.f_bavail
            if free_space > file_size * 2:
                if os.path.exists(self.RESTORE_DIR + restore_file_name):
                    os.remove(self.RESTORE_DIR + restore_file_name)
                if oe.copy_file(restore_file_path, self.RESTORE_DIR + restore_file_name) != None:
                    copy_success = 1
                    log.log('Restore file successfully copied.', log.INFO)
                else:
                    log.log(f'Failed to copy restore file to: {self.RESTORE_DIR}', log.ERROR)
                    oe.execute(f'rm -rf {self.RESTORE_DIR}')
            else:
                txt = oe.split_dialog_text(oe._(32379))   #32379 #msgid "There is not enough free storage space to continue!" 
                answer = xbmcDialog.ok('Restore', f'{txt[0]}\n{txt[1]}\n{txt[2]}')
            if copy_success == 1:
                txt = oe.split_dialog_text(oe._(32380))   #32380 #msgid "Restoring system settings requires a reboot. Are you sure you want to restore?"
                answer = xbmcDialog.yesno('Restore', f'{txt[0]}\n{txt[1]}\n{txt[2]}')
                if answer == 1:
                    if oe.reboot_counter(10, oe._(32371)) == 1:     #32371 #msgid "Backup"
                        oe.winOeMain.close()
                        oe.xbmcm.waitForAbort(1)
                        subprocess.call(['/usr/bin/systemctl', '--no-block', 'reboot'], close_fds=True)
                else:
                    log.log('User Abort!')
                    oe.execute(f'rm -rf {self.RESTORE_DIR}')

    @log.log_function()
    def do_send_system_logs(self, listItem=None):
        self.do_send_logs('/usr/bin/pastekodi')

    @log.log_function()
    def do_send_crash_logs(self, listItem=None):
        self.do_send_logs('/usr/bin/pastecrash')

    @log.log_function()
    def do_send_logs(self, log_cmd):
        paste_dlg = xbmcgui.DialogProgress()
        paste_dlg.create('Pasting log files', 'Pasting...')
        result = oe.execute(log_cmd, get_result=1)
        if not paste_dlg.iscanceled():
            paste_dlg.close()
            link = result.find('http')
            if link != -1:
                log.log(result[link:], log.WARNING)
                xbmcDialog.ok('Paste complete', f'Log files pasted to {result[link:]}')
            else:
                xbmcDialog.ok('Failed paste', 'Failed to paste log files, try again')

    @log.log_function()
    def tar_add_folder(self, tar, folder):
        try:
            print_folder = log.asciify(folder)
            for item in os.listdir(folder):
                if item == self.backup_file:
                    continue
                if self.backup_dlg.iscanceled():
                    return
                itempath = os.path.join(folder, item)
                if itempath in self.BACKUP_FILTER:
                    continue
                elif os.path.islink(itempath):
                    tar.add(itempath)
                elif os.path.ismount(itempath):
                    tar.add(itempath, recursive=False)
                elif os.path.isdir(itempath):
                    if os.listdir(itempath) == []:
                        tar.add(itempath)
                    else:
                        self.tar_add_folder(tar, itempath)
                        if self.backup_dlg is None:
                            return
                else:
                    self.done_backup_size += os.path.getsize(itempath)
                    log.log(f'Adding to backup: {log.asciify(itempath)}', log.DEBUG)
                    tar.add(itempath)
                    if hasattr(self, 'backup_dlg'):
                        progress = round(1.0 * self.done_backup_size / self.total_backup_size * 100)
                        self.backup_dlg.update(int(progress), f'{print_folder}\n{log.asciify(item)}')
        except:
            self.backup_dlg.close()
            self.backup_dlg = None
            xbmcDialog.ok(oe._(32371), oe._(32402))
            raise

    @log.log_function()
    def get_folder_size(self, folder):
        for item in os.listdir(folder):
            itempath = os.path.join(folder, item)
            if itempath in self.BACKUP_FILTER or os.path.islink(itempath):
                continue
            elif os.path.isfile(itempath):
                self.total_backup_size += os.path.getsize(itempath)
            elif os.path.ismount(itempath):
                continue
            elif os.path.isdir(itempath):
                self.get_folder_size(itempath)

    @log.log_function()
    def init_pinlock(self, listItem=None):
        if not listItem == None:
            self.set_value(listItem)
        if self.struct['pinlock']['settings']['pinlock_enable']['value'] == '1':
            oe.PIN.enable()
        else:
            oe.PIN.disable()
        if oe.PIN.isEnabled() and oe.PIN.isSet() == False:
            self.set_pinlock()

    @log.log_function()
    def set_pinlock(self, listItem=None):
        newpin = xbmcDialog.input(oe._(32226), type=xbmcgui.INPUT_NUMERIC)
        if len(newpin) == 4 :
           newpinConfirm = xbmcDialog.input(oe._(32227), type=xbmcgui.INPUT_NUMERIC)
           if newpin != newpinConfirm:
               xbmcDialog.ok(oe._(32228), oe._(32229))
           else:
               oe.PIN.set(newpin)
               xbmcDialog.ok(oe._(32230), f'{oe._(32231)}\n\n{newpin}')
        else:
            xbmcDialog.ok(oe._(32232), oe._(32229))
        if oe.PIN.isSet() == False:
            self.struct['pinlock']['settings']['pinlock_enable']['value'] = '0'
            oe.PIN.disable()

    @log.log_function()
    def do_journald(self, listItem=None):
        if not listItem == None:
            self.set_value(listItem)
            if self.struct['journal']['settings']['journal_persistent']['value'] == '0':
                try:
                    os.remove(self.JOURNALD_CONFIG_FILE)
                except:
                    pass
            else:
                config_file = open(self.JOURNALD_CONFIG_FILE, 'w')
                config_file.write("# SPDX-License-Identifier: GPL-2.0-or-later\n" +
                                  "# Copyright (C) 2021-present Team FunHomeTV (https://libreelec.tv)\n\n" +
                                  "# This file is generated automatically, don't modify.\n\n" +
                                  "[Journal]\n")

                size = self.struct['journal']['settings']['journal_size']['value'].replace(' MiB', 'M')
                config_file.write(f"SystemMaxUse={size}\n" +
                                  "MaxRetentionSec=0\n")
                if self.struct['journal']['settings']['journal_rate_limit']['value'] == '1':
                    config_file.write("RateLimitInterval=0\n" +
                                      "RateLimitBurst=0\n")
                config_file.close()

    @log.log_function()
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32003))   #32003 #msgid "Interface"
        oe.winOeMain.set_wizard_text(oe._(32304))   #32304 #msgid "To be identified easily on the network, your new @DISTRONAME@ machine needs a name.[CR][CR]Try to choose something meaningful - like the room it's in - so you'll know what it is when you see it on the network.[CR][CR]This name is used when configuring network services, like file sharing using samba."
        oe.winOeMain.set_wizard_button_title(oe._(32308))   #32308 #msgid "Hostname:"
        oe.winOeMain.set_wizard_button_1(self.struct['ident']['settings']['hostname']['value'], self, 'wizard_set_hostname')

    @log.log_function()
    def wizard_set_hostname(self):
        currentHostname = self.struct['ident']['settings']['hostname']['value']
        #make user don't need to input or modify the '.funhome.tv' part.
        if(currentHostname[-11:]== '.funhome.tv'):
            userInputHostname = currentHostname.split('.')[0]
        else:
            userInputHostname = currentHostname
        xbmcKeyboard = xbmc.Keyboard(userInputHostname)
        result_is_valid = False
        while not result_is_valid:
            xbmcKeyboard.doModal()
            if xbmcKeyboard.isConfirmed():
                result_is_valid = True
                validate_string = self.struct['ident']['settings']['hostname']['validate']
                if validate_string != '':
                    if not re.search(validate_string, xbmcKeyboard.getText()):
                            result_is_valid = False
                            oe.notify('Hostname Input','invalid host name')
                            continue
                    oe.hostname_2_funhomenic = xbmcKeyboard.getText().lower().strip() + '.funhome.tv'
                    if(oe.hostname_2_funhomenic[-11:]!= '.funhome.tv'):
                        result_is_valid = False
                        continue
                    else :
                        #should be hostname first part + '6.funhome.tv'
                        oe.hostname6_2_funhomenic = oe.hostname_2_funhomenic.split('.')[0].lower().strip()+ '6.funhome.tv'
                    #hostname should ok 
                    if self.funhomenic() is None:
                        result_is_valid = False
            else:
                result_is_valid = True
        if xbmcKeyboard.isConfirmed():
            self.struct['ident']['settings']['hostname']['value'] = oe.hostname_2_funhomenic
            self.set_hostname()
            oe.winOeMain.getControl(1401).setLabel(self.struct['ident']['settings']['hostname']['value'])
            oe.write_setting('system', 'hostname', self.struct['ident']['settings']['hostname']['value'])    



            
#######################            
####### until end , just copied from early work, need check.
    @log.log_function()
    def gen_cert(self):   #old one , generate selfsigned certificate.
            certret = oe.execute('/usr/bin/make-tls-cert generate-default-snakeoil 2>/dev/null', get_result=1)    
    
    @log.log_function()
    def funhomenic(self):
        oe.dbg_log('system::funhomenic ipv4-ipv6-name-name6:',repr(oe.ipv4address_2_funhomenic) + '-' + repr(oe.ipv6address_2_funhomenic) + '-' +  repr(oe.hostname_2_funhomenic) + '-' + repr(oe.hostname6_2_funhomenic), log.DEBUG)
        if(not self.need_funhomenic()):
            oe.dbg_log('system::funhomenic',' not need funhomenic,exit_function', log.DEBUG)
            return
        oe.dbg_log('system::funhomenic','need funhomenic', log.DEBUG)




        if oe.ipv4address_2_funhomenic == None:
                oe.ipv4address_2_funhomenic = '0.0.0.0'
        if oe.ipv6address_2_funhomenic == None:
                oe.ipv6address_2_funhomenic = '0::1'

        #for display name6 and ipaddress(4/6)
        self.struct['ident']['settings']['hostname6']['value'] = oe.hostname6_2_funhomenic
        self.struct['ident']['settings']['ip6address']['value'] = oe.ipv6address_2_funhomenic
        self.struct['ident']['settings']['ipaddress']['value'] = oe.ipv4address_2_funhomenic



        #setup machineid for nic 
        # if postreg.py make the work , the .flagreg should exist , and contains machineid for funhometv
        # let just assume /etc/machine-id exists, if not , it's postreg's work to create one.
        
        #it should not , if really do , just put in logs -- if there is NO internet access and file NOT exist , we should create , and prompt user.

        #cmdgetmid="openssl dgst -sha3-256 /etc/machine-id"
        #dgst = subprocess.Popen([cmdgetmid], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, #stderr=subprocess.PIPE)
        #readout1 = dgst.stdout.readline()
        #dgstpart = readout1.split(" ")[-1]
        if (len(oe.MACHINEID)==0):
            #try to postreg.py first , if still wrong , then return.
            oe.dbg_log('system::funhomenic',' NO MACHINEID ,We try to reg', log.DEBUG)
            cmdpostreg="/usr/bin/python2 /usr/bin/postreg.py"
            readout2 = subprocess.Popen([cmdpostreg], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            readout2out=readout2.stdout.read()
            readout2err=readout2.stderr.read()
            if os.path.exists(oe.flagreg):
                with open(oe.flagreg,'r') as flagregh:
                    content=flagregh.read()
                jc = json.loads(content)
                if ((jc['StatusCode'] == '200') and (not (len(jc['id']) == 0))):
                    oe.FACTORY_STATUS = 'OK'
                    oe.MACHINEID = jc['id']
                else:
                    oe.dbg_log('system::funhomenic',' NO MACHINEID tryed ,but still no id ,exit_function', log.INFO)
                    return
            else:
                oe.dbg_log('system::funhomenic',' NO MACHINEID try , get:out:'+ repr(readout2out) +' err:' + repr(readout2err), log.INFO)
        
        oe.dbg_log('system::funhomenic','MACHINEID '+repr(oe.MACHINEID), log.DEBUG)
        if(len(oe.MACHINEID)==0):
            return
        if(oe.ENV_DEVELOPMENT):
            nicurl="https://reg.com.funhome.tv/devnic"
        else:
            nicurl="https://reg.com.funhome.tv/nic"            
        urldatastr = "machineid=%s&a=%s&name=%s&aaaa=%s&name6=%s" %( 
            urllib.parse.quote(oe.MACHINEID) ,
            urllib.parse.quote(oe.ipv4address_2_funhomenic),
            urllib.parse.quote(oe.hostname_2_funhomenic),
            urllib.parse.quote(oe.ipv6address_2_funhomenic),
            urllib.parse.quote(oe.hostname6_2_funhomenic)
        )
        oe.dbg_log('system::funhomenic','nicurl:'+nicurl+',urldatastr:'+urldatastr, log.DEBUG)
        try:
            response = urllib.request.urlopen(nicurl,urldatastr.encode('utf-8'))
            content = response.read()
        except Exception as e:
            oe.dbg_log('system::funhomenic', 'ERROR: (' + repr(e) + ')')

        #in order to archive HA effect , here should make some work for try at least 3 time.
        jc=json.loads(content)
        oe.dbg_log('system::funhomenic', 'jc:' + repr(jc) , 0)
        if jc['StatusCode'] == '200':
            #record the changes
            oe.last_hostname = oe.hostname_2_funhomenic
            oe.last_hostname6 = oe.hostname6_2_funhomenic
            oe.last_ipv4a = oe.ipv4address_2_funhomenic
            oe.last_ipv6aaaa  = oe.ipv6address_2_funhomenic

            #get certificate and setup apache2
            #can be done after the wizard , and report 
            #because that user maybe need to select and test the name several time
            # or start a thread of apply ceriticate , report when finished.
            oe.write_setting('system', 'last_hostname', str(oe.last_hostname))
            oe.write_setting('system', 'last_hostname6', str(oe.last_hostname6))
            oe.write_setting('system', 'last_ipv4a', str(oe.last_ipv4a))
            oe.write_setting('system', 'last_ipv6aaaa', str(oe.last_ipv6aaaa))
            oe.write_setting('system', 'funhomenic_serial', str(oe.funhomenic_serial))

            self.struct['ident']['settings']['dnsreg']['value']= oe._(32334)   #32334" msgid "Yes"

            oe.notify(oe._(32600),oe.hostname_2_funhomenic) # need insert 32600#'funhometvnic OK ' ok

            self.certapply()            

            return "OK"
        else :
            self.struct['ident']['settings']['dnsreg']['value']= oe._(32335)   #32335" msgid "No"
            oe.notify(oe._(32601),oe.hostname_2_funhomenic + '; '+ jc['Message']) # need insert 32601#'funhometvnic Failed' ok
            return None


    @log.log_function()
    def update_system_address(self):
        self.struct['ident']['settings']['ip6address']['value'] = oe.ipv6address_2_funhomenic
        self.struct['ident']['settings']['ipaddress']['value'] = oe.ipv4address_2_funhomenic
        #check if it is needed to update address in dns
        self.funhomenic()


    @log.log_function()
    def need_funhomenic(self):
        oe.dbg_log('system::need_funhomenic,serial:',repr(oe.funhomenic_serial), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,from_connman:',repr(oe.ipaddress_from_connman), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,from_zerotier',repr(oe.ipaddress_from_zerotier), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,ipv4address_2_funhomenic',repr(oe.ipv4address_2_funhomenic), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,hostname_2_funhomenic',repr(oe.hostname_2_funhomenic), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,ipv6address_2_funhomenic',repr(oe.ipv6address_2_funhomenic), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,hostname6_2_funhomenic',repr(oe.hostname6_2_funhomenic), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,last_ipv4a',repr(oe.last_ipv4a), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,last_hostname',repr(oe.last_hostname), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,last_ipv6aaaa',repr(oe.last_ipv6aaaa), log.DEBUG)
        oe.dbg_log('system::need_funhomenic,last_hostname6',repr(oe.last_hostname6), log.DEBUG)
        if oe.funhomenic_serial == None:
            oe.funhomenic_serial = 0
        if( oe.ipaddress_from_connman == None and oe.ipaddress_from_zerotier == None):
            #oe.funhomenic_serial = oe.funhomenic_serial + 1
            oe.dbg_log('system::need_funhomenic',' neither connman nor zerotier set address, not needed,serial:' + repr(oe.funhomenic_serial) + ',exit_function', log.INFO)
            return (False)
        #no address , update next
        if (oe.ipv4address_2_funhomenic == None):
            oe.dbg_log('system::need_funhomenic','no address exit_function', log.DEBUG)
            return(False)
        if oe.funhomenic_serial == 0:
            oe.dbg_log('system::need_funhomenic','first needed exit_function', log.DEBUG)
            oe.funhomenic_serial = 1
            return(True)
        if ((oe.last_hostname == oe.hostname_2_funhomenic) and (oe.last_hostname6 == oe.hostname6_2_funhomenic) and (oe.last_ipv4a == oe.ipv4address_2_funhomenic) and (oe.last_ipv6aaaa  == oe.ipv6address_2_funhomenic)):
            oe.dbg_log('system::need_funhomenic','allsame ,not need ,exit_function', log.DEBUG)
            return(False)
        else:
            oe.funhomenic_serial = int(oe.funhomenic_serial) + 1
            oe.dbg_log('system::need_funhomenic','needed, serial:'+repr(oe.funhomenic_serial)+',exit_function', log.DEBUG)
            return(True)


    @log.log_function()
    def certificatesupplier(self,listItem=None):
        try:
            #Before apply certificate , we should collect user email , register to certificate account , and set the issuer . Once set , it should not changed in lifecycle.
            oe.dbg_log('system::certificatesupplier','enter')
            self.current_set=oe.read_setting('system','issuer_set')
            if(self.current_set == None) or ((self.current_set!="Let's Encrypt") and (self.current_set!="ZeroSSL")):
                set_issuer_cmd="/storage/.acme.sh/acme.sh --set-default-ca --server letsencrypt"
                cmdresult=subprocess.Popen([set_issuer_cmd],shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmdout=cmdresult.stdout.read()
                oe.dbg_log('system::certapply', 'set issuer cmd:'+set_issuer_cmd+' out:' + repr(cmdout) , log.DEBUG)
                oe.write_setting('system','issuer_set',"Let's Encrypt")
                self.struct['ident']['settings']['certificatesupplier']['value']= "Let's Encrypt"
            
            elif(self.current_set == "Let's Encrypt"):
                set_issuer_cmd="/storage/.acme.sh/acme.sh --set-default-ca --server zerossl"
                cmdresult=subprocess.Popen([set_issuer_cmd],shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmdout=cmdresult.stdout.read()
                oe.dbg_log('system::certapply', 'set issuer cmd:'+set_issuer_cmd+' out:' + repr(cmdout) , log.DEBUG)
                oe.write_setting('system','issuer_set',"ZeroSSL")
                self.struct['ident']['settings']['certificatesupplier']['value']= "ZeroSSL"
                oe.notify("FunHomeTV" , oe._(36600)) # need insert 36600#'Switched to ZeroSSL' ｏｋ

            elif(self.current_set == "ZeroSSL"):
                set_issuer_cmd="/storage/.acme.sh/acme.sh --set-default-ca --server letsencrypt"
                cmdresult=subprocess.Popen([set_issuer_cmd],shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmdout=cmdresult.stdout.read()
                oe.dbg_log('system::certapply', 'set issuer cmd:'+set_issuer_cmd+' out:' + repr(cmdout) , log.DEBUG)
                oe.write_setting('system','issuer_set',"Let's Encrypt")
                self.struct['ident']['settings']['certificatesupplier']['value']= "Let's Encrypt"
                oe.notify("FunHomeTV" , oe._(36601)) # need insert 36601#'Switched to Let's Encrypt'  OK
            oe.dbg_log('system::certificatesupplier','leave')                
        except Exception as e:
                oe.dbg_log('system::certificatesupplier', 'ERROR: (' + repr(e) + ')')

           
            



    @log.log_function()
    def certapply(self):
        try:
            oe.dbg_log('system::certapply','enter')
            #check if acme.sh exist
            if (not os.path.exists("/storage/.acme.sh/acme.sh")):
                oe.dbg_log('system::certapply','no acme.sh , need wait', log.ERROR)
                return
            oe.dbg_log('system::certapply','acme.sh exist.', log.DEBUG)

            #check current apply status
            apply_status = "/storage/.kodi/apache/apply_status"
            if os.path.exists(apply_status):
                with open(apply_status,'r') as ash:
                    fcont=ash.read()
                jc2=json.loads(fcont)
                ash.close()
                if (jc2['status']=='Complete'):
                    oe.dbg_log('system::certapply','already applied')
                    self.struct['ident']['settings']['certificateapplydone']['value']= oe._(32334)   #32334" msgid "Yes"
                    return

            #Before apply certificate , we should collect user email , register to certificate account , and set the issuer . Once set , it should not changed in lifecycle.
            if(oe.read_setting('system','issuer_set') == None):
                set_issuer_cmd="/storage/.acme.sh/acme.sh --set-default-ca --server letsencrypt"
                cmdresult=subprocess.Popen([set_issuer_cmd],shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmdout=cmdresult.stdout.read()
                oe.dbg_log('system::certapply', 'set issuer cmd:'+set_issuer_cmd+' out:' + repr(cmdout) , log.DEBUG)
                oe.write_setting('system','issuer_set','True')

            # email 
            if(oe.read_setting('system','account_set') == None):
                set_account_cmd="/storage/.acme.sh/acme.sh --register-account -m my@aol.com"
                cmdresult=subprocess.Popen([set_account_cmd],shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cmdout=cmdresult.stdout.read()
                oe.dbg_log('system::certapply', 'set account cmd:'+set_account_cmd+' out:' + repr(cmdout) , log.DEBUG)
                oe.write_setting('system','account_set','True')
                
            #2022/12/06 about the apply cert . first set a state of start applying 
            cert_apply_status={"status":"Start"}
            json.dump(cert_apply_status,fp=open("/storage/.kodi/apache/apply_status",'w'),indent=4)

            #here we should apply certificate and restart apache2
            #call acme.sh --issue -d last_hostname --dnsapi funhometv 
            cmdapplycert = "PDD_Token=\"" + oe.MACHINEID + "\" /storage/.acme.sh/acme.sh --issue -d " + oe.last_hostname + " --dns dns_funhometv --key-file /storage/.kodi/apache/etc/ssl/private/ssl-cert-snakeoil.key --fullchain-file /storage/.kodi/apache/etc/ssl/certs/ssl-cert-snakeoil.pem --reloadcmd /storage/.kodi/apache/reloadcmd.sh  --debug 3 > /storage/.kodi/apache/certapplylog.txt 2>&1 "
            #when acme.sh finished , store certificate and restart apache2 and tell user to scan the address with qrcode  to link with nextcloud client . This action is performed by a service in background , when ready display the qrcode to user. 
            
            oe.dbg_log('system::certapply', 'cmdapplycert:' + repr(cmdapplycert) , log.DEBUG)
            cmdresult=subprocess.Popen([cmdapplycert], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cmdout = cmdresult.stdout.read()
            oe.dbg_log('system::certapply', 'cmdapplycert out:' + repr(cmdout) , log.DEBUG)
            #when reloadcmd.sh is run , apache server should reload , and the user interface should get the message(a service is waiting , and get the result , ready to display the progress to user) and display qrcode to user  , for user to scan and link nextcloud client .
            # 2022/12/06 about the apply cert .second in reloadcmd.sh set the state to finished of apply, and generate image for user to scan.
            # 2022/12/06 about the apply cert .third  in funhome.tv.settings , we inspect the first and second step setup state, and display to user. 
            #check current apply status
            self.check_current_apply_status()
            oe.dbg_log('system::certapply','leave')

        except Exception as e:
                oe.dbg_log('system::certapply', 'ERROR: (' + repr(e) + ')')


    @log.log_function()
    def displaynextcloudentry(self,listItem=None):
        try:
            oe.dbg_log('system::displaynextcloudentry','enter')
            if(self.struct['ident']['settings']['certificateapplydone']['value']== oe._(32334)):   #32334" msgid "Yes"
                oe.dictModules['services'].nextcloud_link()
            oe.dbg_log('system::displaynextcloudentry','leave')

        except Exception as e:
            oe.dbg_log('system::displaynextcloudentry', 'ERROR: (' + repr(e) + ')')

    @log.log_function()   
    def check_current_apply_status(self):
        try:
            oe.dbg_log('system::check_current_apply_status','enter')
            apply_status = "/storage/.kodi/apache/apply_status"
            self.struct['ident']['settings']['certificateapplydone']['value']= oe._(32335)   #32335" msgid "No"
            if os.path.exists(apply_status):
                with open(apply_status,'r') as ash:
                    fcont=ash.read()
                jc2=json.loads(fcont)
                ash.close()
                if (jc2['status']=='Complete'):
                    oe.dbg_log('system::certapply','applied success')
                    self.struct['ident']['settings']['certificateapplydone']['value']= oe._(32334)   #32334" msgid "Yes"
                else:
                    oe.dbg_log('system::certapply','applied should start')
                    #self.struct['ident']['settings']['certificateapplydone']['value']= oe._(32335)   #32335" msgid "No"
            oe.dbg_log('system::check_current_apply_status','leave')
        except Exception as e:
            oe.dbg_log('system::check_current_apply_status', 'ERROR: (' + repr(e) + ')')


    @log.log_function()
    def displayapplylog(self,listItem=None):
        try:
            log_to_view= "/storage/.kodi/apache/certapplylog.txt"
            if os.path.exists(log_to_view):
                oe.navigation.run(True)
            else:
                oe.notify("FunHomeTV" , oe._(36606)) # need insert 36606#'The certificate apply log file is not exist.'  OK

        except Exception as e:
            oe.dbg_log('system::displayapplylog', 'ERROR: (' + repr(e) + ')')

           