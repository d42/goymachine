from configparser import ConfigParser

from collections import deque, namedtuple, UserDict, defaultdict
from functools import wraps

import logging
import os


log_core = logging.getLogger("core")
log_glue = logging.getLogger("glue")
log_plugins = logging.getLogger("plugins")


class Triggers:
    _triggers = ('link', 'message', 'join', 'part', 'action', 'hello', 'init',
                 'cap_ack')

    def __init__(self):
        for i, t in enumerate(self._triggers):
            setattr(self, t, t)

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

    def is_cap_ack(self, event):
        return event.name == 'CAP' and event.data.startswith('ACK')

    def is_init(self, event):
        return event.name == 'INIT'

    def to_triggers(self, event):
        for t in self._triggers:
            if getattr(self, 'is_' + t)(event):
                yield getattr(self, t)

        if event.name.isdigit():
            yield int(event.name)
        else:
            yield event.name


triggers = Triggers()


class ConfigParser(ConfigParser):
    pass


class Permissions:
    pass


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
