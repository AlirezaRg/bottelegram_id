import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from . import config
from .handlers import start, verification, reports, ads

logging.basicConfig(level=logging.INFO)


def _build_bot() -> Bot:
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)

    if config.TELEGRAM_PROXY:
        # Routes all Telegram API calls through a local proxy — needed when
        # api.telegram.org isn't directly reachable (e.g. from Iran without
        # a system-wide VPN). Requires: pip install aiohttp-socks (for socks5://)
        from aiogram.client.session.aiohttp import AiohttpSession

        session = AiohttpSession(proxy=config.TELEGRAM_PROXY)
        return Bot(token=config.BOT_TOKEN, default=default, session=session)

    return Bot(token=config.BOT_TOKEN, default=default)


async def main():
    bot = _build_bot()

    # MemoryStorage is fine for development. For production with multiple
    # workers or restarts that shouldn't lose in-progress conversations,
    # switch to RedisStorage (aiogram.fsm.storage.redis).
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(verification.router)
    dp.include_router(reports.router)
    dp.include_router(ads.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
