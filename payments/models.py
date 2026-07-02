import uuid

from django.db import models

from accounts.models import TelegramUser


class PaymentPurpose(models.TextChoices):
    VERIFICATION_FEE = "verification_fee", "هزینه تأیید هویت"
    AD_PUBLISH = "ad_publish", "انتشار آگهی"
    PREMIUM_BADGE = "premium_badge", "نشان ویژه"


class Payment(models.Model):
    """A payment transaction, gateway-agnostic (Zarinpal/IDPay/etc can plug in)."""

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        PAID = "paid", "پرداخت شده"
        FAILED = "failed", "ناموفق"
        REFUNDED = "refunded", "بازگشت داده شده"

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="payments")
    purpose = models.CharField(max_length=32, choices=PaymentPurpose.choices)
    amount_toman = models.PositiveIntegerField()

    # Unique reference we generate, sent to the gateway as order id.
    reference_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    gateway = models.CharField(max_length=32, default="zarinpal")
    gateway_authority = models.CharField(max_length=128, blank=True)
    gateway_ref_id = models.CharField(max_length=128, blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    related_object_type = models.CharField(max_length=32, blank=True)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.amount_toman} toman - {self.status}"
