from django.contrib import admin
from django.utils.html import format_html

from .models import TelegramUser, VerificationRequest
from .telegram_files import get_telegram_file_url


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_id", "username", "first_name", "last_name", "is_blocked", "created_at")
    search_fields = ("telegram_id", "username", "first_name", "last_name", "phone_number")
    list_filter = ("is_blocked", "created_at")
    readonly_fields = ("public_slug", "created_at", "updated_at")


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "status", "submitted_at", "reviewed_by")
    list_filter = ("status",)
    search_fields = ("full_name", "user__username", "user__telegram_id")
    readonly_fields = ("submitted_at", "document_preview", "selfie_preview")
    fields = (
        "user", "full_name", "country", "city",
        "document_file_id", "document_preview",
        "selfie_file_id", "selfie_preview",
        "status", "admin_note", "reviewed_by", "reviewed_at", "submitted_at",
    )
    actions = ["approve_selected", "reject_selected"]

    def _preview(self, file_id):
        url = get_telegram_file_url(file_id)
        if not url:
            return "— (لینک قابل بازیابی نیست؛ ممکنه توکن ربات تنظیم نشده باشه یا فایل منقضی شده باشه)"
        return format_html(
            '<a href="{0}" target="_blank">'
            '<img src="{0}" style="max-width:320px;max-height:320px;border-radius:8px;" />'
            "</a>",
            url,
        )

    @admin.display(description="پیش‌نمایش مدرک شناسایی")
    def document_preview(self, obj):
        return self._preview(obj.document_file_id)

    @admin.display(description="پیش‌نمایش سلفی")
    def selfie_preview(self, obj):
        return self._preview(obj.selfie_file_id)

    @admin.action(description="تأیید درخواست‌های انتخاب‌شده")
    def approve_selected(self, request, queryset):
        # Notification to the user is handled automatically by the
        # post_save signal in accounts/signals.py — no need to duplicate it here.
        for vr in queryset:
            vr.approve(reviewer=request.user.username or "admin")

    @admin.action(description="رد درخواست‌های انتخاب‌شده")
    def reject_selected(self, request, queryset):
        for vr in queryset:
            vr.reject(reviewer=request.user.username or "admin")
