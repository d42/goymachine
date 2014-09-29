#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import PluginBase, triggered_by, triggers as t
from core.settings import resources
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
            'pszyspamuj': self.pszyspamuj,
            'wololo': self.wololo,
            'ty janie': self.dzbanie

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

    def wololo(self, event, conn):

        def herp(nc, mg):
            nc = list(nc)
            i = random.randrange(len(nc))

            nc_i = ord(nc[i])
            derp = nc_i + mg

            derp = sorted([97, derp, 122])[1]
            a, b = sorted([nc_i, derp])
            new_c = random.randint(a, b)

            mg += (nc_i - new_c)
            nc[i] = chr(new_c)
            return ''.join(nc), mg

        h = lambda s: sum(ord(c) for c in s)
        current_nick = self.bot.nickname
        owner_nick = event.source.split('!')[0]
        print(current_nick, owner_nick)

        δ = (h(owner_nick) - h(current_nick)) % 110
        nc = current_nick

        print(h(owner_nick) % 110, h(current_nick) % 110)

        while δ:
            nc, δ = herp(nc, δ)

        print(h(nc) % 10, h(nc) % 11)
        print(h(owner_nick) % 10, h(owner_nick) % 11)
        conn.nick(nc)

    @authorized
    def pszyspamuj(self, event, conn):
        #import ipdb; ipdb.set_trace()
        words = ['siema', 'co', 'tam', 'xD']
        for i in range(10):
            line = ' '.join(random.choice(words) for _ in range(5))
            conn.msg(event.target, line)

    def siemacotam(self, event, conn):
        return 'siema nic tu xD'

    def dzbanie(self, event, conn):
        word = random.choice(resources['an'])
        adj = random.choice(resources['adj'])

        return 'ty janie {}ie {} xD'.format(word, adj)
