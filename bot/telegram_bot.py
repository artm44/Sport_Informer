from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import TELEGRAMM_TOKEN
from bot.handlers.commands_router import commands_router
from bot.handlers.messages_router import messages_router


class TelegramBot:
    
    def __init__(self) -> None:
        self.allowed_updates = ['message']           
        self.bot = Bot(token=TELEGRAMM_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self.dp.include_routers(commands_router, messages_router)

    async def run(self) -> None:
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot, allowed_updates=self.allowed_updates)