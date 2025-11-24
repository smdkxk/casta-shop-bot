from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from .menu import get_main_menu_kb


router = Router()


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    kb = get_main_menu_kb(message.from_user.id)

    await message.answer(
        "Привет! Это *Casta Shop Bot*.\n\n"
        "Выбери действие в меню:",
        parse_mode="Markdown",
        reply_markup=kb
    )
