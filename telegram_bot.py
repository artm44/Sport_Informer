import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from routers.commands_router import commands_router
from routers.message_router import message_router


ALLOWED_UPDATES = ['message']

load_dotenv()
bot = Bot(token=os.getenv('TELEGRAMM_TOKEN'), parse_mode=ParseMode.HTML)

dp = Dispatcher()

dp.include_routers(commands_router, message_router)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!\n" +
                         "Выбери команду из списка или напиши название спортивной команды или" \
                         " имя спортсмена, чтобы узнать информацию:")



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    print('Bot is running')

if __name__ == "__main__":
    asyncio.run(main())