"""
Run ONCE after each deploy (or whenever PUBLIC_BASE_URL changes) to tell
Telegram where to send updates:
    python create_webhook.py

Requires PUBLIC_BASE_URL and TELEGRAM_WEBHOOK_SECRET to be set in the
environment (Render dashboard -> Environment tab).
"""

import asyncio
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.conf import settings  # noqa: E402
from bot.dispatcher import bot  # noqa: E402


async def main():
    if not settings.PUBLIC_BASE_URL:
        print("ERROR: set PUBLIC_BASE_URL env var first (e.g. https://your-app.onrender.com)")
        return
    if not settings.TELEGRAM_WEBHOOK_SECRET:
        print("ERROR: set TELEGRAM_WEBHOOK_SECRET env var first")
        return

    url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/bot/webhook/{settings.TELEGRAM_WEBHOOK_SECRET}/"
    await bot.set_webhook(url=url, drop_pending_updates=True)
    info = await bot.get_webhook_info()
    print("Webhook set to:", url)
    print("Telegram confirms:", info.url)
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
