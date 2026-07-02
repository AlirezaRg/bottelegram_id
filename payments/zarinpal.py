"""
Minimal Zarinpal payment gateway client (REST API v4).
Docs: https://docs.zarinpal.com/paymentGateway/

Two-step flow:
  1. request_payment()  -> get an "authority" + redirect the user to Zarinpal's page
  2. verify_payment()   -> after the user pays and is redirected back, confirm it
"""

import requests
from django.conf import settings

ZARINPAL_BASE = "https://api.zarinpal.com/pg/v4/payment"
ZARINPAL_STARTPAY = "https://www.zarinpal.com/pg/StartPay"


class ZarinpalError(Exception):
    pass


def request_payment(amount_toman: int, description: str, callback_url: str,
                     mobile: str = "", email: str = "") -> str:
    """
    Starts a payment and returns the authority code needed to build the
    redirect URL. Raises ZarinpalError if the gateway rejects the request.
    """
    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        # Zarinpal expects amount in Rial, not Toman — multiply by 10.
        "amount": amount_toman * 10,
        "description": description,
        "callback_url": callback_url,
    }
    if mobile:
        payload["metadata"] = {"mobile": mobile}
    if email:
        payload.setdefault("metadata", {})["email"] = email

    resp = requests.post(f"{ZARINPAL_BASE}/request.json", json=payload, timeout=15)
    data = resp.json()

    errors = data.get("errors")
    if errors:
        raise ZarinpalError(str(errors))

    authority = data["data"]["authority"]
    return authority


def build_redirect_url(authority: str) -> str:
    return f"{ZARINPAL_STARTPAY}/{authority}"


def verify_payment(amount_toman: int, authority: str) -> dict:
    """
    Confirms a payment after the user is redirected back from Zarinpal.
    Returns the gateway's response dict (contains ref_id on success).
    Raises ZarinpalError if verification fails.
    """
    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": amount_toman * 10,
        "authority": authority,
    }
    resp = requests.post(f"{ZARINPAL_BASE}/verify.json", json=payload, timeout=15)
    data = resp.json()

    errors = data.get("errors")
    if errors:
        raise ZarinpalError(str(errors))

    return data["data"]
