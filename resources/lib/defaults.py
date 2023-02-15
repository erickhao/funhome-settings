# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2020-present Team LibreELEC (https://libreelec.tv)

import os


################################################################################
# Base
################################################################################

XBMC_USER_HOME = os.environ.get('XBMC_USER_HOME', '/storage/.kodi')
CONFIG_CACHE = os.environ.get('CONFIG_CACHE', '/storage/.cache')
USER_CONFIG = os.environ.get('USER_CONFIG', '/storage/.config')

################################################################################
# Connamn Module
################################################################################

connman = {
    'CONNMAN_DAEMON': '/usr/sbin/connmand',
    'WAIT_CONF_FILE': f'{CONFIG_CACHE}/funhometv/network_wait',
    'ENABLED': lambda : (True if os.path.exists(connman['CONNMAN_DAEMON']) and not os.path.exists('/dev/.kernel_ipconfig') else False),
    }
connman['ENABLED'] = connman['ENABLED']()

################################################################################
# Bluez Module
################################################################################

bluetooth = {
    'BLUETOOTH_DAEMON': '/usr/lib/bluetooth/bluetoothd',
    'OBEX_DAEMON': '/usr/lib/bluetooth/obexd',
    'ENABLED': lambda : (True if os.path.exists(bluetooth['BLUETOOTH_DAEMON']) else False),
    'D_OBEXD_ROOT': '/storage/downloads/',
    }
bluetooth['ENABLED'] = bluetooth['ENABLED']()

################################################################################
# Service Module
################################################################################

services = {
    'ENABLED': True,
    'KERNEL_CMD': '/proc/cmdline',
    'SAMBA_NMDB': '/usr/sbin/nmbd',
    'SAMBA_SMDB': '/usr/sbin/smbd',
    'D_SAMBA_WORKGROUP': 'WORKGROUP',
    'D_SAMBA_SECURE': '0',
    'D_SAMBA_USERNAME': 'funhometv',
    'D_SAMBA_PASSWORD': 'funhometv',
    'D_SAMBA_MINPROTOCOL': 'SMB2',
    'D_SAMBA_MAXPROTOCOL': 'SMB3',
    'D_SAMBA_AUTOSHARE': '1',
    'SSH_DAEMON': '/usr/sbin/sshd',
    'OPT_SSH_NOPASSWD': "-o 'PasswordAuthentication no'",
    'D_SSH_DISABLE_PW_AUTH': '0',
    'AVAHI_DAEMON': '/usr/sbin/avahi-daemon',
    'CRON_DAEMON': '/sbin/crond',
    'ZEROTIER_DAEMON': '/usr/sbin/zerotier-one',#we haoyq added until transmission 
    'NEXTCLOUD_MARIADB': '/usr/bin/mysqld',
    'NEXTCLOUD_APACHE2': '/usr/sbin/httpd' ,
    'NEXTCLOUD_PHP_FPM': '/usr/sbin/php-fpm',
    'TRANSMISSION': '/usr/bin/transmission-daemon',
    }

system = {
    'ENABLED': True,
    'KERNEL_CMD': '/proc/cmdline',
    'SET_CLOCK_CMD': '/sbin/hwclock --systohc --utc',
    'XBMC_RESET_FILE': f'{CONFIG_CACHE}/reset_soft',
    'FUNHOMETV_RESET_FILE': f'{CONFIG_CACHE}/reset_hard',
    'KEYBOARD_INFO': '/usr/share/X11/xkb/rules/base.xml',
    'UDEV_KEYBOARD_INFO': f'{CONFIG_CACHE}/xkb/layout',
    'NOX_KEYBOARD_INFO': '/usr/lib/keymaps',
    'BACKUP_DIRS': [
        XBMC_USER_HOME,
        USER_CONFIG,
        CONFIG_CACHE,
        '/storage/.ssh',
        ],
    'BACKUP_FILTER' : [
        f'{XBMC_USER_HOME}/addons/packages',
        f'{XBMC_USER_HOME}/addons/temp',
        f'{XBMC_USER_HOME}/temp'
        ],
    'BACKUP_DESTINATION': '/storage/backup/',
    'RESTORE_DIR': '/storage/.restore/',
    'JOURNALD_CONFIG_FILE': '/storage/.cache/journald.conf.d/00_settings.conf'
    }

updates = {
    'ENABLED': not os.path.exists('/dev/.update_disabled'),
    #'UPDATE_REQUEST_URL': 'https://update.com.funhome.tv:6443/updates', #--production--#we make a python script instead of php , return json.  In production , we return [releases].com.funhome.tv:9080/[FunHome-Generic.x86-64-1.0.x.tar] in json.
    'UPDATE_REQUEST_URL': 'http://reg.com.funhome.tv:5003/updates', #--development in hwm sh ~/shs/tonele.sh  ; in development we can return [reldevel].com.funhome.tv/[FunHomeTV-Generic.x86-64-1.0.x.tar] in json . 
    'UPDATE_DOWNLOAD_URL': 'http://%sdev.com.funhome.tv:8003/%s', # --development releases.com.funhome.tv in http return .torrent file indeed. real 'tar' or '.img.gz' on a pc with torrent seed. also in tonele.sh make a tunnel to 80
    #'UPDATE_DOWNLOAD_URL': 'http://%s.com.funhome.tv:9080/%s', #--production-- releases.com.funhome.tv:9080 in nginx http file service
    'LOCAL_UPDATE_DIR': '/storage/.update/',

    'RPI_FLASHING_TRIGGER': '/storage/.rpi_flash_firmware',
    }

about = {'ENABLED': True}

_services = {
    'sshd': ['sshd.service'],
    'avahi': ['avahi-daemon.service'],
    'samba': ['nmbd.service', 'smbd.service'],
    'bluez': ['bluetooth.service'],
    'obexd': ['obex.service'],
    'crond': ['cron.service'],
    'iptables': ['iptables.service'],
    'zerotier': ['zerotier.service'], #from zerotier to transmission is haoyq we added 
    'nextcloud': ['php-fpm.service', 'mariadb.service', 'apache2.service' ], 
    'transmission': ['transmission.service'],
    }
