from core.irc import Bot
from core.settings import settings
import plugins
import logging


def handler(exception):
    """:type exception: Exception """
    logging.debug(exception.message)


def main():

    plugins_on = settings['general']['plugins']
    pluglist = [getattr(plugins, plugname)
                for plugname in plugins_on.split(',')]

    bot = Bot(settings=settings, plugins=pluglist)
    bot.process_forever()

if __name__ == '__main__':
    main()
