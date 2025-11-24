from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile


router = Router()

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛍 Каталог"),
            KeyboardButton(text="📏 Размеры"),
        ],
        [
            KeyboardButton(text="ℹ О магазине"),
            KeyboardButton(text="📞 Связаться"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие…",
)

# 🔹 Меню размеров
sizes_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1. Футболки / худи / свитшоты")],
        [KeyboardButton(text="2. Штаны / джоггеры / джинсы")],
        [KeyboardButton(text="3. Обувь")],
        [KeyboardButton(text="4. Куртки / ветровки / пуховики")],
        [KeyboardButton(text="5. Рубашки")],
        [KeyboardButton(text="6. Шорты")],
        [KeyboardButton(text="7. Трусы")],
        [KeyboardButton(text="⬅ Назад")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите категорию…",
)


# 🟣 КАТАЛОГ (из главного меню)
@router.message(F.text == "🛍 Каталог")
async def catalog_handler(message: Message):
    await message.answer(
        "Каталог скоро будет тут 😎\n"
        "Пока можешь посмотреть вещи в Telegram-канале:\n"
        "👉 @твой_канал"
    )


# 🟣 КНОПКА «📏 Размеры» — открываем меню размеров
@router.message(F.text == "📏 Размеры")
async def open_sizes_menu(message: Message):
    await message.answer(
        "Выбери категорию, для которой нужны размеры 👇",
        reply_markup=sizes_menu_kb,
    )


# 🟣 ОБРАБОТЧИКИ КАТЕГОРИЙ РАЗМЕРОВ

@router.message(F.text == "1. Футболки / худи / свитшоты")
async def sizes_tshirts(message: Message):
    photo = FSInputFile("data/images/sizefutbolka.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: футболки / худи / свитшоты",
    )


@router.message(F.text == "2. Штаны / джоггеры / джинсы")
async def sizes_pants(message: Message):
    photo = FSInputFile("data/images/sizeshtani.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: штаны / джоггеры / джинсы",
    )



@router.message(F.text == "3. Обувь")
async def sizes_shoes(message: Message):
    photo = FSInputFile("data/images/sizeobyv.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: обувь",
    )


@router.message(F.text == "4. Куртки / ветровки / пуховики")
async def sizes_outerwear(message: Message):
    photo = FSInputFile("data/images/sizekurtka.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: куртки / ветровки / пуховики",
    )


@router.message(F.text == "5. Рубашки")
async def sizes_shirts(message: Message):
    photo = FSInputFile("data/images/sizerubashka.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: рубашки",
    )


@router.message(F.text == "6. Шорты")
async def sizes_shorts(message: Message):
    photo = FSInputFile("data/images/sizeshorti.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: шорты",
    )


@router.message(F.text == "7. Нижнее белье")
async def sizes_underwear(message: Message):
    photo = FSInputFile("data/images/sizetryci.png")
    await message.answer_photo(
        photo,
        caption="Размерная сетка: нижнее бельё",
    )


# 🟣 КНОПКА «⬅ Назад» — возвращаем главное меню

@router.message(F.text == "⬅ Назад")
async def back_to_main_menu(message: Message):
    await message.answer(
        "Вернулся в главное меню 👇",
        reply_markup=main_menu_kb,
    )


# 🟣 ПРОЧЕЕ ИЗ ГЛАВНОГО МЕНЮ

@router.message(F.text == "ℹ О магазине")
async def about_handler(message: Message):
    await message.answer(
        "Casta Shop — студенческий магазин одежды из Китая 🇨🇳\n\n"
        "• Везём с Taobao, Pinduoduo и др.\n"
        "• Делаем живые фото вещей\n"
        "• Помогаем с размером\n\n"
        "Заказы можно оформить через бота или в Telegram-канале."
    )


@router.message(F.text == "📞 Связаться")
async def contact_handler(message: Message):
    await message.answer(
        "По всем вопросам пиши сюда:\n"
        "👉 @yaroslaaavkaa\n\n"
        "Отвечу по размеру, наличию, доставке и т.д."
    )