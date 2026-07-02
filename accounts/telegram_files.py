"""
Resolves a Telegram file_id into a temporary, directly-viewable URL so the
admin can preview uploaded documents/selfies right inside the Django admin
panel, without manually querying the Bot API.

Note: Telegram file URLs are only valid for ~1 hour, so we don't store
them — we resolve fresh on every admin page load.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_telegram_file_url(file_id: str) -> str | None:
    if not file_id or not settings.TELEGRAM_BOT_TOKEN:
        return None

    token = settings.TELEGRAM_BOT_TOKEN
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getFile",
            params={"file_id": file_id},
            timeout=10,
        )
        data = resp.json()
        if not data.get("ok"):
            logger.warning("getFile failed for %s: %s", file_id, data)
            return None
        file_path = data["result"]["file_path"]
        return f"https://api.telegram.org/file/bot{token}/{file_path}"
    except requests.RequestException:
        logger.exception("getFile request error for %s", file_id)
        return None
