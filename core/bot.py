#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from imp import reload
from glob import glob
from configparser import ConfigParser

from core.events import TimedReactor, EventReactor, event_dict, Event
from core.irc import IRCEventMachine
from core.settings import settings
from core.utils import log_core
import plugins


class Bot(IRCEventMachine):

    def __init__(self, settings=settings, plugins=None):
        self.general_settings = settings['general']

        super().__init__(settings['irc'])

        self.timed = TimedReactor(self.loop, self.conn)
        self.eventd = EventReactor(self.conn)
        self.subscribe(self.eventd.event)

        self.load_plugins()
        self.connect()

    def load_plugins(self):
        conf_path = self.general_settings['plugin_conf_path']
        files = glob(conf_path)

        for file in files:
            config = ConfigParser()
            config.read(file)
            for section_name in config.sections():
                section = config[section_name]
                if section['enabled'] != 'true':
                    log_core.info("plugin %s disabled", section_name)
                    continue

                plugin = getattr(plugins, section['plugin'], None)
                if not plugin:
                    log_core.error("plugin %s does not exist", section_name)
                    continue
                log_core.info("plugin %s loaded correctly(probably!)", section_name)
                self.add_plugin(plugin, section)

    def add_plugin(self, Plugin, settings):
        p = Plugin(self, settings)

        viable_methods = (getattr(p, m) for m in dir(p)
                          if not m.startswith('_'))

        for method in viable_methods:
            triggers = getattr(method, 'triggers', [])
            time = getattr(method, 'fire_every', 0)

            for trigger in triggers: self.eventd.subscribe(method, trigger)
            if time: self.timed.subscribe(method, time)

    def reload_plugins(self):
        reload(plugins)

        self.timed.halt()
        self.eventd.halt()
        self.load_plugins()

        return sum(len(v) for v in self.timed.values())

    def authorized(self, source):
        auth_backend = getattr(self, 'auth_backend', None)

        if not auth_backend:
            return source == self.general_settings['owner']

    def hello(self, conn):
        init = Event(None, 'INIT', None, None)
        self.call_subscribers(conn, init)
        conn.nick(self.nickname)
        conn.user(self.nickname, 0, self.settings['realname'])

        def start_conn(conn, event):
            for c in self.settings['channels'].split(','):
                conn.join(c)

        self.eventd.subscribe(start_conn, 'MOTDEND', single=True)

    def run(self, delay=1):

        def do_irc(loop):
            self.process_once()
            loop.call_later(0.5, do_irc, loop)

        self.loop.call_soon(do_irc, self.loop)
        self.loop.run_forever()
