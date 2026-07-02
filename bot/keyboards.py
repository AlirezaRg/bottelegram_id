from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ ثبت‌نام / تأیید هویت")],
            [KeyboardButton(text="🔗 لینک اختصاصی من"), KeyboardButton(text="⭐ امتیاز من")],
            [KeyboardButton(text="🧳 ثبت آگهی بار و چمدان"), KeyboardButton(text="🚩 گزارش تخلف")],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ انصراف")]], resize_keyboard=True)


def confirm_kb(yes_data: str, no_data: str = "cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ تأیید", callback_data=yes_data),
            InlineKeyboardButton(text="❌ انصراف", callback_data=no_data),
        ]]
    )
