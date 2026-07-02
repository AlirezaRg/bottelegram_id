from django.db import models

from accounts.models import TelegramUser


class AdCategory(models.TextChoices):
    LUGGAGE = "luggage", "بار و چمدان"
    # Future categories can be appended here without breaking existing data,
    # e.g. RIDE = "ride", "هم‌سفری" / HOUSING = "housing", "اجاره مسکن"


class Ad(models.Model):
    """A classified ad posted by a verified user (starting with luggage/baggage)."""

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING_REVIEW = "pending_review", "در انتظار تأیید"
        PUBLISHED = "published", "منتشر شده"
        EXPIRED = "expired", "منقضی شده"
        REJECTED = "rejected", "رد شده"

    owner = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="ads")
    category = models.CharField(max_length=32, choices=AdCategory.choices, default=AdCategory.LUGGAGE)

    title = models.CharField(max_length=128)
    description = models.TextField()

    origin = models.CharField(max_length=64, blank=True)
    destination = models.CharField(max_length=64, blank=True)
    travel_date = models.DateField(blank=True, null=True)
    available_weight_kg = models.PositiveIntegerField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_REVIEW)
    admin_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.owner})"
