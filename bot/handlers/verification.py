from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..api_client import api_client
from ..keyboards import main_menu_kb, cancel_kb
from ..states import VerificationForm

router = Router()


@router.message(F.text == "✅ ثبت‌نام / تأیید هویت")
async def start_verification(message: Message, state: FSMContext):
    await state.set_state(VerificationForm.full_name)
    await message.answer(
        "برای تأیید هویت، لطفاً نام و نام خانوادگی کامل خودتون رو وارد کنید:",
        reply_markup=cancel_kb(),
    )


@router.message(VerificationForm.full_name, F.text == "❌ انصراف")
@router.message(VerificationForm.country, F.text == "❌ انصراف")
@router.message(VerificationForm.city, F.text == "❌ انصراف")
async def cancel_verification(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("لغو شد.", reply_markup=main_menu_kb())


@router.message(VerificationForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(VerificationForm.country)
    await message.answer("کشور محل سکونت فعلی شما؟")


@router.message(VerificationForm.country)
async def get_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await state.set_state(VerificationForm.city)
    await message.answer("شهر محل سکونت؟")


@router.message(VerificationForm.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(VerificationForm.document)
    await message.answer(
        "حالا لطفاً عکس مدرک شناسایی‌تون (مثلاً پاسپورت یا کارت ملی) رو ارسال کنید.\n"
        "⚠️ این تصویر فقط برای بررسی ادمین استفاده می‌شه."
    )


@router.message(VerificationForm.document, F.photo)
async def get_document(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(document_file_id=file_id)
    await state.set_state(VerificationForm.selfie)
    await message.answer("یک عکس سلفی از خودتون (در کنار مدرک، ترجیحاً) ارسال کنید:")


@router.message(VerificationForm.document)
async def document_invalid(message: Message):
    await message.answer("لطفاً یک تصویر ارسال کنید، نه متن.")


@router.message(VerificationForm.selfie, F.photo)
async def get_selfie(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    data = await state.get_data()

    user = await api_client.get_user(message.from_user.id)
    if not user:
        await message.answer("خطا: ابتدا با /start ثبت‌نام کنید.")
        await state.clear()
        return

    await api_client.submit_verification(
        user_id=user["id"],
        full_name=data["full_name"],
        country=data["country"],
        city=data["city"],
        document_file_id=data["document_file_id"],
        selfie_file_id=file_id,
    )

    await state.clear()
    await message.answer(
        "✅ درخواست تأیید هویت شما ثبت شد.\n"
        "نتیجه‌ی بررسی توسط تیم پشتیبانی، طی ۲۴ تا ۴۸ ساعت اعلام می‌شه.",
        reply_markup=main_menu_kb(),
    )


@router.message(VerificationForm.selfie)
async def selfie_invalid(message: Message):
    await message.answer("لطفاً یک تصویر ارسال کنید، نه متن.")
