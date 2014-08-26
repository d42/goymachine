#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
import tempfile
from datetime import date

from core.pluginface import PluginBase, triggered_by, triggers as t
from core.utils import get_nick


class Logger(PluginBase):

    def setup(self):
        self.files = {}

    def get_file(self, conn, event):
        if event.target not in self.files:
            fd, path = tempfile.mkstemp(prefix='such_log')
            file = self.files[event.target] = os.fdopen(fd, 'w+')

        else:
            file = self.files[event.target]
        return file

    @triggered_by(t.message)
    def log_message(self, conn, event):
        derp = date.today()

        such_formatting = {
            'd': derp.day,
            'y': derp.year,
            'm': derp.month,
            'channel': event.target,
            'nick': get_nick(event.source),
            'server': conn.host
        }

        path = self.t_path.format_map(such_formatting)
        file = self.get_file(conn, event, path)

        msg = self.t_msg.format_map(such_formatting)

        print(msg, file=file, flush=True)
