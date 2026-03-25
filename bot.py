import logging
from aiogram import Bot, Dispatcher, types, executor
from config import BOT_TOKEN, ADMIN_ID

# =========================
# 🌐 UPTIMEROBOT (24/7)
# =========================
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# =========================
# BOT
# =========================
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =========================
# MENULAR
# =========================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📤 Sotish", "📥 Sotib olish")
    kb.add("💰 Hisob", "📊 Statistika")
    kb.add("💎 UC Narxlari", "🆘 Yordam")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Balans qo‘shish", "➖ Balans yechish")
    kb.add("🔙 Orqaga")
    return kb

def narx_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👤 Sotuvchi narxlari", "🛒 Xaridor narxlari")
    kb.add("🔙 Orqaga")
    return kb

# =========================
# START
# =========================
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer("Xush kelibsiz!", reply_markup=main_menu())

# =========================
# 🔐 ADMIN PANEL
# =========================
@dp.message_handler(commands=['admin'])
async def admin(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("❌ Siz admin emassiz")
        return

    await msg.answer("🔐 Admin panel", reply_markup=admin_menu())

# =========================
# 🔙 ORQAGA
# =========================
@dp.message_handler(lambda m: m.text == "🔙 Orqaga")
async def back(msg: types.Message):
    await msg.answer("Menu", reply_markup=main_menu())

# =========================
# 💎 UC NARXLARI
# =========================
@dp.message_handler(lambda m: m.text == "💎 UC Narxlari")
async def narx(msg: types.Message):
    await msg.answer("Bo‘limni tanlang:", reply_markup=narx_menu())

# 👤 SOTUVCHI
@dp.message_handler(lambda m: m.text == "👤 Sotuvchi narxlari")
async def seller_price(msg: types.Message):
    text = """
👤 SOTUVCHI UCHUN NARXLAR:

60 UC = 7 000 so‘m
120 UC = 14 000 so‘m
240 UC = 28 000 so‘m
325 UC = 38 000 so‘m
660 UC = 77 000 so‘m
"""
    await msg.answer(text)

# 🛒 XARIDOR
@dp.message_handler(lambda m: m.text == "🛒 Xaridor narxlari")
async def buyer_price(msg: types.Message):
    text = """
🛒 XARIDOR UCHUN NARXLAR:

60 UC = 10 000 so‘m
120 UC = 20 000 so‘m
240 UC = 40 000 so‘m
325 UC = 52 000 so‘m
660 UC = 110 000 so‘m
"""
    await msg.answer(text)

# =========================
# 🆘 YORDAM
# =========================
@dp.message_handler(lambda m: m.text == "🆘 Yordam")
async def help_section(msg: types.Message):
    await msg.answer("Muammo yozing:")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    keep_alive()  # 🔥 24/7 uchun
    executor.start_polling(dp, skip_updates=True)
