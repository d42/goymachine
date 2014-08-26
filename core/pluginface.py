from core.utils import triggers
import logging

plog = logging.getLogger('plugin')
plog.setLevel(logging.INFO)


class PluginBase:
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.setup()


def triggered_by(*triggers, permlevel=0):
    def deco(func):

        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner.triggers = set(triggers)
        inner.permlevel = permlevel
        return inner

    return deco

def trigger_every(seconds):
    def deco(func):

        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner.fire_every = seconds
        return inner

    return deco
