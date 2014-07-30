from core.utils import triggers


class PluginBase:
    def __init__(self, name, triggers):
        self.name = name
        self.triggers = triggers


def triggered_by(func):
    def deco(*triggers):
        func.triggers = set(triggers)

        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return deco
