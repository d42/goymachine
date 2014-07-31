#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import PluginBase, triggered_by, triggers as t


class StubPlugin(PluginBase):

    def setup(self):
        self.message = self.settings['plugin-stub']['message']

    @triggered_by(t.join)
    def say_hello(self, conn, event, em):
        em.msg(conn, event.target, self.message)

        return self.message
