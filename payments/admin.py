from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "purpose", "amount_toman", "status", "gateway", "created_at", "paid_at")
    list_filter = ("status", "purpose", "gateway")
    search_fields = ("user__username", "reference_code", "gateway_ref_id")
    readonly_fields = ("reference_code", "created_at")
