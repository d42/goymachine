from configparser import ConfigParser
from collections import deque, namedtuple, UserDict
import os

from core.exceptions import NoConfigException

event_dict = {
    '375': 'MOTDSTART',
    '372': 'MOTD',
    '376': 'MOTDEND',
    '353': 'NAMES',
    '366': 'NAMESEND'
}


class EventListener:
    def __init__(self, em, method, triggers, single=False):
        """:type em: IRCEventMachine"""

        self.single = single
        self.em = em
        self.method = method
        self.trigger = trigger

    def subscribe(self):
        pass

    def unsusbcribe(self):
        pass

    def __call__(self, *args, **kwargs):
        if self.single:
            self.unsusbcribe()
        self.method(*args, **kwargs)


class Triggers:
    _triggers = ('link', 'message', 'join', 'part', 'action', 'hello')

    def __init__(self):
        for i, t in enumerate(self._triggers):
            setattr(self, t, i)

    def is_message(self, event):
        return event.name == 'PRIVMSG'

    def is_link(self, event):
        return event.name == 'PRIVMSG' and 'http' in event.data

    def is_action(self, event):
        return event.name == 'PRIVMSG' and '\x01' in event.data

    def is_join(self, event):
        return event.name == 'JOIN'

    def is_part(self, event):
        return event.name == 'PART'

    def is_hello(self, event):
        return event.name == 'MOTDEND'

    def to_triggers(self, event):
        for t in self._triggers:
            if getattr(self, 'is_' + t)(event):
                yield getattr(self, t)


triggers = Triggers()


class ConfigParser(ConfigParser):
    pass


class Permissions:
    pass


def find_settings():
    paths = [
        '~/.config/goymachine/settings.ini',
        '~/.goymachinerc',
        'settings.ini'
    ]

    for path in paths:
        expanded = os.path.expanduser(path)
        try:
            os.stat(expanded)
        except FileNotFoundError:
            continue
        return expanded

    raise NoConfigException


class LineBuffer:

    def __init__(self):
        self.buffer = b''
        self.lines = deque()

    def feed(self, data):
        b = b''

        all_fits = data.endswith(b'\r\n')
        if all_fits:
            lines = data.split(b'\r\n')

        else:
            *lines, b = data.split(b'\r\n')

        if lines:
            lines[0] = self.buffer + lines[0]
            self.buffer = b''
            for l in lines:
                self.lines.append(l)

        self.buffer += b

    @property
    def ready_lines(self):
        while self.lines:
            yield self.lines.popleft()


def get_nick(nick):
    pass
