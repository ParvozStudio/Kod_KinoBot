from aiogram.fsm.state import State, StatesGroup


class WaitingCode(StatesGroup):
    """Foydalanuvchi kod kiritishini kutish holati."""
    active = State()


class AddVideo(StatesGroup):
    choosing_category = State()
    waiting_title = State()
    waiting_description = State()
    waiting_code = State()
    waiting_file = State()


class DeleteVideo(StatesGroup):
    waiting_code = State()


class AddAdmin(StatesGroup):
    waiting_id = State()


class RemoveAdmin(StatesGroup):
    waiting_id = State()


class Broadcast(StatesGroup):
    waiting_message = State()
