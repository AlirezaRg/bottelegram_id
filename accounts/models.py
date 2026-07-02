import uuid

from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    """A user who interacts with the bot, identified by their Telegram ID."""

    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)

    # Public-facing unique slug used in the shareable verification link.
    public_slug = models.SlugField(max_length=40, unique=True, db_index=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.public_slug:
            self.public_slug = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.username or self.telegram_id}"


class VerificationStatus(models.TextChoices):
    NOT_SUBMITTED = "not_submitted", "ثبت نشده"
    PENDING = "pending", "در انتظار بررسی"
    APPROVED = "approved", "تأیید شده"
    REJECTED = "rejected", "رد شده"
    REVOKED = "revoked", "لغو شده"


class VerificationRequest(models.Model):
    """One identity-verification submission made by a user."""

    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="verification_requests"
    )
    full_name = models.CharField(max_length=128)
    country = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64, blank=True)

    # Path/file-id of the uploaded document (stored as a Telegram file_id,
    # or a path if later moved to object storage).
    document_file_id = models.CharField(max_length=255, blank=True)
    selfie_file_id = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=16, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )
    admin_note = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=128, blank=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def approve(self, reviewer: str, note: str = ""):
        self.status = VerificationStatus.APPROVED
        self.reviewed_by = reviewer
        self.admin_note = note
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_by", "admin_note", "reviewed_at"])

    def reject(self, reviewer: str, note: str = ""):
        self.status = VerificationStatus.REJECTED
        self.reviewed_by = reviewer
        self.admin_note = note
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_by", "admin_note", "reviewed_at"])

    def __str__(self):
        return f"{self.user} - {self.status}"
