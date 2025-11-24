from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from handlers.cart import load_orders, save_orders

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

@router.callback_query(F.data.startswith("order_status_"))
async def change_order_status_cb(callback: CallbackQuery):
    # Проверяем, что нажал именно админ
    if not is_admin(callback.from_user.id):
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    # Формат: order_status_<id>_<status>
    parts = callback.data.split("_")
    if len(parts) != 4:
        return await callback.answer("Некорректные данные", show_alert=True)

    try:
        order_id = int(parts[2])
    except ValueError:
        return await callback.answer("Некорректный ID", show_alert=True)

    new_status = parts[3]
    allowed = ["new", "processing", "shipped", "done"]
    if new_status not in allowed:
        return await callback.answer("Некорректный статус", show_alert=True)

    data = load_orders()
    orders = data.get("orders", [])

    target_order = None
    for o in orders:
        if o["id"] == order_id:
            target_order = o
            break

    if not target_order:
        return await callback.answer(f"Заказ #{order_id} не найден", show_alert=True)

    target_order["status"] = new_status
    save_orders(data)

    status_map = {
        "new": "🟡 Новый",
        "processing": "🟠 В обработке",
        "shipped": "🛫 Отправлен",
        "done": "🟢 Завершён",
    }
    status_text = status_map.get(new_status, new_status)

    # Обновим подпись (если хочешь – можно отредактировать msg)
    await callback.answer(f"Статус: {status_text}")

    # Уведомим пользователя
    try:
        user_id = int(target_order["user_id"])
        await callback.message.bot.send_message(
            user_id,
            f"🔔 Обновление статуса заказа #{order_id}:\n{status_text}"
        )
    except Exception:
        # если не получилось отправить — просто молчим
        pass


@router.message(F.text == "/orders")
async def list_orders(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа")

    data = load_orders()
    orders = data.get("orders", [])

    if not orders:
        return await message.answer("Пока нет ни одного заказа.")

    # показываем последние 10
    last_orders = orders[-10:]

    status_map = {
        "new": "🟡 Новый",
        "processing": "🟠 В обработке",
        "shipped": "🛫 Отправлен",
        "done": "🟢 Завершён",
    }

    lines = ["<b>Последние заказы:</b>\n"]

    for o in last_orders:
        status_emoji = status_map.get(o["status"], o["status"])
        lines.append(
            f"#{o['id']} — {status_emoji} — {o['total']} ₽\n"
            f"👤 @{o.get('username') or 'без username'} (ID: {o['user_id']})"
        )
        lines.append("")  # пустая строка

    await message.answer("\n".join(lines))

    @router.message(F.text.startswith("/setstatus"))
    async def set_order_status(message: Message):
        if not is_admin(message.from_user.id):
            return await message.answer("⛔ У вас нет доступа")

        parts = message.text.split()

        if len(parts) != 3:
            return await message.answer(
                "Использование:\n"
                "/setstatus <id> <status>\n\n"
                "Статусы: new, processing, shipped, done"
            )

        try:
            order_id = int(parts[1])
        except ValueError:
            return await message.answer("ID заказа должен быть числом.")

        new_status = parts[2].strip().lower()
        allowed = ["new", "processing", "shipped", "done"]

        if new_status not in allowed:
            return await message.answer(
                "Неверный статус.\nДопустимые: new, processing, shipped, done"
            )

        data = load_orders()
        orders = data.get("orders", [])

        target_order = None
        for o in orders:
            if o["id"] == order_id:
                target_order = o
                break

        if not target_order:
            return await message.answer(f"Заказ #{order_id} не найден.")

        target_order["status"] = new_status
        save_orders(data)

        # карта для красивого текста
        status_map = {
            "new": "🟡 Новый",
            "processing": "🟠 В обработке",
            "shipped": "🛫 Отправлен",
            "done": "🟢 Завершён",
        }
        status_text = status_map[new_status]

        await message.answer(f"Статус заказа #{order_id} изменён на: {status_text}")

        # уведомим пользователя
        try:
            user_id = int(target_order["user_id"])
            await message.bot.send_message(
                user_id,
                f"🔔 Обновление статуса заказа #{order_id}:\n{status_text}"
            )
        except Exception:
            # если не получилось отправить (юзер заблокал бота и т.п.) — просто молчим
            pass



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

@router.callback_query(F.data == "admin_list_items")
async def admin_list_items(callback):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)

    catalog = load_catalog()
    categories = catalog.get("categories", {})

    if not categories or all(len(items) == 0 for items in categories.values()):
        await callback.message.answer("📭 В каталоге пока нет ни одного товара.")
        return await callback.answer()

    text_lines = ["📦 <b>Список товаров:</b>\n"]

    name_map = {
        "shorts": "Шорты",
        "pants": "Штаны",
        "tshirts": "Футболки",
        "hoodies": "Кофты / худи",
        "jackets": "Куртки",
        "hats": "Головные уборы",
        "accessories": "Аксессуары",
    }

    for key, items in categories.items():
        if not items:
            continue

        cat_name = name_map.get(key, key)
        text_lines.append(f"🗂 <b>{cat_name}</b>:")

        for product in items:
            text_lines.append(
                f"  • #{product['id']} — {product['title']} ({product['price']})"
            )

        text_lines.append("")  # пустая строка между категориями

    await callback.message.answer("\n".join(text_lines))
    await callback.answer()

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

    # 🔹 ГЛОБАЛЬНЫЙ ID ТОВАРА
    max_id = 0
    for items in catalog["categories"].values():
        for p in items:
            if p["id"] > max_id:
                max_id = p["id"]
    new_id = max_id + 1

    product = {
        "id": new_id,
        "title": title,
        "price": price,
        "description": description,
        "photo_file_id": photo_file_id,
        "category": category,
    }

    catalog["categories"][category].append(product)
    save_catalog(catalog)

    await state.clear()

    await message.answer(
        "✅ Товар добавлен!\n\n"
        f"ID: {new_id}\n"
        f"Категория: {category}\n"
        f"Название: {title}\n"
        f"Цена: {price}\n"
        f"Описание: {description}"
    )

    await state.clear()

    await message.answer(
        "✅ Товар добавлен!\n\n"
        f"Категория: {category}\n"
        f"Название: {title}\n"
        f"Цена: {price}\n"
        f"Описание: {description}"
    )

@router.message(F.text.startswith("/del"))
async def delete_product(message: Message):
    """Удаление товара по ID, например: /del 5"""
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ У вас нет доступа")

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        return await message.answer("Использование: /del <ID_товара>\nНапример: /del 5")

    target_id = int(parts[1])

    catalog = load_catalog()
    categories = catalog.get("categories", {})

    found = False
    found_cat = None
    found_title = None

    # Ищем товар по всем категориям
    for cat_key, items in categories.items():
        for idx, product in enumerate(items):
            if product["id"] == target_id:
                found = True
                found_cat = cat_key
                found_title = product["title"]
                # Удаляем товар
                del items[idx]
                break
        if found:
            break

    if not found:
        return await message.answer(f"❌ Товар с ID {target_id} не найден.")

    # сохраняем обновлённый каталог
    catalog["categories"] = categories
    save_catalog(catalog)

    await message.answer(
        f"🗑 Товар удалён.\n\n"
        f"ID: {target_id}\n"
        f"Категория: {found_cat}\n"
        f"Название: {found_title}"
    )