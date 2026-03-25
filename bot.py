from aiogram import Bot, Dispatcher, types, executor
from config import *
from db import *

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

prices_sell = {"60":7000,"120":14000,"240":28000,"325":38000,"660":77000}
prices_buy = {"60":10000,"120":20000,"240":40000,"325":52000,"660":110000}

# START
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    create_user(msg.from_user.id)
    bot_id, bal, dep = get_user(msg.from_user.id)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📤 Sotish","📥 Sotib olish")
    kb.add("💰 Hisob","📊 Statistika","🆘 Yordam")

    await msg.answer(f"Sizning ID: {bot_id}", reply_markup=kb)

# =========================
# 📤 SOTISH
# =========================
@dp.message_handler(lambda m: m.text=="📤 Sotish")
async def sell(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_sell:
        kb.add(f"{k} UC")
    await msg.answer(
        "UC tanlang\n\n⚠️ Promokod ishlatilgan bo‘lsa pul berilmaydi!",
        reply_markup=kb
    )

@dp.message_handler(lambda m: m.text.endswith("UC"))
async def uc_choose(msg: types.Message):
    uc = msg.text.split()[0]
    await msg.answer("18 belgili promokod yuboring:")

    @dp.message_handler()
    async def promo(m: types.Message):
        if len(m.text) != 18:
            await m.answer("❌ Faqat 18 belgili promokod!")
            return

        bot_id, _, _ = get_user(m.from_user.id)

        await bot.send_message(
            CHANNEL_ID,
            f"📤 SOTISH\nID:{bot_id}\nUC:{uc}\nKod:{m.text}"
        )

        await m.answer(f"✅ Yuborildi\nSiz {prices_sell[uc]} so‘m olasiz")
        dp.message_handlers.unregister(promo)

# =========================
# 📥 SOTIB OLISH
# =========================
@dp.message_handler(lambda m: m.text=="📥 Sotib olish")
async def buy(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for k in prices_buy:
        kb.add(f"{k} UC")
    await msg.answer("UC tanlang\n24 soat ichida tashlab beriladi", reply_markup=kb)

@dp.message_handler(lambda m: m.text.endswith("UC"))
async def buy2(msg: types.Message):
    uc = msg.text.split()[0]
    price = prices_buy[uc]

    bot_id, bal, _ = get_user(msg.from_user.id)

    if bal < price:
        await msg.answer("❌ Mablag‘ yetarli emas")
        return

    await msg.answer("PUBG ID + Nick yuboring:")

    @dp.message_handler()
    async def finish(m: types.Message):
        minus_balance(m.from_user.id, price)

        await bot.send_message(
            CHANNEL_ID,
            f"📥 SOTIB OLISH\nID:{bot_id}\nUC:{uc}\nNick:{m.text}"
        )

        await bot.send_message(
            ADMIN_ID,
            f"Sotib olish\nID:{bot_id}\nUC:{uc}\nNick:{m.text}"
        )

        await m.answer("✅ 24 soat ichida UC tashlanadi")
        dp.message_handlers.unregister(finish)

# =========================
# 💰 HISOB
# =========================
@dp.message_handler(lambda m: m.text=="💰 Hisob")
async def account(msg: types.Message):
    bot_id, bal, _ = get_user(msg.from_user.id)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ To‘ldirish","➖ Yechish")

    await msg.answer(f"ID:{bot_id}\nBalans:{bal}", reply_markup=kb)

# ➕ TO‘LDIRISH
@dp.message_handler(lambda m: m.text=="➕ To‘ldirish")
async def dep(msg: types.Message):
    await msg.answer(f"Karta:\n{CARD_NUMBER}\nMin:5000\nChek yuboring")

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def check(msg: types.Message):
    bot_id, _, _ = get_user(msg.from_user.id)

    await bot.send_photo(
        ADMIN_ID,
        msg.photo[-1].file_id,
        caption=f"💰 TO‘LDIRISH\nID:{bot_id}"
    )

    await msg.answer("⏳ Kuting...")

# ➖ YECHISH
@dp.message_handler(lambda m: m.text=="➖ Yechish")
async def out(msg: types.Message):
    bot_id, bal, _ = get_user(msg.from_user.id)

    if bal < 14000:
        await msg.answer("❌ Min 14000")
        return

    await msg.answer("Karta yuboring:")

    @dp.message_handler()
    async def finish(m: types.Message):
        minus_balance(m.from_user.id, 14000)

        await bot.send_message(
            ADMIN_ID,
            f"💸 YECHISH\nID:{bot_id}\nKarta:{m.text}"
        )

        await m.answer("Yuborildi")
        dp.message_handlers.unregister(finish)

# =========================
# 📊 STATISTIKA
# =========================
@dp.message_handler(lambda m: m.text=="📊 Statistika")
async def stat(msg: types.Message):
    top = top_users()
    text = "🏆 TOP DONAT:\n\n"

    for i, u in enumerate(top,1):
        text += f"{i}. ID:{u[0]} - {u[1]} so‘m\n"

    await msg.answer(text)

# =========================
# 🆘 YORDAM
# =========================
@dp.message_handler(lambda m: m.text=="🆘 Yordam")
async def help(msg: types.Message):
    await msg.answer("Muammo yozing:")

    @dp.message_handler()
    async def send(m: types.Message):
        bot_id,_,_ = get_user(m.from_user.id)

        await bot.send_message(
            ADMIN_ID,
            f"🆘 Yordam\nID:{bot_id}\nText:{m.text}"
        )

        await m.answer("Yuborildi")
        dp.message_handlers.unregister(send)

# ADMIN JAVOB
@dp.message_handler(lambda m: m.text.startswith("/javob"))
async def reply(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    _, bot_id, text = msg.text.split(" ",2)

    cursor.execute("SELECT user_id FROM users WHERE bot_id=?", (bot_id,))
    user = cursor.fetchone()

    if user:
        await bot.send_message(user[0], f"Admin:\n{text}")

# RUN
executor.start_polling(dp)
