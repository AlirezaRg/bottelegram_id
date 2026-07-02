"""
Builds a single shared Bot + Dispatcher instance used by:
  - bot/main.py    (local development: polling)
  - api/telegram_webhook.py  (production: webhook, fed from Django's process)

Keeping this in one place means both modes register the exact same
handlers/routers — no risk of local dev and production behaving differently.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from . import config
from .handlers import start, verification, reports, ads


def build_bot() -> Bot:
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)

    if config.TELEGRAM_PROXY:
        # Routes all Telegram API calls through a local proxy — needed when
        # api.telegram.org isn't directly reachable (e.g. from Iran without
        # a system-wide VPN). Requires: pip install aiohttp-socks (for socks5://)
        from aiogram.client.session.aiohttp import AiohttpSession

        session = AiohttpSession(proxy=config.TELEGRAM_PROXY)
        return Bot(token=config.BOT_TOKEN, default=default, session=session)

    return Bot(token=config.BOT_TOKEN, default=default)


def build_dispatcher() -> Dispatcher:
    # MemoryStorage is fine for a single-process deployment. If you ever run
    # multiple web workers/instances behind a load balancer, switch to
    # RedisStorage (aiogram.fsm.storage.redis) so FSM state is shared.
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(verification.router)
    dp.include_router(reports.router)
    dp.include_router(ads.router)
    return dp


# Module-level singletons — built once per process, reused by every request.
bot = build_bot()
dp = build_dispatcher()
