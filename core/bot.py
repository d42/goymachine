from .pluginface import PluginBase

class Bot:
    def __init__(self, settings=None):
        if settings:
            self.read_settings(settings)


    def read_settings(self, settings):
        irc_options = (
            'nickname', 'realname', 'ident', 'server', 'port'
        )

        for option in irc_options:
            if getattr(self.__dict__, option, None):
                raise KekException
            setattr(self.__dict__, option, settings['irc'][option])

    def register_plugin(self, plugin):
        """:type plugin: PluginBase"""

        for trig in plugin.triggers

    def run(self):
        pass
