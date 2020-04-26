#!/usr/bin/env python3
import os
import signal
from subprocess import Popen, check_output

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import GLib, Gtk, Notify


# LinDota2Accepter
# apt install xdotool gir1.2-appindicator3-0.1 libnotify-bin
# sudo apt install python3-psutil


class gDotaAccepterIndicator:
    def __init__(self):
        self.APPINDICATOR_ID = "gdota-Acceptor"
        self.APPIND_SUPPORT = 1
        self.CURRDIR = os.path.dirname(os.path.abspath(__file__))
        self.ICONS_DIR = os.path.join(self.CURRDIR, 'icons')
        self.DOTAACC_BIN = os.path.join(self.CURRDIR, 'dotaaccepter.sh')
        self.ICON = os.path.join(self.ICONS_DIR, 'Antu_dota.svg')
        self.ICONRED = os.path.join(self.ICONS_DIR, 'dota2emble.png')
        self.proc = False
        self.ACTIVATED = False

        self.menu = Gtk.Menu()
        self.menu_find_match = Gtk.MenuItem(label="Find Match")
        self.menu_find_match.connect('activate', self.find_match)
        self.menu.append(self.menu_find_match)
        self.menu_find_match.show()

        self.menu_activate_scan = Gtk.MenuItem(label="Activate")
        self.menu_activate_scan.connect('activate', self.activate)
        self.menu.append(self.menu_activate_scan)
        self.menu_activate_scan.show()

        self.menu_deactivate_scan = Gtk.MenuItem(label="Deactivate")
        self.menu_deactivate_scan.connect('activate', self.deactivate)
        self.menu.append(self.menu_deactivate_scan)

        self.menu_sep = Gtk.SeparatorMenuItem()
        self.menu.append(self.menu_sep)
        self.menu_sep.show()

        self.item_quit = Gtk.MenuItem(label="Quit")
        self.item_quit.connect('activate', self.quit)
        self.menu.append(self.item_quit)
        self.item_quit.show()

        try:
            from gi.repository import AppIndicator3
        except Exception as e:
            print(e)
            self.APPIND_SUPPORT = 0

        if self.APPIND_SUPPORT == 1:
            self.indicator = AppIndicator3.Indicator.new(
                self.APPINDICATOR_ID,
                os.path.abspath(self.ICON),
                AppIndicator3.IndicatorCategory.OTHER)
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_label("Inactive", "Inactive")
            self.indicator.set_menu(self.menu)
            Notify.init(self.APPINDICATOR_ID)

        else:
            self.indicator = Gtk.StatusIcon
            self.indicator.set_from_file(self.ICON)
            self.indicator.connect(self.menu)
        # self.menu.show_all()

        GLib.timeout_add_seconds(2, self.handler_timeout)

    def find_match(self, source):
        """Presses the FIND MATCH button"""
        # TODO: replace popen with call
        if not self.is_dota_running():
            return

        if not self.proc:
            print("not proc")
            self.proc = Popen([self.DOTAACC_BIN, "-p"])

        Popen([self.DOTAACC_BIN, "-r"])

        print("proc is", self.proc)
        print("pid is", self.proc.pid)
        self.ACTIVATED = True

    def activate(self, source):
        """ activates scan"""
        if not self.proc:
            self.proc = Popen([self.DOTAACC_BIN, "-p"])
            self.ACTIVATED = True
        else:
            print("already running")

    def deactivate(self, source):
        """ deactivates scan"""
        if self.proc:
            Popen([self.DOTAACC_BIN, "-s"])
            self.proc.terminate()
            self.proc.kill()
            self.proc.communicate()
            self.ACTIVATED = False
            self.proc = False

    def quit(self, source):
        if self.proc:
            # os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            self.deactivate(source)
        Notify.uninit()
        Gtk.main_quit()

    def main(self):
        Gtk.main()

    def handler_timeout(self):
        """This will be called every few seconds by the GLib.timeout.
        """
        # return True so that we get called again
        # returning False will make the timeout stop
        self.get_active_status()
        return True

    def get_active_status(self):
        if self.ACTIVATED:
            # print("Activated")
            # self.indicator.set_icon(self.ICONRED)
            self.indicator.set_icon_full(self.ICONRED, "activated")
            self.indicator.set_label("active", "active")
            self.menu_activate_scan.hide()
            self.menu_deactivate_scan.show()

        else:
            # print ("Activate in get_active_status")
            # self.indicator.set_icon(self.ICON)
            self.indicator.set_icon_full(self.ICON, "deactivated")
            self.indicator.set_label("Inactive", "Inactive")
            self.menu_activate_scan.show()
            self.menu_deactivate_scan.hide()

    def is_dota_running(self):
        output = str(check_output(
            [self.DOTAACC_BIN, '-vc'],
            universal_newlines=True)).strip()
        print(output)
        if output != 'Dota2 is running':
            Notify.Notification.new(
                "Gdota Accepter", "Dota is not running",
                self.ICON).show()
            return False
        return True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    ind = gDotaAccepterIndicator()
    ind.main()
