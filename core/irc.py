import asyncio
from collections import namedtuple, defaultdict

from core.utils import LineBuffer
from core.utils import event_dict, triggers as t
from core.permissions import RandomPermissions
from core.settings import settings
from plugins.stubplugin import StubPlugin


class Event(namedtuple('event', ['source', 'name', 'target', 'data'])):
    def __new__(cls, source, name, target=None, data=None):
        name = event_dict.get(name, name)
        return super(Event, cls).__new__(cls, source, name, target, data)


class IRCEventMachine:

    def __init__(self, settings=settings):
        self.settings = settings
        self.pmanager = RandomPermissions()
        self.connections = []
        self.connection_channels = {}
        self.handlers = defaultdict(list)
        self.nickname = settings['irc']['nickname']
        self.realname = settings['irc']['realname']
        self.ident = settings['irc']['ident']

    def add_plugin(self, Plugin):
        p = Plugin(self, settings)
        for method_name in dir(p):
            if method_name.startswith('_'):
                continue

            method = getattr(p, method_name)
            triggers = getattr(method, 'triggers', [])

            for trigger in triggers:
                self.handlers[trigger].append(method)

    def register_user(self, user, stuff):
        return self.pmanager(register_user(self, user, stuff))

    def handle_event(self, conn, data):
        if not data:
            return

        stuff = data.replace(':', '', 2).split(' ', 3)
        if not data.startswith(':'):  # no prefix, therefore no source :c
            stuff = [None] + stuff

        e = Event(*stuff)
        print(e)

        getattr(self, 'on_' + e.name.lower(), self._stub)(conn, e)
        self.run_hooked_plugins(conn, e)

    def run_hooked_plugins(self, conn, e):
        any_viable = False
        executed = False
        for trigger in t.to_triggers(e):
            for handler in self.handlers[trigger]:
                any_viable = True

                if self.pmanager.verify(e, handler):
                    executed = True
                    handler(conn, e, self)
        if any_viable and not executed:
            self.msg(conn, e.source, "lrn2permissions lol")

    def _stub(self, conn, event):
        print(event.name, "is not implemented!")

    def on_notice(self, conn, event):
        pass

    def on_ping(self, conn, event):
        self.pong(conn, event.target)

    def hello(self, conn):
        self.nick(conn, self.nickname)
        self.user(conn, self.nickname, 0, self.realname)
        for c in self.settings['irc']['channels'].split(','):
            self.join(conn, c)

    def msg(self, conn, dest, msg):
        conn.data_send("PRIVMSG {dest} :{msg}".format(**locals()))

    def pong(self, conn, dst):
        conn.data_send("PONG {}".format(dst))

    def nick(self, conn, nick):
        conn.data_send("NICK {nick}".format(nick=nick))

    def user(self, conn, nick, mode, realname):
        msg = "USER {nick} {mode} * :{realname}".format(**locals())
        conn.data_send(msg)

    def join(self, conn, channel):
        if channel not in self.connection_channels:
            conn.data_send('JOIN {}'.format(channel))

    def register_connection(self, conn):
        self.connections.append(conn)
        self.connection_channels[conn] = []


class IRCConnection(asyncio.Protocol):
    def __init__(self, em=None, settings=settings):
        self.settings = settings
        self.em = em
        self.buf = LineBuffer()

    def connection_made(self, transport):
        self.transport = transport
        self._write = transport.write
        self.em.hello(self)

    def data_send(self, data):
        if not data.endswith('\r\n'):
            data = data + '\r\n'

        if isinstance(data, str):
            data = data.encode('utf-8')

        print('>', data)
        self._write(data)

    def data_received(self, data):
        print('<', data)
        self.buf.feed(data)

        for line in self.buf.ready_lines:
            line = line.decode('utf-8', errors='replace')
            self.em.handle_event(self, line)

    def connection_lost(self, exc):
        print("connection lost")

    def run_once(self):
        pass


class Bot:
    def __init__(self, c_class=IRCConnection, em_class=IRCEventMachine,
                 settings=settings, plugins=None):

        self.settings = settings
        host, port = (settings['irc'][k] for k in ('host', 'port'))
        self.em = em_class()

        for p in plugins or ():
            self.em.add_plugin(p)

        def such_factory():
            c = c_class()
            c.em = self.em
            self.em.connection = c
            return c

        self.loop = asyncio.get_event_loop()
        self.conn = self.loop.create_connection(such_factory, host, port)

    def process_once(self):
        self.loop.run_until_complete(self.conn)

    def process_forever(self):
        self.process_once()
        self.loop.run_forever()
