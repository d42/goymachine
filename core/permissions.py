#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import abc
from random import choice


class BasePermissions():
    __metaclass = abc.ABCMeta

    @abc.abstractmethod
    def verify(self, event, handler) -> bool:
        pass

    @abc.abstractmethod
    def register_user(self, user, stuff) -> bool:
        pass


class StubPermissions:

    def verify(self, event, handler):
        return 999

    def register_user(self, user, stuff):
        return True


class RandomPermissions:

    registered = set()

    def verify(self, event, handler):
        if event.source in self.registered:
            return True

        if handler.permlevel == 0:
            return True

        return False

    def register_user(self, user, stuff):

        if choice([True, False]):
            self.registered.add(user)
            return True
        return False
