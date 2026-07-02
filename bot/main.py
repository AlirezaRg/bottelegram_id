"""
Local development entry point ONLY — runs the bot in polling mode.

In production (Render), the bot does NOT run this file. Instead, Telegram
delivers updates via webhook straight to the Django web service
(see api/telegram_webhook.py), so there's no separate always-on process
needed — which is what makes the free tier possible.
"""

import asyncio
import logging

from .dispatcher import bot, dp

logging.basicConfig(level=logging.INFO)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
