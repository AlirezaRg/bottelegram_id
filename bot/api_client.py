"""
Thin async HTTP client the bot uses to talk to the Django backend.
Keeping all API calls in one place makes it easy to swap transport later
(e.g. move from REST to gRPC) without touching handler logic.
"""

import aiohttp

from . import config


class APIClient:
    def __init__(self):
        self._headers = {"X-Bot-Api-Key": config.BOT_API_KEY}

    async def _request(self, method: str, path: str, **kwargs):
        url = f"{config.API_BASE_URL}{path}"
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.request(method, url, **kwargs) as resp:
                data = await resp.json()
                return resp.status, data

    async def get_or_create_user(self, telegram_id: int, username: str, first_name: str, last_name: str):
        status, data = await self._request(
            "POST",
            "/users/get-or-create/",
            json={
                "telegram_id": telegram_id,
                "username": username or "",
                "first_name": first_name or "",
                "last_name": last_name or "",
            },
        )
        return data

    async def get_user(self, telegram_id: int):
        status, data = await self._request("GET", f"/users/{telegram_id}/")
        return data if status == 200 else None

    async def get_status(self, telegram_id: int):
        status, data = await self._request("GET", f"/users/status/{telegram_id}/")
        return data if status == 200 else None

    async def lookup_by_username(self, username: str):
        status, data = await self._request("GET", f"/users/by-username/{username}/")
        return data if status == 200 else None

    async def submit_verification(self, user_id: int, full_name: str, country: str, city: str,
                                   document_file_id: str = "", selfie_file_id: str = ""):
        status, data = await self._request(
            "POST",
            "/verifications/",
            json={
                "user": user_id,
                "full_name": full_name,
                "country": country,
                "city": city,
                "document_file_id": document_file_id,
                "selfie_file_id": selfie_file_id,
            },
        )
        return data

    async def file_report(self, reporter_id: int, target_id: int, reason: str, evidence_file_id: str = ""):
        status, data = await self._request(
            "POST",
            "/reports/",
            json={
                "reporter": reporter_id,
                "target": target_id,
                "reason": reason,
                "evidence_file_id": evidence_file_id,
            },
        )
        return data

    async def create_ad(self, owner_id: int, title: str, description: str, category: str = "luggage", **extra):
        payload = {"owner": owner_id, "title": title, "description": description, "category": category}
        payload.update(extra)
        status, data = await self._request("POST", "/ads/", json=payload)
        return data

    async def get_public_profile(self, slug: str):
        status, data = await self._request("GET", f"/public/{slug}/")
        return data if status == 200 else None


api_client = APIClient()
