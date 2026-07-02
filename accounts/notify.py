"""
Sends push notifications straight to Telegram users from Django, using the
plain Bot API over HTTP — independent of whether the bot's own aiogram
polling process happens to be running. Used when an admin approves/rejects
something in the admin panel, so the user finds out immediately instead of
having to come back and ask the bot.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(telegram_id: int, text: str) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not configured — skipping notification to %s", telegram_id)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": telegram_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        if not resp.ok:
            logger.error("Telegram notify failed for %s: %s", telegram_id, resp.text)
        return resp.ok
    except requests.RequestException:
        logger.exception("Telegram notify request error for %s", telegram_id)
        return False
