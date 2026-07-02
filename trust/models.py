from django.db import models
from django.utils import timezone

from accounts.models import TelegramUser


class TrustScoreEvent(models.Model):
    """An individual event that adjusts a user's trust score (audit trail)."""

    class Reason(models.TextChoices):
        VERIFIED = "verified", "تأیید هویت"
        POSITIVE_REVIEW = "positive_review", "بازخورد مثبت دیگران"
        SUCCESSFUL_DEAL = "successful_deal", "معامله موفق"
        REPORT_RECEIVED = "report_received", "ثبت گزارش تخلف علیه کاربر"
        REPORT_CONFIRMED = "report_confirmed", "تأیید گزارش تخلف توسط ادمین"
        MANUAL_ADMIN = "manual_admin", "تنظیم دستی توسط ادمین"

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="score_events")
    reason = models.CharField(max_length=32, choices=Reason.choices)
    delta = models.IntegerField(help_text="Positive or negative point change")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} {self.delta:+d} ({self.reason})"


class TrustProfile(models.Model):
    """Aggregated, denormalized score per user — fast to read for the bot/admin."""

    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name="trust_profile")
    score = models.IntegerField(default=0)
    total_reports_against = models.PositiveIntegerField(default=0)
    confirmed_reports_against = models.PositiveIntegerField(default=0)
    last_recalculated = models.DateTimeField(default=timezone.now)

    def recalculate(self):
        agg = self.user.score_events.aggregate(total=models.Sum("delta"))
        self.score = agg["total"] or 0
        self.last_recalculated = timezone.now()
        self.save(update_fields=["score", "last_recalculated"])

    def __str__(self):
        return f"{self.user} -> {self.score}"


class Report(models.Model):
    """A complaint/violation report filed by one user against another."""

    class Status(models.TextChoices):
        OPEN = "open", "در حال بررسی"
        CONFIRMED = "confirmed", "تأیید شده"
        DISMISSED = "dismissed", "رد شده"

    reporter = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="reports_filed"
    )
    target = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="reports_received"
    )
    reason = models.TextField()
    evidence_file_id = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    admin_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report {self.reporter} -> {self.target} [{self.status}]"
