import asyncio
from collections import namedtuple

from core.utils import LineBuffer
from core.utils import to_trigger, event_dict



class Event(namedtuple('event', ['source', 'name', 'target', 'data'])):
    def __new__(cls, source, name, target=None, data=None):
        name = event_dict.get(name, name)
        return super(Event, cls).__new__(cls, source, name, target, data)


class IRCEventMachine:

    def __init__(self):
        self.connections = []
        self.connection_channels = {}


    def add_plugin(self, plugin):


    def handle_event(self, conn, data):
        if not data:
            return

        stuff = data.replace(':', '', 2).split(' ', 3)

        e = Event(*stuff)
        print(e)

        getattr(self, 'on_' + e.name, self._stub)(conn, e)
        self.run_hooked_plugins(conn, e)

    def self.run_hooked_plugins(self, conn, e):
        for trigger in t.to_trigger(e):
            for handler in self.handlers[trigger]:
                handler(conn, e, self)


    def _stub(self, conn, event):
        print(event.name, "is not implemented!")

    def on_notice(self, conn, event):
        pass

    def on_ping(self, conn, event):
        self.pong(event.source)

    def hello(self, conn):
        nickname = "herpderp123"
        realname = "xDD"
        print('dsfsdf')

        self.nick(conn, nickname)
        self.user(conn, nickname, 0, realname)
        self.join(conn, "#hehechan")

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
    def __init__(self, em=None):
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
        import ipdb; ipdb.set_trace()

    def run_once(self):
        pass


class Bot:
    def __init__(self, settings, c_class=IRCConnection, em_class=IRCEventMachine):
        host, port = (settings['irc'][k] for k in ('host', 'port'))
        self.em = em_class()

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

