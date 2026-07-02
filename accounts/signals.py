"""
Catches verification status changes regardless of how they happen (bulk admin
action, single object edit+save, or future API endpoint) and ensures the
user gets notified exactly once per transition — without duplicating the
notify call in every possible code path.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import VerificationRequest, VerificationStatus
from .notify import send_telegram_message

_STATUS_MESSAGES = {
    VerificationStatus.APPROVED: (
        "✅ <b>هویت شما تأیید شد!</b>\n\n"
        "حالا می‌تونید لینک اختصاصی‌تون رو برای دیگران بفرستید."
    ),
    VerificationStatus.REJECTED: (
        "❌ <b>درخواست تأیید هویت شما رد شد.</b>\n\n"
        "لطفاً مدارک خودتون رو بررسی و دوباره از طریق ربات اقدام کنید."
    ),
}


@receiver(pre_save, sender=VerificationRequest)
def _capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = VerificationRequest.objects.get(pk=instance.pk).status
        except VerificationRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=VerificationRequest)
def _notify_on_status_change(sender, instance, created, **kwargs):
    if created:
        return
    old_status = getattr(instance, "_old_status", None)
    if old_status == instance.status:
        return
    message = _STATUS_MESSAGES.get(instance.status)
    if message:
        send_telegram_message(instance.user.telegram_id, message)
