# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import os
import subprocess

import xbmc
import xbmcgui
import json
import re

import log
import modules
import oe
import qrcode

xbmcDialog = xbmcgui.Dialog()

import pyxbmct

# Create a class for our UI
class QRWin(pyxbmct.AddonDialogWindow):

    def __init__(self, title='', img = None , textContent1 ='' , textContent2 = '', textContent3 = ''):
        """Class constructor"""
        # Call the base class' constructor.
        super(QRWin, self).__init__(title)
        # Set width, height and the grid parameters
        self.setGeometry(912, 684, 16, 16)
        # Call set controls method
        self.image = img
        self.text1 = textContent1
        self.text2 = textContent2
        self.text3 = textContent3
        self.set_controls()
        # Call set navigation method.
        self.set_navigation()
        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_controls(self):
        """Set up UI controls"""
        # Image control
        pimage = pyxbmct.Image(self.image)
        self.placeControl(pimage, 0, 4, rowspan=8, columnspan=8)
        # Text label1
        label1 = pyxbmct.Label(self.text1)
        self.placeControl(label1, 8, 0, rowspan=2, columnspan=16)
        # Text label2
        label2 = pyxbmct.Label(self.text2)
        self.placeControl(label2, 10, 0, rowspan=2, columnspan=16)
        # Text label3
        label3 = pyxbmct.Label(self.text3)
        self.placeControl(label3, 12, 0, rowspan=2, columnspan=16)
        #self.placeControl(self.name_field, 3, 1)
        # Close button
        self.close_button = pyxbmct.Button('OK')
        self.placeControl(self.close_button, 14, 6, rowspan=2, columnspan=4)
        # Connect close button
        self.connect(self.close_button, self.close)
        # Hello button.
        #self.hello_buton = pyxbmct.Button('Hello')
        #self.placeControl(self.hello_buton, 4, 1)
        # Connect Hello button.
        #self.connect(self.hello_buton, lambda:
            #xbmc.executebuiltin('Notification(Hello {0}!, Welcome to PyXBMCt.)'.format(
               #self.name_field.getText())))

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        # Note there is a new feature:
        # if you instead write self.autoNavigation() PyXBMCT will set up
        # the navigation between the controls for you automatically!
        #self.name_field.controlUp(self.hello_buton)
        #self.name_field.controlDown(self.hello_buton)
        #self.close_button.controlLeft(self.hello_buton)
        #self.close_button.controlRight(self.hello_buton)
        #self.hello_buton.setNavigation(self.name_field, self.name_field, self.close_button, self.close_button)
        # Set initial focus.
        self.setFocus(self.close_button)




