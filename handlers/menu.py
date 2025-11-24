from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
import json
import os


router = Router()

CATALOG_PATH = "data/catalog.json"


def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        return {"categories": {}}
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

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
        [
            KeyboardButton(text="🛒 Корзина"),   # 👈 ДОБАВИЛИ ОТДЕЛЬНОЙ СТРОКОЙ
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
        [KeyboardButton(text="7. Нижнее белье")],
        [KeyboardButton(text="⬅ Назад")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите категорию…",
)


# 🟣 КАТАЛОГ (из главного меню)
@router.message(F.text == "🛍 Каталог")
async def catalog_handler(message: Message):
    catalog = load_catalog()
    categories = catalog.get("categories", {})

    # Названия для пользователя
    name_map = {
        "shorts": "Шорты",
        "pants": "Штаны",
        "tshirts": "Футболки",
        "hoodies": "Кофты / худи",
        "jackets": "Куртки",
        "hats": "Головные уборы",
        "accessories": "Аксессуары",
    }

    buttons = []
    for key, items in categories.items():
        if not items:  # категорию без товаров не показываем
            continue
        label = name_map.get(key, key)
        buttons.append(
            [InlineKeyboardButton(text=label, callback_data=f"user_cat_{key}")]
        )

    if not buttons:
        await message.answer("Пока в каталоге нет товаров, скоро всё появится 🙂")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выбери категорию 👇", reply_markup=kb)

@router.callback_query(F.data.startswith("user_cat_"))
async def show_category_products(callback: CallbackQuery):
    category_key = callback.data.replace("user_cat_", "")

    catalog = load_catalog()
    categories = catalog.get("categories", {})
    items = categories.get(category_key, [])

    if not items:
        await callback.answer("В этой категории пока нет товаров", show_alert=True)
        return

    # Можно красивое имя категории, как выше
    name_map = {
        "shorts": "Шорты",
        "pants": "Штаны",
        "tshirts": "Футболки",
        "hoodies": "Кофты / худи",
        "jackets": "Куртки",
        "hats": "Головные уборы",
        "accessories": "Аксессуары",
    }
    cat_name = name_map.get(category_key, category_key)

    await callback.message.answer(f"📦 Товары в категории: {cat_name}")

    for product in items:
        caption = (
            f"🛍 {product['title']}\n\n"
            f"Описание: {product['description']}\n\n"
            f"💰Цена: {product['price']} ₽\n"
            "Если интересно — напиши мне, оформим заказ 🙂"
        )

        # Отправляем по file_id, который ты сохранил в admin.py
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Добавить в корзину",
                    callback_data=f"add_to_cart_{product['id']}"
                )
            ]
        ])

        await callback.message.answer_photo(
            product["photo_file_id"],
            caption=caption,
            reply_markup=kb
        )

    await callback.answer()

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
    photo = FSInputFile("data/images/rubashka.png")
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