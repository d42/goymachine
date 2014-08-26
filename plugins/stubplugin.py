#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import(PluginBase, triggered_by,
                            trigger_every, triggers as t)


class StubPlugin(PluginBase):

    def setup(self):
        self.message = self.settings['message']

    @triggered_by(t.join)
    def say_hello(self, conn, event):
        conn.msg(event.target, self.message)

    @trigger_every(5)
    def recur_hello(self, conn):
        conn.msg("#hehechan", self.message)
