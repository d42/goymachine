#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from collections import namedtuple, UserDict, defaultdict
from core.utils import log_glue, triggers

event_dict = {
    '375': 'MOTDSTART',
    '372': 'MOTD',
    '376': 'MOTDEND',
    '353': 'NAMES',
    '366': 'NAMESEND'
}


class Event(namedtuple('event', ['source', 'name', 'target', 'data'])):
    def __new__(cls, source, name, target=None, data=None):
        name = event_dict.get(name, name)
        return super(Event, cls).__new__(cls, source, name, target, data)


class TimedReactor(UserDict):
    def __init__(self, loop, conn):
        self.data = defaultdict(list)
        self.handlers = {}

        self.loop = loop
        self.conn = conn

    def subscribe(self, method, timeout, single=False):
        start = False

        def run_single(*args, **kwargs):
            self.unsubscribe(method)
            return method(*args, **kwargs)

        if single: method = run_single
        if not self.data[timeout]: start = True

        self.data[timeout].append(method)

        if start:
            self.tick(timeout)

    def unsubscribe(self, method):
        for loop in self.data:
            if method in loop:
                loop.remove(method)

    def tick(self, timeout):
        methods = self.data[timeout][:]
        for method in methods:
            method(self.conn)

        if not methods: return
        handle = self.loop.call_later(timeout, self.tick, timeout)
        self.handlers[timeout] = handle

    def halt(self):
        for handler in self.handlers.values():
            handler.cancel()
        self.handlers = {}


class EventReactor(UserDict):
    def __init__(self, conn):
        self.data = defaultdict(list)
        self.conn = conn

    def subscribe(self, _method, trigger, single=False):
        log_glue.info("register %s to %s", _method, trigger)

        def run_single(*args, **kwargs):
            self.unsubscribe(method)
            return _method(*args, **kwargs)

        if single: method = run_single
        else: method = _method

        self.data[trigger].append(method)

    def unsubscribe(self, method):
        for trigger in self.data:
            methods = self.data[trigger]
            if method in methods:
                log_glue.info("unsubscribe %s from %s", method, trigger)
                methods.remove(method)

    def event(self, conn, event):
        for trigger in triggers.to_triggers(event):
            handlers = self.data[trigger][:] # FIXME: might get removed and this
            for handler in handlers:         # kills the crab ;_;
                handler(conn, event)

    def halt(self):
        self.data = defaultdict(list)
