import logging

from core.irc import Bot
from core.settings import settings
import plugins


def main():
    logging.basicConfig(level=logging.WARN)
    bot = Bot(settings=settings)
    bot.load_plugins()
    bot.run()

if __name__ == '__main__':
    main()
