# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2017-present Team LibreELEC

import os
import random
import string

import xbmc
import xbmcgui
from dbussy import DBusError

import dbus_connman
import log
import modules
import oe
import oeWindows
import regdomain
import ui_tools


####################################################################
## Connection properties class
####################################################################

class connmanService(object):

    menu = {}
    datamap = {
        0: {'AutoConnect': 'AutoConnect'},
        1: {'IPv4': 'IPv4'},
        2: {'IPv4.Configuration': 'IPv4'},
        3: {'IPv6': 'IPv6'},
        4: {'IPv6.Configuration': 'IPv6'},
        5: {'Nameservers': 'Nameservers'},
        6: {'Nameservers.Configuration': 'Nameservers'},
        7: {'Domains': 'Domains'},
        8: {'Domains.Configuration': 'Domains'},
        9: {'Timeservers': 'Timeservers'},
        10: {'Timeservers.Configuration': 'Timeservers'},
    }
    struct = {
        'AutoConnect': {
            'order': 1,
            'name': 32110,  #32110 #msgid "Connection"
            'type': 'Boolean',
            'menuLoader': 'menu_network_configuration',
            'settings': {'AutoConnect': {
                'order': 1,
                'name': 32109,  #32109 #msgid "Connect Automatically"
                'value': '',
                'type': 'bool',
                'action': 'set_value',
            }},
        },
        'IPv4': {
            'order': 2,
            'name': 32111,   #32111 #msgid "IPv4"
            'type': 'Dictionary',
            'settings': {
                'Method': {
                    'order': 1,
                    'name': 32113,   #32113 #msgid "IP Address Method"
                    'value': '',
                    'type': 'multivalue',
                    'values': [
                        'dhcp',
                        'manual',
                        'off',
                    ],
                    'action': 'set_value',
                },
                'Address': {
                    'order': 2,
                    'name': 32114,    #32114 #msgid "IP Address"
                    'value': '',
                    'type': 'ip',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'action': 'set_value',
                    'notempty': True,
                },
                'Netmask': {
                    'order': 3,
                    'name': 32115,     #32115 #msgid "Subnet Mask"
                    'value': '',
                    'type': 'ip',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'action': 'set_value',
                    'notempty': True,
                },
                'Gateway': {
                    'order': 4,
                    'name': 32116,   #32116 #msgid "Default Gateway"
                    'value': '',
                    'type': 'ip',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'action': 'set_value',
                    'notempty': True,
                },
            },
        },
        'IPv6': {
            'order': 3,
            'name': 32112,    #32112 #msgid "IPv6"
            'type': 'Dictionary',
            'settings': {
                'Method': {
                    'order': 1,
                    'name': 32113,    #32113 #msgid "IP Address Method"
                    'value': '',
                    'type': 'multivalue',
                    'values': [
                        'auto',
                        'manual',
                        '6to4',
                        'off',
                    ],
                    'action': 'set_value',
                },
                'Address': {
                    'order': 2,
                    'name': 32114,   #32114 #msgid "IP Address"
                    'value': '',
                    'type': 'text',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'action': 'set_value',
                },
                'PrefixLength': {
                    'order': 4,
                    'name': 32117,    #32117 #msgid "Prefix Length"
                    'value': '',
                    'type': 'text',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'action': 'set_value',
                },
                'Gateway': {
                    'order': 3,
                    'name': 32116,   #32116 #msgid "Default Gateway"
                    'value': '',
                    'type': 'text',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'action': 'set_value',
                },
                'Privacy': {
                    'order': 5,
                    'name': 32118,   #32118 #msgid "Privacy"
                    'value': '',
                    'type': 'multivalue',
                    'parent': {
                        'entry': 'Method',
                        'value': ['manual'],
                    },
                    'values': [
                        'disabled',
                        'enabled',
                        'prefered',
                    ],
                    'action': 'set_value',
                },
            },
        },
        'Nameservers': {
            'order': 4,
            'name': 32119,    #32119 #msgid "DNS Servers"
            'type': 'Array',
            'settings': {
                '0': {
                    'order': 1,
                    'name': 32120,  #32120 #msgid "Nameserver #1"
                    'value': '',
                    'type': 'ip',
                    'action': 'set_value_checkdhcp',
                },
                '1': {
                    'order': 2,
                    'name': 32121,    #32121 #msgid "Nameserver #2"
                    'value': '',
                    'type': 'ip',
                    'action': 'set_value_checkdhcp',
                },
                '2': {
                    'order': 3,
                    'name': 32122,   #32122 #msgid "Nameserver #3"
                    'value': '',
                    'type': 'ip',
                    'action': 'set_value_checkdhcp',
                },
            },
        },
        'Timeservers': {
            'order': 6,
            'name': 32123,   #32123 #msgid "NTP Servers"
            'type': 'Array',
            'settings': {
                '0': {
                    'order': 1,
                    'name': 32124,   #32124 #msgid "Timeserver #1"
                    'value': '',
                    'type': 'text',
                    'action': 'set_value_checkdhcp',
                },
                '1': {
                    'order': 2,
                    'name': 32125,   #32125 #msgid "Timeserver #2"
                    'value': '',
                    'type': 'text',
                    'action': 'set_value_checkdhcp',
                },
                '2': {
                    'order': 3,
                    'name': 32126,   #32126 #msgid "Timeserver #3"
                    'value': '',
                    'type': 'text',
                    'action': 'set_value_checkdhcp',
                },
            },
        },
        'Domains': {
            'order': 5,
            'name': 32127,   #32127 #msgid "DNS Domains"
            'type': 'Array',
            'settings': {
                '0': {
                    'order': 1,
                    'name': 32128,   #32128 #msgid "Domain #1"
                    'value': '',
                    'type': 'text',
                    'action': 'set_value_checkdhcp',
                },
                '1': {
                    'order': 2,
                    'name': 32129,   #32129 #msgid "Domain #2"
                    'value': '',
                    'type': 'text',
                    'action': 'set_value_checkdhcp',
                },
                '2': {
                    'order': 3,
                    'name': 32130,   #32130 #msgid "Domain #3"
                    'value': '',
                    'type': 'text',
                    'action': 'set_value_checkdhcp',
                },
            },
        },
    }

    @log.log_function()
    def __init__(self, servicePath, oeMain):
        self.winOeCon = oeWindows.mainWindow('service-FunHomeTV-Settings-mainWindow.xml', oe.__cwd__, 'Default', oeMain=oe, isChild=True)
        self.servicePath = servicePath
        oe.dictModules['connmanNetworkConfig'] = self
        self.service_properties = dbus_connman.service_get_properties(servicePath)
        for entry in sorted(self.datamap):
            for (key, value) in self.datamap[entry].items():
                if self.struct[value]['type'] == 'Boolean':
                    if key in self.service_properties:
                        self.struct[value]['settings'][value]['value'] = str(self.service_properties[key])
                if self.struct[value]['type'] == 'Dictionary':
                    if key in self.service_properties:
                        for setting in self.struct[value]['settings']:
                            if setting in self.service_properties[key]:
                                self.struct[value]['settings'][setting]['value'] = self.service_properties[key][setting]
                if self.struct[value]['type'] == 'Array':
                    if key in self.service_properties:
                        for setting in self.struct[value]['settings']:
                            if int(setting) < len(self.service_properties[key]):
                                self.struct[value]['settings'][setting]['value'] = self.service_properties[key][int(setting)]
        self.winOeCon.show()
        for strEntry in sorted(self.struct, key=lambda x: self.struct[x]['order']):
            dictProperties = {
                'modul': 'connmanNetworkConfig',
                'listTyp': oe.listObject['list'],
                'menuLoader': 'menu_loader',
                'category': strEntry,
                }
            self.winOeCon.addMenuItem(self.struct[strEntry]['name'], dictProperties)
        self.winOeCon.doModal()
        del self.winOeCon
        del oe.dictModules['connmanNetworkConfig']

    @log.log_function()
    def cancel(self):
        self.winOeCon.close()

    @log.log_function()
    def menu_loader(self, menuItem):
        self.winOeCon.showButton(1, 32140, 'connmanNetworkConfig', 'save_network')   #32140 #msgid "Save"
        self.winOeCon.showButton(2, 32212, 'connmanNetworkConfig', 'cancel')   #32212 #msgid "Cancel"
        self.winOeCon.build_menu(self.struct, fltr=[menuItem.getProperty('category')])

    @log.log_function()
    def set_value_checkdhcp(self, listItem):
        if self.struct['IPv4']['settings']['Method']['value'] == 'dhcp':
            ok_window = xbmcgui.Dialog()
            answer = ok_window.ok('Not allowed', 'IPv4 method is set to DHCP.\n\nChanging this option is not allowed')
            return
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True

    @log.log_function()
    def set_value(self, listItem):
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True

    @log.log_function()
    def save_network(self):
        try:
            def get_array(root):
                return [root[key]['value'] for key in root.keys() if root[key]['value'] != '']

            def get_dict(root):
                return {key:root[key]['value'] for key in root.keys() if root[key]['value'] != ''}

            dbus_connman.service_set_autoconnect(self.servicePath,
                self.struct['AutoConnect']['settings']['AutoConnect']['value'])
            dbus_connman.service_set_domains_configuration(self.servicePath,
                get_array(self.struct['Domains']['settings']))
            dbus_connman.service_set_ipv4_configuration(self.servicePath,
                get_dict(self.struct['IPv4']['settings']))
            dbus_connman.service_set_ipv6_configuration(self.servicePath,
                get_dict(self.struct['IPv6']['settings']))
            dbus_connman.service_set_nameservers_configuration(self.servicePath,
                get_array(self.struct['Nameservers']['settings']))
            dbus_connman.service_set_timeservers_configuration(self.servicePath,
                get_array(self.struct['Timeservers']['settings']))
        finally:
            return 'close'

    @log.log_function()
    def delete_network(self):
        try:
            oe.dictModules['connman'].delete_network(None)
        finally:
            return 'close'

    @log.log_function()
    def connect_network(self):
        try:
            oe.dictModules['connman'].connect_network(None)
        finally:
            return 'close'

    @log.log_function()
    def disconnect_network(self):
        try:
            oe.dictModules['connman'].disconnect_network(None)
        finally:
            return 'close'


