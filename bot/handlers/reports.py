from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..api_client import api_client
from ..keyboards import main_menu_kb, cancel_kb
from ..states import ReportForm

router = Router()


@router.message(F.text == "🚩 گزارش تخلف")
async def start_report(message: Message, state: FSMContext):
    await state.set_state(ReportForm.target_username)
    await message.answer(
        "یوزرنیم تلگرام شخصی که می‌خواید گزارش بدید رو وارد کنید (مثال: @username):",
        reply_markup=cancel_kb(),
    )


@router.message(ReportForm.target_username, F.text == "❌ انصراف")
@router.message(ReportForm.reason, F.text == "❌ انصراف")
async def cancel_report(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("لغو شد.", reply_markup=main_menu_kb())


@router.message(ReportForm.target_username)
async def get_target(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    target = await api_client.lookup_by_username(username)

    if not target:
        await message.answer(
            "❗ این کاربر پیدا نشد. توجه کنید این شخص باید قبلاً حداقل یک‌بار "
            "ربات رو با /start باز کرده باشه تا توی سیستم ثبت شده باشه.\n\n"
            "یوزرنیم رو دوباره وارد کنید یا «❌ انصراف» رو بزنید:"
        )
        return

    reporter = await api_client.get_user(message.from_user.id)
    if reporter and target["telegram_id"] == reporter["telegram_id"]:
        await message.answer("نمی‌تونید خودتون رو گزارش بدید 🙂 یوزرنیم دیگه‌ای وارد کنید:")
        return

    await state.update_data(target_id=target["id"], target_username=username)
    await state.set_state(ReportForm.reason)
    await message.answer(f"دلیل گزارش علیه @{username} رو به‌طور کامل توضیح بدید:")


@router.message(ReportForm.reason)
async def get_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    reporter = await api_client.get_user(message.from_user.id)

    if not reporter:
        await message.answer("ابتدا با /start ثبت‌نام کنید.")
        await state.clear()
        return

    await api_client.file_report(
        reporter_id=reporter["id"],
        target_id=data["target_id"],
        reason=message.text.strip(),
    )

    await message.answer(
        "✅ گزارش شما ثبت شد و توسط تیم بررسی می‌شه.\n"
        "از همکاری شما برای امن‌تر شدن جامعه متشکریم.",
        reply_markup=main_menu_kb(),
    )
    await state.clear()
