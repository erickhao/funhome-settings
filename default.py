# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import socket

import xbmc
import xbmcaddon

__scriptid__ = 'service.funhometv.settings'
__addon__ = xbmcaddon.Addon(id=__scriptid__)
__cwd__ = __addon__.getAddonInfo('path')
__media__ = f'{__cwd__}/resources/skins/Default/media'
_ = __addon__.getLocalizedString

try:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/var/run/service.funhometv.settings.sock')
    sock.send(b'openConfigurationWindow')
    sock.close()
except Exception as e:
    xbmc.executebuiltin('Notification("FunHome.TV", "%s", 5000, "%sicons/icon.png")' % (_(32390), __media__))   #32390 #msgid "Settings addon is not yet ready, please try again later."
