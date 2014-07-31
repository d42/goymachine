from core.utils import triggers


class PluginBase:
    def __init__(self, em, settings):
        self.em = em
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
