from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..api_client import api_client
from ..keyboards import main_menu_kb, cancel_kb
from ..states import AdForm

router = Router()


@router.message(F.text == "🧳 ثبت آگهی بار و چمدان")
async def start_ad(message: Message, state: FSMContext):
    await state.set_state(AdForm.title)
    await message.answer(
        "عنوان کوتاهی برای آگهی بنویسید (مثلاً «۵ کیلو جا برای تهران-لندن»):",
        reply_markup=cancel_kb(),
    )


@router.message(AdForm.title, F.text == "❌ انصراف")
@router.message(AdForm.description, F.text == "❌ انصراف")
@router.message(AdForm.origin, F.text == "❌ انصراف")
@router.message(AdForm.destination, F.text == "❌ انصراف")
async def cancel_ad(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("لغو شد.", reply_markup=main_menu_kb())


@router.message(AdForm.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdForm.description)
    await message.answer("توضیحات کامل آگهی رو بنویسید:")


@router.message(AdForm.description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdForm.origin)
    await message.answer("مبدا سفر؟")


@router.message(AdForm.origin)
async def get_origin(message: Message, state: FSMContext):
    await state.update_data(origin=message.text.strip())
    await state.set_state(AdForm.destination)
    await message.answer("مقصد سفر؟")


@router.message(AdForm.destination)
async def get_destination(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await api_client.get_user(message.from_user.id)
    if not user:
        await message.answer("ابتدا با /start ثبت‌نام کنید.")
        await state.clear()
        return

    await api_client.create_ad(
        owner_id=user["id"],
        title=data["title"],
        description=data["description"],
        origin=data["origin"],
        destination=message.text.strip(),
    )

    await state.clear()
    await message.answer(
        "✅ آگهی شما ثبت شد و پس از تأیید ادمین منتشر می‌شه.",
        reply_markup=main_menu_kb(),
    )
