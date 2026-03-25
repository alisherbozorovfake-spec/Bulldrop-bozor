import logging
from aiogram import Bot, Dispatcher, types, executor
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID, CARD_NUMBER
from db import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# UC NARXLAR
prices_buy = {
    "60": 10000,
    "120": 20000,
    "240": 40000,
    "325": 52000,
    "660": 110000
}

# =========================
# START
# =========================
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (msg.from_user.id,))
    db.commit()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📤 Sotish", "📥 Sotib olish")
    kb.add("💰 Hisob", "🆘 Yordam")

    await msg.answer("Menu:", reply_markup=kb)

# =========================
# 📤 SOTISH (KANALGA TUSHADI)
# =========================
@dp.message_handler(lambda m: m.text == "📤 Sotish")
async def sell(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("60 UC", "120 UC", "240 UC", "325 UC", "660 UC")
    await msg.answer("UC tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: m.text.endswith("UC"))
async def choose_uc(msg: types.Message):
    uc = msg.text.split()[0]

    await msg.answer("Promokodni yuboring:")

    @dp.message_handler()
    async def promo_handler(m: types.Message):

        # KANALGA
        await bot.send_message(
            CHANNEL_ID,
            f"🔥 YANGI PROMOKOD\n\n👤 @{m.from_user.username}\n💎 UC: {uc}\n🔑 Kod: {m.text}"
        )

        # ADMINGA
        await bot.send_message(
            ADMIN_ID,
            f"📤 Sotish\nUser: {m.from_user.id}\nUC: {uc}\nKod: {m.text}"
        )

        await m.answer("✅ Kanalga joylandi")
        dp.message_handlers.unregister(promo_handler)

# =========================
# 📥 SOTIB OLISH
# =========================
@dp.message_handler(lambda m: m.text == "📥 Sotib olish")
async def buy(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_buy:
        kb.add(f"{k} UC")
    await msg.answer("UC tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: m.text.endswith("UC"))
async def buy_uc(msg: types.Message):
    uc = msg.text.split()[0]
    price = prices_buy.get(uc)

    if not price:
        return

    if get_balance(msg.from_user.id) < price:
        await msg.answer("❌ Mablag‘ yetarli emas")
        return

    await msg.answer("PUBG ID va Nick yuboring:")

    @dp.message_handler()
    async def finish(m: types.Message):
        minus_balance(m.from_user.id, price)

        await bot.send_message(
            ADMIN_ID,
            f"🛒 SOTIB OLISH\nUser: {m.from_user.id}\nUC: {uc}\nID+Nick: {m.text}\nSumma: {price}"
        )

        await m.answer("✅ Zayafka yuborildi")
        dp.message_handlers.unregister(finish)

# =========================
# 💰 HISOB
# =========================
@dp.message_handler(lambda m: m.text == "💰 Hisob")
async def account(msg: types.Message):
    bal = get_balance(msg.from_user.id)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ To‘ldirish", "➖ Yechish")
    kb.add("🔙 Orqaga")

    await msg.answer(f"Balans: {bal} so‘m", reply_markup=kb)

# ➕ TO‘LDIRISH
@dp.message_handler(lambda m: m.text == "➕ To‘ldirish")
async def deposit(msg: types.Message):
    await msg.answer(f"Kartaga to‘lang:\n{CARD_NUMBER}\nMin: 10000\nChek yuboring")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def check(msg: types.Message):
    await bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=f"💰 TO‘LDIRISH\nUser: {msg.from_user.id}"
    )
    await msg.answer("⏳ Adminga yuborildi")

# ➖ YECHISH
@dp.message_handler(lambda m: m.text == "➖ Yechish")
async def withdraw(msg: types.Message):
    if get_balance(msg.from_user.id) < 14000:
        await msg.answer("❌ Min 14 000 so‘m kerak")
        return

    await msg.answer("Karta raqam yuboring:")

    @dp.message_handler()
    async def finish(m: types.Message):
        minus_balance(m.from_user.id, 14000)

        await bot.send_message(
            ADMIN_ID,
            f"💸 YECHISH\nUser: {m.from_user.id}\nKarta: {m.text}\nSumma: 14000"
        )

        await m.answer("✅ Yuborildi")
        dp.message_handlers.unregister(finish)

# =========================
# 🆘 YORDAM
# =========================
@dp.message_handler(lambda m: m.text == "🆘 Yordam")
async def help_section(msg: types.Message):
    await msg.answer("Muammo yozing:")

    @dp.message_handler()
    async def help_send(m: types.Message):
        await bot.send_message(
            ADMIN_ID,
            f"🆘 Yordam\nUser:{m.from_user.id}\n{m.text}"
        )
        await m.answer("Yuborildi")
        dp.message_handlers.unregister(help_send)

# =========================
# 🔐 ADMIN PANEL
# =========================
@dp.message_handler(commands=['admin'])
async def admin(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Balans qo‘shish", "➖ Balans yechish")

    await msg.answer("Admin panel", reply_markup=kb)

# ➕ BALANS QO‘SHISH
@dp.message_handler(lambda m: m.text == "➕ Balans qo‘shish")
async def add_bal(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("UserID va summa:\n123456 10000")

    @dp.message_handler()
    async def process(m: types.Message):
        user_id, amount = m.text.split()
        add_balance(int(user_id), int(amount))

        await bot.send_message(user_id, f"✅ {amount} qo‘shildi")
        await m.answer("Qo‘shildi")
        dp.message_handlers.unregister(process)

# ➖ BALANS YECHISH
@dp.message_handler(lambda m: m.text == "➖ Balans yechish")
async def minus_bal(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("UserID va summa")

    @dp.message_handler()
    async def process(m: types.Message):
        user_id, amount = m.text.split()
        minus_balance(int(user_id), int(amount))

        await bot.send_message(user_id, f"❌ {amount} yechildi")
        await m.answer("Yechildi")
        dp.message_handlers.unregister(process)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
