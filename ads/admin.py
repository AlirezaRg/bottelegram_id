from django.contrib import admin

from .models import Ad


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "category", "status", "origin", "destination", "travel_date", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "owner__username")
    actions = ["publish_selected", "reject_selected"]

    @admin.action(description="انتشار آگهی‌های انتخاب‌شده")
    def publish_selected(self, request, queryset):
        queryset.update(status=Ad.Status.PUBLISHED)

    @admin.action(description="رد آگهی‌های انتخاب‌شده")
    def reject_selected(self, request, queryset):
        queryset.update(status=Ad.Status.REJECTED)
