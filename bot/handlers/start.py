from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from ..api_client import api_client
from ..keyboards import main_menu_kb
from .. import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    result = await api_client.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    user = result.get("user", {}) if result else {}
    slug = user.get("public_slug", "")

    welcome = (
        "سلام 👋\n\n"
        "به ربات اعتمادسنجی خوش اومدید.\n"
        "اینجا می‌تونید هویت خودتون رو تأیید کنید و یک لینک اختصاصی بگیرید "
        "که هرکسی باهاش می‌تونه وضعیت تأیید شما رو ببینه — بدون اینکه اطلاعات "
        "حساس‌تون رو فاش کنید.\n\n"
        "از منوی پایین شروع کنید 👇"
    )
    await message.answer(welcome, reply_markup=main_menu_kb())

    if slug:
        link = f"{config.PUBLIC_LINK_BASE}/{slug}"
        await message.answer(f"🔗 لینک اختصاصی شما:\n{link}")


@router.message(F.text == "🔗 لینک اختصاصی من")
async def my_link(message: Message):
    user = await api_client.get_user(message.from_user.id)
    if not user:
        await message.answer("ابتدا با /start ثبت‌نام کنید.")
        return
    link = f"{config.PUBLIC_LINK_BASE}/{user['public_slug']}"
    await message.answer(f"🔗 لینک اختصاصی شما:\n{link}\n\nاین لینک رو می‌تونید برای هرکسی بفرستید.")


_STATUS_LABELS = {
    "not_submitted": "هنوز ثبت نکردید",
    "pending": "در انتظار بررسی ⏳",
    "approved": "تأیید شده ✅",
    "rejected": "رد شده ❌",
    "revoked": "لغو شده",
}


@router.message(F.text == "⭐ امتیاز من")
async def my_score(message: Message):
    status_data = await api_client.get_status(message.from_user.id)
    if not status_data:
        await message.answer("ابتدا با /start ثبت‌نام کنید.")
        return

    label = _STATUS_LABELS.get(status_data["verification_status"], status_data["verification_status"])
    text = (
        f"📋 وضعیت تأیید هویت: <b>{label}</b>\n"
        f"⭐ امتیاز اعتماد: <b>{status_data['trust_score']}</b>\n"
        f"🚩 تعداد گزارش‌های ثبت‌شده علیه شما: <b>{status_data['total_reports_against']}</b>"
    )
    await message.answer(text)
