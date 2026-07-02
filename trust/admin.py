from django.contrib import admin

from .models import TrustScoreEvent, TrustProfile, Report


@admin.register(TrustScoreEvent)
class TrustScoreEventAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "reason", "delta", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__username", "user__telegram_id")


@admin.register(TrustProfile)
class TrustProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "total_reports_against", "confirmed_reports_against", "last_recalculated")
    search_fields = ("user__username", "user__telegram_id")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "target", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reporter__username", "target__username")
    actions = ["confirm_selected", "dismiss_selected"]

    @admin.action(description="تأیید گزارش‌های انتخاب‌شده (و کسر امتیاز هدف)")
    def confirm_selected(self, request, queryset):
        from django.utils import timezone
        for report in queryset:
            report.status = Report.Status.CONFIRMED
            report.resolved_at = timezone.now()
            report.save(update_fields=["status", "resolved_at"])
            TrustScoreEvent.objects.create(
                user=report.target,
                reason=TrustScoreEvent.Reason.REPORT_CONFIRMED,
                delta=-15,
                note=f"Report #{report.id} confirmed",
            )
            profile, _ = TrustProfile.objects.get_or_create(user=report.target)
            profile.confirmed_reports_against += 1
            profile.save(update_fields=["confirmed_reports_against"])
            profile.recalculate()

    @admin.action(description="رد گزارش‌های انتخاب‌شده")
    def dismiss_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(status=Report.Status.DISMISSED, resolved_at=timezone.now())
