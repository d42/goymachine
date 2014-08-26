import asyncio
import time
import logging
import os

from imp import reload
from configparser import ConfigParser
from glob import glob
from collections import namedtuple, defaultdict

import plugins

from core.utils import LineBuffer
from core.utils import event_dict, triggers as t
from core.permissions import RandomPermissions
from core.settings import settings
from plugins.stubplugin import StubPlugin


class Event(namedtuple('event', ['source', 'name', 'target', 'data'])):
    def __new__(cls, source, name, target=None, data=None):
        name = event_dict.get(name, name)
        return super(Event, cls).__new__(cls, source, name, target, data)


class IRCConnection(asyncio.Protocol):
    """Simple send-receive class"""
    def __init__(self, em=None, settings=settings):
        self.settings = settings
        self.em = em
        self.buf = LineBuffer()
        loop = asyncio.get_event_loop()

        self.out_buffer = []

        def send_tick():
            now = self.out_buffer[:5]
            self.out_buffer = self.out_buffer[5:]

            for line in now:
                self._data_send(line)
            loop.call_later(3, send_tick)

        loop.call_later(3, send_tick)

    def connection_made(self, transport):
        self.transport = transport
        self._write = transport.write
        self.em.hello(self)

    def data_send(self, data, buffered=False):
        if buffered:
            self.out_buffer.append(data)
        else:
            self._data_send(data)

    def _data_send(self, data):
        if not data.endswith('\r\n'):
            data = data + '\r\n'

        if isinstance(data, str):
            data = data.encode('utf-8')

        logging.debug('> %s', data)
        self._write(data)

    def data_received(self, data):
        logging.debug('< %s', data)
        self.buf.feed(data)

        for line in self.buf.ready_lines:
            line = line.decode('utf-8', errors='replace')
            self.em.handle_event(self, line)

    def connection_lost(self, exc):
        logging.info("connection lost")

    def msg(self, dest, msg):
        self.data_send("PRIVMSG {dest} :{msg}".format_map(locals()),
                       buffered=True)

    def pong(self, dst):
        self.data_send("PONG {}".format(dst))

    def nick(self, nick):
        self.data_send("NICK {nick}".format(nick=nick))

    def user(self, nick, mode, realname):
        msg = "USER {nick} {mode} * :{realname}".format_map(locals())
        self.data_send(msg)

    def part(self, channel, message="Lewakom śmierć!"):
        msg = "PART {channel}: {message}".format_map(locals())
        self.data_send(msg)

    def join(self, channel):
        self.data_send('JOIN {}'.format(channel))


class IRCEventMachine:

    def __init__(self, settings=settings, c_class=IRCConnection):
        self.settings = settings
        self.c_class = c_class

        self.nickname = self.settings['nickname']
        self.subscribers = []
        self.online_channels = []

    def connect(self):
        host, port = [self.settings[v] for v in ('host', 'port')]
        self.connetion_channels = []

        def such_factory():
            c = self.c_class()
            c.host = host  # FIXME: is this a hack, or just a fantasy?
            c.em = self
            self.conn = c
            return c

        self.irc_loop = asyncio.new_event_loop()
        self.connection = self.irc_loop.create_connection(such_factory, host, port)
        self.irc_loop.run_until_complete(self.connection)

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def process_once(self):
        self.irc_loop.run_until_complete(self.connection)

    def handle_event(self, conn, data):
        if not data:
            return

        stuff = data.replace(':', '', 2).split(' ', 3)
        if not data.startswith(':'):  # no prefix, therefore no source :c
            stuff = [None] + stuff

        try:
            e = Event(*stuff)
        except:
            import ipdb; ipdb.set_trace()

        derp = getattr(self, 'on_' + e.name.lower(), self._stub)
        if derp:
            derp(conn, e)

        for subscriber in self.subscribers:
            subscriber(conn, e)

    # responses
    def _stub(self, conn, event):
        logging.info("%s, is not implemented!", event.name)

    def on_notice(self, conn, event):
        pass

    def on_ping(self, conn, event):
        conn.pong(event.target)

    def on_join(self, conn, event):
        pass

    # actions

    def hello(self, conn):
        conn.nick(self.nickname)
        conn.user(self.nickname, 0, self.settings['realname'])

        for c in self.settings['channels'].split(','):
            conn.join(c)


class Bot(IRCEventMachine):

    def __init__(self, c_class=IRCConnection, em_class=IRCEventMachine,
                 settings=settings, plugins=None):
        self.general_settings = settings['general']

        super().__init__(settings['irc'])
        self.subscribe(self.event)

        self.handlers = defaultdict(list)
        self.timed_events = defaultdict(list)
        self.timed_events_handles = {}
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
                    logging.info("plugin %s disabled", section_name)
                    continue

                plugin = getattr(plugins, section['plugin'], None)
                if not plugin:
                    logging.error("plugin %s couldn't be loaded", section_name)
                    continue
                logging.info("plugin %s loaded correctly(probably!)", section_name)
                self.add_plugin(plugin, section)

    def add_plugin(self, Plugin, settings):
        p = Plugin(self, settings)
        for method_name in dir(p):
            if method_name.startswith('_'):
                continue

            method = getattr(p, method_name)
            triggers = getattr(method, 'triggers', [])
            time = getattr(method, 'fire_every', 0)

            if time:
                self.timed_events[time].append(method)

            for trigger in triggers:
                self.handlers[trigger].append(method)

    def register_handler(self, trigger, method):

        self.handlers[trigger].append(method)

    def handle_once(self, trigger, method):

        def unregister(func):
            def inner(*args, **kwargs):

                pass
            return inner

    def reload_plugins(self):
        reload(plugins)

        self.stop_timed_events()
        self.timed_events = defaultdict(list)
        self.handlers = defaultdict(list)

        self.load_plugins()
        self.start_timed_events()
        return sum(len(v) for v in self.timed_events.values())

    def event(self, conn, event):
        for trigger in t.to_triggers(event):
            for handler in self.handlers[trigger]:
                handler(conn, event)

    def authorized(self, source):
        auth_backend = getattr(self, 'auth_backend', None)
        if not auth_backend:
            return source == self.general_settings['owner']

    def stop_timed_events(self):
        keys = list(self.timed_events_handles.keys())

        for key in keys:
            handle = self.timed_events_handles[key]
            handle.cancel()
            del self.timed_events_handles[key]

    def start_timed_events(self):

        def timed_events(loop, delay, methods):
            for method in methods:
                method(self.conn)
            handle = loop.call_later(delay, timed_events, loop, delay, methods)
            self.timed_events_handles[delay] = handle

        loop = asyncio.get_event_loop()
        for delay, methods in self.timed_events.items():
            handle = loop.call_later(delay, timed_events, loop, delay, methods)
            self.timed_events_handles[delay] = handle

    def run(self, delay=1):

        def do_irc(loop):
            self.process_once()
            loop.call_later(1, do_irc, loop)

        loop = asyncio.get_event_loop()
        self.start_timed_events()

        loop.call_soon(do_irc, loop)
        loop.run_forever()
