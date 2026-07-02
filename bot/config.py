import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
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
