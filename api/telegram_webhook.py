"""
Receives Telegram updates via webhook (production mode on Render's free
tier — no separate always-on polling process needed). Telegram POSTs each
new message/click here; we hand it straight to the same aiogram Dispatcher
that would otherwise be driven by polling in local development.
"""

import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from aiogram.types import Update

from bot.dispatcher import bot, dp

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
async def telegram_webhook(request, secret):
    # The secret in the URL path stops randoms from POSTing fake updates to
    # this endpoint — only someone who knows the secret (i.e. our own
    # set_webhook.py script, which reads it from settings) can register it
    # with Telegram in the first place.
    if not settings.TELEGRAM_WEBHOOK_SECRET or secret != settings.TELEGRAM_WEBHOOK_SECRET:
        return HttpResponseForbidden("invalid secret")

    try:
        data = json.loads(request.body)
        update = Update.model_validate(data)
    except Exception:
        logger.exception("Failed to parse Telegram webhook payload")
        return HttpResponse("bad request", status=400)

    await dp.feed_update(bot, update)
    return HttpResponse("ok")
