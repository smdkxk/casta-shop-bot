from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
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

    # формируем текст заказа
    order_text = "🆕 Новый заказ\n\n"
    order_text += f"👤 Пользователь: @{message.from_user.username or 'без username'} (ID: {user_id})\n"
    order_text += f"📞 Контакты(@твой юзернейм): {contact_text}\n\n"
    order_text += "🛒 Товары:\n"

    total = 0
    for product_id in cart[user_id]:
        for cat_items in catalog.get("categories", {}).values():
            for p in cat_items:
                if str(p["id"]) == product_id:
                    order_text += f"• {p['title']} — {p['price']} ₽\n"
                    total += int(p["price"])

    order_text += f"\n💰 Итого: {total} ₽"

    # отправляем заказ тебе как админу
    await message.bot.send_message(ADMIN_ID, order_text)

    # очищаем корзину пользователя
    cart[user_id] = []
    save_cart(cart)

    await message.answer(
        "Спасибо! ✅\n\n"
        "Твой заказ отправлен, скоро я с тобой свяжусь по указанным контактам."
    )

    await state.clear()