####################################################################
## Connman main class
####################################################################

class connman(modules.Module):

    ENABLED = False
    CONNMAN_DAEMON = None
    WAIT_CONF_FILE = None
    NF_CUSTOM_PATH = "/storage/.config/iptables/"
    connect_attempt = 0
    log_error = 1
    net_disconnected = 0
    notify_error = 1
    menu = {
        '3': {
            'name': 32101,   #32101 #msgid "Network"
            'menuLoader': 'menu_loader',
            'listTyp': 'list',
            'InfoText': 701,   #701 #msgid "Configure network startup options, NTP and VPNs"
        },
        '4': {
            'name': 32100,   #32100 #msgid "Connections"
            'menuLoader': 'menu_connections',
            'listTyp': 'netlist',
            'InfoText': 702,   #702 #msgid "Manage the Ethernet, Wireless and VPN connections available to the system"
        },
    }
    struct = {
        dbus_connman.PATH_TECH_WIFI: {
            'hidden': 'true',
            'order': 1,
            'name': 32102,    #32102 #msgid "Wireless Networks"
            'settings': {
                'Powered': {
                    'order': 1,
                    'name': 32105,    #32105 #msgid "Active"
                    'value': '',
                    'action': 'set_technologie',
                    'type': 'bool',
                    'InfoText': 726,   #726 #msgid "Enable or disable support for Wireless (WLAN) networks"
                },
                'Tethering': {
                    'order': 2,
                    'name': 32108,   #32108 #msgid "Enable 'tethered' Wireless Access Point"
                    'value': '',
                    'action': 'set_technologie',
                    'type': 'bool',
                    'parent': {
                        'entry': 'Powered',
                        'value': ['1'],
                    },
                    'InfoText': 727,   #727 #msgid "Enable a 'tethered' Wireless Access Point. This requires your wireless card (and driver) to support bridging and access point mode. Not all cards are capable."
                },
                'TetheringIdentifier': {
                    'order': 3,
                    'name': 32198,   #32198 #msgid "SSID"
                    'value': 'FunHomeTV-AP',
                    'action': 'set_technologie',
                    'type': 'text',
                    'parent': {
                        'entry': 'Tethering',
                        'value': ['1'],
                    },
                    'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$',
                    'InfoText': 728,   #728 #msgid "Configure the Access Point SSID"
                },
                'TetheringPassphrase': {
                    'order': 4,
                    'name': 32107,   #32107 #msgid "Passphrase"
                    'value': ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10)),
                    'action': 'set_technologie',
                    'type': 'text',
                    'parent': {
                        'entry': 'Tethering',
                        'value': ['1'],
                    },
                    'validate': '^[\\x00-\\x7F]{8,64}$',
                    'InfoText': 729,    #729 #msgid "Configure the Access Point Passphrase"
                },
                'regdom': {
                    'order': 5,
                    'name': 32240,
                    'value': '',
                    'action': 'custom_regdom',
                    'type': 'multivalue',
                    'values': [],
                    'parent': {
                        'entry': 'Powered',
                        'value': ['1'],
                    },
                    'InfoText': 749,
                },
            },
            'order': 0,
        },
        dbus_connman.PATH_TECH_ETHERNET: {
            'hidden': 'true',
            'order': 2,
            'name': 32103,   #32103 #msgid "Wired Networks"
            'settings': {'Powered': {
                'order': 1,
                'name': 32105,   #32105 #msgid "Active"
                'value': '',
                'action': 'set_technologie',
                'type': 'bool',
                'InfoText': 730,   #730 #msgid "Enable or disable support for Wired (Ethernet) networks"
            }, },
            'order': 1,
        },
        'Timeservers': {
            'order': 4,
            'name': 32123,   #32123 #msgid "NTP Servers"
            'settings': {
                '0': {
                    'order': 1,
                    'name': 32124,   #32124 #msgid "Timeserver #1"
                    'value': '',
                    'action': 'set_timeservers',
                    'type': 'text',
                    'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$|^$',
                    'InfoText': 732,   #732 #msgid "Configure the 1st time (NTP) server"
                },
                '1': {
                    'order': 2,
                    'name': 32125,    #32125 #msgid "Timeserver #2"
                    'value': '',
                    'action': 'set_timeservers',
                    'type': 'text',
                    'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$|^$',
                    'InfoText': 733,   #733 #msgid "Configure the 2nd time (NTP) server"
                },
                '2': {
                    'order': 3,
                    'name': 32126,   #32126 #msgid "Timeserver #3"
                    'value': '',
                    'action': 'set_timeservers',
                    'type': 'text',
                    'validate': '^([a-zA-Z0-9](?:[a-zA-Z0-9-\.]*[a-zA-Z0-9]))$|^$',
                    'InfoText': 734,    #734 #msgid "Configure the 3rd time (NTP) server"
                },
            },
            'order': 2,
        },
        'advanced': {
            'order': 6,
            'name': 32368,   #32368 #msgid "Advanced Network Settings"
            'settings': {
                'wait_for_network': {
                    'order': 1,
                    'name': 32369,    #32369 #msgid "Wait for network before starting Kodi"
                    'value': '0',
                    'action': 'set_network_wait',
                    'type': 'bool',
                    'InfoText': 736,   #736 #msgid "Set to ON to delay Kodi startup until the network is available. Use this if the OS is booting into Kodi before the network is up and central MySQL databases are accessible."
                },
                'wait_for_network_time': {
                    'order': 2,
                    'name': 32370,   #32370 #msgid "Maximum Wait Time (Sec.)"
                    'value': '10',
                    'action': 'set_network_wait',
                    'type': 'num',
                    'parent': {
                        'entry': 'wait_for_network',
                        'value': ['1'],
                    },
                    'InfoText': 737,   #737 #msgid "Time in seconds to wait for an established network connection."
                },
                'netfilter': {
                    'order': 3,
                    'name': 32395,    #32395 #msgid "Firewall"
                    'type': 'multivalue',
                    'values': [],
                    'action': 'init_netfilter',
                    'InfoText': 771,   #771 #msgid "The firewall blocks unwanted network traffic. Home (default) allows traffic from private network ranges (192.168.x.x, 172.16.x.x and 10.x.x.x) only. Public blocks all traffic from all networks. Custom uses rules in /storage/.config/iptables. Off disables the firewall."
                },
            },
            'order': 4,
        },
    }

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.listItems = {}
        self.busy = 0
        self.visible = False

    @log.log_function()
    def clear_list(self):
        remove = [entry for entry in self.listItems]
        for entry in remove:
            self.listItems[entry] = None
            del self.listItems[entry]

    @log.log_function()
    def do_init(self):
        self.visible = True

    @log.log_function()
    def exit(self):
        self.visible = False
        self.clear_list()

    @log.log_function()
    def load_values(self):
        # Network Wait
        self.struct['advanced']['settings']['wait_for_network']['value'] = '0'
        self.struct['advanced']['settings']['wait_for_network_time']['value'] = '10'
        if os.path.exists(self.WAIT_CONF_FILE):
            wait_file = open(self.WAIT_CONF_FILE, 'r')
            for line in wait_file:
                if 'WAIT_NETWORK=' in line:
                    if line.split('=')[-1].lower().strip().replace('"', '') == 'true':
                        self.struct['advanced']['settings']['wait_for_network']['value'] = '1'
                    else:
                        self.struct['advanced']['settings']['wait_for_network']['value'] = '0'
                if 'WAIT_NETWORK_TIME=' in line:
                    self.struct['advanced']['settings']['wait_for_network_time']['value'] = line.split('=')[-1].lower().strip().replace('"',
                            '')
            wait_file.close()
        # IPTABLES
        nf_values = [oe._(32397), oe._(32398), oe._(32399)]    #32397 #msgid "Off"   #32398 #msgid "Home"   #32399 #msgid "Public"
        nf_custom_rules = [self.NF_CUSTOM_PATH + "rules.v4" , self.NF_CUSTOM_PATH + "rules.v6"]
        for custom_rule in nf_custom_rules:
            if os.path.exists(custom_rule):
                nf_values.append(oe._(32396))   #32396 #msgid "Custom"
                break
        self.struct['advanced']['settings']['netfilter']['values'] = nf_values
        if oe.get_service_state('iptables') == '1':
            nf_option = oe.get_service_option('iptables', 'RULES', 'home')
            if nf_option == "custom":
                nf_option_str = oe._(32396)    #32396 #msgid "Custom"
            elif nf_option == "home":
                nf_option_str = oe._(32398)    #32398 #msgid "Home"
            elif nf_option == "public":
                nf_option_str = oe._(32399)    #32399 #msgid "Public"
        else:
            nf_option_str = oe._(32397)
        self.struct['advanced']['settings']['netfilter']['value'] = nf_option_str
        # regdom
        self.struct[dbus_connman.PATH_TECH_WIFI]['settings']['regdom']['values'] = regdomain.REGDOMAIN_LIST
        regValue = regdomain.get_regdomain()
        self.struct[dbus_connman.PATH_TECH_WIFI]['settings']['regdom']['value'] = str(regValue)

    @log.log_function()
    def menu_connections(self, focusItem, services={}, removed={}, force=False):
        # type 1=int, 2=string, 3=array
        properties = {
            0: {
                'flag': 0,
                'type': 2,
                'values': ['State'],
                },
            1: {
                'flag': 0,
                'type': 1,
                'values': ['Strength'],
                },
            2: {
                'flag': 0,
                'type': 1,
                'values': ['Favorite'],
                },
            3: {
                'flag': 0,
                'type': 3,
                'values': ['Security'],
                },
            4: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4', 'Method'],
                },
            5: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4', 'Address'],
                },
            6: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4.Configuration', 'Method'],
                },
            7: {
                'flag': 0,
                'type': 2,
                'values': ['IPv4.Configuration', 'Address'],
                },
            8: {
                'flag': 0,
                'type': 2,
                'values': ['Ethernet', 'Interface'],
                },
            }
        dbusServices = dbus_connman.manager_get_services()
        dbusConnmanManager = None
        rebuildList = 0
        if len(dbusServices) != len(self.listItems) or force:
            rebuildList = 1
            oe.winOeMain.getControl(int(oe.listObject['netlist'])).reset()
        else:
            for (dbusServicePath, dbusServiceValues) in dbusServices:
                if dbusServicePath not in self.listItems:
                    rebuildList = 1
                    oe.winOeMain.getControl(int(oe.listObject['netlist'])).reset()
                    break
        oe.dbg_log('connman::menuconnection dump-0:',repr(dbusServices),0)        
        for (dbusServicePath, dbusServiceProperties) in dbusServices:
            oe.dbg_log('connman::menuconnection dbusServices dump-1:',repr(dbusServicePath) + "==" + repr(dbusServiceProperties),0)
            if ('IPv4' in dbusServiceProperties):
                if ('Address' in dbusServiceProperties['IPv4']):
                    oe.ipv4address_2_funhomenic = dbusServiceProperties['IPv4']['Address']
            if ('IPv6' in dbusServiceProperties):
                if ('Address' in dbusServiceProperties['IPv6']):
                    oe.ipv6address_2_funhomenic = dbusServiceProperties['IPv6']['Address']
            
            dictProperties = {}
            if rebuildList == 1:
                if 'Name' in dbusServiceProperties:
                    apName = dbusServiceProperties['Name']
                else:
                    if 'Security' in dbusServiceProperties:
                        apName = oe._(32208) + ' (' + str(dbusServiceProperties['Security'][0]) + ')'   #32208 #msgid "Hidden Wlan"
                    else:
                        apName = ''
                if apName != '':
                    dictProperties['entry'] = dbusServicePath
                    dictProperties['modul'] = self.__class__.__name__
                    if 'Type' in dbusServiceProperties:
                        dictProperties['netType'] = dbusServiceProperties['Type']
                        dictProperties['action'] = 'open_context_menu'
            for prop in properties:
                oe.dbg_log('connman::menuconnection properties dump-2:',repr(prop),0)
                result = dbusServiceProperties
                for value in properties[prop]['values']:
                    if value in result:
                        result = result[value]
                        properties[prop]['flag'] = 1
                    else:
                        properties[prop]['flag'] = 0
                if properties[prop]['flag'] == 1:
                    if properties[prop]['type'] == 1:
                        result = str(int(result))
                    if properties[prop]['type'] == 2:
                        result = str(result)
                    if properties[prop]['type'] == 3:
                        if any(x in result for x in ['psk','ieee8021x','wep']):
                            result = str('1')
                        elif 'none' in result:
                            result = str('0')
                        else:
                            result = str('-1')
                    if rebuildList == 1:
                        dictProperties[value] = result
                    else:
                        if self.listItems[dbusServicePath] != None:
                            self.listItems[dbusServicePath].setProperty(value, result)
            if rebuildList == 1:
                self.listItems[dbusServicePath] = oe.winOeMain.addConfigItem(apName, dictProperties, oe.listObject['netlist'])

    @log.log_function()
    def menu_loader(self, menuItem=None):
        if menuItem == None:
            menuItem = oe.winOeMain.getControl(oe.winOeMain.guiMenList).getSelectedItem()
        self.technologie_properties = dbus_connman.manager_get_technologies()
        self.clock_properties = dbus_connman.clock_get_properties()
        self.struct[dbus_connman.PATH_TECH_WIFI]['hidden'] = 'true'
        self.struct[dbus_connman.PATH_TECH_ETHERNET]['hidden'] = 'true'
        for (path, technologie) in self.technologie_properties:
            if path in self.struct:
                if 'hidden' in self.struct[path]:
                    del self.struct[path]['hidden']
                for entry in self.struct[path]['settings']:
                    if entry in technologie:
                        self.struct[path]['settings'][entry]['value'] = str(technologie[entry])
        for setting in self.struct['Timeservers']['settings']:
            if 'Timeservers' in self.clock_properties:
                if int(setting) < len(self.clock_properties['Timeservers']):
                    self.struct['Timeservers']['settings'][setting]['value'] = self.clock_properties['Timeservers'][int(setting)]
            else:
                self.struct['Timeservers']['settings'][setting]['value'] = ''
        oe.winOeMain.build_menu(self.struct)

    @log.log_function()
    def open_context_menu(self, listItem):
        values = {}
        if listItem is None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        if listItem is None:
            return
        if listItem.getProperty('State') in ['ready', 'online']:
            values[1] = {
                'text': oe._(32143),   #32143 #msgid "Disconnect"
                'action': 'disconnect_network',
                }
        else:
            values[1] = {
                'text': oe._(32144),   #32144 #msgid "Connect"
                'action': 'connect_network',
                }
        if listItem.getProperty('Favorite') == '1':
            values[2] = {
                'text': oe._(32150),   #32150 #msgid "Edit"
                'action': 'configure_network',
                }
        if listItem.getProperty('Favorite') == '1' and listItem.getProperty('netType') == 'wifi':
            values[3] = {
                'text': oe._(32141),   #32141 #msgid "Delete"
                'action': 'delete_network',
                }
        if hasattr(self, 'technologie_properties'):
            for (path, technologie) in self.technologie_properties:
                if path == dbus_connman.PATH_TECH_WIFI:
                    values[4] = {
                        'text': oe._(32142),  #32142 #msgid "Refresh"
                        'action': 'refresh_network',
                        }
                    break
        items = []
        actions = []
        for key in list(values.keys()):
            items.append(values[key]['text'])
            actions.append(values[key]['action'])
        select_window = xbmcgui.Dialog()
        title = oe._(32012)      #32012 #msgid "Select Action"
        result = select_window.select(title, items)
        if result >= 0:
            getattr(self, actions[result])(listItem)

    @log.log_function()
    def set_timeservers(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        timeservers = []
        for setting in sorted(self.struct['Timeservers']['settings']):
            if self.struct['Timeservers']['settings'][setting]['value'] != '':
                timeservers.append(self.struct['Timeservers']['settings'][setting]['value'])
        dbus_connman.clock_set_timeservers(timeservers)

    @log.log_function()
    def set_value(self, listItem=None):
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
        self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['changed'] = True

    @log.log_function()
    def set_technologie(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        techPath = dbus_connman.PATH_TECH_WIFI
        for (path, technologie) in self.technologie_properties:
            if path == techPath:
                for setting in self.struct[techPath]['settings']:
                    settings = self.struct[techPath]['settings']
                    if settings['Powered']['value'] == '1':
                        if technologie['Powered'] != True:
                            dbus_connman.technology_set_powered(techPath, True)
                        if (settings['Tethering']['value'] == '1' and
                            settings['TetheringIdentifier']['value'] != '' and
                            settings['TetheringPassphrase']['value'] != ''):
                            oe.xbmcm.waitForAbort(5)
                            dbus_connman.technology_wifi_set_tethering_identifier(settings['TetheringIdentifier']['value'])
                            dbus_connman.technology_wifi_set_tethering_passphrase(settings['TetheringPassphrase']['value'])
                            if technologie['Tethering'] != True:
                                dbus_connman.technology_wifi_set_tethering(True)
                        else:
                            if technologie['Tethering'] != False:
                                dbus_connman.technology_wifi_set_tethering(False)
                    else:
                        if technologie['Powered'] != False:
                            dbus_connman.technology_set_powered(techPath, False)
                    break
        techPath = dbus_connman.PATH_TECH_ETHERNET
        for (path, technologie) in self.technologie_properties:
            if path == techPath:
                for setting in self.struct[techPath]['settings']:
                    settings = self.struct[techPath]['settings']
                    if settings['Powered']['value'] == '1':
                        if technologie['Powered'] != True:
                            dbus_connman.technology_set_powered(techPath, True)
                    else:
                        if technologie['Powered'] != False:
                            dbus_connman.technology_set_powered(techPath, False)
                    break
        self.menu_loader(None)

    @log.log_function()
    def custom_regdom(self, **kwargs):
            if 'listItem' in kwargs:
                regSelect = str((kwargs['listItem']).getProperty('value'))
                regdomain.set_regdomain(regSelect)
                self.set_value(kwargs['listItem'])

    @log.log_function()
    def configure_network(self, listItem=None):
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        self.configureService = connmanService(listItem.getProperty('entry'), oe)
        del self.configureService
        self.menu_connections(None)

    @log.log_function()
    def connect_network(self, listItem=None):
        self.connect_attempt += 1
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        entry = listItem.getProperty('entry')
        try:
            dbus_connman.service_connect(entry)
            self.menu_connections(None)
        except DBusError as e:
            self.dbus_error_handler(e)

    @log.log_function()
    def connect_reply_handler(self):
        self.menu_connections(None)

    @log.log_function()
    def dbus_error_handler(self, error):
        err_name = error.name               #from dbus-python to dbussy , changed a lot
        if 'InProgress' in err_name:
            if self.net_disconnected != 1:
                self.disconnect_network()
            else:
                self.net_disconnected = 0
            self.connect_network()
        else:
            err_message = error.message
            if 'Operation aborted' in err_message or 'Input/output error' in err_message:
                if oe.input_request:
                    oe.input_request = False
                    self.connect_attempt = 0
                    self.log_error = 1
                    self.notify_error = 0
                elif self.connect_attempt == 1:
                    self.log_error = 0
                    self.notify_error = 0
                    oe.xbmcm.waitForAbort(5)
                    self.connect_network()
                else:
                    self.log_error = 1
                    self.notify_error = 1
            elif 'Did not receive a reply' in err_message:
                self.log_error = 1
                self.notify_error = 0
            else:
                self.log_error = 1
                self.notify_error = 1
            if self.notify_error == 1:
                ui_tools.notification(err_message, 'Network Error')
            else:
                self.notify_error = 1
            if self.log_error == 1:
                log.log(repr(error), log.ERROR)
            else:
                self.log_error = 1

    @log.log_function()
    def disconnect_network(self, listItem=None):
        self.connect_attempt = 0
        self.net_disconnected = 1
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        entry = listItem.getProperty('entry')
        dbus_connman.service_disconnect(entry)

    @log.log_function()
    def delete_network(self, listItem=None):
        self.connect_attempt = 0
        if listItem == None:
            listItem = oe.winOeMain.getControl(oe.listObject['netlist']).getSelectedItem()
        service_path = listItem.getProperty('entry')
        dbus_connman.service_remove(service_path)

    @log.log_function()
    def refresh_network(self, listItem=None):
        dbus_connman.technology_wifi_scan()
        self.menu_connections(None)

    @log.log_function()
    def start_service(self):
        self.load_values()          #from  dbus-python to dbussy , changed a lot , agent and listner added
        self.init_netfilter(service=1)
        self.agent = Agent()
        self.listener = Listener(self)

    @log.log_function()
    def stop_service(self):
        #self.agent.unregister_agent()
        del self.listener       #release it 
        del self.agent
        if hasattr(self, 'dbusConnmanManager'):
            self.dbusConnmanManager = None
            del self.dbusConnmanManager

    @log.log_function()
    def set_network_wait(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        if self.struct['advanced']['settings']['wait_for_network']['value'] == '0':
            if os.path.exists(self.WAIT_CONF_FILE):
                wait_conf = open(self.WAIT_CONF_FILE, 'w')
                wait_conf.close()
            return
        else:
            if not os.path.exists(os.path.dirname(self.WAIT_CONF_FILE)):
                os.makedirs(os.path.dirname(self.WAIT_CONF_FILE))
            wait_conf = open(self.WAIT_CONF_FILE, 'w')
            wait_conf.write('WAIT_NETWORK="true"\n')
            wait_conf.write(f"WAIT_NETWORK_TIME=\"{self.struct['advanced']['settings']['wait_for_network_time']['value']}\"\n")
            wait_conf.close()

    def init_netfilter(self, **kwargs):
        if 'listItem' in kwargs:
            self.set_value(kwargs['listItem'])
        state = 1
        options = {}
        if self.struct['advanced']['settings']['netfilter']['value'] == oe._(32396):   #32396 #msgid "Custom"
            options['RULES'] = "custom"
        elif self.struct['advanced']['settings']['netfilter']['value'] == oe._(32398):   #32398 #msgid "Home"
            options['RULES'] = "home"
        elif self.struct['advanced']['settings']['netfilter']['value'] == oe._(32399):   #32399 #msgid "Public"
            options['RULES'] = "public"
        else:
            state = 0
        oe.set_service('iptables', options, state)

    @log.log_function()
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32305))   #32305 #msgid "Networking"
        oe.winOeMain.set_wizard_text(oe._(32306))     #32306 #msgid "In order to download backdrops, banners and thumbnails for your movies and TV shows and to stream online content from sites like YouTube, @DISTRONAME@ needs to be connected the Internet.[CR][CR]An Internet connection is also required for @DISTRONAME@ to automatically update itself."
        oe.winOeMain.set_wizard_button_title('')
        oe.winOeMain.set_wizard_list_title(oe._(32309))   #32309 #msgid "The following Networks are currently available:"
        oe.winOeMain.getControl(1391).setLabel('show')

        oe.winOeMain.getControl(oe.winOeMain.buttons[2]['id'
                                     ]).controlUp(oe.winOeMain.getControl(oe.winOeMain.guiNetList))
        oe.winOeMain.getControl(oe.winOeMain.buttons[2]['id'
                                     ]).controlRight(oe.winOeMain.getControl(oe.winOeMain.buttons[1]['id']))
        oe.winOeMain.getControl(oe.winOeMain.buttons[1]['id'
                                     ]).controlUp(oe.winOeMain.getControl(oe.winOeMain.guiNetList))
        oe.winOeMain.getControl(oe.winOeMain.buttons[1]['id'
                                     ]).controlLeft(oe.winOeMain.getControl(oe.winOeMain.buttons[2]['id']))
        self.menu_connections(None)


class Agent(dbus_connman.Agent):

    def report_error(self, path, error):
        oe.input_request = False
        ui_tools.notification(error)

    def request_input(self, path, fields):
        oe.input_request = True
        response = {}
        input_fields = {
            'Name': 32146,
            'Passphrase': 32147,
            'Username': 32148,
            'Password': 32148,
        }
        for field, label in input_fields.items():
            if field in fields:
                xbmcKeyboard = xbmc.Keyboard('', oe._(label))
                xbmcKeyboard.doModal()
                if xbmcKeyboard.isConfirmed() and xbmcKeyboard.getText():
                    response[field] = xbmcKeyboard.getText()
                else:
                    self.agent_abort()
        passphrase = response.get('Passphrase')
        if passphrase:
            if 'Identity' in fields:
                response['Identity'] = passphrase
            if 'wpspin' in fields:
                response['wpspin'] = passphrase
        oe.input_request = False
        return response


class Listener(dbus_connman.Listener):

    @log.log_function()
    def __init__(self, parent):
        self.parent = parent
        super().__init__()
    
    @log.log_function()
    def __del__(self, parent):
        super().__del__()
        self.parent = None



    @log.log_function()
    async def on_property_changed(self, name, value, path):
        oe.dbg_log('connman::monitor::propertyChanged::name', repr(name), 0)
        oe.dbg_log('connman::monitor::propertyChanged::value', repr(value), 0)
        oe.dbg_log('connman::monitor::propertyChanged::path', repr(path), 0)
        if name == 'IPv4':
            if 'Address' in value:
                va = str(value['Address'])
                oe.ipv4address_local = va
                #self.parent.listItems[path].setProperty('Address', va)
                #add address if zerotier not added address
                if (oe.ipaddress_from_zerotier == None):
                    oe.ipv4address_2_funhomenic = va
                    oe.ipaddress_from_connman = True
                    oe.updateSystemAddress()
        if name == 'IPv6':
            if 'Address' in value:
                va = str(value['Address'])
                oe.ipv6address_local = va
                #self.parent.listItems[path].setProperty('Address', va)
                #add address if zerotier not added address
                if (oe.ipaddress_from_zerotier == None):
                    oe.ipv6address_2_funhomenic = va
                    oe.ipaddress_from_connman = True
                    oe.updateSystemAddress()
        if self.parent.visible:
            self.updateGui(name, value, path)

    @log.log_function()
    async def on_technology_changed(self, name, value, path):
        oe.dbg_log('connman::monitor::technologyChanged::name', repr(name), 0)
        oe.dbg_log('connman::monitor::technologyChanged::value', repr(value), 0)
        oe.dbg_log('connman::monitor::technologyChanged::path', repr(path), 0)
        if name == 'IPv4':
            if 'Address' in value:
                va = str(value['Address'])
                oe.ipv4address_local = va
                #self.parent.listItems[path].setProperty('Address', va)
                #add address if zerotier not added address
                if (oe.ipaddress_from_zerotier == None):
                    oe.ipv4address_2_funhomenic = va
                    oe.ipaddress_from_connman = True
                    oe.updateSystemAddress()
        if name == 'IPv6':
            if 'Address' in value:
                va = str(value['Address'])
                oe.ipv6address_local = va
                #self.parent.listItems[path].setProperty('Address', va)
                #add address if zerotier not added address
                if (oe.ipaddress_from_zerotier == None):
                    oe.ipv6address_2_funhomenic = va
                    oe.ipaddress_from_connman = True
                    oe.updateSystemAddress()

        if self.parent.visible:
            if oe.winOeMain.lastMenu == 1:
                oe.winOeMain.lastMenu = -1
                oe.winOeMain.onFocus(oe.winOeMain.guiMenList)
            else:
                self.updateGui(name, value, path)

    @log.log_function()
    async def on_services_changed(self, services, removed):
        if self.parent.visible:
            self.parent.menu_connections(None, services, removed, force=True)

    @log.log_function()
    def updateGui(self, name, value, path):
        try:
            if name == 'Strength':
                value = str(int(value))
                self.parent.listItems[path].setProperty(name, value)
                self.forceRender()
            elif name == 'State':
                value = str(value)
                self.parent.listItems[path].setProperty(name, value)
                self.forceRender()
            elif name == 'IPv4':
                if 'Address' in value:
                    value = str(value['Address'])
                    self.parent.listItems[path].setProperty('Address', value)
                if 'Method' in value:
                    value = str(value['Method'])
                    self.parent.listItems[path].setProperty('Address', value)
                self.forceRender()
            elif name == 'Favorite':
                value = str(int(value))
                self.parent.listItems[path].setProperty(name, value)
                self.forceRender()
            if hasattr(self.parent, 'is_wizard'):
                self.parent.menu_connections(None, {}, {}, force=True)
        except KeyError:
            self.parent.menu_connections(None, {}, {}, force=True)

    @log.log_function()
    def forceRender(self):
            focusId = oe.winOeMain.getFocusId()
            oe.winOeMain.setFocusId(oe.listObject['netlist'])
            oe.winOeMain.setFocusId(focusId)
