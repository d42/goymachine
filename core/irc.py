import asyncio
import time
import logging
import os

from glob import glob

from core.utils import LineBuffer
from core.events import Event


class IRCConnection(asyncio.Protocol):
    """Simple send-receive class"""
    def __init__(self, em, settings):
        self.settings = settings
        self.em = em
        self.buf = LineBuffer()
        self.loop = asyncio.get_event_loop()

        self.out_buffer = []

        def send_tick():
            now = self.out_buffer[:5]
            self.out_buffer = self.out_buffer[5:]

            for line in now:
                self._data_send(line)
            self.loop.call_later(3, send_tick)

        self.loop.call_later(3, send_tick)

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
        print('>', data)
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
        self.nickname = nick
        self.data_send("NICK {nick}".format(nick=nick))

    def user(self, nick, mode, realname):
        msg = "USER {nick} {mode} * :{realname}".format_map(locals())
        self.data_send(msg)

    def part(self, channel, message="Lewakom śmierć!"):
        msg = "PART {channel}: {message}".format_map(locals())
        self.data_send(msg)

    def cap_req(self, r):
        msg = "CAP REQ :{}".format(r)
        self.data_send(msg)

    def join(self, channel):
        self.data_send('JOIN {}'.format(channel))


class IRCEventMachine:

    def __init__(self, settings, c_class=IRCConnection):
        self.settings = settings
        self.conn = c_class(self, settings)
        self.loop = asyncio.get_event_loop()

        self.nickname = self.settings['nickname']
        self.subscribers = []
        self.online_channels = []

    def connect(self):
        host, port = [self.settings[v] for v in ('host', 'port')]
        self.connetion_channels = []
        ssl = (self.settings['ssl'] == 'true')

        def such_factory():
            self.conn.host = host  # FIXME: is this a hack, or just a fantasy?
            self.conn.em = self
            return self.conn

        self.irc_loop = asyncio.new_event_loop()
        self.connection = self.irc_loop.create_connection(such_factory, host, port, ssl=ssl)
        self.irc_loop.run_until_complete(self.connection)

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def process_once(self):
        self.irc_loop.run_until_complete(self.connection)


    def call_subscribers(self, conn, event):
        for subscriber in self.subscribers:
            subscriber(conn, event)

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
        print(e)

        derp = getattr(self, 'on_' + e.name.lower(), self._stub)
        if derp:
            derp(conn, e)

        self.call_subscribers(conn, e)


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
        init = Event(None, 'INIT', None, None)
        self.call_subscribers(conn, init)
        conn.nick(self.nickname)
        conn.user(self.nickname, 0, self.settings['realname'])

        for c in self.settings['channels'].split(','):
            conn.join(c)


