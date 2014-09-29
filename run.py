import logging

from core.bot import Bot
from core.settings import settings
import plugins


def main():
    logging.basicConfig(level=logging.WARN)
    bot = Bot(settings=settings)
    bot.run()

if __name__ == '__main__':
    main()
