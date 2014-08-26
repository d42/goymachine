#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import PluginBase, triggered_by, triggers as t


class NickServ(PluginBase):
    def setup(self):
        pass

    @triggered_by(t.hello)
    def register(self, conn, event):
        nick = self.settings['login']
        passw = self.settings['password']
        conn.msg("nickserv", "identify {nick} {passw}".format_map(locals()))
