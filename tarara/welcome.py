#!/usr/bin/python
# coding: utf-8

import os
import urwid.curses_display
import urwid
from ara_form import *
import widget

class ara_welcome(ara_form, urwid.Widget):
    def get_banner(self):
	banner = self.server.notice_manager.get_welcome()
	if banner[0] == False:
            return u"오늘의 환영 인사는 없습니다."
        else:
            return banner[1]

    def get_ip(self):
        return "127.0.0.1"

    def get_location(self):
        return "Web"

    def get_date(self):
        return "Today"

    def keypress(self, size, key):
        if "enter" in key:
            self.parent.change_page("main",{'session_key':self.session_key})

    def __initwidgets__(self):
        self.banner = urwid.Filler(urwid.Text(self.get_banner()))

        logintext = "Last login: %(IP)s/%(location)s at %(date)s"
        logindata = {"IP": self.get_ip(), "location": self.get_location(), "date":self.get_date()}
        self.logininfo = urwid.Filler(urwid.Text(logintext % logindata))

        self.entertext = urwid.Filler(urwid.Text("Press [Enter] key to continue"))

        content = [self.banner,('fixed',1, self.logininfo),('fixed',1,widget.blank), ("fixed", 1, self.entertext)]
        self.mainpile = urwid.Pile(content)

if __name__=="__main__":
    ara_welcome().main()

# vim: set et ts=8 sw=4 sts=4:
