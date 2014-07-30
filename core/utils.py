from configparser import ConfigParser
from collections import deque, namedtuple
import os

from core.exceptions import NoConfigException

event_dict = {
    '375': 'MOTDSTART',
    '372': 'MOTD',
    '376': 'MOTDEND',
    '353': 'NAMES',
    '366': 'NAMESEND'
}


class Triggers:
    _triggers = ('link', 'message', 'join', 'part', 'action')
    def __init__(self):
        for i, t in enumerate(_triggers):
            setattr(self, t, i)


    def is_link(self, event):
        return event.name is 'PRIVMSG' and 'http' in event.data

    def is_message(self, event):
        return event.name is 'PRIVMSG'

    def is_join(self, event):
        return self.name is 'JOIN'

    def is_part(self, event):
        return self.name is 'PART'

    def is_action(self, event):
        return event.name is 'PRIVMSG' and 0x01 in event.data

    def to_triggers(self, event):
        for t in _triggers:
            if not getattr('is_' + t)(event):
                yield t



triggers = Triggers()

to_trigger(name, data):


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
