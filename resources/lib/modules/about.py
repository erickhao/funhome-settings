# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2019-present Team LibreELEC (https://libreelec.tv)

import log
import oe


class about:

    ENABLED = False
    menu = {'99': {
        'name': 32196,   #32196 #msgid "About"
        'menuLoader': 'menu_loader',
        'listTyp': 'other',
        'InfoText': 705,   #705 #msgid "Useful information like version and architecture details, support and documentation links, and how to donate and support the project."
    }}

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.controls = {}

    @log.log_function()
    def menu_loader(self, menuItem):
        pass

    @log.log_function()
    def exit_addon(self):
        oe.winOeMain.close()

    @log.log_function()
    def init_controls(self):
        pass

    @log.log_function()
    def exit(self):
        for control in self.controls:
            try:
                oe.winOeMain.removeControl(self.controls[control])
            finally:
                self.controls = {}

    @log.log_function()
    def do_wizard(self):
        oe.winOeMain.set_wizard_title(oe._(32317))   #32317 #msgid "Thank you"
        oe.winOeMain.set_wizard_text(oe._(32318))   #32318 #msgid "Your @DISTRONAME@ installation is now complete and you are about to enter Kodi where you can set up your media libraries. For help with this, there is a guide available at wiki.kodi.tv[CR][CR]@DISTRONAME@ is developed by a dedicated team of developers who work purely in their spare time. Even as a volunteer project, we still have to pay for our internet bandwidth and development resources so if you find @DISTRONAME@ useful we will always appreciate a donation of any amount.[CR][CR]Finally, we hope you enjoy using @DISTRONAME@ as much as we've enjoyed building it. If you need any more help, you can find links to our support forum along with latest news at our website."
