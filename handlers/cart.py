from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import json
import os

router = Router()

USERS_CART_PATH = "data/cart.json"


def load_cart():
    if not os.path.exists(USERS_CART_PATH):
        return {}
    with open(USERS_CART_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cart(data):
    with open(USERS_CART_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# 🔹 Добавление товара в корзину
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


# 🔹 Команда /cart — показать корзину
@router.message(F.text == "🛒 Корзина")
@router.message(F.text == "/cart")
async def show_cart(message: Message):
    user_id = str(message.from_user.id)
    cart = load_cart()

    if user_id not in cart or len(cart[user_id]) == 0:
        await message.answer("Корзина пустая 🛒")
        return

    # Загружаем каталог
    from handlers.menu import load_catalog
    catalog = load_catalog()

    text = "🛒 Твоя корзина:\n\n"
    total = 0

    for product_id in cart[user_id]:
        for cat_items in catalog.get("categories", {}).values():
            for p in cat_items:
                if str(p["id"]) == product_id:
                    text += f"• {p['title']} — {p['price']} ₽\n"
                    total += int(p['price'])

    text += f"\nИтого: {total} ₽\n\n"
    text += "Чтобы оформить заказ, нажми:\n👉 /order"

    await message.answer(text)
