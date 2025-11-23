from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог")],
            [KeyboardButton(text="📏 Размеры")],
            [KeyboardButton(text="ℹ О магазине")],
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Привет! Это *Casta Shop Bot*.\n\n"
        "Выбери действие в меню:",
        parse_mode="Markdown",
        reply_markup=kb
    )
