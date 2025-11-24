from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import json
import os

router = Router()

USERS_CART_PATH = "data/cart.json"

ORDERS_PATH = "data/orders.json"


def load_orders():
    if not os.path.exists(ORDERS_PATH):
        return {"last_id": 0, "orders": []}
    with open(ORDERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_orders(data):
    with open(ORDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_cart():
    if not os.path.exists(USERS_CART_PATH):
        return {}
    with open(USERS_CART_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cart(data):
    with open(USERS_CART_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# --------- СОСТОЯНИЕ ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА ---------

class OrderStates(StatesGroup):
    waiting_for_contact = State()


# --------- ДОБАВЛЕНИЕ ТОВАРА В КОРЗИНУ ---------

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    product_id = callback.data.replace("add_to_cart_", "")
    user_id = str(callback.from_user.id)

    cart = load_cart()

    if user_id not in cart:
        cart[user_id] = []

    cart[user_id].append(product_id)
    save_cart(cart)

    await callback.answer("Добавлено в корзину 🛒", show_alert=False)


# --------- ПОКАЗАТЬ КОРЗИНУ (кнопка 🛒 Корзина или /cart) ---------

@router.message(F.text == "🛒 Корзина")
@router.message(F.text == "/cart")
async def show_cart(message: Message):
    user_id = str(message.from_user.id)
    cart = load_cart()

    if user_id not in cart or len(cart[user_id]) == 0:
        await message.answer("Корзина пустая 🛒")
        return

    # Загружаем каталог, чтобы получить данные товаров
    from handlers.menu import load_catalog
    catalog = load_catalog()

    text = "🛒 Твоя корзина:\n\n"
    total = 0

    for product_id in cart[user_id]:
        for cat_items in catalog.get("categories", {}).values():
            for p in cat_items:
                if str(p["id"]) == product_id:
                    text += f"• {p['title']} — {p['price']} ₽\n"
                    total += int(p["price"])

    text += f"\nИтого: {total} ₽\n\n"
    text += "Если всё ок, нажми кнопку ниже, чтобы оформить заказ 👇"

    # 🔹 Инлайн-кнопка "Оформить заказ"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧾 Оформить заказ", callback_data="start_order")]
        ]
    )

    await message.answer(text, reply_markup=kb)


# --------- НАЖАЛИ "🧾 Оформить заказ" ---------

@router.callback_query(F.data == "start_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    cart = load_cart()

    if user_id not in cart or len(cart[user_id]) == 0:
        await callback.answer("Ваша корзина пуста", show_alert=True)
        return

    await state.set_state(OrderStates.waiting_for_contact)
    await callback.message.answer(
        "Напиши, пожалуйста, как к тебе обращаться и как с тобой связаться "
        "(телега @юзернейм или номер телефона):"
    )
    await callback.answer()


# --------- ПОЛУЧАЕМ КОНТАКТ И ОТПРАВЛЯЕМ ЗАКАЗ АДМИНУ ---------

@router.message(OrderStates.waiting_for_contact)
async def process_contact(message: Message, state: FSMContext):
    contact_text = message.text
    user_id = str(message.from_user.id)

    cart = load_cart()

    if user_id not in cart or len(cart[user_id]) == 0:
        await message.answer("Похоже, корзина уже пустая 🛒")
        await state.clear()
        return

    from handlers.menu import load_catalog
    from handlers.admin import ADMIN_ID  # используем тот же ADMIN_ID, что и в админке

    catalog = load_catalog()

    # считаем сумму и собираем список товаров
    items = []
    total = 0

    for product_id in cart[user_id]:
        for cat_items in catalog.get("categories", {}).values():
            for p in cat_items:
                if str(p["id"]) == product_id:
                    items.append({
                        "id": p["id"],
                        "title": p["title"],
                        "price": int(p["price"])
                    })
                    total += int(p["price"])

    # загружаем существующие заказы
    orders_data = load_orders()
    last_id = orders_data.get("last_id", 0)
    new_id = last_id + 1

    # готовим структуру заказа
    order = {
        "id": new_id,
        "user_id": user_id,
        "username": message.from_user.username,
        "contact": contact_text,
        "items": items,
        "total": total,
        "status": "new"  # 🟡 Новый
    }

    orders_data["last_id"] = new_id
    orders_data.setdefault("orders", []).append(order)
    save_orders(orders_data)

    # формируем текст для админа
    order_text = f"🆕 Новый заказ #{new_id}\n\n"
    order_text += f"👤 Пользователь: @{message.from_user.username or 'без username'} (ID: {user_id})\n"
    order_text += f"📞 Контакты: {contact_text}\n\n"
    order_text += "🛒 Товары:\n"

    for item in items:
        order_text += f"• {item['title']} — {item['price']} ₽\n"

    order_text += f"\n💰 Итого: {total} ₽\n"
    order_text += f"Статус: 🟡 Новый\n\n"
    order_text += f"Чтобы изменить статус: /setstatus {new_id} processing|shipped|done"

    # отправляем заказ тебе как админу
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    ...
    # ...

    # 🔹 Клавиатура статусов для админа
    status_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟠 В обработке",
                    callback_data=f"order_status_{new_id}_processing"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛫 Отправлен",
                    callback_data=f"order_status_{new_id}_shipped"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🟢 Завершён",
                    callback_data=f"order_status_{new_id}_done"
                )
            ],
        ]
    )

    # отправляем заказ тебе как админу
    await message.bot.send_message(ADMIN_ID, order_text, reply_markup=status_kb)

    # очищаем корзину пользователя
    cart[user_id] = []
    save_cart(cart)

    await message.answer(
        f"Спасибо! ✅\n\n"
        f"Твой заказ оформлен.\n"
        f"Номер заказа: #{new_id}\n"
        f"Я свяжусь с тобой по указанным контактам."
    )

    await state.clear()

@router.message(F.text == "/myorders")
@router.message(F.text == "🧾 Мои заказы")
async def my_orders(message: Message):
    user_id = str(message.from_user.id)
    data = load_orders()
    orders = data.get("orders", [])

    user_orders = [o for o in orders if o["user_id"] == user_id]

    if not user_orders:
        return await message.answer("У тебя пока нет заказов 🙂")

    status_map = {
        "new": "🟡 Новый",
        "processing": "🟠 В обработке",
        "shipped": "🛫 Отправлен",
        "done": "🟢 Завершён",
    }

    lines = ["<b>Твои заказы:</b>\n"]

    # показываем последние 5
    for o in user_orders[-5:]:
        status_text = status_map.get(o["status"], o["status"])
        lines.append(
            f"#{o['id']} — {status_text} — {o['total']} ₽"
        )

    await message.answer("\n".join(lines))

