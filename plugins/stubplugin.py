#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import PluginBase, triggered_by
from core.pluginface import Triggers as t


class StubPlugin(PluginBase):

    def __init__(self, settings):
        self.settings = settings
        self.message = self.settings['plugin-stub']['message']

    @triggered_by(t.join)
    def say_hello(self, event):
        return self.message
