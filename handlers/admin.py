from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import json
import os

router = Router()

# ⚠️ ВСТАВЬ СЮДА СВОЙ TG ID
ADMIN_ID = 1120835057

CATALOG_PATH = "data/catalog.json"


# ------- Вспомогательные функции работы с JSON -------

def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        # если файла нет, создаём базовую структуру
        data = {
            "categories": {
                "shorts": [],
                "pants": [],
                "tshirts": [],
                "hoodies": [],
                "jackets": [],
                "hats": [],
                "accessories": []
            }
        }
        save_catalog(data)
        return data

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_catalog(data):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ------- Состояния для добавления товара -------

class AddProductStates(StatesGroup):
    choosing_category = State()
    entering_title = State()
    entering_price = State()
    entering_description = State()
    sending_photo = State()


# ------- Команда /admin: панель админа -------

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_item")],
            [InlineKeyboardButton(text="📦 Список товаров", callback_data="admin_list_items")]
        ]
    )

    await message.answer("🔧 Админ-панель", reply_markup=keyboard)


# ------- Нажали «➕ Добавить товар» -------

@router.callback_query(F.data == "admin_add_item")
async def admin_add_item(callback, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)

    # Клавиатура категорий
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Шорты", callback_data="cat_shorts")],
            [InlineKeyboardButton(text="Штаны", callback_data="cat_pants")],
            [InlineKeyboardButton(text="Футболки", callback_data="cat_tshirts")],
            [InlineKeyboardButton(text="Кофты (худи/свиты)", callback_data="cat_hoodies")],
            [InlineKeyboardButton(text="Куртки", callback_data="cat_jackets")],
            [InlineKeyboardButton(text="Головные уборы", callback_data="cat_hats")],
            [InlineKeyboardButton(text="Аксессуары", callback_data="cat_accessories")],
        ]
    )

    await state.set_state(AddProductStates.choosing_category)
    await callback.message.edit_text("Выбери категорию для нового товара:", reply_markup=keyboard)


# ------- Выбор категории -------

@router.callback_query(F.data.startswith("cat_"))
async def choose_category(callback, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)

    category_key = callback.data.replace("cat_", "")  # shorts / pants / tshirts ...

    await state.update_data(category=category_key)
    await state.set_state(AddProductStates.entering_title)

    await callback.message.edit_text(
        f"Категория выбрана: <b>{category_key}</b>\n\n"
        "Теперь отправь название товара (например: «Чёрный худи oversize»)."
    )


# ------- Ввод названия -------

@router.message(AddProductStates.entering_title)
async def set_title(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(title=message.text)
    await state.set_state(AddProductStates.entering_price)

    await message.answer("Отправь цену (например: 3200).")


# ------- Ввод цены -------

@router.message(AddProductStates.entering_price)
async def set_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(price=message.text)
    await state.set_state(AddProductStates.entering_description)

    await message.answer("Теперь отправь описание товара (коротко: ткань, посадка, стиль).")


# ------- Ввод описания -------

@router.message(AddProductStates.entering_description)
async def set_description(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.update_data(description=message.text)
    await state.set_state(AddProductStates.sending_photo)

    await message.answer("Теперь отправь фото товара одним сообщением.")


# ------- Приём фото -------

@router.message(AddProductStates.sending_photo)
async def set_photo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    if not message.photo:
        return await message.answer("Пожалуйста, отправь именно фото, не текст.")

    photo = message.photo[-1]
    photo_file_id = photo.file_id

    data = await state.get_data()
    category = data["category"]
    title = data["title"]
    price = data["price"]
    description = data["description"]

    catalog = load_catalog()

    # генерируем id на основе длины списка
    new_id = len(catalog["categories"][category]) + 1

    product = {
        "id": new_id,
        "title": title,
        "price": price,
        "description": description,
        "photo_file_id": photo_file_id,
        "category": category
    }

    catalog["categories"][category].append(product)
    save_catalog(catalog)

    await state.clear()

    await message.answer(
        "✅ Товар добавлен!\n\n"
        f"Категория: {category}\n"
        f"Название: {title}\n"
        f"Цена: {price}\n"
        f"Описание: {description}"
    )