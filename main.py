import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# --- ВСТАВТЕ ВАШІ ДАНІ СЮДИ ---
API_TOKEN = '8720986706:AAHIDSo-G1LpVigxY0cHIYsKjJWBUYI1ADU'
ADMIN_ID = 7896490903  # Ваш ID з кроку 2
GROUP_EVA = -1003958248631  # ID групи з кроку 2

# Словник груп
GROUP_MAP = {
    GROUP_EVA: 'Єва'
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

orders_db = {}
stats_db = []

@dp.message_handler(lambda m: m.chat.id in GROUP_MAP)
async def handle_orders(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        data = message.text.split()
        if len(data) < 3: return

        phone, price, time = data[0], int(data[1]), data[2]
        await message.delete()

        last_three = phone[-3:]
        girl_name = GROUP_MAP[message.chat.id]
        order_key = f"{datetime.now().strftime('%H%M%S')}_{last_three}"

        keyboard = InlineKeyboardMarkup()
        btn = InlineKeyboardButton(text="✅ Клієнт прийшов", callback_data=f"done_{order_key}")
        keyboard.add(btn)

        text = (
            f"📌 **НОВИЙ БУКІНГ**\n"
            f"🔢 Номер: #{last_three}\n"
            f"🕒 Час: {time}\n"
            f"💰 Сума: {price}$\n"
            f"👤 Виконавець: {girl_name}\n"
            f"📍 Вірменія"
        )

        orders_db[order_key] = {'price': price, 'name': girl_name, 'id': last_three}
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    except:
        pass

@dp.callback_query_handler(lambda c: c.data.startswith('done_'))
async def process_done(callback_query: types.CallbackQuery):
    order_key = callback_query.data.replace('done_', '')
    if order_key in orders_db:
        order = orders_db[order_key]
        girl_name = order['name']
        stats_db.append({'price': order['price'], 'name': girl_name, 'date': datetime.now()})

        today = datetime.now().date()
        g_today = sum(item['price'] for item in stats_db if item['name'] == girl_name and item['date'].date() == today)
        g_total = sum(item['price'] for item in stats_db if item['name'] == girl_name)

        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=(
                f"✅ **Booking #{order['id']} — ВИКОНАНО**\n"
                f"👤 Виконавець: {girl_name}\n"
                f"💵 Оплата: {order['price']}$\n"
                f"--------------------------\n"
                f"📈 **Статистика {girl_name}:**\n"
                f"💰 Сьогодні: {g_today}$\n"
                f"🏦 Загальна каса: {g_total}$"
            ),
            parse_mode="Markdown"
        )
        del orders_db[order_key]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
