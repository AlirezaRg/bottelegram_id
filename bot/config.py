import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# In webhook mode the bot handlers run inside the Django process and call back
# into the same app's REST API over HTTP. The old default (:8000) is wrong on
# Render, where the app listens on $PORT — so fall back to the deployment's own
# public URL (RENDER_EXTERNAL_URL, injected automatically) when API_BASE_URL
# isn't set explicitly. Locally this still defaults to the dev server.
_render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
_default_api_base = f"{_render_url.rstrip('/')}/api/v1" if _render_url else "http://127.0.0.1:8000/api/v1"
API_BASE_URL = os.environ.get("API_BASE_URL", _default_api_base)
BOT_API_KEY = os.environ.get("BOT_API_KEY")
PUBLIC_LINK_BASE = os.environ.get("PUBLIC_LINK_BASE", "https://yourdomain.com/p")

# Optional: if Telegram's API is blocked/unreachable directly (common from
# Iran without a VPN), set this to a local proxy address, e.g.:
#   TELEGRAM_PROXY=socks5://127.0.0.1:10808
#   TELEGRAM_PROXY=http://127.0.0.1:10809
# Leave empty if you have a system-wide VPN already routing traffic.
TELEGRAM_PROXY = os.environ.get("TELEGRAM_PROXY", "")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set — check your .env file")
if not BOT_API_KEY:
    raise RuntimeError("BOT_API_KEY is not set — check your .env file")