class services(modules.Module):

    ENABLED = False
    SAMBA_NMDB = None
    SAMBA_SMDB = None
    D_SAMBA_SECURE = None
    D_SAMBA_WORKGROUP = None
    D_SAMBA_USERNAME = None
    D_SAMBA_PASSWORD = None
    D_SAMBA_MINPROTOCOL = None
    D_SAMBA_MAXPROTOCOL = None
    D_SAMBA_AUTOSHARE = None
    KERNEL_CMD = None
    SSH_DAEMON = None
    D_SSH_DISABLE_PW_AUTH = None
    OPT_SSH_NOPASSWD = None
    AVAHI_DAEMON = None
    CRON_DAEMON = None
    ZEROTIER_DAEMON = None   #we added haoyq
    NEXTCLOUD_MARIADB = None
    NEXTCLOUD_APACHE2 = None
    NEXTCLOUD_PHP_FPM = None
    TRANSMISSION = None    
    menu = {'4': {
        'name': 32001,     #32001 #msgid "Services"
        'menuLoader': 'load_menu',
        'listTyp': 'list',
        'InfoText': 703,   #703 #msgid "Configure system services like Samba, SSH, Cron, Avahi and Syslog" need insert string.po add zerotier,nextcloud , transmission
        }}

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.struct = {
            'samba': {
                'order': 4,
                'name': 32200,  #32200 #msgid "Samba"
                'not_supported': [],
                'settings': {
                    'samba_autostart': {
                        'order': 1,
                        'name': 32204,   #32204 #msgid "Enable Samba"
                        'value': None,
                        'action': 'initialize_samba',
                        'type': 'bool',
                        'InfoText': 738,   #738 #msgid "Set to ON to enable the embedded Samba (SMB) filesharing service"
                        },
                    'samba_workgroup': {
                        'order': 2,
                        'name': 32215,  #32215 #msgid "Workgroup name"
                        'value': "WORKGROUP",
                        'action': 'initialize_samba',
                        'type': 'text',
                        'parent': {
                            'entry': 'samba_autostart',
                            'value': ['1'],
                            },
                        'InfoText': 758,  #758 #msgid "NetBIOS group to which the server belongs. Default is WORKGROUP."
                        },
                    'samba_secure': {
                        'order': 3,
                        'name': 32202,  #32202 #msgid "Use Samba Password Authentication"
                        'value': None,
                        'action': 'initialize_samba',
                        'type': 'bool',
                        'parent': {
                            'entry': 'samba_autostart',
                            'value': ['1'],
                            },
                        'InfoText': 739,  #739 #msgid "Set to ON to require username/password access to local Samba fileshares"
                        },
                    'samba_username': {
                        'order': 4,
                        'name': 32106,  #32106 #msgid "Username"
                        'value': None,
                        'action': 'initialize_samba',
                        'type': 'text',
                        'parent': {
                            'entry': 'samba_secure',
                            'value': ['1'],
                            },
                        'InfoText': 740,  #740 #msgid "Set the username for Samba sharing"
                        },
                    'samba_password': {
                        'order': 5,
                        'name': 32107,   #32107 #msgid "Passphrase"
                        'value': None,
                        'action': 'initialize_samba',
                        'type': 'text',
                        'parent': {
                            'entry': 'samba_secure',
                            'value': ['1'],
                            },
                        'InfoText': 741,  #741 #msgid "Set the password for Samba sharing"
                        },
                    'samba_minprotocol': {
                        'order': 6,
                        'name': 32217,   #32217 #msgid "Minimum supported protocol"
                        'value': 'SMB2',
                        'action': 'initialize_samba',
                        'type': 'multivalue',
                        'values': [
                            'SMB1',
                            'SMB2',
                            'SMB3',
                            ],
                        'parent': {
                            'entry': 'samba_autostart',
                            'value': ['1'],
                            },
                        'InfoText': 756,  #756 #msgid "Disable older SMB protocols by specifying the minimum supported protocol."
                        },
                    'samba_maxprotocol': {
                        'order': 7,
                        'name': 32218,  #32218 #msgid "Maximum supported protocol"
                        'value': 'SMB3',
                        'action': 'initialize_samba',
                        'type': 'multivalue',
                        'values': [
                            'SMB1',
                            'SMB2',
                            'SMB3',
                            ],
                        'parent': {
                            'entry': 'samba_autostart',
                            'value': ['1'],
                            },
                        'InfoText': 757,  #757 #msgid "Disable more recent SMB protocols for backward compatability with legacy clients."
                        },
                    'samba_autoshare': {
                        'order': 8,
                        'name': 32216,   #32216 #msgid "Auto-Share External Drives"
                        'value': None,
                        'action': 'initialize_samba',
                        'type': 'bool',
                        'parent': {
                            'entry': 'samba_autostart',
                            'value': ['1'],
                            },
                        'InfoText': 755,  #755 #msgid "Auto share external drives / partitions"
                        },
                    },
                },
            'ssh': {
                'order': 3,
                'name': 32201,   #32201 #msgid "SSH"
                'not_supported': [],
                'settings': {
                    'ssh_autostart': {
                        'order': 1,
                        'name': 32205,   #32205 #msgid "Enable SSH"
                        'value': None,
                        'action': 'initialize_ssh',
                        'type': 'bool',
                        'InfoText': 742,  #742 #msgid "Set to ON to enable the embedded SSH server. The SSH console can be accessed with username 'root' and password '@ROOT_PASSWORD@'."
                        }, 
                    'ssh_secure': {
                        'order': 2,
                        'name': 32203,  #32203 #msgid "Disable SSH Password"
                        'value': None,
                        'action': 'initialize_ssh',
                        'type': 'bool',
                        'parent': {
                            'entry': 'ssh_autostart',
                            'value': ['1'],
                            },
                        'InfoText': 743,    #743 #msgid "Set to ON if you have copied private SSH keys to your HTPC and would like to improve security by disabling SSH username and password authentication."
                        },
                    'ssh_passwd': {
                        'order': 3,
                        'name': 32209,   #32209 #msgid "SSH Password"
                        'value': None,
                        'action': 'do_sshpasswd',
                        'type': 'button',
                        'parent': {
                            'entry': 'ssh_secure',
                            'value': ['0'],
                            },
                        'InfoText': 746,  #746 #msgid "Set the password for SSH"
                        },
                    },
                },
            'avahi': {
                'order': 5,
                'name': 32207,  #32207 #msgid "Avahi"
                'not_supported': [],
                'settings': {'avahi_autostart': {
                    'order': 1,
                    'name': 32206,  #32206 #msgid "Enable Avahi (Zeroconf)"
                    'value': None,
                    'action': 'initialize_avahi',
                    'type': 'bool',
                    'InfoText': 744,  #744 #msgid "Set to ON to enable the Avahi (Zeroconf/Bonjour) network discovery service"
                    }},
                },
            'cron': {
                'order': 6,
                'name': 32319,   #32319 #msgid "Cron"
                'not_supported': [],
                'settings': {'cron_autostart': {
                    'order': 1,
                    'name': 32320,  #32320 #msgid "Enable Cron"
                    'value': None,
                    'action': 'initialize_cron',
                    'type': 'bool',
                    'InfoText': 745,      #745 #msgid "Set to ON to enable the cron daemon"
                    }},
                },
            'nextcloud': {  #combind mariadb and apache2, even php-fpm
                    'order': 1,
                    'name': 32430,  #need insert string.po "Nextcloud "ok
                    'not_supported': [],
                    'settings': {
                        'nextcloud_autostart': {
                            'order': 1,
                            'name': 32431,   #need insert string.po 32331 #msgid "Enable cloud"ok
                            'value': None,
                            'action': 'initialize_nextcloud',
                            'type': 'bool',
                            'InfoText': 970,   #need insert 970 #msgid "Set to ON to enable the nextcloud needed mariadb/apache2/php-fpm daemon, and Use address to access it -- https://[funhometv-box-ip]; if disabled , users will not able to access the nextcloud service."ok
                            },
                        },
                    },
                #'nextcloud_apache2': {
                #    'order': 8,
                #    'name': 33010,  #need insert string.po "Nextcloud apache2"ok
                #    'not_supported': [],
                #    'settings': {
                #        'apache2_autostart': {
                #            'order': 1,
                #            'name': 33011,   #need insert string.po 33011 #msgid "Enable apache2"ok
                #            'value': None,
                #            'action': 'initialize_nextcloud_apache2',
                #            'type': 'bool',
                #            'InfoText': 971,   #need insert 971 #msgid "Set to ON to enable the apache2 httpd daemon"ok
                #            },
                #        },
                #    },
                'zerotier': {
                    'order': 2,
                    'name': 32738,  #need insert string.po32538 "Zerotier One"ok
                    'not_supported': [],
                    'settings': {
                        'zerotier_autostart': {
                            'order': 1,
                            'name': 32739,   #need insert string.po 32539 #msgid "Enable Zerotier One"ok
                            'value': None,
                            'action': 'initialize_zerotier',
                            'type': 'bool',
                            'InfoText': 32672,   #need insert 32672  #msgid "Set to ON to enable the Zerotier One daemon"ok
                            },
                        'zerotier_nodeid': {
                            'order': 2,
                            'name': 32540, #need insert string.po 32540 #msgid "Zerotier Network Node ID"ok
                            'value': None,
                            'action': 'noaction',
                            'type': 'text', 
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 32561 , #need insert 32561 #msgid "the Zerotier network Node id"ok
                            },
                        'zerotier_node_online': {
                            'order': 3,
                            'name': 32562, #need insert string.po 32562 #msgid "Network Node Online status"ok
                            'value': None,
                            'action': 'noaction',
                            'type': 'text', 
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 32563 , #need insert 32563 #msgid "whether the Zerotier network Node Online or not"ok
                            },
                        'zerotier_network_join': {
                            'order': 4,
                            'name': 32434,   #need insert string.po 32434 #msgid "Input Zerotier Network ID and Join "ok
                            'value': None,
                            'action': 'zerotier_join_network',  #ok
                            'type': 'button',
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 977,   #need insert string.po 977 #msgid "Input the private network id of zerotier"ok
                            },
                        'zerotier_network_totalnum': {
                            'order': 6,
                            'name': 32564,   #need insert string.po 32564 #msgid "Number of Zerotier Network Join "ok
                            'value': None,
                            'action': 'noaction',  #ok
                            'type': 'text',
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 32565,   #need insert string.po 32565 #msgid "Current Number of Zerotier Network this node totally joined"ok
                            },
                        'zerotier_network_id': {
                            'order': 7,
                            'name': 32567,   #need insert string.po 32567 #msgid "Zerotier Network ID  "ok
                            'value': None,
                            'action': 'noaction',  #ok
                            'type': 'text',
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 32566,   #need insert string.po 32566 #msgid "current network id of zerotier "ok
                            },
                        'zerotier_network_type': {
                            'order': 9,
                            'name': 32435,     #need insert string.po 32435 #msgid "Zerotier network type"ok
                            'value': None,
                            'action': 'noaction',   #ok
                            'type': 'text',  # multivalue
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 975,    #need insert string.po 975 #msgid "Display Current Zerotier Network Type. 'Private' is more safe than 'Public' , 'Private' is recommended. Use "Public" zerotier one Network type , RISK AT YOUR OWN , You ARE WARNED. "ok
                            },
                        'zerotier_network_assigned_addresses4': {
                            'order': 10,
                            'name': 32436,  #need insert string.po 32436 #msgid "Zerotier network assigned IPv4 addresses"ok
                            'value': None,
                            'action': 'noaction',  #ok
                            'type': 'text',  # multivalue
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                 },
                            'InfoText': 32980 ,   #need insert string.po 32980 #msgid "Current NetworkID got Zerotier Network IPv4 addresses."ok
                            },
                        'zerotier_network_assigned_addresses6': {
                            'order': 11,
                            'name': 32981,  #need insert string.po 32981 #msgid "Zerotier network assigned IPv6 addresses"ok
                            'value': None,
                            'action': 'noaction',  #ok
                            'type': 'text',  # multivalue
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                 },
                            'InfoText': 32982 ,   #need insert string.po 32982 #msgid "Current got Zerotier Network IPv6 addresses."ok LongAddress to display ##
                            },    
                        'zerotier_network_status': {
                            'order': 8,
                            'name': 32437,   #need insert string.po 32437 #msgid "Zerotier network status"ok
                            'value': None,
                            'action': 'noaction',   #ok
                            'type': 'text',  # multivalue
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 978,   #need insert string.po 978 #msgid "Current Zerotier Network Status.First start it in None (need to join a network) status;After Join a Network(after User input the network ID), it in REQUESTING_CONFIGURATION status, Wait User to accept the node in zerotier control panel(at  https://my.zerotier.com); After User accept the node in zerotier control panel, it in Connected state. If User want the node to leave the network , please select 'Leave the Network' under the item."ok 
                            },
                        'zerotier_network_leave': {
                            'order': 12,
                            'name': 32438 ,    #need insert string.po 32438 #msgid "Zerotier Network Leave"ok
                            'value': None ,
                            'action': 'zerotier_network_leave',  #==
                            'type': 'button',
                            'parent': {
                                'entry': 'zerotier_autostart',
                                'value': ['1'],
                                },
                            'InfoText': 32979 ,  #need insert string.po 32979 #msgid "Leave the Zerotier Network"ok
                            },
                        },
                    },
                'transmission': {
                    'order': 10,
                    'name': 32499,  #need insert string.po "Transmission"ok
                    'not_supported': [],
                    'settings': {'transmission_autostart': {
                        'order': 1,
                        'name': 32440,   #need insert string.po 32440 #msgid "Enable TransmissionBT"ok
                        'value': None,
                        'action': 'initialize_transmission',
                        'type': 'bool',
                        'InfoText': 973,   #need insert 973 #msgid "Set to ON to enable the TransmissionBT daemon"ok
                        }},
                    },
            'bluez': {
                'order': 7,
                'name': 32331,  #32331 #msgid "Bluetooth"
                'not_supported': [],
                'settings': {
                    'enabled': {
                        'order': 1,
                        'name': 32344,   #32344 #msgid "Enable Bluetooth"
                        'value': None,
                        'action': 'initialize_bluetooth',
                        'type': 'bool',
                        'InfoText': 720,   #720 #msgid "Set to ON and Bluetooth devices will be disabled during power-saving modes"
                        },
                    'obex_enabled': {
                        'order': 2,
                        'name': 32384,    #32384 #msgid "OBEX Enabled"
                        'value': None,
                        'action': 'initialize_obex',
                        'type': 'bool',
                        'parent': {
                            'entry': 'enabled',
                            'value': ['1'],
                            },
                        'InfoText': 751,  #751 #msgid "With OBEX filetransfer you can send files, for example movies or pictures over bluetooth to @DISTRONAME@."
                        },
                    'obex_root': {
                        'order': 3,
                        'name': 32385,   #32385 #msgid "OBEX Upload Folder"
                        'value': None,
                        'action': 'initialize_obex',
                        'type': 'folder',
                        'parent': {
                            'entry': 'obex_enabled',
                            'value': ['1'],
                            },
                        'InfoText': 752,   #752 #msgid "Here you can set the folder location where OBEX file transfer should store incoming files"
                        },
                    'idle_timeout': {
                        'order': 4,
                        'name': 32400,
                        'value': None,
                        'action': 'idle_timeout',
                        'type': 'multivalue',
                        'values': [
                            '0',
                            '1',
                            '3',
                            '5',
                            '15',
                            '30',
                            '60',
                            ],
                        'parent': {
                            'entry': 'enabled',
                            'value': ['1'],
                            },
                        'InfoText': 773,
                        },
                    },
                },
            }

    @log.log_function()
    def start_service(self):
        self.load_values()
        self.initialize_samba(service=1)
        self.initialize_ssh(service=1)
        self.initialize_avahi(service=1)
        self.initialize_cron(service=1)
        self.initialize_bluetooth(service=1)
        self.initialize_nextcloud(service=1)
        #self.initialize_nextcloud_apache2(service=1)
        self.initialize_transmission(service=1)
        self.initialize_zerotier(service=1)

    @log.log_function()
    def do_init(self):
        self.load_values()

    @log.log_function()
    def set_value(self, listItem):
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')

    @log.log_function()
    def load_menu(self, focusItem):
        oe.winOeMain.build_menu(self.struct)

    @log.log_function()
    def load_values(self):
        # SAMBA
        if os.path.isfile(self.SAMBA_NMDB) and os.path.isfile(self.SAMBA_SMDB):
            self.struct['samba']['settings']['samba_autostart']['value'] = oe.get_service_state('samba')
            self.struct['samba']['settings']['samba_workgroup']['value'] = oe.get_service_option('samba', 'SAMBA_WORKGROUP',
                    self.D_SAMBA_WORKGROUP).replace('"', '')
            self.struct['samba']['settings']['samba_secure']['value'] = oe.get_service_option('samba', 'SAMBA_SECURE',
                    self.D_SAMBA_SECURE).replace('true', '1').replace('false', '0').replace('"', '')
            self.struct['samba']['settings']['samba_username']['value'] = oe.get_service_option('samba', 'SAMBA_USERNAME',
                    self.D_SAMBA_USERNAME).replace('"', '')
            self.struct['samba']['settings']['samba_password']['value'] = oe.get_service_option('samba', 'SAMBA_PASSWORD',
                    self.D_SAMBA_PASSWORD).replace('"', '')
            self.struct['samba']['settings']['samba_minprotocol']['value'] = oe.get_service_option('samba', 'SAMBA_MINPROTOCOL',
                    self.D_SAMBA_MINPROTOCOL).replace('"', '')
            self.struct['samba']['settings']['samba_maxprotocol']['value'] = oe.get_service_option('samba', 'SAMBA_MAXPROTOCOL',
                    self.D_SAMBA_MAXPROTOCOL).replace('"', '')
            self.struct['samba']['settings']['samba_autoshare']['value'] = oe.get_service_option('samba', 'SAMBA_AUTOSHARE',
                    self.D_SAMBA_AUTOSHARE).replace('true', '1').replace('false', '0').replace('"', '')
        else:
            self.struct['samba']['hidden'] = 'true'
        # SSH
        if os.path.isfile(self.SSH_DAEMON):
            self.struct['ssh']['settings']['ssh_autostart']['value'] = oe.get_service_state('sshd')
            self.struct['ssh']['settings']['ssh_secure']['value'] = oe.get_service_option('sshd', 'SSHD_DISABLE_PW_AUTH',
                    self.D_SSH_DISABLE_PW_AUTH).replace('true', '1').replace('false', '0').replace('"', '')
            # hide ssh settings if Kernel Parameter is set
            with open(self.KERNEL_CMD, 'r') as cmd_file:
                cmd_args = cmd_file.read().split(' ')
            if 'ssh' in cmd_args:
                self.struct['ssh']['settings']['ssh_autostart']['value'] = '1'
                self.struct['ssh']['settings']['ssh_autostart']['hidden'] = 'true'
        else:
            self.struct['ssh']['hidden'] = 'true'
        # AVAHI
        if os.path.isfile(self.AVAHI_DAEMON):
            self.struct['avahi']['settings']['avahi_autostart']['value'] = oe.get_service_state('avahi')
        else:
            self.struct['avahi']['hidden'] = 'true'
        # CRON
        if os.path.isfile(self.CRON_DAEMON):
            self.struct['cron']['settings']['cron_autostart']['value'] = oe.get_service_state('crond')
        else:
            self.struct['cron']['hidden'] = 'true'
        # Nextcloud

        if os.path.isfile(self.NEXTCLOUD_MARIADB) and os.path.isfile(self.NEXTCLOUD_APACHE2) and os.path.isfile(self.NEXTCLOUD_PHP_FPM):
            self.struct['nextcloud']['settings']['nextcloud_autostart']['value'] = oe.get_service_state('nextcloud')
        else:
            self.struct['nextcloud']['hidden'] = 'true'

        # Nextcloud-apache2
        #if os.path.isfile(self.NEXTCLOUD_APACHE2) :
        #    self.struct['nextcloud_apache2']['settings']['apache2_autostart']#['value'] = oe.get_service_state('apache2')
        #else:
        #    self.struct['nextcloud_apache2']['hidden'] = 'true'

        # zerotier
        if os.path.isfile(self.ZEROTIER_DAEMON) :
            self.struct['zerotier']['settings']['zerotier_autostart']['value'] = oe.get_service_state('zerotier')
        else:
            self.struct['zerotier']['hidden'] = 'true'
        
        # transmission
        if os.path.isfile(self.TRANSMISSION) :
            self.struct['transmission']['settings']['transmission_autostart']['value'] = oe.get_service_state('transmission')
        else:
            self.struct['transmission']['hidden'] = 'true'

        # BLUEZ / OBEX
        if 'bluetooth' in oe.dictModules:
            if os.path.isfile(oe.dictModules['bluetooth'].BLUETOOTH_DAEMON):
                self.struct['bluez']['settings']['enabled']['value'] = oe.get_service_state('bluez')
                if os.path.isfile(oe.dictModules['bluetooth'].OBEX_DAEMON):
                    self.struct['bluez']['settings']['obex_enabled']['value'] = oe.get_service_state('obexd')
                    self.struct['bluez']['settings']['obex_root']['value'] = oe.get_service_option('obexd', 'OBEXD_ROOT',
                            oe.dictModules['bluetooth'].D_OBEXD_ROOT).replace('"', '')
                else:
                    self.struct['bluez']['settings']['obex_enabled']['hidden'] = True
                    self.struct['bluez']['settings']['obex_root']['hidden'] = True

                value = oe.read_setting('bluetooth', 'idle_timeout')
                if not value:
                    value = '0'
                self.struct['bluez']['settings']['idle_timeout']['value'] = oe.read_setting('bluetooth', 'idle_timeout')
            else:
                self.struct['bluez']['hidden'] = 'true'

    @log.log_function()
    def initialize_samba(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        options = {}
        if self.struct['samba']['settings']['samba_autostart']['value'] == '1':
            state = 1
            if 'hidden' in self.struct['samba']['settings']['samba_username']:
                del self.struct['samba']['settings']['samba_username']['hidden']
            if 'hidden' in self.struct['samba']['settings']['samba_password']:
                del self.struct['samba']['settings']['samba_password']['hidden']
            if self.struct['samba']['settings']['samba_secure']['value'] == '1':
                val_secure = 'true'
            else:
                val_secure = 'false'
            if self.struct['samba']['settings']['samba_autoshare']['value'] == '1':
                val_autoshare = 'true'
            else:
                val_autoshare = 'false'
            options['SAMBA_WORKGROUP'] = self.struct['samba']['settings']['samba_workgroup']['value']
            options['SAMBA_SECURE'] = val_secure
            options['SAMBA_AUTOSHARE'] = val_autoshare
            options['SAMBA_MINPROTOCOL'] = self.struct['samba']['settings']['samba_minprotocol']['value']
            options['SAMBA_MAXPROTOCOL'] = self.struct['samba']['settings']['samba_maxprotocol']['value']
            options['SAMBA_USERNAME'] = self.struct['samba']['settings']['samba_username']['value']
            options['SAMBA_PASSWORD'] = self.struct['samba']['settings']['samba_password']['value']
        else:
            state = 0
            self.struct['samba']['settings']['samba_username']['hidden'] = True
            self.struct['samba']['settings']['samba_password']['hidden'] = True
        oe.set_service('samba', options, state)

    @log.log_function()
    def initialize_ssh(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        options = {}
        if self.struct['ssh']['settings']['ssh_autostart']['value'] == '1':
            state = 1
            if self.struct['ssh']['settings']['ssh_secure']['value'] == '1':
                val = 'true'
                options['SSH_ARGS'] = self.OPT_SSH_NOPASSWD
            else:
                val = 'false'
                options['SSH_ARGS'] = '""'
            options['SSHD_DISABLE_PW_AUTH'] = val
        else:
            state = 0
        oe.set_service('sshd', options, state)

    @log.log_function()
    def initialize_avahi(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        options = {}
        if self.struct['avahi']['settings']['avahi_autostart']['value'] == '1':
            state = 1
        else:
            state = 0
        oe.set_service('avahi', options, state)

    @log.log_function()
    def initialize_cron(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        options = {}
        if self.struct['cron']['settings']['cron_autostart']['value'] == '1':
            state = 1
        else:
            state = 0
        oe.set_service('crond', options, state)


    
    
    @log.log_function()
    def initialize_nextcloud(self, **kwargs):
        #oe.set_busy(1)
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        state = 1
        options = {}
        if self.struct['nextcloud']['settings']['nextcloud_autostart']['value'] != '1':
            state = 0
        oe.set_service('nextcloud', options, state)
        #oe.set_busy(0)


    @log.log_function()
    def initialize_zerotier(self, **kwargs):
        #oe.set_busy(1)
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        state = 1
        options = {}
        if self.struct['zerotier']['settings']['zerotier_autostart']['value'] != '1':
            state = 0
            oe.ipaddress_from_zerotier = None
            #oe.ipv4address_2_funhomenic = None
            #oe.ipv6address_2_funhomenic = None
            if (oe.ipv4address_local != None ):
                oe.ipv4address_2_funhomenic = oe.ipv4address_local
                oe.ipaddress_from_connman = True
            oe.updateSystemAddress()

        oe.set_service('zerotier', options, state)
        #oe.set_busy(0)
        self.zerotier_node_status(**kwargs)
        self.zerotier_network_status(**kwargs)

    @log.log_function()
    def initialize_transmission(self, **kwargs):
        #oe.set_busy(1)
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        state = 1
        options = {}
        if self.struct['transmission']['settings']['transmission_autostart']['value'] != '1':
            state = 0
        oe.set_service('transmission', options, state)
        #oe.set_busy(0)

    @log.log_function()
    def initialize_bluetooth(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        options = {}
        if self.struct['bluez']['settings']['enabled']['value'] == '1':
            state = 1
            if 'hidden' in self.struct['bluez']['settings']['obex_enabled']:
                del self.struct['bluez']['settings']['obex_enabled']['hidden']
            if 'hidden' in self.struct['bluez']['settings']['obex_root']:
                del self.struct['bluez']['settings']['obex_root']['hidden']
        else:
            state = 0
            self.struct['bluez']['settings']['obex_enabled']['hidden'] = True
            self.struct['bluez']['settings']['obex_root']['hidden'] = True
        oe.set_service('bluez', options, state)

    @log.log_function()
    def initialize_obex(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        options = {}
        if self.struct['bluez']['settings']['obex_enabled']['value'] == '1':
            state = 1
            options['OBEXD_ROOT'] = self.struct['bluez']['settings']['obex_root']['value']
        else:
            state = 0
        oe.set_service('obexd', options, state)

    @log.log_function()
    def idle_timeout(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        oe.write_setting('bluetooth', 'idle_timeout', self.struct['bluez']['settings']['idle_timeout']['value'])

    @log.log_function()
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32311))    #32311 #msgid "Sharing and Remote Access"
        #haoyq add input zerotier_network_id(zerotier enabled default), enable nextcloud radio. 20200206

        #enable nextcloud and disable zerotier, for user to enable zerotier and input the NWID
        #self.struct['zerotier']['settings']['zerotier_autostart']['value'] = '0'
        self.initialize_zerotier()
        self.struct['nextcloud']['settings']['nextcloud_autostart']['value'] = '1'
        self.initialize_nextcloud()            

        # Enable samba ---- default disable samba
        self.struct['samba']['settings']['samba_autostart']['value'] = '0'
        self.initialize_samba()

        #howto put these 2 buttons.
        texttoset=""
        #if hasattr(self, 'samba'):
        texttoset = oe._(32313) + '[CR][CR]' + oe._(32312)
                #32312 #msgid "@DISTRONAME@ also supports SSH for remote access. This is for advanced users who wish to interact with @DISTRONAME@'s underlying operating system. The default user is [COLOR blue]root[/COLOR] and the default password is [COLOR blue]@ROOT_PASSWORD@[/COLOR]."   #32313 #msgid "In order to share your files between your computers @DISTRONAME@ has incorporated a samba server. This samba server can be integrated into your local network by accessing it in a familiar way with Finder or Windows Explorer."
        #else:
            #texttoset = oe._(32312)   #32312 #msgid "@DISTRONAME@ also supports SSH for remote access. This is for advanced users who wish to interact with @DISTRONAME@'s underlying operating system. The default user is [COLOR blue]root[/COLOR] and the default password is [COLOR blue]@ROOT_PASSWORD@[/COLOR]."
        #should not alwayes add zerotier description
        if hasattr(self, 'zerotier'):
            texttoset += ('[CR][CR]' + oe._(32541))  #32541 #msgid " Zerotier is the software defined network , you should first register at https://my.zerotier.com  and create your own network. then get the network id fill in the following field ." ok
        oe.winOeMain.set_wizard_text(texttoset)  

        oe.winOeMain.set_wizard_button_title(oe._(32316))  #32316 #msgid "Configure Services:"
        self.set_wizard_buttons()

    @log.log_function()
    def set_wizard_buttons(self):
        if self.struct['ssh']['settings']['ssh_autostart']['value'] == '1':
            oe.winOeMain.set_wizard_radiobutton_1(oe._(32201), self, 'wizard_set_ssh', True)  #32201 #msgid "SSH"
        else:
            oe.winOeMain.set_wizard_radiobutton_1(oe._(32201), self, 'wizard_set_ssh')    #32201 #msgid "SSH"
        if not 'hidden' in self.struct['samba']:
            if self.struct['samba']['settings']['samba_autostart']['value'] == '1':
                oe.winOeMain.set_wizard_radiobutton_2(oe._(32200), self, 'wizard_set_samba', True)    #32200 #msgid "Samba"
            else:
                oe.winOeMain.set_wizard_radiobutton_2(oe._(32200), self, 'wizard_set_samba')     #32200 #msgid "Samba"
                    
        if self.struct['zerotier']['settings']['zerotier_autostart']['value'] == '1':
            oe.winOeMain.set_wizard_radiobutton_3(oe._(32542), self, 'wizard_set_zerotier', True)   #32542 #msgid "Zerotier " ok
        else:
            oe.winOeMain.set_wizard_radiobutton_3(oe._(32542), self, 'wizard_set_zerotier')   #32542 #msgid "Zerotier" 


    @log.log_function()
    def wizard_set_ssh(self):
        if self.struct['ssh']['settings']['ssh_autostart']['value'] == '1':
            self.struct['ssh']['settings']['ssh_autostart']['value'] = '0'
        else:
            self.struct['ssh']['settings']['ssh_autostart']['value'] = '1'
        # ssh button does nothing if "ssh" set on kernel commandline
        with open(self.KERNEL_CMD, 'r') as cmd_file:
            cmd_args = cmd_file.read().split(' ')
        if 'ssh' in cmd_args:
            oe.notify('ssh', 'ssh enabled as boot parameter. can not disable')
        self.initialize_ssh()
        self.load_values()
        if self.struct['ssh']['settings']['ssh_autostart']['value'] == '1':
            self.wizard_sshpasswd()
        self.set_wizard_buttons()

    @log.log_function()
    def wizard_set_samba(self):
        if self.struct['samba']['settings']['samba_autostart']['value'] == '1':
            self.struct['samba']['settings']['samba_autostart']['value'] = '0'
        else:
            self.struct['samba']['settings']['samba_autostart']['value'] = '1'
        self.initialize_samba()
        self.load_values()
        self.set_wizard_buttons()

    @log.log_function()
    def wizard_sshpasswd(self):
        SSHresult = False
        while SSHresult == False:
            changeSSH = xbmcDialog.yesno(oe._(32209), oe._(32210), yeslabel=oe._(32213), nolabel=oe._(32214))      #32209 #msgid "SSH Password"   #32210 #msgid "The default SSH password is widely known and considered insecure.[CR][CR]Setting a personal password is recommended."   #32213 #msgid "Keep Existing"   #32214 #msgid "Set Password"
            if changeSSH:
                SSHresult = True
            else:
                changeSSHresult = self.do_sshpasswd()
                if changeSSHresult:
                    SSHresult = True
        return

    @log.log_function()
    def do_sshpasswd(self, **kwargs):
        SSHchange = False
        newpwd = xbmcDialog.input(oe._(746))    #746 #msgid "Set the password for SSH"
        if newpwd:
            if newpwd == "funhometv":
                oe.execute('cp -fp /usr/cache/shadow /storage/.cache/shadow')
                readout3 = "Retype password"
            else:
                ssh = subprocess.Popen(["passwd"], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=0)
                readout1 = ssh.stdout.readline()
                ssh.stdin.write(f'{newpwd}\n')
                readout2 = ssh.stdout.readline()
                ssh.stdin.write(f'{newpwd}\n')
                readout3 = ssh.stdout.readline()
            if "Bad password" in readout3:
                xbmcDialog.ok(oe._(32220), oe._(32221))   #32220 #msgid "Bad password!"   #32221 #msgid "The entered password is too weak.[CR]SSH password is unchanged."
                log.log('Password too weak')
                return
            elif "Retype password" in readout3:
                xbmcDialog.ok(oe._(32222), oe._(32223))  #32222 #msgid "Password changed!"   #32223 #msgid "The SSH password has been successfully changed."
                SSHchange = True
            else:
                xbmcDialog.ok(oe._(32224), oe._(32225))  #32224 #msgid "Unknown error!"   #32225 #msgid "There was an error during the process.[CR]SSH password is unchanged."
        else:
            log.log('User cancelled')
        return SSHchange




    @log.log_function()
    def zerotier_join_network(self, **kwargs):
        #NetworkIDchange = False
        newNetworkID = xbmcDialog.input(oe._(32434))   #32434 #msgid "Input the private network id of zerotier"
        #the newNetworkID should checked for valid in 16 byte hex.
        #  old one from where?'^([a-fA-F0-9](?:[a-fA-F0-9-\.]*[a-fA-F0-9]))$'
        validate_str = r'^([a-fA-F0-9](?:[a-fA-F0-9]*[a-fA-F0-9]))$'
        while  not (re.search(validate_str, newNetworkID) and len(newNetworkID) == 16):
            oe.notify(oe._(32550), oe._(32551))  #32550 Input Error#32551 Not in range a-f 0-9 and length should be 16, please reenter. ==
            newNetworkID = xbmcDialog.input(oe._(32434)) 
            if not newNetworkID :
                oe.dbg_log('services::zerotier_join_network', 'exit-user_cancelled', 0)
                return                                        
        if newNetworkID:
            commandjoin="zerotier-cli join " + newNetworkID
            zerotier = subprocess.Popen([commandjoin], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            readout1 = zerotier.stdout.readline()
            if "OK" in readout1:
                self.zerotier_node_status(**kwargs)
                #redirect user to https://my.zerotier.com with the login page , to accept the node.
                zt_address = "https://accounts.zerotier.com/auth/realms/zerotier/protocol/openid-connect/auth?client_id=zt-central&redirect_uri=https%3A%2F%2Fmy.zerotier.com%2Fapi%2F_auth%2Foidc%2Fcallback&response_type=code&scope=all&state=state"

                img = qrcode.make(zt_address)  #img in png
                img.save('/storage/.kodi/zt_address.png')
                #displayQRcodeDialog() with pyxbmct module .
                #add QRCode
                #another place is host name , where user can access nextcloud.
                # Create a window instance.
                qrDialog = QRWin(self.oe._(32552), '/storage/.kodi/zt_address.png' , self.oe._(32574), self.oe._(32553) + self.struct['zerotier']['settings']['zerotier_nodeid']['value']  , self.oe._(32575))
                qrDialog.doModal()
                del qrDialog

                #xbmcDialog.ok(oe._(32552), oe._(32553) + self.struct['zerotier']['settings']['zerotier_nodeid']['value'])   #need to insert 32552 #msgid "Nextwork Join OK !"   #32553 #msgid "You should accept the node with PC or mobile on https://my.zeritier.com , the node id is :" ok
                self.zerotier_network_status(**kwargs)
                oe.dbg_log('services::zerotier_join_network', 'exit_function join OK', 0)
                return
            else:
                xbmcDialog.ok(oe._(32554), oe._(32555))   #need to insert 32554 #msgid "Unknown error!"   #32555 #msgid "There was an error during the process.[CR]network id should be unchanged."ok
                self.zerotier_network_status(**kwargs)
                oe.dbg_log('services::zerotier_join_network', 'exit_function', 0)
        else:
            oe.dbg_log('services::zerotier_join_network', 'exit-user_cancelled', 0)

    @log.log_function()
    def zerotier_network_leave(self, **kwargs):
        #import web_pdb; web_pdb.set_trace()
        #user should select which network to leave. or no network to leave , just return
        if self.struct['zerotier']['settings']['zerotier_network_id']['value'] == "None" : 
            oe.dbg_log('services::zerotier_network_leave', 'exit_function no network to leave', 0)
            return
        select_window = xbmcgui.Dialog()
        title = oe._(32557).encode('utf-8')   #need insert 32557 #msgid "Select Which Network to leave"ok
        result = select_window.select(title, self.struct['zerotier']['settings']['zerotier_network_id']['value'])
        if result >= 0:
            network2leave = self.struct['zerotier']['settings']['zerotier_network_id']['value'][result].split(":")[0]
        else:
            oe.dbg_log('services::zerotier_network_leave', 'exit_function user not selected', 0)
            return
        commandleave = "zerotier-cli leave " + network2leave
        zerotier = subprocess.Popen([commandleave], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        readout1 = zerotier.stdout.readline()
        if "OK" in readout1:
            xbmcDialog.ok(oe._(32558), oe._(32556))   #need to insert 32558 #msgid "Nextwork Leave OK !"   #32556 #msgid "The Zerotier Network successfully left."ok
            if(self.struct['zerotier']['settings']['zerotier_network_totalnum']['value'] - 1 == 0 ):  #all network are left
                oe.ipaddress_from_zerotier = None
                #oe.ipv4address_2_funhomenic = None
                oe.ipv6address_2_funhomenic = None
                if (oe.ipv4address_local != None ):
                    oe.ipv4address_2_funhomenic = oe.ipv4address_local
                    oe.ipaddress_from_connman = True
                oe.updateSystemAddress()
            oe.dbg_log('services::zerotier_network_leave', 'exit_function leave OK', 0)
            return
        else:
            xbmcDialog.ok(oe._(32559), oe._(32560))   #need to insert 32559 #msgid "Unknown error!"   #32560 #msgid "There was an error during the process.[CR]network is unchanged."ok
        self.zerotier_node_status(**kwargs)
        self.zerotier_network_status(**kwargs)

    @log.log_function()
    def zerotier_network_status(self, **kwargs):
        if self.struct['zerotier']['settings']['zerotier_autostart']['value'] != '1':
            oe.dbg_log('servies::zerotier_network_status,service not enabled','exit_function',0)
            return    
        commandlistnetworks = "zerotier-cli -j listnetworks"
        zerotier = subprocess.Popen([commandlistnetworks], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        content = zerotier.stdout.read()
        zerotier.stdout.close()
        networks = json.loads(content)
        oe.dbg_log('services::zerotier_network_status:get zerotier-cli -j listnetworks=',content,0)
        #print "network:" + repr(networks)
        #print 'str'+str(networks)
        #print 'len'+str(len(networks))
        #print 'networks[0]' + str(networks[0])
        #print 'len(networks[0])=' + str(len(networks[0]))
        #for w in networks[0]:
        #    print w , networks[0][w]

        #print "json:nwid" + repr(networks[0]['nwid'].encode('utf-8'))
        #print "len assignedaddresses" + repr(len(networks[0]['assignedAddresses']))
        #print "assignedAddresses:"
        #for a in range(len(networks[0]['assignedAddresses'])):
        #    print a, networks[0]['assignedAddresses'][a]

        self.struct['zerotier']['settings']['zerotier_network_id']['value'] = []
        self.struct['zerotier']['settings']['zerotier_network_type']['value'] = []
        self.struct['zerotier']['settings']['zerotier_network_status']['value'] = []
        self.struct['zerotier']['settings']['zerotier_network_assigned_addresses4']['value'] = []
        self.struct['zerotier']['settings']['zerotier_network_assigned_addresses6']['value'] = []
        self.struct['zerotier']['settings']['zerotier_network_totalnum']['value'] = len(networks)

        ipv4_str = r'^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\/[0-9]+)$'
        ipv4count=0
        ipv6count=0
        oe.ipaddress_from_zerotier = None
        oe.ip6address_from_zerotier = None
        #also should set the system module's ipaddress ip6address to None
        for i in range(len(networks)):
            self.struct['zerotier']['settings']['zerotier_network_id']['value'].append(networks[i]['nwid'].encode('utf-8') + ':' + networks[i]['name'].encode('utf-8'))
            self.struct['zerotier']['settings']['zerotier_network_type']['value'].append(networks[i]['type'].encode('utf-8'))
            self.struct['zerotier']['settings']['zerotier_network_status']['value'].append(networks[i]['status'].encode('utf-8'))
            for j in range(len(networks[i]['assignedAddresses'])):
                if(re.search(ipv4_str, networks[i]['assignedAddresses'][j].encode('utf-8'))):
                    self.struct['zerotier']['settings']['zerotier_network_assigned_addresses4']['value'].append(networks[i]['assignedAddresses'][j].encode('utf-8'))
                    oe.dbg_log('services::zerotier_network_status:ipv4:',repr(ipv4count) + '=' + repr(networks[i]['assignedAddresses'][j].encode('utf-8')),0)
                    if(ipv4count == 0):
                        oe.ipaddress_from_zerotier = True
                        oe.ipv4address_2_funhomenic = networks[i]['assignedAddresses'][j].encode('utf-8').split('/')[0]
                    ipv4count = ipv4count + 1
                else:
                    oe.dbg_log('services::zerotier_network_status:ipv6:',repr(ipv6count) + '=' + repr(networks[i]['assignedAddresses'][j].encode('utf-8')),0)
                    if(ipv6count == 0):
                        oe.ip6address_from_zerotier = True
                        oe.ipv6address_2_funhomenic = networks[i]['assignedAddresses'][j].encode('utf-8').split('/')[0]
                    self.struct['zerotier']['settings']['zerotier_network_assigned_addresses6']['value'].append(networks[i]['assignedAddresses'][j].encode('utf-8'))
                    ipv6count = ipv6count + 1
        oe.updateSystemAddress()


    @log.log_function()
    def zerotier_node_status(self,**kwargs):
        if self.struct['zerotier']['settings']['zerotier_autostart']['value'] != '1':
            oe.dbg_log('servies::zerotier_node_status,service not enabled','exit_function',0)
            return    

        commandinfo = "zerotier-cli -j info"
        zerotier = subprocess.Popen([commandinfo], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        content = zerotier.stdout.read()
        zerotier.stdout.close()
        node = json.loads(content)
        #print "json:address -- " + repr(node['address'].encode('utf-8'))
        #print "json:online -- " + repr(node['online'])
        oe.dbg_log('services::zerotier_node_status:get zerotier-cli -j info=',content,0)
        self.struct['zerotier']['settings']['zerotier_nodeid']['value'] = node['address'].encode('utf-8')
        oe.hostname_2_funhomenic = node['address'].encode('utf-8')
        if (node['online']):
            self.struct['zerotier']['settings']['zerotier_node_online']['value'] = oe._(32544)#32544 - 'Yes'===
        else:
            self.struct['zerotier']['settings']['zerotier_node_online']['value'] = oe._(32545)#32545 -- 'No'===


    @log.log_function()
    def wizard_zerotier(self):
        self.zerotier_join_network()


    @log.log_function()
    def wizard_set_zerotier(self):
        if self.struct['zerotier']['settings']['zerotier_autostart']['value'] == '1':
            self.struct['zerotier']['settings']['zerotier_autostart']['value'] = '0'
        else:
            self.struct['zerotier']['settings']['zerotier_autostart']['value'] = '1'            
        self.initialize_zerotier()
        self.load_values()
        if self.struct['zerotier']['settings']['zerotier_autostart']['value'] == '1':
            self.wizard_zerotier()
        self.set_wizard_buttons()

    @log.log_function()
    def nextcloud_link(self):
        apply_status = "/storage/.kodi/apache/apply_status"
        if os.path.exists(apply_status):
            with open(apply_status,'r') as ash:
                fcont=ash.read()
            jc2=json.loads(fcont)
            ash.close()
            #print("read file ok")
            if (jc2['status']=='Complete'):
                nextcloud_address = "nc://login/user:nc&password:funhome.tv&server:" + "https://" + oe.last_hostname
                img=qrcode.make(nextcloud_address)
                img.save('/storage/.kodi/nextcloud_address.png')
                # Create a window instance.
                qrDialog = QRWin(oe._(32599), '/storage/.kodi/nextcloud_address.png' , oe._(32598) + "https://" +oe.last_hostname , oe._(32597)  , oe._(32596))  
                #32599 title:Please use your mobile phone nextcloud client to scan the QR code. 
                # #32598: The default administror username of the Nextcloud Hub is 'nc' , password is 'funhometv'. After you scan the QR code , remember to set a new password for security reason. 
                # #32597: Please download Nextcloud app from your mobile's appstore. If you are using Android , maybe from Google Play Store or your vendor's appstore. If you are using iPhone , maybe from Apple Appstore. The application's name is 'Nextcloud' . Should be free.  
                # #32596: The entrance to scan the QR code is at lower part of your mobile screen , after you press 'Login' button (Your mobile phone and the funhometv device should be on same WLAN , or network setup ok ). Then follow the guide you should link your mobile with this device . 
                qrDialog.doModal()
                del qrDialog
                

