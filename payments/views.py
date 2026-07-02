from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Payment
from .zarinpal import request_payment, build_redirect_url, verify_payment, ZarinpalError


def start_payment(request, reference_code):
    """
    Entry point that kicks the user over to Zarinpal's payment page.
    Typically reached via a link the bot sends, e.g.:
        https://yourdomain.com/pay/<reference_code>/start/
    """
    payment = Payment.objects.filter(reference_code=reference_code, status=Payment.Status.PENDING).first()
    if not payment:
        return render(request, "payments/error.html", {"message": "تراکنش پیدا نشد یا قبلاً پردازش شده."})

    callback_url = request.build_absolute_uri(
        reverse("payment-callback", kwargs={"reference_code": payment.reference_code})
    )

    try:
        authority = request_payment(
            amount_toman=payment.amount_toman,
            description=payment.get_purpose_display(),
            callback_url=callback_url,
        )
    except ZarinpalError as e:
        return render(request, "payments/error.html", {"message": f"خطا در اتصال به درگاه پرداخت: {e}"})

    payment.gateway_authority = authority
    payment.save(update_fields=["gateway_authority"])

    return redirect(build_redirect_url(authority))


@csrf_exempt
def payment_callback(request, reference_code):
    """Zarinpal redirects the user's browser back here after they pay (or cancel)."""
    payment = Payment.objects.filter(reference_code=reference_code).first()
    if not payment:
        return render(request, "payments/error.html", {"message": "تراکنش پیدا نشد."})

    status_param = request.GET.get("Status")
    authority = request.GET.get("Authority", payment.gateway_authority)

    if status_param != "OK":
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        return render(request, "payments/result.html", {"success": False, "payment": payment})

    try:
        result = verify_payment(amount_toman=payment.amount_toman, authority=authority)
    except ZarinpalError:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        return render(request, "payments/result.html", {"success": False, "payment": payment})

    payment.status = Payment.Status.PAID
    payment.gateway_ref_id = str(result.get("ref_id", ""))
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "gateway_ref_id", "paid_at"])

    # Hook point: this is where you'd trigger whatever the payment unlocks
    # (e.g. publish the ad, grant the premium badge) based on
    # payment.purpose / payment.related_object_type — left for the
    # next iteration once the specific unlock-logic per purpose is decided.

    return render(request, "payments/result.html", {"success": True, "payment": payment})
