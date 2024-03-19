import asyncio
from bot.telegram_bot import TelegramBot


def main():
    bot = TelegramBot()
    print('Bot has started')
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
