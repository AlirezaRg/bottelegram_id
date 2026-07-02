from django.shortcuts import render, get_object_or_404

from .models import TelegramUser, VerificationStatus

_STATUS_DISPLAY = {
    VerificationStatus.APPROVED: ("✅", "تأیید شده", "approved"),
    VerificationStatus.PENDING: ("⏳", "در انتظار بررسی", "pending"),
    VerificationStatus.REJECTED: ("❌", "تأیید نشده", "rejected"),
    VerificationStatus.REVOKED: ("⚠️", "لغو شده", "revoked"),
    VerificationStatus.NOT_SUBMITTED: ("➖", "هنوز تأیید نشده", "not_submitted"),
}


def public_profile_page(request, slug):
    """
    The human-readable page behind a user's shareable link
    (e.g. https://yourdomain.com/p/<slug>/). This is what people see when
    they click a link someone sent them — not the raw JSON API.
    """
    user = get_object_or_404(TelegramUser, public_slug=slug)
    latest = user.verification_requests.order_by("-submitted_at").first()
    status = latest.status if latest else VerificationStatus.NOT_SUBMITTED
    icon, label, status_code = _STATUS_DISPLAY[status]

    trust_profile = getattr(user, "trust_profile", None)

    display_name = (latest.full_name if latest and latest.status == VerificationStatus.APPROVED
                     else (user.first_name or user.username or "کاربر"))

    context = {
        "display_name": display_name,
        "username": user.username,
        "status_icon": icon,
        "status_label": label,
        "status_code": status_code,
        "trust_score": trust_profile.score if trust_profile else 0,
        "total_reports": trust_profile.total_reports_against if trust_profile else 0,
    }
    return render(request, "public/profile.html", context)
