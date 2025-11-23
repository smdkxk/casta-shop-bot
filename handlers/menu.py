from aiogram import Router, types

router = Router()

@router.message()
async def menu_handler(message: types.Message):
    text = message.text

    if text == "ℹ О магазине":
        await message.answer(
            "Casta Shop — магазин студента РЭУ.\n"
            "Привожу одежду из Китая, проверяю качество.\n"
            "Низкие цены, быстрые поставки.\n\n"
            "Выбери другой пункт меню."
        )

    elif text == "🛍 Каталог":
        await message.answer(
            "Каталог пока пуст. Скоро добавим товары 👀"
        )

    elif text == "📏 Размеры":
        await message.answer(
            "Размерные сетки скоро будут добавлены 📐"
        )

    else:
        await message.answer("Не понял команду 🤔")