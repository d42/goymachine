#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import PluginBase, triggered_by, triggers as t
import random


def authorized(func):
    def inner(self, *args, event, conn):
        if not self.bot.authorized(event.source):
            return "lolnope ;_;"
        return func(self, *args, event=event, conn=conn)
    return inner



class BasementCommander(PluginBase):

    def setup(self):

        self.commands = {
            'siema co tam': self.siemacotam,
            'dej rejestruj': self.dejrejestruj,
            'dej kalifornie': self.dejkalifornie,
            'hoc': self.hoc,
            'icstot': self.icstont,
            'debuguj': self.debuguj,
            'pszeladuj': self.pszeladuj,
            'pszyspamuj': self.pszyspamuj

        }
        self.cs = self.settings['callsign']

    @triggered_by(t.message)
    def handle_callsign(self, conn, event):
        cmd, cs, params = event.data.partition(self.cs)
        cmd = cmd.strip()
        params = params.strip().split()
        if not cs:
            return

        handler = self.commands.get(cmd, None)
        if not handler:
            return
        try:
            message = handler(*params, event=event, conn=conn)
        except Exception as e:
            message = e
        if message:
            conn.msg(event.target, message)

    def dejrejestruj(self, event, conn):
        """:type event: Event"""
        if self.em.register_user(event.source, None):
            return "yay!"
        return "nay!"

    def dejkalifornie(self, event, conn):
        time = datetime.datetime.utcnow() - datetime.timedelta(hours=7)
        return time.ctime()

    @authorized
    def hoc(self, channel, event, conn):
        conn.join(channel)
        return "lol ok ;_;"

    @authorized
    def icstont(self, event, conn):
        conn.msg(event.target, "lol ok ;_;")
        conn.part(event.target)

    @authorized
    def debuguj(self, event, conn):
        import ipdb; ipdb.set_trace()

    @authorized
    def pszeladuj(self, event, conn):
        count = self.bot.reload_plugins()
        return 'ok x' + 'D' * count

    @authorized
    def pszyspamuj(self, event, conn):
        #import ipdb; ipdb.set_trace()
        words = ['siema', 'co', 'tam', 'xD']
        for i in range(10):
            line = ' '.join(random.choice(words) for _ in range(5))
            conn.msg(event.target, line)

    def siemacotam(self, event, conn):
        return 'siema nic tu xD'
