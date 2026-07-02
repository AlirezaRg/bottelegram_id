from aiogram.fsm.state import State, StatesGroup


class VerificationForm(StatesGroup):
    full_name = State()
    country = State()
    city = State()
    document = State()
    selfie = State()


class ReportForm(StatesGroup):
    target_username = State()
    reason = State()
    evidence = State()


class AdForm(StatesGroup):
    title = State()
    description = State()
    origin = State()
    destination = State()
    weight = State()
