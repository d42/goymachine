from core.irc import Bot
from core.utils import ConfigParser, find_settings
import logging


def handler(exception):
    """:type exception: Exception """
    logging.debug(exception.message)


def main():

    settings = ConfigParser()
    settings.read(find_settings())

    bot = Bot(settings=settings)
    bot.process_forever()

if __name__ == '__main__':
    main()
